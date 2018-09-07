
import application.models

def register(username, password, verify):
    if len(username) < 4 or len(username) > 32:
        return (None, "register.error.invalid_username_length")
    if len(password) < 8 or len(password) > 256:
        return (None, "register.error.invalid_password_length")
    if password != verify:
        return (None, "register.error.password_not_match")
    user = application.models.User(username, "", password)
    user.add_itself()
    return (user, None)
