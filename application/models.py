
import application.config
from application import db
from application.misc import get_mentions, sql_like_escape

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
            user.notify_of_follow(self) # notification
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
            msg._author.notify_of_like(self, msg) # notification

    def get_notification_count(self):
        return Notification.query.filter_by(userid = self.userid, unread = True).count()

    def get_notifications(self, set_as_read):
        result = []
        for notif in Notification.query.filter_by(userid = self.userid, unread = True).order_by(Notification.notifid.desc()).all():
            result.append(notif)
        if set_as_read:
            for notif in result:
                notif.read()
        return result

    def set_notifications_read_up_to(self, max_id):
        db.engine.execute(text("UPDATE " + Notification.__tablename__ + " SET unread = FALSE WHERE notifid <= :notifid AND userid = :userid").params(userid = self.userid, notifid = max_id))

    def notify_of_follow(self, followed_by):
        if self.is_banned(): # no notifications for banned users
            return
        Notification.clean_up_old()
        # if already notified with this user, block to avoid spam
        if Notification.query.filter_by(userid = self.userid, otheruserid = followed_by.userid).first():
            return
        notif = Notification.follow_notification(self, followed_by)
        if notif:
            notif.add_itself()

    def notify_of_like(self, like_by, liked_msg):
        if self.is_banned(): # no notifications for banned users
            return
        Notification.clean_up_old()
        # if already notified with this user and message, block to avoid spam
        if Notification.query.filter_by(userid = self.userid, otheruserid = like_by.userid, messageid = liked_msg.msgid).first():
            return
        notif = Notification.like_notification(self, like_by, liked_msg)
        if notif:
            notif.add_itself()

    def notify_of_reply(self, reply_by, reply_msg):
        if self.is_banned(): # no notifications for banned users
            return
        Notification.clean_up_old()
        notif = Notification.reply_notification(self, reply_by, reply_msg)
        if notif:
            notif.add_itself()

    def notify_of_mention(self, mention_by, message):
        if self.is_banned(): # no notifications for banned users
            return
        Notification.clean_up_old()
        notif = Notification.mention_notification(self, mention_by, message)
        if notif:
            notif.add_itself()

    @staticmethod
    def search_users(current_user, search, limit, before, after):
        rev = before != None
        cons, keys, stok = "", {}, 0
        for word in search[0]:
            stok += 1
            cons += " AND (lower(' ' || users.username || ' ') LIKE '% ' || :stok" + str(stok) + " || ' %' ESCAPE '\\'"
            cons += " OR lower(' ' || users.displayname || ' ') LIKE '% ' || :stok" + str(stok) + " || ' %' ESCAPE '\\')"
            keys["stok" + str(stok)] = sql_like_escape(word).lower()
        stmt = text(("SELECT users.* FROM users WHERE users.banned = false "
                   + "{} {} GROUP BY users.userid ORDER BY users.userid " 
                   + ("ASC" if rev else "DESC") + " LIMIT :limit"
                   ).format(cons, "AND users.userid >= :before" if before != None else 
                           ("AND users.userid <= :after" if after != None else ""))
                   ).params(userid = current_user.get_id(), limit = limit, before = before, after = after, **keys)
        res = db.engine.execute(stmt)
        users = []
        for row in res:
            users.append({"id": row[0], "user": User.reconstruct(row[:11])})
        if rev:
            users = users[::-1]
        return users

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

    _author = relationship("User", foreign_keys = [author])
    _reply = relationship("Message", foreign_keys = [reply], lazy = "dynamic")

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
        if self.is_reply: # reply notification
            Message.query.filter_by(msgid = self.reply).first()._author.notify_of_reply(self._author, self)
        for username in get_mentions(self.contents): # mention notification
            u = User.query.filter_by(username = username).first()
            if u:
                u.notify_of_mention(self._author, self)

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

    def get_message_replies(self, current_user, limit, before, after):
        rev = before != None
        stmt = text(("SELECT m.*, u.userid, u.username, u.displayname, "
                   + "COUNT(CASE WHEN likes.user = :userid THEN likes.user "
                   + "ELSE NULL END), COUNT(likes.user), COUNT(r.msgid) "
                   + "FROM msgs m JOIN users u ON (u.userid = m.author) "
                   + "LEFT JOIN likes ON likes.msg = m.msgid LEFT JOIN "
                   + "msgs r ON r.reply = m.msgid WHERE m.reply = :msgid AND "
                   + "(u.userid = :userid OR (u.banned = false AND "
                   + "u.msgsareprivate = false)) {} GROUP BY m.msgid, u.userid "
                   + "ORDER BY m.postdate " + ("ASC" if rev else "DESC") 
                   + " LIMIT :limit"
                   ).format("AND m.msgid >= :before" if before != None else 
                           ("AND m.msgid <= :after" if after != None else ""))
                   ).params(msgid = self.msgid, userid = current_user.get_id(), limit = limit, before = before, after = after)
        res = db.engine.execute(stmt)
        msgs = []
        for row in res:
            msgs.append({"id": row[0], "msg": Message.reconstruct(row[:8]), "user": {"userid": row[8], "username": row[9], "displayname": row[10]}, "has_liked": row[11] > 0, "likes": row[12], "replies": row[13]})
        if rev:
            msgs = msgs[::-1]
        return msgs

    def get_most_important_message_replies(self, current_user):
        stmt = text(("SELECT m.*, u.userid, u.username, u.displayname, "
                   + "COUNT(CASE WHEN likes.user = :userid THEN likes.user "
                   + "ELSE NULL END), COUNT(likes.user), COUNT(r.msgid) "
                   + "FROM msgs m JOIN users u ON (u.userid = m.author) "
                   + "LEFT JOIN likes ON likes.msg = m.msgid LEFT JOIN "
                   + "msgs r ON r.reply = m.msgid WHERE m.reply = :msgid AND "
                   + "(u.userid = :userid OR (u.banned = false AND "
                   + "u.msgsareprivate = false)) GROUP BY m.msgid, u.userid "
                   + "ORDER BY COUNT(likes.user) DESC LIMIT :limit" 
                   )).params(msgid = self.msgid, userid = current_user.get_id(), limit = 10)
        res = db.engine.execute(stmt)
        msgs = []
        for row in res:
            msgs.append({"id": row[0], "msg": Message.reconstruct(row[:8]), "user": {"userid": row[8], "username": row[9], "displayname": row[10]}, "has_liked": row[11] > 0, "likes": row[12], "replies": row[13]})
        return msgs

    @staticmethod
    def search_messages(current_user, search, limit, before, after):
        rev = before != None
        cons, keys, stok = "", {}, 0
        for word in search[0]:
            stok += 1
            cons += " AND lower(' ' || m.contents || ' ') LIKE '% ' || :stok" + str(stok) + " || ' %' ESCAPE '\\'"
            keys["stok" + str(stok)] = sql_like_escape(word).lower()
        if "by" in search[1]:
            cons += " AND lower(u.username) = lower(:byusername)"
            keys["byusername"] = search[1]["by"].lower()
        stmt = text(("SELECT m.*, u.userid, u.username, "
                   + "u.displayname, COUNT(CASE WHEN likes.user = :userid THEN "
                   + "likes.user ELSE NULL END), COUNT(likes.user), "
                   + "COUNT(r.msgid) FROM msgs m JOIN users u ON "
                   + "(u.userid = m.author) LEFT "
                   + "JOIN likes ON likes.msg = m.msgid LEFT JOIN msgs r ON "
                   + "r.reply = m.msgid WHERE (u.userid = :userid OR "
                   + "(u.banned = false AND u.msgsareprivate = false)) {} {} "
                   + "GROUP BY m.msgid, u.userid ORDER BY m.postdate "
                   + ("ASC" if rev else "DESC") + " LIMIT :limit"
                   ).format(cons, "AND m.msgid >= :before" if before != None else 
                           ("AND m.msgid <= :after" if after != None else ""))
                   ).params(userid = current_user.get_id(), limit = limit, before = before, after = after, **keys)
        res = db.engine.execute(stmt)
        msgs = []
        for row in res:
            msgs.append({"id": row[0], "msg": Message.reconstruct(row[:8]), "user": {"userid": row[8], "username": row[9], "displayname": row[10]}, "has_liked": row[11] > 0, "likes": row[12], "replies": row[13]})
        if rev:
            msgs = msgs[::-1]
        return msgs

class ReportUser(db.Model):
    __tablename__ = "userreports"
    reportid = Column(Integer, primary_key = True)
    reported_by = Column(Integer, ForeignKey("users.userid", ondelete = "CASCADE"))
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

    @staticmethod
    def get_reports(current_user, limit, before, after):
        if not current_user.is_authenticated or not current_user.has_admin_rights():
            return []
        rev = before != None
        stmt = text(("SELECT r.reportid, r.reason, a.username, a.displayname, "
                   + "u.username, u.displayname FROM userreports r JOIN "
                   + "users a ON a.userid = r.reported_by JOIN users u ON "
                   + "u.userid = r.user_reported GROUP BY r.reportid, "
                   + "a.userid, u.userid "
                   + "ORDER BY r.reportdate " + ("ASC" if rev else "DESC") 
                   + " LIMIT :limit"
                   ).format("AND r.reportid >= :before" if before != None else 
                           ("AND r.reportid <= :after" if after != None else ""))
                   ).params(limit = limit, before = before, after = after)
        res = db.engine.execute(stmt)
        reports = []
        for row in res:
            reports.append({"id": row[0], "reason": row[1], "author_username": row[2], "author_name": row[3], "target_username": row[4], "target_name": row[5]})
        if rev:
            reports = reports[::-1]
        return reports

class ReportMessage(db.Model):
    __tablename__ = "msgreports"
    reportid = Column(Integer, primary_key = True)
    reported_by = Column(Integer, ForeignKey("users.userid", ondelete = "CASCADE"))
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

    @staticmethod
    def get_reports(current_user, limit, before, after):
        if not current_user.is_authenticated or not current_user.has_admin_rights():
            return []
        rev = before != None
        stmt = text(("SELECT r.reportid, r.reason, a.username, a.displayname, "
                   + "u.username, u.displayname, m.msgid, m.contents FROM "
                   + "msgreports r JOIN users a ON a.userid = r.reported_by " 
                   + "JOIN msgs m ON m.msgid = r.msg_reported JOIN users u ON "
                   + "u.userid = m.author GROUP BY r.reportid, "
                   + "a.userid, u.userid, m.msgid "
                   + "ORDER BY r.reportdate " + ("ASC" if rev else "DESC") 
                   + " LIMIT :limit"
                   ).format("AND r.reportid >= :before" if before != None else 
                           ("AND r.reportid <= :after" if after != None else ""))
                   ).params(limit = limit, before = before, after = after)
        res = db.engine.execute(stmt)
        reports = []
        for row in res:
            reports.append({"id": row[0], "reason": row[1], "author_username": row[2], "author_name": row[3], "target_username": row[4], "target_name": row[5], "msg_id": row[6], "msg_text": row[7]})
        if rev:
            reports = reports[::-1]
        return reports

class Notification(db.Model):
    __tablename__ = "notifications"
    notifid = Column(Integer, primary_key = True)
    kind = Column(Integer, nullable = False)
        # 0 = new follower, 1 = message liked, 2 = reply to message, 3 = new mention
    userid = Column(Integer, ForeignKey("users.userid", ondelete = "CASCADE"), nullable = False)
    otheruserid = Column(Integer, ForeignKey("users.userid", ondelete = "CASCADE"))
    messageid = Column(Integer, ForeignKey("msgs.msgid", ondelete = "CASCADE"))
    notificationdate = Column(DateTime, nullable = False, default = func.current_timestamp())
    unread = Column(Boolean, nullable = False, default = True)

    user = relationship("User", foreign_keys = [userid])
    otheruser = relationship("User", foreign_keys = [otheruserid])
    message = relationship("Message", foreign_keys = [messageid])

    # not to be used directly: use one of the four class methods instead
    def __init__(self, kind, userid, otheruserid = None, messageid = None):
        self.kind = kind
        self.userid = userid
        self.otheruserid = otheruserid
        self.messageid = messageid
        self.unread = True

    @classmethod
    def follow_notification(cls, user, follower):
        if user.is_banned() or user.get_id() == follower.get_id():
            return None
        return cls(0, user.get_id(), follower.get_id())

    @classmethod
    def like_notification(cls, user, liked_by, liked_msg):
        if user.is_banned() or user.get_id() == liked_by.get_id():
            return None
        return cls(1, user.get_id(), liked_by.get_id(), liked_msg.get_id())

    @classmethod
    def reply_notification(cls, user, reply_by, reply_to_msg):
        if user.is_banned() or user.get_id() == reply_by.get_id():
            return None
        return cls(2, user.get_id(), reply_by.get_id(), reply_to_msg.get_id())

    @classmethod
    def mention_notification(cls, user, mention_by, mention_in_msg):
        if user.is_banned() or user.get_id() == mention_by.get_id():
            return None
        return cls(3, user.get_id(), mention_by.get_id(), mention_in_msg.get_id())

    @staticmethod
    def clean_up_old():
        db.engine.execute(text("DELETE FROM " + Notification.__tablename__ + " WHERE notificationdate < now() - interval '{} hours'".format(int(application.config.NOTIFICATIONS_MAX_AGE))))

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

db.Index("idx_user_from_id", User.userid, unique = True)
db.Index("idx_msg_from_id", Message.msgid, unique = True)
db.Index("idx_msgs_from_user", Message.author)
db.Index("idx_followeds_from_user", table_Follows.c.follower)
db.Index("idx_likes_from_msg", table_Likes.c.msg)
db.Index("idx_notifs_from_user", Notification.userid)
