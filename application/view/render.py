
import re, urllib.parse

from flask import render_template, url_for
from flask_login import current_user

def render_message(lang, message, user = None, userid = None, username = None, 
                    displayname = None, is_private = None, is_banned = None,
                    has_liked = None, likes = None, replies = None, 
                    fallback_if_deleted = False, **kw):
    if message == None:
        return render_template("message_deleted.html", lang = lang) if fallback_if_deleted else None
    if userid == None or username == None or displayname == None:
        if user == None:
            user = message.get_author()
        if userid == None:
            userid = user.get_id()
        if username == None:
            username = user.get_user_name()
        if displayname == None:
            displayname = user.get_display_name()
    else:
        is_private = False if is_private == None else is_private
        is_banned = False if is_banned == None else is_banned
    if has_liked == None:
        if current_user.is_authenticated:
            has_liked = current_user.has_liked_message(message)
        else:
            has_liked = False
    if likes == None:
        likes = message.get_total_likes()
    if replies == None:
        replies = message.get_total_replies()
    return render_template("message.html",  lang = lang, 
                                            msg = message, 
                                            userid = userid,
                                            username = username,
                                            displayname = displayname, 
                                            has_liked = has_liked,
                                            is_private = is_private,
                                            is_banned = is_banned,
                                            likes = likes, 
                                            replies = replies,
                                            extra = kw)

# add links to ~username and #tag
user_links = re.compile(r"~([A-Za-z_][0-9A-Za-z_]*)")
tag_links = re.compile(r"(#[^\s#]+)")
def format_links(text):
    text = user_links.sub(lambda x: "<a href=\"" + 
                                    url_for("route_profile", username = x.group(1)) + "\">~" + 
                                    x.group(1) + "</a>", text)
    text = tag_links.sub(lambda x: "<a href=\"" + url_for("route_search") + "?q=" + 
                                    urllib.parse.quote_plus(x.group(1)) + "\">" + 
                                    x.group(1) + "</a>", text)
    return text
