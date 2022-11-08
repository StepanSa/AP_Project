from marshmallow import Schema, validate, fields
from flask_bcrypt import generate_password_hash
from datetime import date


class User(Schema):
    id = fields.Integer()
    username = fields.String()
    firstName = fields.String()
    lastName = fields.String()
    email = fields.String(validate=validate.Email())
    password = fields.Function()
    phone = fields.Function()
    birthDate = fields.Date()
    userStatus = fields.Integer(validate=validate.OneOf(["0", "1"]))


class CreateUser(Schema):
    username = fields.String()
    firstName = fields.String()
    lastName = fields.String()
    email = fields.String(validate=validate.Email())
    password = fields.Function(deserialize=lambda obj: generate_password_hash(obj), load_only=True)
    phone = fields.Function(validate=validate.Regexp('^[+]*[(]{0,1}[0-9]{1,4}[)]{0,1}[\s0-9]{4,20}$'))
    birthDate = fields.Date(validate=lambda x: x < date.today())
