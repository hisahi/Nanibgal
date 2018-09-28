
import json, os.path

class Language():
    def __init__(self, code):
        self._code = code
        try:
            with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "lang", code + ".json"), "r", encoding = "utf-8") as f:
                self.table = json.load(f)
        except:
            with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "lang", "en.json"), "r", encoding = "utf-8") as f:
                self.table = json.load(f)

    def tr(self, key):
        try:
            return self.table[key]
        except:
            return "{" + key + "}"

    def code(self):
        return self._code
