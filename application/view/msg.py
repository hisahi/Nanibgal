
import application.models

def get_user_messages(user, offset=0, limit=25):
    return user.get_user_messages(limit, offset)

def get_feed_from_user(user, offset=0, limit=25):
    return user.get_feed(limit, offset)
