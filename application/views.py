
from application import app

import application.config
import jinja2.exceptions, urllib.parse
from application.misc import *

from flask import render_template, request, redirect, url_for, abort
from flask_login import current_user, login_required, login_user, logout_user, fresh_login_required
from application.i18n import Language
from application.view.feed import compute_pages
from application.view.msg import get_user_messages, get_feed_from_user
from application.view.render import render_message, format_links
from application.view.form import DeleteAccountForm, EditPostForm, LoginForm, RegisterForm, NewPostForm, SettingsForm
from application.controller.messages import get_message_by_id, new_message, edit_message
from application.controller.auth import login, register
from application.controller.reports import handle_user_report, handle_message_report
from application.controller.settings import handle_settings, handle_delete_account
from application.controller.users import get_user_by_id, get_user_by_name

# make urllib.parse available for Jinja
app.jinja_env.globals.update(urllib = urllib)
# make utility functions available for Jinja
app.jinja_env.globals.update(format_links = format_links)
app.jinja_env.globals.update(escape_html = escape_html)
app.jinja_env.globals.update(prefix_nonempty = prefix_nonempty)

# http://flask.pocoo.org/snippets/128/
def get_preferred_anon_lang(headers):
    UA_langs = request.headers.get('Accept-Language').split(",")
    matches = filter(lambda x: x.split(";")[0] in application.config.LANGUAGES, UA_langs)
    return next(matches) or "en"

def get_user_lang(headers, current_user):
    if not current_user.is_authenticated:
        return get_preferred_anon_lang(headers)
    lang = current_user.get_language()
    if lang not in application.config.LANGUAGES:
        lang = "en"
    return lang

@app.route("/")
def route_feed(): # 𒀭𒀭𒊺𒉀
    lang = Language(get_user_lang(request.headers, current_user))
    if not current_user.is_authenticated:
        return redirect(url_for("route_login"))
    msgs, offset, next_page, prev_page = compute_pages(request.args, get_feed_from_user, current_user)
    return render_template("feed.html", lang = lang, msgs = msgs, 
                            render_message = bind1(render_message, lang), 
                            prev_page = prev_page, next_page = next_page)

@app.route("/~<username>")
def route_profile(username):
    lang = Language(get_user_lang(request.headers, current_user))
    user = get_user_by_name(username)
    if user == None:
        return abort(404)
    msgs, offset, next_page, prev_page = compute_pages(request.args, get_user_messages, user, current_user)
    return render_template("profile.html", lang = lang, user = user, msgs = msgs, 
                            render_message = bind1(render_message, lang), 
                            prev_page = prev_page, next_page = next_page)

@app.route("/~<username>/<int:postid>")
def route_message(username, postid):
    lang = Language(get_user_lang(request.headers, current_user))
    user = get_user_by_name(username)
    if user == None:
        return abort(404)
    msg = get_message_by_id(postid)
    if msg == None:
        return abort(404)
    reply = None
    if msg.reply != None:
        reply = get_message_by_id(msg.reply)
    return render_template("viewmessage.html", lang = lang, user = user, msg = msg, 
                            reply = reply, reply_id = msg.reply, is_reply = msg.is_reply, 
                            render_message = bind1(render_message, lang))

@app.route("/login", methods = ["GET", "POST"])
def route_login():
    lang = Language(get_user_lang(request.headers, current_user))
    if current_user.is_authenticated:
        return redirect(url_for("route_feed"))
    error, oldform = None, None
    if request.method == "POST":
        lform = LoginForm(request.form)
        if lform.validate():
            user_obj, error = login(lform.username.data, lform.password.data)
            if user_obj:
                login_user(user_obj, remember = request.form.get("remember", False))
                return redirect(get_safe_url(request.host_url, request.form["next"] or url_for("route_feed"), url_for("route_feed")))
            if error:
                error = lang.tr(error)
        else:
            error = lang.tr("login.invalid")
            oldform = lform
    nform = LoginForm().localized(lang)
    if oldform == None:
        oldform = nform
    return render_template("login.html", lang = lang, form = nform, oldform = oldform, 
                            error = error)

@app.route("/register", methods = ["GET", "POST"])
def route_register():
    lang = Language(get_user_lang(request.headers, current_user))
    if current_user.is_authenticated:
        return redirect(url_for("route_feed"))
    error, oldform = None, None
    if request.method == "POST":
        lform = RegisterForm(request.form)
        if lform.validate():
            user_obj, error = register(lform.username.data, lform.password.data, lform.verify.data)
            if user_obj:
                login_user(user_obj, remember = request.form.get("remember", False))
                return redirect(url_for("route_feed"))
            if error:
                error = lang.tr(error)
        else:
            oldform = lform
    nform = RegisterForm().localized(lang)
    if oldform == None:
        oldform = nform
    return render_template("register.html", lang = lang, form = nform, oldform = oldform, 
                            error = error)

@app.route("/search", methods = ["GET", "POST"])
def route_search():
    lang = Language(get_user_lang(request.headers, current_user))
    return render_template("search.html", lang = lang)

@app.route("/new", methods = ["GET", "POST"])
@login_required
def route_new():
    lang = Language(get_user_lang(request.headers, current_user))
    error, oldform = None, None
    if request.method == "POST":
        lform = NewPostForm(request.form)
        if lform.validate():
            (postid, error) = new_message(current_user.get_id(), request.form)
            if error:
                error = lang.tr(error)
            else:
                return redirect(url_for("route_message", username = current_user.get_user_name(), postid = postid))
        else:
            oldform = lform
    test_reply_id = request.args.get("reply", default = None)
    try:
        msg, reply_id = get_message_by_id(int(test_reply_id)), test_reply_id
    except:
        msg, reply_id = None, ""
    nform = NewPostForm().localized(lang)
    if oldform == None:
        oldform = nform
    return render_template("new.html", lang = lang, form = nform, oldform = oldform, 
                            reply = render_message(lang, msg), reply_id = reply_id, error = error)

@app.route("/settings", methods = ["GET", "POST"])
@fresh_login_required
def route_settings():
    lang = Language(get_user_lang(request.headers, current_user))
    error, oldform, success = None, None, False
    if request.method == "POST":
        lform = SettingsForm(request.form).localized(lang)
        if lform.validate():
            error = handle_settings(current_user.get_id(), request.form)
            if error:
                error = lang.tr(error)
            else:
                success = True
        else:
            oldform = lform
    nform = SettingsForm(obj = populate_dict({
        "username": current_user.get_user_name(),
        "displayname": current_user.get_display_name(),
        "bio": current_user.get_user_bio(),
        "language": current_user.get_language(),
        "privatemessages": current_user.are_messages_private(), 
        "privatefollows": current_user.are_follows_private(),
        "privatelikes": current_user.are_likes_private()
    })).localized(lang)
    if oldform == None:
        oldform = nform
    return render_template("settings.html", lang = lang, form = nform, 
                            deleteform = DeleteAccountForm().localized(lang), 
                            oldform = oldform, error = error, success = success)

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

@app.route("/like", methods = ["POST"])
@login_required
def route_toggle_like():
    form = request.form
    msg_id = form["mid"]
    try:
        msg = get_message_by_id(int(msg_id))
    except:
        return abort(400)
    if msg == None:
        return redirect(get_safe_url(request.host_url, request.form["next"] or url_for("route_feed"), url_for("route_feed")))
    current_user.toggle_like(msg)
    return redirect(get_safe_url(request.host_url, request.form["next"] or url_for("route_feed"), url_for("route_feed")))

@app.route("/edit", methods = ["GET", "POST"])
@login_required
def route_msg_edit():
    lang = Language(get_user_lang(request.headers, current_user))
    error, oldform = None, None
    if request.method == "POST":
        lform = EditPostForm(request.form)
        if lform.validate():
            error = edit_message(current_user.get_id(), request.form)
            if error:
                error = lang.tr(error)
            else:
                return redirect(url_for("route_message", username = current_user.get_user_name(), postid = request.form["msg"]))
        else:
            oldform = lform
    test_msg_id = request.args.get("msg", default = None)
    try:
        msg = get_message_by_id(int(test_msg_id))
        if msg.get_author_id() != current_user.get_id():
            return abort(403)
    except:
        return redirect(url_for("route_feed"))
    nform = EditPostForm().localized(lang)
    if oldform == None:
        oldform = nform
    return render_template("edit.html", lang = lang, form = nform, oldform = oldform, 
                                msg = msg, error = error, render_message = bind1(render_message, lang))

@app.route("/msg_delete", methods = ["POST"])
@login_required
def route_msg_delete():
    form = request.form
    mid = form["mid"]
    msg = get_message_by_id(mid)
    if msg == None:
        return abort(400)
    if not current_user.has_admin_rights():
        if msg.get_author_id() != current_user.get_id():
            return abort(403)
    msg.terminate()
    return redirect(url_for("route_profile", username = msg.get_author().get_user_name()))

@app.route("/delete_account", methods = ["POST"])
@fresh_login_required
def route_delete_account():
    lform = DeleteAccountForm(request.form)
    if lform.validate():
        if not handle_delete_account(current_user.get_id(), request.form):
            return redirect(url_for("route_feed"))
    return redirect(url_for("route_settings"))

@app.route("/reportuser", methods = ["GET", "POST"])
@login_required
def route_report_user():
    lang = Language(get_user_lang(request.headers, current_user))
    if request.method == "POST":
        error = handle_user_report(current_user.get_id(), request.form)
        return render_template("report_ok.html")
    return render_template("report_user.html", lang = lang)

@app.route("/logout")
@login_required
def route_logout():
    logout_user()
    return redirect(url_for("route_feed"))
