from base64 import b64encode
import base64
import pytest
from total.app import app
from total.models import User, Session, Ticket, Transaction, BaseModel, engine
from flask import url_for, Flask, request


# @pytest.fixture(scope='function')
# def wrapper():
#     # Session().close()
#     BaseModel.metadata.drop_all(engine)
#     BaseModel.metadata.create_all(engine)


@pytest.fixture
def user_info1():
    user_info = {
        "username": "bebey1",
        "firstName": "play",
        "lastName": "boy",
        "email": "playboy@gmail.com",
        "password": "bebbebbeb",
        "phone": "+380930232722",
        "birthDate": "2003-01-11",
        "isAdmin": "0"
    }
    return user_info


@pytest.fixture
def user_info2():
    user_info = {
        "username": "bebey2",
        "firstName": "beb",
        "lastName": "us",
        "email": "bebus@gmail.com",
        "password": "beb123beb",
        "phone": "+380930232722",
        "birthDate": "2003-01-11",
        "isAdmin": "0"
    }
    return user_info


@pytest.fixture
def user_info3():
    user_info = {
        "username": "admin",
        "firstName": "admin",
        "lastName": "admin",
        "email": "admin@gmail.com",
        "password": "admin123",
        "phone": "+380689098277",
        "birthDate": "1998-04-12",
        "isAdmin": "1"
    }
    return user_info


@pytest.fixture(scope='function')
def wrapper(request):
    Session.close()
    BaseModel.metadata.drop_all(engine)
    BaseModel.metadata.create_all(engine)


class TestUser:

    def test_user_create(self, wrapper, user_info1):
        response = app.test_client().post('/user', json=user_info1)
        assert response.status_code == 200
        assert response.data == b"New user was successfully created!"

    def test_user_create_invalid(self, wrapper, user_info1):
        user_info1["isAdmin"] = "1"
        response = app.test_client().post('/user', json=user_info1)
        assert response.status_code == 405
        assert response.data == b"Only admins can create other admins"

    def test_user_create_username_used(self, wrapper, user_info1, user_info2):
        user_info2["username"] = "bebey1"
        app.test_client().post('/user', json=user_info1)
        response = app.test_client().post('/user', json=user_info2)
        assert response.status_code == 400
        assert response.data == b'Username already taken'

    def test_user_login(self, wrapper, user_info1):
        app.test_client().post('/user', json=user_info1)

        new_user = Session.query(User).filter(User.username == user_info1["username"]).first()

        resp = app.test_client().get('/login', json={"username": new_user.username, "password": "bebbebbeb"})
        token = resp.json['token']

        assert token is not None

    def test_user_delete(self, wrapper, user_info1):
        app.test_client().post('/user', json=user_info1)

        new_user = Session.query(User).filter(User.username == user_info1["username"]).first()

        resp = app.test_client().get('/login', json={"username": new_user.username, "password": "bebbebbeb"})
        token = resp.json['token']

        response = app.test_client().delete(f'/user/self', headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 200
        assert response.data == b"User deleted"

    def test_user_get_by_id(self, wrapper, user_info2):
        app.test_client().post('/user', json=user_info2)

        new_user = Session.query(User).filter(User.username == user_info2["username"]).first()

        resp = app.test_client().get('/login', json={"username": new_user.username, "password": "beb123beb"})
        token = resp.json['token']

        response = app.test_client().get(f'/user/{new_user.id}', headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        ui = response.json
        assert ui["firstName"] == "beb"
        assert ui["lastName"] == "us"
        assert ui["email"] == "bebus@gmail.com"
        assert ui["phone"] == "+380930232722"
        assert ui["birthDate"] == "2003-01-11"
        assert ui["username"] == "bebey2"

    def test_user_delete_by_id(self, wrapper, user_info1):
        app.test_client().post('/user', json=user_info1)

        new_user = Session.query(User).filter(User.username == user_info1["username"]).first()

        resp = app.test_client().get('/login', json={"username": new_user.username, "password": "bebbebbeb"})
        token = resp.json['token']

        response = app.test_client().delete(f'/user/{new_user.id}', headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 200
        assert response.data == b"User deleted"

    def test_user_get_self(self, wrapper, user_info2):
        app.test_client().post('/user', json=user_info2)

        new_user = Session.query(User).filter(User.username == user_info2["username"]).first()

        resp = app.test_client().get('/login', json={"username": new_user.username, "password": "beb123beb"})
        token = resp.json['token']

        response = app.test_client().get(f'/user/self', headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        ui = response.json
        assert ui["firstName"] == "beb"
        assert ui["lastName"] == "us"
        assert ui["email"] == "bebus@gmail.com"
        assert ui["phone"] == "+380930232722"
        assert ui["birthDate"] == "2003-01-11"
        assert ui["username"] == "bebey2"

    def test_user_update_self(self, wrapper, user_info2):
        app.test_client().post('/user', json=user_info2)

        new_user = Session.query(User).filter(User.username == user_info2["username"]).first()

        resp = app.test_client().get('/login', json={"username": new_user.username, "password": "beb123beb"})
        token = resp.json['token']

        response = app.test_client().put(f'/user/self', json={"firstName": "new8"}, headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 200
        assert response.data == b"Updated successfully"


@pytest.fixture
def ticket1():
    ticket = {
        "name": "Jazz Concert",
        "status": "free",
        "price": 100
    }
    return ticket


class TestTicket:
    def test_ticket_create(self, wrapper, ticket1, user_info2):
        app.test_client().post('/user', json=user_info2)

        new_user = Session.query(User).filter(User.username == user_info2["username"]).first()

        resp = app.test_client().get('/login', json={"username": new_user.username, "password": "beb123beb"})
        token = resp.json['token']

        response = app.test_client().post('/ticket', json=ticket1, headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        assert response.data == b"Ticket created"

    def test_ticket_get_by_status(self, wrapper, ticket1, user_info2):
        app.test_client().post('/user', json=user_info2)

        new_user = Session.query(User).filter(User.username == user_info2["username"]).first()

        resp = app.test_client().get('/login', json={"username": new_user.username, "password": "beb123beb"})
        token = resp.json['token']

        app.test_client().post('/ticket', json=ticket1, headers={"Authorization": f"Bearer {token}"})

        ts = "free"
        response = app.test_client().get(f'/ticket/inventory/{ts}', headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 200
        ti = response.json
        assert ti[0]["name"] == "Jazz Concert"
        assert ti[0]["price"] == 100
        assert ti[0]["status"] == "free"
        assert ti[0]["id"] == 1

    # def test_ticket_get_by_status_invalid(self, wrapper, ticket1, user_info2):
    #     app.test_client().post('/user', json=user_info2)
    #
    #     new_user = Session.query(User).filter(User.username == user_info2["username"]).first()
    #
    #     resp = app.test_client().get('/login', json={"username": new_user.username, "password": "beb123beb"})
    #     token = resp.json['token']
    #
    #     app.test_client().post('/ticket', json=ticket1, headers={"Authorization": f"Bearer {token}"})
    #
    #     ts = "free"
    #     response = app.test_client().get(f'/ticket/inventory/{ts}', headers={"Authorization": f"Bearer {token}"})
    #     print('---------------------------------------')
    #     print(response.json)
    #
    #     assert response.json == {'code': 401, 'error': 'User must be an admin to use get_ticket_by_status.'}






@pytest.fixture
def transaction1():
    order = {
        "ticketId": 1,
        "userId": 1,
        "status": "placed"
    }
    return order


class TestTransaction:
    def test_transaction_create(self, wrapper, transaction1, ticket1, user_info1):
        app.test_client().post('/user', json=user_info1)

        new_user = Session.query(User).filter(User.username == user_info1["username"]).first()

        resp = app.test_client().get('/login', json={"username": new_user.username, "password": "bebbebbeb"})
        token = resp.json['token']

        app.test_client().post('/ticket', json=ticket1, headers={"Authorization": f"Bearer {token}"})

        response = app.test_client().post('/transaction/order', json=transaction1, headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 200
        assert response.data == b'Order added'

    def test_transaction_cancel(self, wrapper, transaction1, ticket1, user_info1):
        app.test_client().post('/user', json=user_info1)

        new_user = Session.query(User).filter(User.username == user_info1["username"]).first()

        resp = app.test_client().get('/login', json={"username": new_user.username, "password": "bebbebbeb"})
        token = resp.json['token']

        app.test_client().post('/ticket', json=ticket1, headers={"Authorization": f"Bearer {token}"})

        app.test_client().post('/transaction/order', json=transaction1, headers={"Authorization": f"Bearer {token}"})

        tid = 1

        response = app.test_client().put(f'/transaction/order/{tid}', json={"status": "denied"}, headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 200
        assert response.data == b"Updated successfully"

    def test_transaction_orders_by_user(self, wrapper, transaction1, ticket1, user_info1):
        app.test_client().post('/user', json=user_info1)

        new_user = Session.query(User).filter(User.username == user_info1["username"]).first()

        resp = app.test_client().get('/login', json={"username": new_user.username, "password": "bebbebbeb"})
        token = resp.json['token']

        app.test_client().post('/ticket', json=ticket1, headers={"Authorization": f"Bearer {token}"})

        app.test_client().post('/transaction/order', json=transaction1, headers={"Authorization": f"Bearer {token}"})

        uid = 1
        response = app.test_client().get(f'/transaction/ordersby/{uid}', headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 200
        oi = response.json
        assert oi[0]["ticketId"] == 1
        assert oi[0]["userId"] == 1
        assert oi[0]["status"] == "placed"
        assert oi[0]["id"] == 1



