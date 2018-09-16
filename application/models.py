
from application import db
import application.config

from sqlalchemy import *
from sqlalchemy.orm import relationship

import bcrypt, json, datetime

table_Likes = db.Table("likes",
    Column("user", Integer, ForeignKey("users.userid", ondelete = "CASCADE")),
    Column("msg", Integer, ForeignKey("msgs.msgid", ondelete = "CASCADE"))
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
    banned = Column(Boolean, default = False)
    msgsareprivate = Column(Boolean, default = False)
    config = Column(Text, default = False)

    messages = relationship("Message")
    likes = relationship("Message", secondary = table_Likes, backref = db.backref("users_who_liked", lazy="dynamic"), lazy="dynamic")
    followers = relationship("User", secondary = table_Follows, foreign_keys = table_Follows.c.followed, backref = db.backref("follows", lazy="dynamic"), lazy="dynamic")

    def __init__(self, username, email, password):
        self.username = username
        self.displayname = username
        self.email = email
        self.config = self.get_default_config()
        self.is_admin = self.banned = self.msgsareprivate = False
        if password != None:
            self.change_password(password)
    
    @staticmethod
    def reconstruct(row):
        user = User(None, None, None)
        user.userid, user.username, user.displayname, user.bio, user.email, user.passhash, user.registered, user.is_admin, user.banned, user.msgsareprivate, user.config = row
        return user

    def add_itself(self):
        db.session.add(self)
        db.session.commit()
        # user should always be following itself
        try:
            if not self.is_following(self):
                self.toggle_follow(self)
        except:
            # follow
            db.session.execute(table_Follows.insert().values(
                                follower = self.userid,
                                followed = self.userid))
            db.session.commit()

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

    def has_admin_rights(self):
        return self.is_admin or False

    def is_banned(self):
        return self.banned or False

    def get_default_config(self):
        settings = {}
        settings["follows_are_private"] = False
        settings["likes_are_private"] = False
        settings["language"] = "en"
        return json.dumps(settings)
    
    def are_messages_private(self):
        return self.msgsareprivate
    
    def are_follows_private(self):
        try:
            return bool(json.loads(self.config)["follows_are_private"])
        except:
            self.config = self.get_default_config()
            self.update()
            return False
    
    def are_likes_private(self):
        try:
            return bool(json.loads(self.config)["likes_are_private"])
        except:
            self.config = self.get_default_config()
            self.update()
            return False
    
    def get_language(self):
        try:
            return json.loads(self.config)["language"]
        except:
            self.config = self.get_default_config()
            self.update()
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

    def set_messages_private(self, value):
        self.msgsareprivate = value

    def set_follows_private(self, value):
        self.set_config_flag("follows_are_private", value)

    def set_likes_private(self, value):
        self.set_config_flag("likes_are_private", value)

    def set_language(self, value):
        if value not in application.config.LANGUAGES:
            value = "en"
        self.set_config_flag("language", value)

    def set_display_name(self, value):
        self.displayname = value

    def set_user_bio(self, bio):
        self.bio = bio[:256]

    def get_user_messages(self, current_user, limit, before, after):
        # return {"id": message ID, "msg": message object, "has_liked": has_this_user_liked, "likes": number_of_likes, "replies": number_of_replies}
        # return empty if user is banned or set messages as private, unless the current user is themselves or an admin
        rev = before != None
        if (self.are_messages_private() or self.is_banned()) and (not current_user.is_authenticated or (self.userid != current_user.userid and not current_user.has_admin_rights())):
            return []
        stmt = text(("SELECT msgs.*, COUNT(CASE WHEN likes.user = :curid THEN "
                   + "likes.user ELSE NULL END), COUNT(likes.user), COUNT(r.msgid) "
                   + "FROM msgs LEFT JOIN likes ON likes.msg = msgs.msgid "
                   + "LEFT JOIN msgs r ON r.reply = msgs.msgid WHERE msgs.author = "
                   + ":userid {} GROUP BY msgs.msgid ORDER BY msgs.postdate " 
                   + ("ASC" if rev else "DESC") + " LIMIT :limit"
                   ).format("AND msgs.msgid >= :before" if before != None else 
                           ("AND msgs.msgid <= :after" if after != None else ""))
                   ).params(userid = self.userid, curid = current_user.get_id(), limit = limit, before = before, after = after)
        res = db.engine.execute(stmt)
        msgs = []
        for row in res:
            msgs.append({"id": row[0], "msg": Message.reconstruct(row[:8]), "has_liked": row[8] > 0, "likes": row[9], "replies": row[10]})
        if rev:
            msgs = msgs[::-1]
        return msgs

    def get_feed(self, limit, before, after):
        # return {"id": message ID, "msg": message object, "user": {"userid": ..., "username": ..., "displayname": ...}, "has_liked": has_this_user_liked, "likes": number_of_likes, "replies": number_of_replies}
        # strip out messages that are sent by banned users or users who have set messages as private, except if the current user is them
        rev = before != None
        stmt = text(("SELECT m.*, u.userid, u.username, "
                   + "u.displayname, COUNT(CASE WHEN likes.user = :userid THEN "
                   + "likes.user ELSE NULL END), COUNT(likes.user), "
                   + "COUNT(r.msgid) FROM follows f JOIN msgs m ON (m.author = "
                   + "f.followed) JOIN users u ON (u.userid = m.author) LEFT "
                   + "JOIN likes ON likes.msg = m.msgid LEFT JOIN msgs r ON "
                   + "r.reply = m.msgid WHERE f.follower = :userid AND "
                   + "(u.userid = :userid OR (u.banned = false AND "
                   + "u.msgsareprivate = false)) {} GROUP BY m.msgid, u.userid "
                   + "ORDER BY m.postdate " + ("ASC" if rev else "DESC") 
                   + " LIMIT :limit"
                   ).format("AND m.msgid >= :before" if before != None else 
                           ("AND m.msgid <= :after" if after != None else ""))
                   ).params(userid = self.userid, limit = limit, before = before, after = after)
        res = db.engine.execute(stmt)
        msgs = []
        for row in res:
            msgs.append({"id": row[0], "msg": Message.reconstruct(row[:8]), "user": {"userid": row[8], "username": row[9], "displayname": row[10]}, "has_liked": row[11] > 0, "likes": row[12], "replies": row[13]})
        if rev:
            msgs = msgs[::-1]
        return msgs

    def get_liked_messages(self, current_user, limit, before, after):
        # return {"id": message ID, "msg": message object, "has_liked": has_this_user_liked, "likes": number_of_likes, "replies": number_of_replies}
        # return empty if user is banned or set likes as private, unless the current user is themselves or an admin
        rev = before != None
        if (self.are_likes_private() or self.is_banned()) and (not current_user.is_authenticated or (self.userid != current_user.userid and not current_user.has_admin_rights())):
            return []
        stmt = text(("SELECT msgs.*, COUNT(CASE WHEN likes.user = :curid THEN "
                   + "likes.user ELSE NULL END), COUNT(likes.user), "
                   + "COUNT(r.msgid) FROM msgs LEFT JOIN likes ON likes.msg = "
                   + "msgs.msgid LEFT JOIN msgs r ON r.reply = msgs.msgid WHERE "
                   + "likes.user = :userid {} GROUP BY msgs.msgid ORDER BY " 
                   + "msgs.postdate " + ("ASC" if rev else "DESC") + " LIMIT :limit"
                   ).format("AND msgs.msgid >= :before" if before != None else 
                           ("AND msgs.msgid <= :after" if after != None else ""))
                   ).params(userid = self.userid, curid = current_user.get_id(), limit = limit, before = before, after = after)
        res = db.engine.execute(stmt)
        msgs = []
        for row in res:
            msgs.append({"id": row[0], "msg": Message.reconstruct(row[:8]), "has_liked": row[8] > 0, "likes": row[9], "replies": row[10]})
        if rev:
            msgs = msgs[::-1]
        return msgs

    def get_followed_users(self, limit, before, after):
        # return users that this user follows
        rev = before != None
        if (self.are_follows_private() or self.is_banned()) and (not current_user.is_authenticated or (self.userid != current_user.userid and not current_user.has_admin_rights())):
            return []
        stmt = text(("SELECT users.* FROM users JOIN follows ON "
                   + "follows.followed = users.userid WHERE follows.follower = "
                   + ":userid AND users.userid <> :userid {} GROUP BY "
                   + "users.userid ORDER BY users.userid " 
                   + ("ASC" if rev else "DESC") + " LIMIT :limit"
                   ).format("AND users.userid >= :before" if before != None else 
                           ("AND users.userid <= :after" if after != None else ""))
                   ).params(userid = self.userid, limit = limit, before = before, after = after)
        res = db.engine.execute(stmt)
        users = []
        for row in res:
            users.append({"id": row[0], "user": User.reconstruct(row[:11])})
        if rev:
            users = users[::-1]
        return users

    def get_followers(self, limit, before, after):
        # return users that follow this user
        rev = before != None
        if (self.are_follows_private() or self.is_banned()) and (not current_user.is_authenticated or (self.userid != current_user.userid and not current_user.has_admin_rights())):
            return []
        stmt = text(("SELECT users.* FROM users JOIN follows ON "
                   + "follows.follower = users.userid WHERE follows.followed = "
                   + ":userid AND users.userid <> :userid {} GROUP BY "
                   + "users.userid ORDER BY users.userid " 
                   + ("ASC" if rev else "DESC") + " LIMIT :limit"
                   ).format("AND users.userid >= :before" if before != None else 
                           ("AND users.userid <= :after" if after != None else ""))
                   ).params(userid = self.userid, limit = limit, before = before, after = after)
        res = db.engine.execute(stmt)
        users = []
        for row in res:
            users.append({"id": row[0], "user": User.reconstruct(row[:11])})
        if rev:
            users = users[::-1]
        return users

    def is_following_id(self, uid):
        return (db.session.query(table_Follows.c.follower)
                            .filter(table_Follows.c.follower == self.userid,
                                    table_Follows.c.followed == uid)).first() != None

    def is_following(self, user):
        return self.is_following_id(user.get_id())

    def toggle_follow(self, user):
        if self.is_following(user):
            # unfollow
            stmt = text("DELETE FROM " + table_Follows.name + " "
                  + "WHERE \"follower\" = :follower AND \"followed\" = :followed"
                  ).params(follower = self.userid, followed = user.userid)
            db.engine.execute(stmt)
        else:
            # follow
            db.session.execute(table_Follows.insert().values(
                                follower = self.userid,
                                followed = user.userid))
            db.session.commit()

    def toggle_ban(self):
        self.banned = not self.banned
        self.update()

    def has_liked_message(self, message):
        return (db.session.query(table_Likes.c.user)
                            .filter(table_Likes.c.user == self.userid)
                            .filter(table_Likes.c.msg == message.msgid)).first() != None

    def toggle_like(self, msg):
        if self.has_liked_message(msg):
            # unlike
            stmt = text("DELETE FROM " + table_Likes.name + " "
                  + "WHERE \"user\" = :user AND \"msg\" = :msg"
                  ).params(user = self.userid, msg = msg.msgid)
            db.engine.execute(stmt)
        else:
            # like
            db.session.execute(table_Likes.insert().values(
                                user = self.userid,
                                msg = msg.msgid))
            db.session.commit()

class Message(db.Model):
    __tablename__ = "msgs"
    msgid = Column(Integer, primary_key = True)
    author = Column(Integer, ForeignKey("users.userid", ondelete = "CASCADE"))
    contents = Column(String(256), nullable = False)
    link = Column(String(256))
    postdate = Column(DateTime, nullable = False, default = func.current_timestamp())
    editdate = Column(DateTime)
    is_reply = Column(Boolean, default = False)
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
            try:
                self.reply = int(reply)
                if not Message.query.filter_by(msgid == self.reply).first() != None:
                    self.reply = None
                else:
                    self.is_reply = True
            except:
                pass
    
    @staticmethod
    def reconstruct(row):
        msg = Message(None, None, None)
        msg.msgid, msg.author, msg.contents, msg.link, msg.postdate, msg.editdate, msg.is_reply, msg.reply = row
        return msg

    def add_itself(self):
        self.is_reply = (self.reply != None)
        db.session.add(self)
        db.session.commit()

    def terminate(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        self.is_reply = (self.reply != None)
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

    def get_author_id(self):
        return self.author

    def get_author(self):
        return User.query.filter_by(userid = self.author).first()

    def can_be_edited(self):
        # allow within 10 minutes
        delta = datetime.datetime.now() - self.postdate
        return delta < datetime.timedelta(0, 60 * 10, 0)

    def edit_message(self, text, link):
        self.contents = text[:256]
        if link:
            self.link = link[:256]
        else:
            self.link = None
        self.editdate = func.current_timestamp()
        self.update()

    def get_total_likes(self):
        return db.session.query(table_Likes.c.user).filter(table_Likes.c.msg == self.msgid).count()

    def get_total_replies(self):
        return Message.query.filter_by(reply = self.msgid).count()

class ReportUser(db.Model):
    __tablename__ = "userreports"
    reportid = Column(Integer, primary_key = True)
    reported_by = Column(Integer, ForeignKey("users.userid", ondelete = "SET NULL"))
    user_reported = Column(Integer, ForeignKey("users.userid", ondelete = "CASCADE"), nullable = False)
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
    msg_reported = Column(Integer, ForeignKey("msgs.msgid", ondelete = "CASCADE"), nullable = False)
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

class Notification(db.Model):
    __tablename__ = "notifications"
    notifid = Column(Integer, primary_key = True)
    kind = Column(Integer, primary_key = True)
        # 0 = new follower, 1 = message liked, 2 = reply to message, 3 = new mention
    userid = Column(Integer, ForeignKey("users.userid", ondelete = "CASCADE"), nullable = False)
    otheruserid = Column(Integer, ForeignKey("users.userid", ondelete = "CASCADE"))
    messageid = Column(Integer, ForeignKey("msgs.msgid", ondelete = "CASCADE"))
    notificationdate = Column(DateTime, nullable = False, default = func.current_timestamp())
    unread = Column(Boolean, nullable = False, default = True)

    # not to be used directly: use one of the four class methods instead
    def __init__(self, kind, userid, otheruserid = None, messageid = None):
        self.kind = kind
        self.userid = userid
        self.otheruserid = otheruserid
        self.messageid = messageid
        self.unread = True

    @classmethod
    def follow_notification(cls, user, follower):
        if user.is_banned():
            return None
        return cls(0, user.get_id(), follower)

    @classmethod
    def like_notification(cls, user, liked_by, liked_msg):
        if user.is_banned():
            return None
        return cls(1, user.get_id(), liked_by, liked_msg)

    @classmethod
    def reply_notification(cls, user, reply_by, reply_to_msg):
        if user.is_banned():
            return None
        return cls(2, user.get_id(), reply_by, reply_to_msg)

    @classmethod
    def mention_notification(cls, user, mention_by, mention_in_msg):
        if user.is_banned():
            return None
        return cls(3, user.get_id(), mention_by, mention_in_msg)

    def add_itself(self):
        db.session.add(self)
        db.session.commit()

    def terminate(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def mark_as_read(self):
        self.read = True
        self.update()

db.Index("idx_msgs_from_user", Message.author)
db.Index("idx_user_from_id", User.userid)
db.Index("idx_followeds_from_user", table_Follows.c.follower)
db.Index("idx_likes_from_msg", table_Likes.c.msg)
db.Index("idx_notifs_from_user", Notification.userid)
