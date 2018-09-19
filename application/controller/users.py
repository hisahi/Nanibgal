
import application.models
from sqlalchemy import func

def get_user_by_id(userid):
    return application.models.User.query.filter_by(userid = userid).first()

def get_user_by_name(username):
    return application.models.User.query.filter(func.lower(application.models.User.username) == func.lower(username)).first()

def toggle_follow(user, other_user):
    if other_user == None:
        return 400
    if other_user.are_messages_private() or other_user.is_banned():
        return 403
    user.toggle_follow(other_user)
    return 200

def toggle_ban(other_user):
    if other_user == None:
        return 400
    other_user.toggle_ban()
    return 200
