DEBUG = False
from flask import Flask # python3 -m pip install flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "𒀭𒀭𒊺𒉀"

if __name__ == "__main__":
    app.run(debug=DEBUG)
