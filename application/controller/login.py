
from application.controller.users import get_user_by_name

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
