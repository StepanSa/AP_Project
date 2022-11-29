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
    isAdmin = fields.String()


class CreateUser(Schema):
    username = fields.String(required=True, validate=validate.Regexp('^[a-zA-Z\d\.-_]{4,120}$'))
    firstName = fields.String(required=True, validate=validate.Length(min=2))
    lastName = fields.String(required=True, validate=validate.Length(min=2))
    email = fields.String(validate=validate.Email())
    password = fields.Function(deserialize=lambda obj: generate_password_hash(obj), load_only=True)
    phone = fields.Function(validate=validate.Regexp('^[+]*[(]{0,1}[0-9]{1,4}[)]{0,1}[\s0-9]{4,20}$'))
    birthDate = fields.Date(validate=lambda x: x < date.today())
    isAdmin = fields.String(validate=validate.OneOf(choices=['0', '1']))


class UpdateUser(Schema):
    firstName = fields.String(validate=validate.Length(min=2))
    lastName = fields.String(validate=validate.Length(min=2))
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
    isAdmin = fields.String(validate=validate.OneOf(choices=['0', '1']), default="0")


class CreateTicket(Schema):
    name = fields.String()
    status = fields.String(validate=validate.OneOf(["free", "booked", "sold"]), default="free")
    price = fields.Integer()


class GetTicket(Schema):
    id = fields.Integer()
    name = fields.String()
    status = fields.String()
    price = fields.Integer()


class UpdateTicket(Schema):
    name = fields.String()
    status = fields.String(validate=validate.OneOf(["free", "booked", "sold"]), default="free")
    price = fields.Integer()


class GetOrder(Schema):
    id = fields.Integer()
    ticketId = fields.Integer()
    userId = fields.Integer()
    status = fields.String()


class PlaceOrder(Schema):
    ticketId = fields.Integer()
    userId = fields.Integer()
    status = fields.String(validate=validate.OneOf(["placed", "approved", "denied"]), default="placed")


class UpdateOrder(Schema):
    ticketId = fields.Integer()
    status = fields.String(validate=validate.OneOf(["placed", "approved", "denied"]))
