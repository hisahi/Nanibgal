
import application.models

def get_user_messages(user, current_user, limit = 25, before = None, after = None):
    return user.get_user_messages(current_user, limit, before, after)

def get_feed_from_user(user, limit = 25, before = None, after = None):
    return user.get_feed(limit, before, after)
