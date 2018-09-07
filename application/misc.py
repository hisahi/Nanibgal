
from urllib.parse import urlparse, urljoin

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

# takes a dict, converts it to a format accepted by the FlaskForm constructor as obj
class populate_dict():
    def __init__(self, data):
        self._data = data
    def __getattr__(self, attr):
        if attr in self._data:
            return self._data[attr]
        else:
            return None
