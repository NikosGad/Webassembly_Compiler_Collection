import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

POSTGRES_USER = os.environ.get("POSTGRES_USER")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
DB_URL = "postgresql://{user}:{password}@ucrm_db:5432/database".format(user=POSTGRES_USER, password=POSTGRES_PASSWORD)

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DB_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from . import rest_server
from . import models

db.create_all()
print("DB created!")
