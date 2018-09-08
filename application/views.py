
from application import app

import application.config
import jinja2.exceptions, urllib.parse
from application.misc import get_safe_url, populate_dict, bind1

from flask import render_template, request, redirect, url_for, abort
from flask_login import current_user, login_required, login_user, logout_user, fresh_login_required
from application.i18n import Language
from application.view.feed import compute_pages
from application.view.msg import get_user_messages, get_feed_from_user
from application.view.render import render_message
from application.view.form import EditPostForm, LoginForm, RegisterForm, NewPostForm, SettingsForm
from application.controller.login import login
from application.controller.messages import get_message_by_id, new_message, edit_message
from application.controller.register import register
from application.controller.reports import handle_user_report, handle_message_report
from application.controller.settings import handle_settings
from application.controller.users import get_user_by_id, get_user_by_name

# make urllib.parse available for Jinja
app.jinja_env.globals.update(urllib = urllib)

@app.route("/")
def route_feed(): # 𒀭𒀭𒊺𒉀
    lang = Language("en")
    if not current_user.is_authenticated:
        return redirect(url_for("route_login"))
    msgs, offset, next_page, prev_page = compute_pages(request.args, get_feed_from_user, current_user)
    return render_template("feed.html", lang = lang, msgs = msgs, render_message = bind1(render_message, lang), prev_page = prev_page, next_page = next_page)

@app.route("/~<username>")
def route_profile(username):
    lang = Language("en")
    user = get_user_by_name(username)
    if user == None:
        return abort(404)
    msgs, offset, next_page, prev_page = compute_pages(request.args, get_user_messages, user)
    return render_template("profile.html", lang = lang, user = user, msgs = msgs, render_message = bind1(render_message, lang), prev_page = prev_page, next_page = next_page)

@app.route("/~<username>/<int:postid>")
def route_message(username, postid):
    lang = Language("en")
    user = get_user_by_name(username)
    if user == None:
        return abort(404)
    msg = get_message_by_id(postid)
    if msg == None:
        return abort(404)
    return render_template("viewmessage.html", lang = lang, user = user, msg = msg, render_message = bind1(render_message, lang))

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
    error = None
    if request.method == "POST":
        (id, error) = new_message(current_user.get_id(), request.form)
        if error:
            error = lang.tr(error)
        else:
            return redirect(url_for("route_message", username=current_user.get_user_name(), postid=id))
    reply_id = request.args.get("reply", default = None)
    msg = get_message_by_id(reply_id)
    return render_template("new.html", lang = lang, form = NewPostForm().localized(lang), reply = render_message(lang, msg), error = error)

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
    form = SettingsForm(obj = populate_dict({
        "displayname": current_user.get_display_name(),
        "privatemessages": current_user.are_messages_private(), 
        "privatefollows": current_user.are_follows_private()
    })).localized(lang)
    return render_template("settings.html", lang = lang, form = form, error = error, success = success)

@app.route("/follow", methods = ["POST"])
@login_required
def route_toggle_follow():
    form = request.form
    if form["uid"] == current_user.get_id():
        return abort(400)
    other_user = get_user_by_id(form["uid"])
    if other_user == None:
        return abort(400)
    current_user.toggle_follow(other_user)
    return redirect(url_for("route_profile", username = other_user.get_user_name()))

@app.route("/reportuser", methods = ["GET", "POST"])
@login_required
def route_report_user():
    lang = Language("en")
    if request.method == "POST":
        error = handle_user_report(current_user.get_id(), request.form)
        return render_template("report_ok.html")
    return render_template("report_user.html", lang = lang)

@app.route("/logout")
@login_required
def route_logout():
    logout_user()
    return redirect(url_for("route_feed"))
