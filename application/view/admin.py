
import application.models
from application.view.feed import MSGS_PER_PAGE

def get_user_reports(current_user, limit = MSGS_PER_PAGE, before = None, after = None):
    return application.models.ReportUser.get_reports(current_user, limit, before, after)

def get_message_reports(current_user, limit = MSGS_PER_PAGE, before = None, after = None):
    return application.models.ReportMessage.get_reports(current_user, limit, before, after)
