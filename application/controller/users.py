
import application.models
from sqlalchemy import func

def get_user_by_id(userid):
    return application.models.User.query.filter_by(userid = userid).first()

def get_user_by_name(username):
    return application.models.User.query.filter(func.lower(application.models.User.username) == func.lower(username)).first()
