
import application.models

def get_user_by_id(userid):
    return application.models.User.query.filter_by(userid = userid).first()

def get_user_by_name(username):
    return application.models.User.query.filter_by(username = username).first()
