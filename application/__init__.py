
# External imports
import os

from flask import Flask
from flask_login import current_user, login_required, login_user, logout_user, fresh_login_required
from urllib.parse import urlparse, urljoin

from application import config

# Initialize app
app = Flask(__name__)

# Initialize database
from flask_sqlalchemy import SQLAlchemy

if os.environ.get("HEROKU"):
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = config.DATABASE_URL

app.config["SQLALCHEMY_ECHO"] = config.DEBUG

db = SQLAlchemy(app)

# Initialize database
import application.models
db.create_all()

import application.views

# Initialize login manager
from flask_login import LoginManager, current_user
login_manager = LoginManager()
login_manager.setup_app(app)

login_manager.login_view = "route_login"
login_manager.login_message = None

# Initialize secret key
from os import urandom
app.config["SECRET_KEY"] = urandom(32)

from application.models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)
