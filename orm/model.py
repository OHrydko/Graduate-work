import uuid

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID

db = SQLAlchemy()


class ormUser(db.Model):
    __tablename__ = 'users'
    mobile_number = db.Column(db.String(), primary_key=True)
    name = db.Column(db.String())
    last_name = db.Column(db.String())
    birthday = db.Column(db.Date)
    user_name = db.Column(db.String())
    password = db.Column(db.String())

    def __init__(self, name, mobile, last_name, birthday, user_name, password):
        self.name = name
        self.mobile_number = mobile
        self.last_name = last_name
        self.birthday = birthday
        self.user_name = user_name
        self.password = password

    def __repr__(self) -> str:
        return '<user {}>'.format(self.mobile_number)


class ormPhoto(db.Model):
    __tablename__ = 'photo'
    photo_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_mobile = db.Column(db.String())
    photo = db.Column(db.LargeBinary())

    def __init__(self, user_mobile, photo):
        self.user_mobile = user_mobile
        self.photo = photo

    def __repr__(self) -> str:
        return '<photo_id {}>'.format(self.photo_id)
