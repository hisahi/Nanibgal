
import application.models, application.config
from application.controller.users import get_user_by_id
from application.controller.messages import get_message_by_id

def handle_user_report(userid, form):
    try:
        curuser = get_user_by_id(userid)
    except:
        return "reportuser.error.invalidform"
    try:
        othuser = get_user_by_id(form["user"])
    except:
        return "reportuser.error.cannotreport"
    if curuser == othuser:
        return "reportuser.error.cannotreport"
    reason = form["reason"]
    application.models.ReportUser(curuser, othuser, reason).add_itself()
    return None
    
def handle_message_report(userid, form):
    try:
        curuser = get_user_by_id(userid)
    except:
        return "reportmsg.error.invalidform"
    try:
        msg = get_message_by_id(form["msg"])
    except:
        return "reportmsg.error.cannotreport"
    if msg.get_author_id() == userid:
        return "reportmsg.error.cannotreport"
    reason = form["reason"]
    application.models.ReportMessage(curuser, msg, reason).add_itself()
    return None
