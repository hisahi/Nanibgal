
import re, urllib.parse

from flask import render_template, url_for
from flask_login import current_user

def render_message(lang, message, user = None, has_liked = None, likes = None, replies = None, fallback_if_deleted = False, **kw):
    if message == None:
        return render_template("message_deleted.html", lang = lang) if fallback_if_deleted else None
    if user == None:
        user = message.get_author()
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
                                            user = user,
                                            username = user.get_user_name(),
                                            displayname = user.get_display_name(), 
                                            has_liked = has_liked,
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
