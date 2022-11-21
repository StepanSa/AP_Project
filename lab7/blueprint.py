from flask import Blueprint, jsonify, request, make_response
from flask_jwt import current_identity
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_bcrypt import check_password_hash
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


def admin_required(func):
	def wrapper(*args, **kwargs):
		current_identity_username = get_jwt_identity()
		user = db_utils.get_entry_by_username(User, current_identity_username)
		if user.isAdmin == '1':
			return func(*args, **kwargs)
		else:
			return StatusResponse(jsonify({"error": f"User must be an admin to use {func.__name__}."}), 401)

	wrapper.__name__ = func.__name__
	return wrapper


def StatusResponse(response, code):
	param = response.json
	if isinstance(param, list):
		param.append({"code": code})
	else:
		param.update({"code": code})
	end_response = make_response(jsonify(param), code)
	return end_response


######################################################################################################
# User


@api_blueprint.route("/user", methods=["POST"])
def create_user():
	try:
		user_data = CreateUser().load(request.json)
		if db_utils.is_name_taken(User, user_data["username"]):
			return make_response({"Username already taken": 400})

		user = None
		if request.authorization is not None:
			current_identity_username = get_jwt_identity()

		if (request.authorization is None or user is None
			or db_utils.get_entry_by_username(User, current_identity_username).isAdmin == '0') and \
				'isAdmin' in user_data.keys() and user_data['isAdmin'] == '1':
			return StatusResponse(jsonify({"error": "Only admins can create other admins"}), 405)
	except ValidationError as e:
		response = dict({"Error": e.normalized_messages()})
		return response

	user = db_utils.create_entry(User, **user_data)
	return jsonify(GetUser().dump(user))


@api_blueprint.route("/login", methods=["GET"])
def login():
	auth = request.authorization

	if not auth or not auth.username or not auth.password:
		return make_response('could not verify', 401, {'WWW.Authentication': 'Basic realm: "login required"'})

	user = db_utils.get_entry_by_username(User, auth.username)

	if check_password_hash(user.password, auth.password):
		access_token = create_access_token(identity=user.username)
		return jsonify({'token': access_token})

	return make_response('could not verify\n', 401, {'WWW.Authentication': 'Basic realm:"login required"'})


@api_blueprint.route("/user/<int:uid>", methods=["GET", "DELETE"])
@jwt_required()
@admin_required
def get_user_by_id(uid):
	if request.method == "GET":
		current_identity_username = get_jwt_identity()
		user = db_utils.get_entry_by_id(User, uid)

		if current_identity_username != user.username:
			return jsonify('Access is denied')

		if user == 400:
			return make_response({"Invalid id": 400})

		return jsonify(GetUser().dump(user))

	elif request.method == "DELETE":
		current_identity_username = get_jwt_identity()
		user = db_utils.get_entry_by_id(User, uid)

		if current_identity_username != user.username:
			return jsonify('Access is denied')

		if user == 400:
			return make_response({"Invalid id": 400})
		db_utils.delete_entry(User, uid)
		return make_response({"code": 200})


@api_blueprint.route("/user/self", methods=["GET"])
@jwt_required()
def get_user_self():
	current_identity_username = get_jwt_identity()
	user = db_utils.get_entry_by_username(User, current_identity_username)

	if current_identity_username != user.username:
		return jsonify('Access is denied')
	return jsonify(GetUser().dump(user))


@api_blueprint.route("/user/self", methods=["PUT"])
@jwt_required()
def update_user_self():
	try:
		current_identity_username = get_jwt_identity()
		user = db_utils.get_entry_by_username(User, current_identity_username)
		user_data = UpdateUser().load(request.json)
		db_utils.update_entry(user, **user_data)
	except ValidationError as e:
		response = dict({"Error": e.normalized_messages()})
		return response
	return make_response({"code": 200})


@api_blueprint.route("/user/self", methods=["DELETE"])
@jwt_required()
def delete_user_self():
	current_identity_username = get_jwt_identity()
	user = db_utils.get_entry_by_username(User, current_identity_username)
	uid = user.id
	db_utils.delete_entry(User, uid)
	return make_response({"code": 200})


######################################################################################################
# Ticket

@api_blueprint.route("/ticket", methods=["POST"])
@jwt_required()
@admin_required
def create_ticket():
	try:
		ticket_data = CreateTicket().load(request.json)
		if ticket_data["price"] < 0:
			return make_response({"Incorrect price input": 400})
		ticket = db_utils.create_entry(Ticket, **ticket_data)
	except ValidationError as e:
		response = dict({"Error": e.normalized_messages()})
		return response
	return jsonify(GetTicket().dump(ticket))


@api_blueprint.route("/ticket/<int:id>", methods=["GET"])
def get_ticket_by_id(id):
	ticket = db_utils.get_entry_by_id(Ticket, id)
	if ticket == 400:
		return make_response({"Invalid id": 400})
	return jsonify(GetTicket().dump(ticket))

@api_blueprint.route("/ticket/<int:id>", methods=["DELETE"])
@jwt_required()
@admin_required
def delete_ticket_by_id(id):
	ticket = db_utils.get_entry_by_id(Ticket, id)
	if ticket == 400:
		return make_response({"Invalid id": 400})
	db_utils.delete_entry(Ticket, id)
	return make_response({"code": 200})


@api_blueprint.route("/ticket/<int:id>", methods=["PUT"])
@jwt_required()
@admin_required
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

@api_blueprint.route("/ticket/inventory/<string:status>", methods=["GET"])
@jwt_required()
@admin_required
def get_ticket_by_status(status):
	try:
		ticket = db_utils.get_entry_all_ticket_by_status(Ticket, status)
		print(status)
		if status != "booked" and status!="sold" and status!="free":
			return make_response({"Invalid status": 400})
	except ValidationError as e:
		response = dict({"Error": e.normalized_messages()})
		return response
	return jsonify(GetTicket(many=True).dump(ticket))


######################################################################################################
# Transaction



@api_blueprint.route("/transaction/order", methods=["POST"])
@jwt_required()
def create_transaction():
	try:
		current_identity_username = get_jwt_identity()
		user = db_utils.get_entry_by_username(User, current_identity_username)
		userId=user.id

		var=request.json
		var.update({"userId": userId})
		varjson = json.dumps(var)

		transaction_data = PlaceOrder().load(json.loads(varjson))

		if(transaction_data["status"]=="denied"):
			return make_response({"The ticket status can`t be denied": 402})

		if not db_utils.does_ticket_exist(Ticket, transaction_data["ticketId"]):
			return make_response({"Ticket does not exists": 401})
		if db_utils.is_ticket_taken(Ticket, transaction_data["ticketId"]):
			return make_response({"Ticket is unavailable": 400})

		ticket=db_utils.get_entry_by_id(Ticket, transaction_data["ticketId"])

		if(transaction_data["status"]=="approved"):
			ticket.status="sold"

		elif (transaction_data["status"] == "placed"):
			ticket.status="booked"

		ticket_data={"status":ticket.status}
		db_utils.update_entry(ticket,**ticket_data)

		transaction = db_utils.create_order(**transaction_data)
	except ValidationError as e:
		response = dict({"Error": e.normalized_messages()})
		return response
	return jsonify(GetOrder().dump(transaction))


@api_blueprint.route("/transaction/order/<int:TransactionId>", methods=["PUT"])
@jwt_required()
def cancel_transaction(TransactionId):
	try:
		current_identity_username = get_jwt_identity()
		user = db_utils.get_entry_by_username(User, current_identity_username)

		transaction = db_utils.get_entry_by_id(Transaction,TransactionId)

		if(transaction.userId!=user.id):
			return make_response({"The transaction id is not yours": 402})
		if (transaction.status == "denied"):
			return make_response({"The ticket is already denied": 403})

		transaction.status="denied"

		transaction_data = {"status":transaction.status}
		db_utils.update_entry(transaction, **transaction_data)

		ticket=db_utils.get_entry_by_id(Ticket, transaction.ticketId)
		ticket.status="free"
		ticket_data = {"status": ticket.status}
		db_utils.update_entry(ticket, **ticket_data)

	except ValidationError as e:
		response = dict({"Error": e.normalized_messages()})
		return response
	return jsonify(GetOrder().dump(transaction))


@api_blueprint.route("/transaction/inventory", methods=["GET"])
@jwt_required()
@admin_required
def get_transactions():
	transaction = db_utils.get_entry_all(Transaction)
	return jsonify(GetOrder(many=True).dump(transaction))


@api_blueprint.route("/transaction/order/<int:id>", methods=["GET"])
@jwt_required()
@admin_required
def get_order_by_id(id):
	if request.method == "GET":
		transaction = db_utils.get_entry_by_id(Transaction, id)
		if transaction == 400:
			return make_response({"Invalid id": 400})
		return jsonify(GetOrder().dump(transaction))

@api_blueprint.route("/transaction/order/<int:id>", methods=["DELETE"])
@jwt_required()
@admin_required
def delete_order_by_id(id):
	transaction = db_utils.get_entry_by_id(Transaction, id)
	if transaction == 400:
		return make_response({"Invalid id": 400})
	db_utils.delete_entry(Transaction, id)
	return make_response({"code": 200})


@api_blueprint.route("/transaction/ordersby/<int:id>", methods=["GET"])
@jwt_required()
def order_by_user(id):
	current_identity_username = get_jwt_identity()
	user = db_utils.get_entry_by_username(User, current_identity_username)

	if(user.isAdmin=="0"):
		if (id != user.id):
			return make_response({"The transaction id is not yours": 402})

		transaction = db_utils.get_entry_all_transaction_by_id(Transaction, id)

		if transaction == 400:
			return make_response({"The user doesn`t have any transactions": 405})

		return jsonify(GetOrder(many=True).dump(transaction))

	else:
		transaction = db_utils.get_entry_all_transaction_by_id(Transaction, id)

		if transaction == 400:
			return make_response({"The user doesn`t have any transactions": 405})

		return jsonify(GetOrder(many=True).dump(transaction))
