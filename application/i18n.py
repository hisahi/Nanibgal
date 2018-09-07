
import json, os.path

class Language():
    def __init__(self, code):
        try:
            with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "lang", code + ".json"), "r") as f:
                self.table = json.load(f)
        except:
            with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "lang", "en.json"), "r") as f:
                self.table = json.load(f)

    def tr(self, key):
        try:
            return self.table[key]
        except:
            return "{" + key + "}"
