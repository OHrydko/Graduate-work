import json
import uuid
from base64 import b64encode

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


class ormProduct(db.Model):
    __tablename__ = 'product'
    name = db.Column(db.String(), primary_key=True)
    user_mobile = db.Column(db.String())
    photo = db.Column(db.LargeBinary())
    danger = db.Column(db.Integer())
    type = db.Column(db.String())
    ingredient = db.Column(db.String())

    def __init__(self, name, user_mobile, photo, danger, type, ingredient):
        self.user_mobile = user_mobile
        self.photo = photo
        self.name = name
        self.danger = danger
        self.type = type
        self.ingredient = ingredient

    def __repr__(self) -> str:
        return '<name {}>'.format(self.name)


class ormE(db.Model):
    __tablename__ = 'supplement'
    number_supplement = db.Column(db.String(), primary_key=True)
    name = db.Column(db.String())
    categories = db.Column(db.String())
    danger = db.Column(db.String())

    def __init__(self, number_supplement, name, categories, danger):
        self.number_supplement = number_supplement
        self.name = name
        self.categories = categories
        self.danger = danger

    def __repr__(self) -> str:
        return '<number_supplement {}>'.format(self.number_supplement)

    def serialize(self):
        return {
            'number_supplement': self.number_supplement,
            'message': self.name,
            'categories': self.categories,
            'danger': self.danger
        }


class ormAllergic(db.Model):
    __tablename__ = 'allergic'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String())
    user_mobile = db.Column(db.String())

    def __init__(self, name, user_mobile):
        self.user_mobile = user_mobile
        self.name = name

    def __repr__(self) -> str:
        return '<id {}>'.format(self.id)


class ormProductHasSupplement(db.Model):
    __tablename__ = 'product_has_supplement'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name_of_product = db.Column(db.String())
    id_of_supplement = db.Column(db.String())

    def __init__(self, name_of_product, id_of_supplement):
        self.id_of_supplement = id_of_supplement
        self.name_of_product = name_of_product

    def __repr__(self) -> str:
        return '<id {}>'.format(self.id)


class ormHistory(db.Model):
    __tablename__ = 'history'
    name = db.Column(db.String(), primary_key=True)
    user_mobile = db.Column(db.String())
    photo = db.Column(db.LargeBinary)
    allergic = db.Column(db.String())

    def __init__(self, name, user_mobile, photo, allergic):
        self.name = name
        self.user_mobile = user_mobile
        self.photo = photo
        self.allergic = allergic

    def __repr__(self) -> str:
        return '<name {}>'.format(self.name)


class History:

    def __init__(self, name, user_mobile, photo, allergic, list_of_e):
        self.name = name
        self.user_mobile = user_mobile
        self.photo = photo
        self.allergic = allergic
        self.list_of_e = list_of_e

    def __repr__(self) -> str:
        return '<name {}>'.format(self.name)

    def serialize(self):
        return {
            'name': self.name,
            'user_mobile': self.user_mobile,
            'photo': self.photo,
            'allergic': self.allergic,
            'list_of_e': self.list_of_e
        }
