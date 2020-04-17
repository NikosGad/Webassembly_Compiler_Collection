import datetime
from marshmallow import fields, Schema
from rest_server import db

class SourceCodeFile(db.Model):
    __tablename__ = 'sourcecodefiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name = db.Column(db.String(), nullable=False)
    directory = db.Column(db.String(), unique=True, nullable=False)
    compilation_options = db.Column(db.ARRAY(db.String()), nullable=True)
    language = db.Column(db.String(), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)

    def __init__(self, name, user_id, directory, compilation_options, language):
        self.name = name
        self.user_id = user_id
        self.directory = directory
        self.compilation_options = compilation_options
        self.language = language
        self.created_at = datetime.datetime.utcnow()
        self.updated_at = self.created_at

    def create(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_files_per_language_by_user_id(user_id):
        return db.session.query(SourceCodeFile.language, db.func.json_agg(db.literal_column(SourceCodeFile.__tablename__))).\
            filter(SourceCodeFile.user_id == user_id).\
            group_by(SourceCodeFile.language).\
            all()

    @staticmethod
    def get_files_per_language_by_user_id_as_json(user_id):
        language_files_subquery = db.session.query(SourceCodeFile.language.label("language"), db.func.json_agg(db.literal_column(SourceCodeFile.__tablename__)).label("files_list")).\
            filter(SourceCodeFile.user_id == user_id).\
            group_by(SourceCodeFile.language).subquery()

        return db.session.query(db.func.json_object_agg(language_files_subquery.c.language, language_files_subquery.c.files_list)).first()[0]

    @staticmethod
    def get_all_files():
        return db.session.query(SourceCodeFile).all()

    def __repr__(self):
        return '<id {}, user_id {}, name {}, directory {}, compilation_options {}, language {}, created_at {}, updated_at {}>'.format(self.id, self.user_id, self.name, self.directory, self.compilation_options, self.language, self.created_at, self.updated_at)

class SourceCodeFileSchema(Schema):
    id = fields.Int(dump_only=True, required=True)
    user_id = fields.Int(required=True)
    name = fields.String(required=True)
    directory = fields.String(required=True)
    compilation_options = fields.List(fields.String())
    language = fields.String(required=True)
    created_at = fields.DateTime(dump_only=True, required=True)
    updated_at = fields.DateTime(dump_only=True, required=True)
