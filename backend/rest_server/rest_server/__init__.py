import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS

POSTGRES_USER = os.environ["POSTGRES_USER"]
POSTGRES_PASSWORD = os.environ["POSTGRES_PASSWORD"]
SYSTEM_IP = os.environ["SYSTEM_IP"]
HOST_FRONTEND_ADDRESS = os.environ["HOST_FRONTEND_ADDRESS"]
DB_URL = "postgresql://{user}:{password}@ucrm_db:5432/database".format(user=POSTGRES_USER, password=POSTGRES_PASSWORD)

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DB_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
CORS(app, origins="http://" + HOST_FRONTEND_ADDRESS)
db = SQLAlchemy(app)
bcr = Bcrypt(app)

from . import models
from . import views

db.create_all()
