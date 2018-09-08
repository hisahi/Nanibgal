
from flask import render_template

def render_message(lang, message, username = None, **kw):
    if message == None:
        return None
    if username == None:
        username = message.get_author_user_name()
    return render_template("message.html", lang = lang, msg = message, username = username, extra = kw)
