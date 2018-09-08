
from application import db
import application.config

from sqlalchemy import *
from sqlalchemy.orm import relationship

import bcrypt, json, datetime

table_Likes = db.Table("likes",
    Column("user", Integer, ForeignKey("users.userid", ondelete = "CASCADE")),
    Column("msg", Integer, ForeignKey("msgs.msgid", ondelete = "CASCADE"))
)

table_MsgTag = db.Table("msgtag",
    Column("msg", Integer, ForeignKey("msgs.msgid", ondelete = "CASCADE")),
    Column("tag", Integer, ForeignKey("tags.tagid", ondelete = "CASCADE"))
)

table_Follows = db.Table("follows",
    Column("follower", Integer, ForeignKey("users.userid", ondelete = "CASCADE")),
    Column("followed", Integer, ForeignKey("users.userid", ondelete = "CASCADE"))
)

class User(db.Model):
    __tablename__ = "users"
    userid = Column(Integer, primary_key = True)
    username = Column(String(32), nullable = False)
    displayname = Column(String(64), nullable = False)
    bio = Column(Text, default = "")
    email = Column(String(256), nullable = False)
    passhash = Column(Binary(60), nullable = False)
    registered = Column(DateTime, nullable = False, default = func.current_timestamp())
    is_admin = Column(Boolean, default = False)
    config = Column(Text, default = False)

    messages = relationship("Message")
    likes = relationship("Message", secondary = table_Likes, backref = db.backref("users_who_liked", lazy="dynamic"), lazy="dynamic")
    followers = relationship("User", secondary = table_Follows, foreign_keys = table_Follows.c.followed, backref = db.backref("follows", lazy="dynamic"), lazy="dynamic")

    def __init__(self, username, email, password):
        self.username = username
        self.displayname = username
        self.email = email
        self.config = self.get_default_config()
        self.change_password(password)

    def add_itself(self):
        db.session.add(self)
        db.session.commit()
        # user should always be following itself
        if not self.is_following(self):
            self.toggle_follow(self)

    def terminate(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()
  
    def get_id(self):
        return self.userid

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True

    def get_default_config(self):
        settings = {}
        settings["follows_are_private"] = False
        settings["messages_are_private"] = False
        return json.dumps(settings)
    
    def are_follows_private(self):
        try:
            return bool(json.loads(self.config)["follows_are_private"])
        except:
            self.config = self.get_default_config()
            return False
    
    def are_messages_private(self):
        try:
            return bool(json.loads(self.config)["messages_are_private"])
        except:
            self.config = self.get_default_config()
            return False

    # True if password correct
    def password_ok(self, password):
        return bcrypt.checkpw(password.encode("utf-8"), self.passhash)

    def get_user_name(self):
        return self.username

    def get_display_name(self):
        return self.displayname

    def get_user_bio(self):
        return self.bio or ""

    def change_password(self, password):
        self.passhash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    def set_config_flag(self, key, value):
        settings = json.loads(self.config)
        settings[key] = value
        self.config = json.dumps(settings)

    def set_follows_private(self, value):
        self.set_config_flag("follows_are_private", value)

    def set_messages_private(self, value):
        self.set_config_flag("messages_are_private", value)

    def set_display_name(self, value):
        self.displayname = value

    def get_user_messages(self, limit, offset):
        stmt = text("SELECT msgs.msgid, msgs.author, msgs.contents, "
                  + "msgs.link, msgs.postdate, msgs.editdate, msgs.reply, "
                  + "COUNT(CASE WHEN likes.user = :userid THEN likes.user "
                  + "ELSE NULL END) FROM msgs LEFT JOIN likes ON "
                  + "likes.msg = msgs.msgid WHERE msgs.author = :userid "
                  + "GROUP BY msgs.msgid LIMIT :limit OFFSET :offset"
                  ).params(userid = self.userid, offset = offset, limit = limit)
        res = db.engine.execute(stmt)
        msgs = []
        for row in res:
            msgs.append({"msg": Message.reconstruct(row[:7]), "liked": row[7] > 0})
        return msgs

    def get_feed(self, limit, offset):
        stmt = text("SELECT m.msgid, m.author, m.contents, m.link, m.postdate, "
                  + "m.editdate, m.reply, u.userid, u.username, COUNT(CASE WHEN "
                  + "likes.user = :userid THEN likes.user ELSE NULL END) FROM "
                  + "follows f JOIN msgs m ON (m.author = f.followed) JOIN "
                  + "users u ON (u.userid = m.author) LEFT JOIN likes ON "
                  + "likes.msg = m.msgid WHERE f.follower = :userid GROUP BY "
                  + "m.msgid, u.userid ORDER BY m.postdate DESC LIMIT :limit "
                  + "OFFSET :offset"
                  ).params(userid = self.userid, offset = offset, limit = limit)
        res = db.engine.execute(stmt)
        msgs = []
        for row in res:
            msgs.append({"msg": Message.reconstruct(row[:7]), "user": FakeUser(row[7], row[8]), "liked": row[9] > 0})
        return msgs

    def is_following_id(self, uid):
        for row in (db.session.query(table_Follows.c.follower)
                            .filter(table_Follows.c.follower == self.userid)
                            .filter(table_Follows.c.followed == uid).all()):
            return True
        return False

    def is_following(self, user):
        return self.is_following_id(user.get_id())

    def toggle_follow(self, user):
        if self.is_following(user):
            # unfollow
            stmt = text("DELETE FROM " + table_Follows.name + " "
                  + "WHERE follower = :follower AND followed = :followed"
                  ).params(follower = self.userid, followed = user.userid)
            db.engine.execute(stmt)
        else:
            # follow
            db.session.execute(table_Follows.insert().values(
                                follower = self.userid,
                                followed = user.userid))
            db.session.commit()

class FakeUser():
    def __init__(self, uid, uname):
        self.userid = uid
        self.username = uname
  
    def get_id(self):
        return self.userid

    def get_user_name(self):
        return self.username

class Message(db.Model):
    __tablename__ = "msgs"
    msgid = Column(Integer, primary_key = True)
    author = Column(Integer, ForeignKey("users.userid", ondelete = "CASCADE"))
    contents = Column(String(256), nullable = False)
    link = Column(String(256))
    postdate = Column(DateTime, nullable = False, default = func.current_timestamp())
    editdate = Column(DateTime)
    reply = Column(Integer, ForeignKey("msgs.msgid", ondelete = "SET NULL"))

    def __init__(self, author, text, link = None, reply = None):
        if type(author) == User:
            self.author = author.get_id()
        else:
            self.author = author
        self.contents = text
        if link:
            self.link = link
        if reply:
            self.reply = reply.msgid
    
    @staticmethod
    def reconstruct(row):
        msg = Message(None, None, None)
        msg.msgid, msg.author, msg.contents, msg.link, msg.postdate, msg.editdate, msg.reply = row
        return msg

    def add_itself(self):
        db.session.add(self)
        db.session.commit()

    def terminate(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def get_id(self):
        return self.msgid

    def get_text(self):
        return self.contents

    def get_date(self):
        return self.editdate or self.postdate

    def has_been_edited(self):
        return self.editdate != None

    def get_date_iso(self):
        res = self.get_date().isoformat()
        if self.has_been_edited():
            res += "*"
        return res

    def get_author_user_name(self):
        return User.query.filter_by(userid = self.author).first().get_user_name()

    def edit_message(self, text):
        self.contents = text[:256]
        self.editdate = func.current_timestamp()
        self.update()

class Tag(db.Model):
    __tablename__ = "tags"
    tagid = Column(Integer, primary_key = True)
    tagname = Column(String(32), nullable = False)

    messages = relationship("Message", secondary = table_MsgTag, backref = db.backref("tags", lazy="dynamic"), lazy="dynamic")

    def __init__(self, name):
        self.tagname = name

    def add_itself(self):
        db.session.add(self)
        db.session.commit()

    def terminate(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()

class ReportUser(db.Model):
    __tablename__ = "userreports"
    reportid = Column(Integer, primary_key = True)
    reported_by = Column(Integer, ForeignKey("users.userid", ondelete = "SET NULL"))
    user_reported = Column(Integer, ForeignKey("users.userid", ondelete = "CASCADE"))
    reason = Column(String(128), nullable = False)
    reportdate = Column(DateTime, nullable = False, default = func.current_timestamp())

    def __init__(self, reporter, reported_user, reason):
        self.reported_by = reporter.userid
        self.user_reported = reported_user.userid
        self.reason = reason

    def add_itself(self):
        db.session.add(self)
        db.session.commit()

    def terminate(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()

class ReportMessage(db.Model):
    __tablename__ = "msgreports"
    reportid = Column(Integer, primary_key = True)
    reported_by = Column(Integer, ForeignKey("users.userid", ondelete = "SET NULL"))
    msg_reported = Column(Integer, ForeignKey("msgs.msgid", ondelete = "CASCADE"))
    reason = Column(String(128), nullable = False)
    reportdate = Column(DateTime, nullable = False, default = func.current_timestamp())

    def __init__(self, reporter, reported_msg, reason):
        self.reported_by = reporter.userid
        self.msg_reported = reported_msg.msgid
        self.reason = reason

    def add_itself(self):
        db.session.add(self)
        db.session.commit()

    def terminate(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()

db.Index("idx_msgs_from_user", Message.author)
db.Index("idx_user_from_id", User.userid)
db.Index("idx_followeds_from_user", table_Follows.c.follower)
db.Index("idx_likes_from_msg", table_Likes.c.msg)
db.Index("idx_tags_from_msg", table_MsgTag.c.msg)
db.Index("idx_msgs_from_tag", table_MsgTag.c.tag)
