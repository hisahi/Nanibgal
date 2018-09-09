
import application.models
from application.controller.users import get_user_by_name

def register(username, password, verify):
    if len(username) < 4 or len(username) > 20:
        return (None, "register.error.invalid_username_length")
    if len(password) < 8 or len(password) > 256:
        return (None, "register.error.invalid_password_length")
    if password != verify:
        return (None, "register.error.password_not_match")
    username = username[:20]
    if get_user_by_name(username = username) != None:
        return (None, "register.error.username_taken")
    # validate username
    if not validate_username(username):
        return (None, "register.error.invalid_username")
    user = application.models.User(username, "", password)
    user.add_itself()
    return (user, None)

def validate_username(username):
    if len(username) < 4 or len(username) > 20:
        return False
    if username[0] in "0123456789":
        return False
    for c in username:
        if c not in "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_":
            return False
    return True

def login(username, password):
    # find user by username
    obj = get_user_by_name(username = username[:32])
    # if no user with this username
    if obj == None:
        return (None, "login.invalid")
    # if password is incorrect
    if not obj.password_ok(password[:256]):
        return (None, "login.invalid")
    # return LoginUser object
    return (obj, None)
