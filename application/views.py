
from application import app

import application.config
import jinja2.exceptions
from application.misc import get_safe_url, populate_dict

from flask import render_template, request, redirect, url_for, abort
from flask_login import current_user, login_required, login_user, logout_user, fresh_login_required
from application.i18n import Language
from application.view.feed import FeedView
from application.view.user import UserView
from application.view.msg import MessageView
from application.view.render import render_message
from application.view.form import LoginForm, RegisterForm, NewPostForm, SettingsForm
from application.controller.login import login
from application.controller.register import register
from application.controller.settings import handle_settings

@app.route("/")
def route_feed(): # 𒀭𒀭𒊺𒉀
    lang = Language("en")
    if current_user.is_authenticated:
        return render_template("feed.html", lang = lang, feed = FeedView())
    else:
        return redirect(url_for("route_login"))

@app.route("/static/<filename>")
def route_static_global(filename):
    try:
        return render_template(url_for("static", filename=filename))
    except jinja2.exceptions.TemplateNotFound:
        abort(404)

@app.route("/@<username>")
def route_profile(username):
    lang = Language("en")
    return render_template("user.html", lang = lang, user = UserView(lang))

@app.route("/@<username>/<int:postid>")
def route_message(username, postid):
    lang = Language("en")
    return render_template("message.html", lang = lang, message = MessageView(lang))

@app.route("/login", methods = ["GET", "POST"])
def route_login():
    lang = Language("en")
    if current_user.is_authenticated:
        return redirect(url_for("route_feed"))
    error = None
    if request.method == "POST":
        user_obj, error = login(request.form["username"], request.form["password"])
        if user_obj:
            login_user(user_obj, remember = request.form.get("remember", False))
            return redirect(get_safe_url(request.host_url, request.form["next"] or url_for("route_feed"), url_for("route_feed")))
        if error:
            error = lang.tr(error)
    return render_template("login.html", lang = lang, form = LoginForm().localized(lang), error = error)

@app.route("/register", methods = ["GET", "POST"])
def route_register():
    lang = Language("en")
    if current_user.is_authenticated:
        return redirect(url_for("route_feed"))
    error = None
    if request.method == "POST":
        user_obj, error = register(request.form["username"], request.form["password"], request.form["verify"])
        if user_obj:
            login_user(user_obj, remember = request.form.get("remember", False))
            return redirect(url_for("route_feed"))
        if error:
            error = lang.tr(error)
    return render_template("register.html", lang = lang, form = RegisterForm().localized(lang), error = error)

@app.route("/search", methods = ["GET", "POST"])
@login_required
def route_search():
    lang = Language("en")
    return render_template("search.html", lang = lang)

@app.route("/new", methods = ["GET", "POST"])
@login_required
def route_new():
    lang = Language("en")
    reply_id = request.args.get("reply", default = None)
    return render_template("new.html", lang = lang, form = NewPostForm().localized(lang), reply = msgrender.render(reply_id))

@app.route("/settings", methods = ["GET", "POST"])
@fresh_login_required
def route_settings():
    lang = Language("en")
    error = None
    success = False
    if request.method == "POST":
        error = handle_settings(current_user.get_id(), request.form)
        if error:
            error = lang.tr(error)
        else:
            success = True
    form = SettingsForm(obj=populate_dict({
        "displayname": current_user.get_display_name(),
        "privatemessages": current_user.are_messages_private(), 
        "privatefollows": current_user.are_follows_private()
    })).localized(lang)
    return render_template("settings.html", lang = lang, form = form, error = error, success = success)

@app.route("/logout")
@login_required
def route_logout():
    logout_user()
    return redirect(url_for("route_login"))
