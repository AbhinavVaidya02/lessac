from dotenv import load_dotenv, dotenv_values
from flask import (
    Flask,
    request,
    jsonify,
    send_from_directory,
    render_template,
    redirect,
    flash,
)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError
from dotenv import dotenv_values
import os
from flask_login import (
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user,
    LoginManager,
)
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import UserMixin
from flask_cors import CORS, cross_origin
from functools import wraps

# app = Flask(__name__,static_url_path="/api/static")
app = Flask(__name__, template_folder='build', static_folder='build/static', static_url_path="/static")


CORS(app, supports_credentials=True)
bcrypt = Bcrypt(app)

config = dotenv_values(".env")
username = config["USERNAME"]
password = config["PASSWORD"]
database_name = config["DATABASE_NAME"]
database_host_name = config["DATABASE_HOST_NAME"]
database_port = config["DATABASE_PORT"]

app.secret_key = "srpilusm"
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = f"postgresql://{username}:{password}@{database_host_name}:{database_port}/{database_name}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "secret key"

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# flask_login stuff
login_manager = LoginManager()

from sqlalchemy import Identity

app.config["IMAGE_EXTENSIONS"] = ["png", "jpg", "jpeg"]

import uuid
import json
