
import application.models
from flask_login import logout_user

def handle_settings(id, request):
    # find user by ID
    user = application.models.User.query.filter_by(userid = id).first()
    # if obj = None, something is really badly wrong
    if user == None:
        return None
    # if password is incorrect
    if not user.password_ok(request["oldpassword"][:256]):
        return "settings.invalid_old_password"
    if request["password"] or request["verify"]:
        if request["password"] == request["verify"]:
            user.change_password(user["password"])
    if request["displayname"]:
        # remove leading and trailing whitespace
        fmt = request["displayname"].strip()[:64]
        if fmt:
            user.set_display_name(fmt)
    if "privatefollows" in request:
        user.set_follows_private(request["privatefollows"])
    if "privatemessages" in request:
        user.set_messages_private(request["privatemessages"])
    user.update()
    if request["deleteaccount"]:
        if request["deleteaccount"] == user.get_user_name():
            user.terminate()
            logout_user()
        else:
            return "settings.account_not_deleted"
    return None
