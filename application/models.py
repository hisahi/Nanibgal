
from application import db
import application.config

from sqlalchemy import *
from sqlalchemy.orm import relationship

import bcrypt, json

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

    def change_password(self, password):
        self.passhash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    def set_config(self, key, value):
        settings = json.loads(self.config)
        settings[key] = value
        self.config = json.dumps(settings)

    def set_follows_private(self, value):
        self.set_config("follows_are_private", value)

    def set_messages_private(self, value):
        self.set_config("messages_are_private", value)

    def set_display_name(self, value):
        self.displayname = value

class Message(db.Model):
    __tablename__ = "msgs"
    msgid = Column(Integer, primary_key = True)
    author = Column(Integer, ForeignKey("users.userid", ondelete = "CASCADE"))
    contents = Column(String(256), nullable = False)
    link = Column(String(256))
    postdate = Column(DateTime, nullable = False, default = func.current_timestamp())
    editdate = Column(DateTime)
    reply = Column(Integer, ForeignKey("msgs.msgid", ondelete = "SET NULL"))

    def __init__(self, author, text, reply = None):
        self.author = author.userid
        self.contents = text
        if self.reply:
            self.reply = reply.msgid

    def add_itself(self):
        db.session.add(self)
        db.session.commit()

    def terminate(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()

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
