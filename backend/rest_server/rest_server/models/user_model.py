import datetime
from marshmallow import fields, Schema, validate
import re

from rest_server import db, bcr
# from sqlalchemy.dialects.postgresql import JSON

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(), unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)
    email = db.Column(db.String(), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)

    def __init__(self, username, password, email):
        self.username = username
        self.password = self.__hash_password(password)
        self.email = email
        self.created_at = datetime.datetime.utcnow()
        self.updated_at = self.created_at

    def create(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_user_by_username(username):
        return db.session.query(User).filter(User.username == username).first()

    @staticmethod
    def get_user_by_email(email):
        return db.session.query(User).filter(User.email == email).first()

    @staticmethod
    def get_all_users():
        return db.session.query(User).all()

    def __hash_password(self, password):
        return bcr.generate_password_hash(password).decode("utf-8")

    def validate_password(self, password):
        return bcr.check_password_hash(self.password, password)

    def __repr__(self):
        return '<id {}, username {}, password {}, email {}, created_at {}, updated_at {}>'.format(self.id, self.username, self.password, self.email, self.created_at, self.updated_at)

class UserSchema(Schema):
    id = fields.Int(dump_only=True, required=True)
    username = fields.String(
        required=True,
        validate=[
            validate.Regexp(r"\A[A-Za-z0-9]+[A-Za-z0-9_ ]*[A-Za-z0-9]+\Z",
                error="Username must contain only latin letters, numbers, _ and spaces. It must start and end with a letter. It must have length greater than 1."
            )
        ]
    )
    password = fields.String(
        required=True,
        validate=[
            validate.Length(min=6, error="Password length must be at least {min}."),
            validate.Regexp(r"\A(\S*)\Z", error="Password must not contain white spaces."),
            validate.Regexp(r".*\d", re.DOTALL, error="Password must contain at least 1 number(s)."),
            validate.Regexp(r".*[A-Za-z]", re.DOTALL, error="Password must contain at least 1 latin letter(s).")
        ]
    )
    email = fields.Email(required=True)
    created_at = fields.DateTime(dump_only=True, required=True)
    updated_at = fields.DateTime(dump_only=True, required=True)
