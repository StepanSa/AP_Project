from marshmallow import Schema, validate, fields
from flask_bcrypt import generate_password_hash
from datetime import date
import json


class UserData(Schema):
    id = fields.Integer()
    username = fields.String()
    firstName = fields.String()
    lastName = fields.String()
    email = fields.String()
    password = fields.String()
    phone = fields.String()
    birthDate = fields.Date()
    userStatus = fields.Integer()


class CreateUser(Schema):
    username = fields.String()
    firstName = fields.String()
    lastName = fields.String()
    email = fields.String(validate=validate.Email())
    password = fields.Function(deserialize=lambda obj: generate_password_hash(obj), load_only=True)
    phone = fields.Function(validate=validate.Regexp('^[+]*[(]{0,1}[0-9]{1,4}[)]{0,1}[\s0-9]{4,20}$'))
    birthDate = fields.Date(validate=lambda x: x < date.today())


class UpdateUser(Schema):
    firstName = fields.String()
    lastName = fields.String()
    email = fields.String(validate=validate.Email())
    password = fields.Function(deserialize=lambda obj: generate_password_hash(obj), load_only=True)
    phone = fields.Function(validate=validate.Regexp('^[+]*[(]{0,1}[0-9]{1,4}[)]{0,1}[\s0-9]{4,20}$'))


class GetUser(Schema):
    id = fields.Integer()
    username = fields.String()
    firstName = fields.String()
    lastName = fields.String()
    email = fields.String()
    phone = fields.String()
    birthDate = fields.Date()
    userStatus = fields.Integer()


class CreateTicket(Schema):
    name = fields.String()
    status = fields.String(validate=validate.OneOf(["free", "booked", "sold"]))
    price = fields.Integer()


class GetTicket(Schema):
    id = fields.Integer()
    name = fields.String()
    status = fields.String()
    price = fields.Integer()


class UpdateTicket(Schema):
    name = fields.String()
    status = fields.String()
    price = fields.Integer()


class GetOrder(Schema):
    id = fields.Integer()
    ticketId = fields.Integer()
    userId = fields.Integer()
    status = fields.String()


class PlaceOrder(Schema):
    # ticketId = fields.List(fields.Pluck(GetTicket, "id"))
    # userId = fields.Nested(UserData(only=("id",)))
    ticketId = fields.Integer()
    userId = fields.Integer()

    status = fields.String(validate=validate.OneOf(["placed", "approved", "denied"]))
