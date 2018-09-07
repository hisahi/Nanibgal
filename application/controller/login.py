
import application.models

def login(username, password):
    # find user by username
    obj = application.models.User.query.filter_by(username = username[:32]).first()
    # if no user with this username
    if obj == None:
        return (None, "login.invalid")
    # if password is incorrect
    if not obj.password_ok(password[:256]):
        return (None, "login.invalid")
    # return LoginUser object
    return (obj, None)
