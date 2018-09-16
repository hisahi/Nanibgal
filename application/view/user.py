
from application.view.feed import MSGS_PER_PAGE

def get_followed_users(user, limit = MSGS_PER_PAGE, before = None, after = None):
    return user.get_followed_users(limit, before, after)

def get_followers(user, limit = MSGS_PER_PAGE, before = None, after = None):
    return user.get_followers(limit, before, after)
