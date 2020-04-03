import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS

POSTGRES_USER = os.environ.get("POSTGRES_USER")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
DB_URL = "postgresql://{user}:{password}@ucrm_db:5432/database".format(user=POSTGRES_USER, password=POSTGRES_PASSWORD)

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DB_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
CORS(app, origins="http://localhost:3535")
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

from . import rest_server
from . import models # Without this import create_all() will NOT create tables

db.create_all()
print("DB created!")
