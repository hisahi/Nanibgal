
import application.models
from application.view.feed import MSGS_PER_PAGE

def get_user_messages(user, current_user, limit = MSGS_PER_PAGE, before = None, after = None):
    return user.get_user_messages(current_user, limit, before, after)

def get_feed_from_user(user, limit = MSGS_PER_PAGE, before = None, after = None):
    return user.get_feed(limit, before, after)

def get_liked_messages(user, current_user, limit = MSGS_PER_PAGE, before = None, after = None):
    return user.get_liked_messages(current_user, limit, before, after)

def get_message_replies(msg, current_user, limit = MSGS_PER_PAGE, before = None, after = None):
    return msg.get_message_replies(current_user, limit, before, after)
