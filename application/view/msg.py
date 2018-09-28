
import application.models
from application.misc import parse_search
from application.view.feed import MSGS_PER_PAGE

def get_user_messages(user, current_user, limit = MSGS_PER_PAGE, before = None, after = None):
    return user.get_user_messages(current_user, limit, before, after)

def get_feed_from_user(user, limit = MSGS_PER_PAGE, before = None, after = None):
    return user.get_feed(limit, before, after)

def get_liked_messages(user, current_user, limit = MSGS_PER_PAGE, before = None, after = None):
    return user.get_liked_messages(current_user, limit, before, after)

def get_message_replies(msg, current_user, limit = MSGS_PER_PAGE, before = None, after = None):
    return msg.get_message_replies(current_user, limit, before, after)

def search_for_messages(current_user, q, limit = MSGS_PER_PAGE, before = None, after = None):
    return application.models.Message.search_messages(current_user, parse_search(q, allowed_keys = ["by"]), limit, before, after)

