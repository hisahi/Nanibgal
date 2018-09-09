
import application.models
from application.controller.users import get_user_by_id

def get_message_by_id(msgid):
    return application.models.Message.query.filter_by(msgid = msgid).first()

# (id, error)
def new_message(uid, request):
    reply = request.get("reply", None) or None
    contents = request.get("contents", None) or None
    link = request.get("link", None) or None
    if not contents:
        return (None, "newpost.error.empty_message")
    if get_user_by_id(uid) == None:
        return (None, None)
    contents = contents[:256].strip()
    if not contents:
        return (None, "newpost.error.empty_message")
    if link:
        link = link[:256]
    if type(reply) in [int, str]:
        reply = int(reply)
        if not get_message_by_id(reply):
            # if reply does not exist, just ignore
            reply = None
    else:
        reply = none
    msg = application.models.Message(uid, contents, link, reply)
    msg.add_itself()
    return (msg.get_id(), None)

# error
def edit_message(uid, request):
    msg = request.get("msg", None) or None
    contents = request.get("contents", None) or None
    link = request.get("link", None) or None
    if msg == None:
        return None
    if get_user_by_id(uid) == None:
        return None
    contents = contents[:256].strip()
    if not contents:
        return (None, "editpost.error.empty_message")
    if link:
        link = link[:256]
    editable = get_message_by_id(msg)
    if not editable:
        return None
    if editable.get_author_id() != uid:
        return "editpost.error.cannot_edit"
    if not editable.can_be_edited():
        return "editpost.error.toolate"
    editable.edit_message(contents, link)
    return None
    
