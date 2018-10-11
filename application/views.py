
from application import app

import application.config
import jinja2.exceptions, urllib.parse
from application.misc import *

from flask import render_template, request, redirect, url_for, abort
from flask_login import current_user, login_required, login_user, logout_user, fresh_login_required
from application.i18n import Language
from application.view.admin import get_message_reports, get_user_reports
from application.view.feed import compute_pages
from application.view.msg import get_user_messages, get_feed_from_user, get_liked_messages, get_message_replies, search_for_messages
from application.view.render import render_message, render_user, render_message_report, render_user_report, render_notification, format_links
from application.view.form import DeleteAccountForm, EditPostForm, LoginForm, RegisterForm, ReportPostForm, ReportUserForm, NewPostForm, SettingsForm, SearchMessageForm, SearchUserForm
from application.view.user import get_followed_users, get_followers, search_for_users
from application.controller.auth import login, register
from application.controller.messages import get_message_by_id, new_message, edit_message, toggle_like
from application.controller.reports import handle_user_report, handle_message_report
from application.controller.settings import handle_settings, handle_delete_account
from application.controller.users import get_user_by_id, get_user_by_name, toggle_ban, toggle_follow

# make urllib.parse available for Jinja
app.jinja_env.globals.update(urllib = urllib)
# make utility functions available for Jinja
app.jinja_env.globals.update(format_links = format_links)
app.jinja_env.globals.update(escape_html = escape_html)
app.jinja_env.globals.update(prefix_nonempty = prefix_nonempty)

# based on http://flask.pocoo.org/snippets/128/
def get_preferred_anon_lang(headers):
    UA_langs = request.headers.get('Accept-Language').split(",")
    matches = filter(lambda x: x.split(";")[0] in application.config.LANGUAGES, UA_langs)
    return next(matches).split(";")[0] or "en"

def get_user_lang(headers, current_user):
    if not current_user.is_authenticated:
        try:
            return get_preferred_anon_lang(headers)
        except:
            return "en"
    lang = current_user.get_language()
    if lang not in application.config.LANGUAGES:
        lang = "en"
    return lang

@app.errorhandler(403)
def page_forbidden(e):
    lang = Language(get_user_lang(request.headers, current_user))
    return render_template("errors/403.html", lang = lang), 403

@app.errorhandler(404)
def page_not_found(e):
    lang = Language(get_user_lang(request.headers, current_user))
    return render_template("errors/404.html", lang = lang), 404

@app.route("/")
def route_feed(): # 𒀭𒀭𒊺𒉀
    lang = Language(get_user_lang(request.headers, current_user))
    if not current_user.is_authenticated:
        return redirect(url_for("route_login"))
    if current_user.is_authenticated and current_user.is_banned():
        return render_template("errors/banned.html", lang = lang)
    msgs, next_page, prev_page = compute_pages(request.args, get_feed_from_user, current_user)
    return render_template("feed.html", lang = lang, msgs = msgs, 
                            render_message = bind1(render_message, lang), 
                            prev_page = prev_page, next_page = next_page,
                            has_before = "b" in request.args or "a" in request.args)

@app.route("/~<username>")
def route_profile(username):
    lang = Language(get_user_lang(request.headers, current_user))
    if current_user.is_authenticated and current_user.is_banned():
        return render_template("errors/banned.html", lang = lang)
    user = get_user_by_name(username)
    if user == None:
        return abort(404)
    msgs, next_page, prev_page = compute_pages(request.args, get_user_messages, user, current_user)
    return render_template("profile/profile.html", lang = lang, user = user, msgs = msgs, 
                            render_message = bind1(render_message, lang), 
                            prev_page = prev_page, next_page = next_page,
                            has_before = "b" in request.args or "a" in request.args)

@app.route("/~<username>/likes")
@login_required
def route_profile_likes(username):
    lang = Language(get_user_lang(request.headers, current_user))
    if current_user.is_authenticated and current_user.is_banned():
        return render_template("errors/banned.html", lang = lang)
    user = get_user_by_name(username)
    if user == None:
        return abort(404)
    if user.is_banned() and (not current_user.is_authenticated or not current_user.has_admin_rights()):
        return redirect(url_for("route_profile", username = username))
    msgs, next_page, prev_page = compute_pages(request.args, get_liked_messages, user, current_user)
    return render_template("profile/profile_likes.html", lang = lang, user = user, msgs = msgs, 
                            render_message = bind1(render_message, lang), 
                            prev_page = prev_page, next_page = next_page,
                            has_before = "b" in request.args or "a" in request.args)

@app.route("/~<username>/follows")
@login_required
def route_profile_follows(username):
    lang = Language(get_user_lang(request.headers, current_user))
    if current_user.is_authenticated and current_user.is_banned():
        return render_template("errors/banned.html", lang = lang)
    user = get_user_by_name(username)
    if user == None:
        return abort(404)
    if user.is_banned() and (not current_user.is_authenticated or not current_user.has_admin_rights()):
        return redirect(url_for("route_profile", username = username))
    users, next_page, prev_page = compute_pages(request.args, get_followed_users, user)
    return render_template("profile/profile_follows.html", lang = lang, user = user, users = users, 
                            render_user = bind1(render_user, lang), 
                            prev_page = prev_page, next_page = next_page,
                            has_before = "b" in request.args or "a" in request.args)

@app.route("/~<username>/followers")
@login_required
def route_profile_followers(username):
    lang = Language(get_user_lang(request.headers, current_user))
    if current_user.is_authenticated and current_user.is_banned():
        return render_template("errors/banned.html", lang = lang)
    user = get_user_by_name(username)
    if user == None:
        return abort(404)
    if user.is_banned() and (not current_user.is_authenticated or not current_user.has_admin_rights()):
        return redirect(url_for("route_profile", username = username))
    users, next_page, prev_page = compute_pages(request.args, get_followers, user)
    return render_template("profile/profile_followers.html", lang = lang, user = user, users = users, 
                            render_user = bind1(render_user, lang), 
                            prev_page = prev_page, next_page = next_page,
                            has_before = "b" in request.args or "a" in request.args)

@app.route("/~<username>/<int:postid>")
def route_message(username, postid):
    lang = Language(get_user_lang(request.headers, current_user))
    if current_user.is_authenticated and current_user.is_banned():
        return render_template("errors/banned.html", lang = lang)
    user = get_user_by_name(username)
    if user == None:
        return abort(404)
    if user.is_banned() and (not current_user.is_authenticated or not current_user.has_admin_rights()):
        return redirect(url_for("route_profile", username = username))
    msg = get_message_by_id(postid)
    if msg == None:
        return abort(404)
    if user.get_id() != msg.get_author_id():
        return abort(404)
    reply = None
    if msg.reply != None:
        reply = get_message_by_id(msg.reply)
    return render_template("message/viewmessage.html", lang = lang, user = user, msg = msg, 
                            reply = reply, reply_id = msg.reply, is_reply = msg.is_reply, 
                            render_message = bind1(render_message, lang),
                            username = username, postid = postid,
                            important_replies = msg.get_most_important_message_replies(current_user))

@app.route("/~<username>/<int:postid>/replies")
def route_message_replies(username, postid):
    lang = Language(get_user_lang(request.headers, current_user))
    if current_user.is_authenticated and current_user.is_banned():
        return render_template("errors/banned.html", lang = lang)
    user = get_user_by_name(username)
    if user == None:
        return abort(404)
    if user.is_banned() and (not current_user.is_authenticated or not current_user.has_admin_rights()):
        return redirect(url_for("route_profile", username = username))
    msg = get_message_by_id(postid)
    if msg == None:
        return abort(404)
    msgs, next_page, prev_page = compute_pages(request.args, get_message_replies, msg, current_user)
    return render_template("message/viewreplies.html", lang = lang, user = user, msgs = msgs, 
                            render_message = bind1(render_message, lang), 
                            prev_page = prev_page, next_page = next_page,
                            has_before = "b" in request.args or "a" in request.args,
                            username = username, postid = postid)

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
    return render_template("auth/login.html", lang = lang, form = nform, oldform = oldform, 
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
    return render_template("auth/register.html", lang = lang, form = nform, oldform = oldform, 
                            error = error)

@app.route("/search")
def route_search():
    lang = Language(get_user_lang(request.headers, current_user))
    if current_user.is_authenticated and current_user.is_banned():
        return render_template("errors/banned.html", lang = lang)
    if request.args.get("q", None):
        q = request.args.get("q")[:512]
        msgs, next_page, prev_page = compute_pages(request.args, search_for_messages, current_user, q)
        return render_template("search/search_results.html", lang = lang, msgs = msgs, 
                                render_message = bind1(render_message, lang), q = q, 
                                prev_page = prev_page, next_page = next_page,
                                has_before = "b" in request.args or "a" in request.args)
    return render_template("search/search.html", lang = lang, form = SearchMessageForm(csrf_enabled = False).localized(lang), formuser = SearchUserForm(csrf_enabled = False).localized(lang))

@app.route("/searchuser")
def route_search_user():
    lang = Language(get_user_lang(request.headers, current_user))
    if current_user.is_authenticated and current_user.is_banned():
        return render_template("errors/banned.html", lang = lang)
    if request.args.get("q", None):
        q = request.args.get("q")[:512]
        users, next_page, prev_page = compute_pages(request.args, search_for_users, current_user, q)
        return render_template("search/searchuser_results.html", lang = lang, users = users, 
                                render_user = bind1(render_user, lang), q = q,
                                prev_page = prev_page, next_page = next_page,
                                has_before = "b" in request.args or "a" in request.args)
    return render_template("search/search.html", lang = lang, form = SearchMessageForm(csrf_enabled = False).localized(lang), formuser = SearchUserForm(csrf_enabled = False).localized(lang))

@app.route("/notifications")
@login_required
def route_notifications():
    lang = Language(get_user_lang(request.headers, current_user))
    if current_user.is_authenticated and current_user.is_banned():
        return render_template("errors/banned.html", lang = lang)
    return render_template("notification/notifications.html", lang = lang, 
                            notifs = current_user.get_notifications(False), 
                            render_notification = bind1(render_notification, lang))

@app.route("/new", methods = ["GET", "POST"])
@login_required
def route_new():
    lang = Language(get_user_lang(request.headers, current_user))
    if current_user.is_banned():
        return render_template("errors/banned.html", lang = lang)
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
    return render_template("write/new.html", lang = lang, form = nform, oldform = oldform, 
                            reply = render_message(lang, msg), reply_id = reply_id, error = error)

@app.route("/edit", methods = ["GET", "POST"])
@login_required
def route_msg_edit():
    lang = Language(get_user_lang(request.headers, current_user))
    if current_user.is_authenticated and current_user.is_banned():
        return render_template("errors/banned.html", lang = lang)
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
    nform = EditPostForm(obj = populate_dict({
        "contents": msg.get_text(),
        "link": msg.get_link()
    })).localized(lang)
    if oldform == None:
        oldform = nform
    return render_template("write/edit.html", lang = lang, form = nform, oldform = oldform, 
                                msg = msg, error = error, render_message = bind1(render_message, lang))

@app.route("/settings", methods = ["GET", "POST"])
@fresh_login_required
def route_settings():
    lang = Language(get_user_lang(request.headers, current_user))
    if current_user.is_banned():
        return render_template("errors/banned.html", lang = lang)
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
    return render_template("auth/settings.html", lang = lang, form = nform, 
                            deleteform = DeleteAccountForm().localized(lang), 
                            oldform = oldform, error = error, success = success)

@app.route("/follow", methods = ["POST"])
@login_required
def route_toggle_follow():
    if current_user.is_banned():
        return abort(403)
    form = request.form
    if form["uid"] == current_user.get_id():
        return abort(400)
    other_user = get_user_by_id(form["uid"])
    code = toggle_follow(current_user, other_user)
    if code == 200:
        return redirect(url_for("route_profile", username = other_user.get_user_name()))
    else:
        return abort(code)

@app.route("/ban", methods = ["POST"])
@login_required
def route_toggle_ban():
    if current_user.is_banned():
        return abort(403)
    form = request.form
    if not current_user.has_admin_rights():
        return abort(403)
    other_user = get_user_by_id(form["uid"])
    code = toggle_ban(other_user)
    if code == 200:
        return redirect(url_for("route_profile", username = other_user.get_user_name()))
    else:
        return abort(code)

@app.route("/like", methods = ["POST"])
@login_required
def route_toggle_like():
    if current_user.is_banned():
        return abort(403)
    form = request.form
    msg_id = form["mid"]
    try:
        msg = get_message_by_id(int(msg_id))
    except:
        return abort(400)
    code = toggle_like(current_user, msg)
    if code == 200:
        return redirect(get_safe_url(request.host_url, request.form["next"] or url_for("route_feed"), url_for("route_feed")))
    else:
        return abort(code)

@app.route("/msg_delete", methods = ["POST"])
@login_required
def route_msg_delete():
    if current_user.is_banned():
        return abort(403)
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
    if current_user.is_banned():
        return abort(403)
    lform = DeleteAccountForm(request.form)
    if lform.validate():
        if not handle_delete_account(current_user.get_id(), request.form):
            return redirect(url_for("route_feed"))
    return redirect(url_for("route_settings"))

@app.route("/notifications/read", methods = ["POST"])
@fresh_login_required
def route_notifications_read():
    if current_user.is_banned():
        return abort(403)
    nid = request.form["nid"]
    current_user.set_notifications_read_up_to(nid)
    return redirect(url_for("route_notifications"))

@app.route("/reportuser", methods = ["GET", "POST"])
@login_required
def route_report_user():
    lang = Language(get_user_lang(request.headers, current_user))
    if current_user.is_banned():
        return render_template("errors/banned.html", lang = lang)
    lform = ReportUserForm(request.form).localized(lang)
    nform = ReportUserForm().localized(lang)
    if request.method == "POST":
        if lform.validate():
            error = handle_user_report(current_user.get_id(), request.form)
            if error:
                return render_template("profile/reportuser.html", lang = lang, form = nform, error = error)
            else:
                return render_template("profile/reportuser.html", lang = lang, success = True, error = None)
        else:
            error = lang.tr("reportuser.error.invalidform")
    user_id = request.args.get("uid", default = None)
    try:
        user_id = int(user_id)
    except:
        return abort(400)
    return render_template("profile/reportuser.html", lang = lang, form = nform, user_id = user_id, error = None)

@app.route("/reportmsg", methods = ["GET", "POST"])
@login_required
def route_report_msg():
    lang = Language(get_user_lang(request.headers, current_user))
    if current_user.is_banned():
        return render_template("errors/banned.html", lang = lang)
    lform = ReportPostForm(request.form).localized(lang)
    nform = ReportPostForm().localized(lang)
    if request.method == "POST":
        if lform.validate():
            error = handle_message_report(current_user.get_id(), request.form)
            if error:
                return render_template("message/reportmsg.html", lang = lang, form = nform, error = lang.tr(error))
            else:
                return render_template("message/reportmsg.html", lang = lang, success = True, error = None)
        else:
            error = lang.tr("reportmsg.error.invalidform")
    msg_id = request.args.get("mid", default = None)
    try:
        msg_id = int(msg_id)
    except:
        return abort(400)
    return render_template("message/reportmsg.html", lang = lang, form = nform, msg_id = msg_id, error = None)

@app.route("/admin")
@login_required
def route_admin():
    lang = Language(get_user_lang(request.headers, current_user))
    if not current_user.has_admin_rights() or current_user.is_banned():
        return render_template("errors/notadmin.html", lang = lang)
    return render_template("admin/admin.html", lang = lang)

@app.route("/admin/reports/user")
@login_required
def route_admin_userreports():
    lang = Language(get_user_lang(request.headers, current_user))
    if not current_user.has_admin_rights() or current_user.is_banned():
        return render_template("errors/notadmin.html", lang = lang)
    reports, next_page, prev_page = compute_pages(request.args, get_user_reports, current_user)
    return render_template("admin/admin_userreports.html", lang = lang, reports = reports, 
                            render_report = bind1(render_user_report, lang), 
                            prev_page = prev_page, next_page = next_page,
                            has_before = "b" in request.args or "a" in request.args)

@app.route("/admin/reports/msg")
@login_required
def route_admin_msgreports():
    lang = Language(get_user_lang(request.headers, current_user))
    if not current_user.has_admin_rights() or current_user.is_banned():
        return render_template("errors/notadmin.html", lang = lang)
    reports, next_page, prev_page = compute_pages(request.args, get_message_reports, current_user)
    return render_template("admin/admin_msgreports.html", lang = lang, reports = reports, 
                            render_report = bind1(render_message_report, lang), 
                            prev_page = prev_page, next_page = next_page,
                            has_before = "b" in request.args or "a" in request.args)

@app.route("/admin/reports/user/delete", methods = ["POST"])
@login_required
def route_remove_user_report():
    if not current_user.has_admin_rights() or current_user.is_banned():
        return abort(403)
    rid = request.form["rid"]
    try:
        application.models.ReportUser.query.filter_by(reportid = rid).first().terminate()
    except:
        return abort(400)
    return redirect(get_safe_url(request.host_url, request.form["next"] or url_for("route_admin_userreports"), url_for("route_admin_userreports")))

@app.route("/admin/reports/msg/delete", methods = ["POST"])
@login_required
def route_remove_msg_report():
    if not current_user.has_admin_rights() or current_user.is_banned():
        return abort(403)
    rid = request.form["rid"]
    try:
        application.models.ReportMessage.query.filter_by(reportid = rid).first().terminate()
    except:
        return abort(400)
    return redirect(get_safe_url(request.host_url, request.form["next"] or url_for("route_admin_msgreports"), url_for("route_admin_msgreports")))

@app.route("/logout")
@login_required
def route_logout():
    logout_user()
    return redirect(url_for("route_feed"))
