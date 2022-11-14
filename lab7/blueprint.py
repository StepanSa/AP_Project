from flask import Blueprint, jsonify, request, make_response
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from lab7 import db_utils
import json
# from middlewares import db_lifecycle
from lab6.models import User, Ticket, Transaction, Session
from schemas import (
    GetOrder,
    PlaceOrder,
    UserData,
    CreateUser,
    UpdateUser,
    GetUser,
    GetTicket,
    CreateTicket,
    UpdateTicket
)


api_blueprint = Blueprint('api', __name__)




######################################################################################################
# User

@api_blueprint.route("/user", methods=["POST"])
def create_user():
    try:
        user_data = CreateUser().load(request.json)
        if db_utils.is_name_taken(User, user_data["username"]):
            return make_response({"Username already taken": 400})
        user = db_utils.create_entry(User, **user_data)
    except ValidationError as e:
        response = dict({"Error": e.normalized_messages()})
        return response
    return jsonify(GetUser().dump(user))


@api_blueprint.route("/user/<int:uid>", methods=["GET", "DELETE"])
def get_user_by_id(uid):
    if request.method == "GET":
        user = db_utils.get_entry_by_id(User, uid)
        if user == 400:
            return make_response({"Invalid id": 400})
        return jsonify(GetUser().dump(user))
    elif request.method == "DELETE":
        user = db_utils.get_entry_by_id(User, uid)
        if user == 400:
            return make_response({"Invalid id": 400})
        db_utils.delete_entry(User, uid)
        return make_response({"code": 200})


@api_blueprint.route("/user/self", methods=["GET"])
def get_user_self(uid=1):
    user = db_utils.get_entry_self(User, uid)
    return jsonify(GetUser().dump(user))


@api_blueprint.route("/user/self", methods=["PUT"])
def update_user_self(uid=1):
    try:
        user_data = UpdateUser().load(request.json)
        user = db_utils.get_entry_self(User, uid)
        db_utils.update_entry(user, **user_data)
    except ValidationError as e:
        response = dict({"Error": e.normalized_messages()})
        return response
    return make_response({"code": 200})


@api_blueprint.route("/user/self", methods=["DELETE"])
def delete_user_self(uid=1):
    db_utils.delete_entry(User, uid)
    return make_response({"code": 200})


######################################################################################################
# Ticket

@api_blueprint.route("/ticket", methods=["POST"])
def create_ticket():
    try:
        selfid = 1
        ticket_data = CreateTicket().load(request.json)
        if ticket_data["price"] < 0:
            return make_response({"Incorrect price input": 400})
        ticket = db_utils.create_entry(Ticket, **ticket_data)
    except ValidationError as e:
        response = dict({"Error": e.normalized_messages()})
        return response
    return jsonify(GetTicket().dump(ticket))


@api_blueprint.route("/ticket/<int:id>", methods=["GET", "DELETE"])
def get_ticket_by_id(id):
    if request.method == "GET":
        ticket = db_utils.get_entry_by_id(Ticket, id)
        if ticket == 400:
            return make_response({"Invalid id": 400})
        return jsonify(GetTicket().dump(ticket))
    elif request.method == "DELETE":
        ticket = db_utils.get_entry_by_id(Ticket, id)
        if ticket == 400:
            return make_response({"Invalid id": 400})
        db_utils.delete_entry(Ticket, id)
        return make_response({"code": 200})


@api_blueprint.route("/ticket/<int:id>", methods=["PUT"])
def update_ticket(id):
    try:
        ticket_data = UpdateTicket().load(request.json)
        ticket = db_utils.get_entry_by_id(Ticket, id)
        if ticket == 400:
            return make_response({"Invalid id": 400})
        db_utils.update_entry(ticket, **ticket_data)
    except ValidationError as e:
        response = dict({"Error": e.normalized_messages()})
        return response
    return make_response({"code": 200})

######################################################################################################
# Transaction


@api_blueprint.route("/transaction/order", methods=["POST"])
def create_transaction():
    try:
        transaction_data = PlaceOrder().load(request.json)
        if db_utils.is_ticket_taken(Transaction, transaction_data["ticketId"]):
            return make_response({"Ticket is unavailable": 400})
        transaction = db_utils.create_entry(Transaction, **transaction_data)
    except ValidationError as e:
        response = dict({"Error": e.normalized_messages()})
        return response
    return jsonify(GetOrder().dump(transaction))


@api_blueprint.route("/transaction/inventory", methods=["GET"])
def get_transactions():
    transaction = db_utils.get_entry_all(Transaction)
    return jsonify(GetOrder(many=True).dump(transaction))


@api_blueprint.route("/transaction/order/<int:id>", methods=["GET", "DELETE"])
def order_by_id(id):
    if request.method == "GET":
        transaction = db_utils.get_entry_by_id(Transaction, id)
        if transaction == 400:
            return make_response({"Invalid id": 400})
        return jsonify(GetOrder().dump(transaction))
    elif request.method == "DELETE":
        transaction = db_utils.get_entry_by_id(Transaction, id)
        if transaction == 400:
            return make_response({"Invalid id": 400})
        db_utils.delete_entry(Transaction, id)
        return make_response({"code": 200})


@api_blueprint.route("/transaction/orderby/<int:id>", methods=["GET"])
def order_by_user(id):
    user = db_utils.get_entry_by_id(User, id)
    if user == 400:
        return make_response({"Invalid id": 400})
    transaction = db_utils.get_entry_user(Transaction, id)
    return jsonify(GetOrder(many=True).dump(transaction))



