from flask import Blueprint, jsonify, request
import db_utils
# from middlewares import db_lifecycle
from lab6.models import User, Ticket, Transaction
from schemas import (
    # Order,
    # PlaceOrder,
    User,
    CreateUser,
    # UpdateUser,
    # GetUser,
    # Ticket,
    # CreateTicket
)


api_blueprint = Blueprint('api', __name__)


@api_blueprint.route("/user", methods=["POST"])
def create_user():
    user_data = CreateUser().load(request.json)
    user = db_utils.create_entry(User, **user_data)
    return jsonify(User().dump(user))


@api_blueprint.route("/hello-world")
def hello_world_def():
    return f"Hello world"


