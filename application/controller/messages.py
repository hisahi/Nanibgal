
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
    contents = contents[:256]
    if link:
        link = link[:256]
    if not get_message_by_id(reply):
        # if reply does not exist, just ignore
        reply = None
    msg = application.models.Message(uid, contents, link, reply)
    msg.add_itself()
    return (msg.get_id(), None)

def edit_message():
    pass
