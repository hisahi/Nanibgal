
from urllib.parse import urlparse, urljoin
import application.config

# http://flask.pocoo.org/snippets/62/
def is_safe_url(host_url, target):
    ref_url = urlparse(host_url)
    test_url = urlparse(urljoin(host_url, target))
    return test_url.scheme in ("http", "https") and \
           ref_url.netloc == test_url.netloc

def get_safe_url(host_url, target, fallback):
    print("get_safe", host_url, target, fallback)
    if is_safe_url(host_url, target):
        return target
    else:
        return fallback

# returns a new function where arg has been bound as the first parameter,
# effectively decreasing the arity of the function by one
def bind1(func, arg):
    return lambda *a, **k: func(arg, *a, **k)

# sanitize and escape HTML
def escape_html(x):
    return x.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

# add a prefix to a string if it isn't empty
def prefix_nonempty(prefix, text):
    return prefix + text if text else text

# generates a list of languages for SelectField
def generate_language_list(lang):
    available_langs = application.config.LANGUAGES
    result = []
    for key in available_langs:
        if lang:
            result.append((key, "{} ({}) [{}]".format(lang.tr("language." + key), available_langs[key], key)))
        else:
            result.append((key, "{} [{}]".format(available_langs[key], key)))
    return result

def generate_list_from(lang, values, prefix):
    result = []
    for key in values:
        val = prefix + key
        if lang:
            result.append((val, lang.tr(val)))
        else:
            result.append((val, val))
    return result

# generates a list of user report reasons
def generate_user_report_reason_list(lang):
    return generate_list_from(lang, application.config.USER_REPORT_REASONS, "reportuser.reason.")

# generates a list of message report reasons
def generate_msg_report_reason_list(lang):
    return generate_list_from(lang, application.config.MSG_REPORT_REASONS, "reportmsg.reason.")

# takes a dict, converts it to a format accepted by the FlaskForm constructor as obj
class populate_dict():
    def __init__(self, data):
        self._data = data
    def __getattr__(self, attr):
        if attr in self._data:
            return self._data[attr]
        else:
            return None
