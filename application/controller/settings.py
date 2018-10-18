
import application.models
from application.controller.auth import validate_username
from flask_login import logout_user

def handle_settings(id, request):
    # find user by ID
    user = application.models.User.query.filter_by(userid = id).first()
    # if obj = None, something is really badly wrong
    if user == None:
        return None
    # if password is incorrect
    if not user.password_ok(request["oldpassword"][:256]):
        return "settings.error.invalid_old_password"
    if request["password"] or request["verify"]:
        if request["password"] == request["verify"]:
            user.change_password(request["password"])
    if request["displayname"]:
        # remove leading and trailing whitespace
        fmt = request["displayname"].strip()[:64]
        if fmt:
            user.set_display_name(fmt)
    if request["bio"]:
        # remove leading and trailing whitespace
        fmt = request["bio"].strip()[:256]
        if fmt:
            user.set_user_bio(fmt)
    if request["language"]:
        user.set_language(request["language"])
    user.set_follows_private("privatefollows" in request)
    user.set_messages_private("privatemessages" in request)
    user.set_likes_private("privatelikes" in request)
    if request["username"]:
        fmt = request["username"].strip()[:20]
        if not validate_username(fmt):
            return "settings.error.invalid_username"
        if user.username != fmt:
            user.username = fmt
    user.update()
    return None

def handle_delete_account(id, request):
    # find user by ID
    user = application.models.User.query.filter_by(userid = id).first()
    # if obj = None, something is really badly wrong
    if user == None:
        return None
    if request["deleteaccount"]:
        if not user.password_ok(request["oldpassword"][:256]):
            return "settings.account_not_deleted"
        if request["deleteaccount"] == user.get_user_name():
            user.delete_self()
            logout_user()
        else:
            return "settings.account_not_deleted"
    return None
