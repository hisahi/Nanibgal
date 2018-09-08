
import application.models
from application.controller.users import get_user_by_name

def register(username, password, verify):
    if len(username) < 4 or len(username) > 32:
        return (None, "register.error.invalid_username_length")
    if len(password) < 8 or len(password) > 256:
        return (None, "register.error.invalid_password_length")
    if password != verify:
        return (None, "register.error.password_not_match")
    if get_user_by_name(username = username[:32]) != None:
        return (None, "register.error.username_taken")
    user = application.models.User(username, "", password)
    user.add_itself()
    return (user, None)
