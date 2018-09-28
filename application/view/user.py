
import application.models
from application.misc import parse_search
from application.view.feed import MSGS_PER_PAGE

def get_followed_users(user, limit = MSGS_PER_PAGE, before = None, after = None):
    return user.get_followed_users(limit, before, after)

def get_followers(user, limit = MSGS_PER_PAGE, before = None, after = None):
    return user.get_followers(limit, before, after)

def search_for_users(current_user, q, limit = MSGS_PER_PAGE, before = None, after = None):
    return application.models.User.search_users(current_user, parse_search(q), limit, before, after)
