import pytest
from total.app import app
from total.models import User, Session, BaseModel, engine


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


@pytest.fixture
def user_info4():
    user_info = {
        "username": "bebey4",
        "firstName": "beb",
        "lastName": "us",
        "email": "wrong",
        "password": "beb123beb",
        "phone": "+380930232722",
        "birthDate": "2003-01-11",
        "isAdmin": "0"
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

    def test_user_create_invalid_isAdmin(self, wrapper, user_info1):
        user_info1["isAdmin"] = "1"
        response = app.test_client().post('/user', json=user_info1)
        assert response.status_code == 405
        assert response.data == b"Only admins can create other admins"

    def test_user_create_invalid_email(self, wrapper, user_info4):
        response = app.test_client().post('/user', json=user_info4)
        assert response.json == {
                        "Error": {
                            "email": [
                                "Not a valid email address."
                            ]
                        }
                    }

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

    def test_user_login_invalid(self, wrapper, user_info1):
        app.test_client().post('/user', json=user_info1)

        new_user = Session.query(User).filter(User.username == user_info1["username"]).first()

        resp = app.test_client().get('/login', json={"username": "", "password": "bebbebbeb"})

        assert resp.status_code == 401

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

    def test_user_update_self_invalid(self, wrapper, user_info2):
        app.test_client().post('/user', json=user_info2)

        new_user = Session.query(User).filter(User.username == user_info2["username"]).first()

        resp = app.test_client().get('/login', json={"username": new_user.username, "password": "beb123beb"})
        token = resp.json['token']
        print(token)

        response = app.test_client().put(f'/user/self', json={"email": "qwerty"}, headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 200
        assert response.json == {
                    "Error": {
                        "email": [
                            "Not a valid email address."
                        ]
                    }
                }


@pytest.fixture
def ticket1():
    ticket = {
        "name": "Jazz Concert",
        "status": "free",
        "price": 100
    }
    return ticket


@pytest.fixture
def ticket2():
    ticket = {
        "name": "Rock Concert",
        "status": "free",
        "price": -100
    }
    return ticket


@pytest.fixture
def ticket3():
    ticket = {
        "name": "Rock Concert",
        "status": "wrong",
        "price": 100
    }
    return ticket


class TestTicket:
    def test_ticket_create(self, wrapper, ticket1, user_info2):
        app.test_client().post('/user', json=user_info2)

        new_user = Session.query(User).filter(User.username == user_info2["username"]).first()
        new_user.isAdmin = '1'

        resp = app.test_client().get('/login', json={"username": new_user.username, "password": "beb123beb"})
        token = resp.json['token']

        response = app.test_client().post('/ticket', json=ticket1, headers={"Authorization": f"Bearer {token}"})
        print(response.json)
        assert response.status_code == 200
        assert response.data == b"Ticket created"

    def test_ticket_create_invalid_price(self, wrapper, ticket2, user_info2):
        app.test_client().post('/user', json=user_info2)

        new_user = Session.query(User).filter(User.username == user_info2["username"]).first()
        new_user.isAdmin = '1'

        resp = app.test_client().get('/login', json={"username": new_user.username, "password": "beb123beb"})
        token = resp.json['token']

        response = app.test_client().post('/ticket', json=ticket2, headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        assert response.json == {"Incorrect price input": 400}

    def test_ticket_create_invalid_status(self, wrapper, ticket3, user_info2):
        app.test_client().post('/user', json=user_info2)

        new_user = Session.query(User).filter(User.username == user_info2["username"]).first()
        new_user.isAdmin = '1'

        resp = app.test_client().get('/login', json={"username": new_user.username, "password": "beb123beb"})
        token = resp.json['token']

        response = app.test_client().post('/ticket', json=ticket3, headers={"Authorization": f"Bearer {token}"})

        assert response.json == { "Error": { "status": [ "Must be one of: free, booked, sold." ] } }

    def test_ticket_get_by_id(self, wrapper, ticket1, user_info2):
        app.test_client().post('/user', json=user_info2)

        new_user = Session.query(User).filter(User.username == user_info2["username"]).first()
        new_user.isAdmin = '1'

        resp = app.test_client().get('/login', json={"username": new_user.username, "password": "beb123beb"})
        token = resp.json['token']

        app.test_client().post('/ticket', json=ticket1, headers={"Authorization": f"Bearer {token}"})
        tid = 1
        response = app.test_client().get(f'/ticket/{tid}', json=ticket1, headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 200
        ti = response.json
        assert ti["name"] == "Jazz Concert"
        assert ti["price"] == 100
        assert ti["status"] == "free"
        assert ti["id"] == 1

    def test_ticket_delete_by_id(self, wrapper, ticket1, user_info2):
        app.test_client().post('/user', json=user_info2)

        new_user = Session.query(User).filter(User.username == user_info2["username"]).first()
        new_user.isAdmin = '1'

        resp = app.test_client().get('/login', json={"username": new_user.username, "password": "beb123beb"})
        token = resp.json['token']

        app.test_client().post('/ticket', json=ticket1, headers={"Authorization": f"Bearer {token}"})
        tid = 1
        response = app.test_client().delete(f'/ticket/{tid}', json=ticket1, headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 200
        assert response.data == b"Deleted successfully"

    def test_ticket_update_by_id(self, wrapper, ticket1, user_info2):
        app.test_client().post('/user', json=user_info2)

        new_user = Session.query(User).filter(User.username == user_info2["username"]).first()
        new_user.isAdmin = '1'

        resp = app.test_client().get('/login', json={"username": new_user.username, "password": "beb123beb"})
        token = resp.json['token']

        app.test_client().post('/ticket', json=ticket1, headers={"Authorization": f"Bearer {token}"})
        tid = 1
        response = app.test_client().put(f'/ticket/{tid}', json={"name": "Rock Concert"}, headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 200
        assert response.data == b"Updated successfully"

    def test_ticket_update_by_id_invalid_status(self, wrapper, ticket1, user_info2):
        app.test_client().post('/user', json=user_info2)

        new_user = Session.query(User).filter(User.username == user_info2["username"]).first()
        new_user.isAdmin = '1'

        resp = app.test_client().get('/login', json={"username": new_user.username, "password": "beb123beb"})
        token = resp.json['token']

        app.test_client().post('/ticket', json=ticket1, headers={"Authorization": f"Bearer {token}"})
        tid = 1
        response = app.test_client().put(f'/ticket/{tid}', json={"status": "wrong"}, headers={"Authorization": f"Bearer {token}"})

        assert response.json == { "Error": { "status": [ "Must be one of: free, booked, sold." ] } }

    def test_ticket_get_by_status(self, wrapper, ticket1, user_info2):
        app.test_client().post('/user', json=user_info2)

        new_user = Session.query(User).filter(User.username == user_info2["username"]).first()
        new_user.isAdmin = '1'

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

    def test_ticket_get_by_status_invalid(self, wrapper, ticket1, user_info2):
        app.test_client().post('/user', json=user_info2)

        new_user = Session.query(User).filter(User.username == user_info2["username"]).first()
        new_user.isAdmin = '1'

        resp = app.test_client().get('/login', json={"username": new_user.username, "password": "beb123beb"})
        token = resp.json['token']

        app.test_client().post('/ticket', json=ticket1, headers={"Authorization": f"Bearer {token}"})

        ts = "wrong"
        response = app.test_client().get(f'/ticket/inventory/{ts}', headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 200
        assert response.json == {'Invalid status': 400}


@pytest.fixture
def transaction1():
    order = {
        "ticketId": 1,
        "userId": 1,
        "status": "placed"
    }
    return order


@pytest.fixture
def transaction2():
    order = {
        "ticketId": 1,
        "userId": 1,
        "status": "wrong"
    }
    return order


class TestTransaction:
    def test_transaction_create(self, wrapper, transaction1, ticket1, user_info1):
        app.test_client().post('/user', json=user_info1)

        new_user = Session.query(User).filter(User.username == user_info1["username"]).first()
        new_user.isAdmin = '1'

        resp = app.test_client().get('/login', json={"username": new_user.username, "password": "bebbebbeb"})
        token = resp.json['token']

        res = app.test_client().post('/ticket', json=ticket1, headers={"Authorization": f"Bearer {token}"})
        print(res.json)

        response = app.test_client().post('/transaction/order', json=transaction1, headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 200
        assert response.data == b'Order added'

    def test_transaction_create_invalid(self, wrapper, transaction2, ticket1, user_info1):
        app.test_client().post('/user', json=user_info1)

        new_user = Session.query(User).filter(User.username == user_info1["username"]).first()
        new_user.isAdmin = '1'

        resp = app.test_client().get('/login', json={"username": new_user.username, "password": "bebbebbeb"})
        token = resp.json['token']

        app.test_client().post('/ticket', json=ticket1, headers={"Authorization": f"Bearer {token}"})

        response = app.test_client().post('/transaction/order', json=transaction2, headers={"Authorization": f"Bearer {token}"})

        assert response.json == { "Error": { "status": [ "Must be one of: placed, approved, denied." ] } }

    def test_transaction_cancel(self, wrapper, transaction1, ticket1, user_info2):
        app.test_client().post('/user', json=user_info2)

        new_user = Session.query(User).filter(User.username == user_info2["username"]).first()
        new_user.isAdmin = '1'

        resp = app.test_client().get('/login', json={"username": new_user.username, "password": "beb123beb"})
        token = resp.json['token']

        app.test_client().post('/ticket', json=ticket1, headers={"Authorization": f"Bearer {token}"})

        app.test_client().post('/transaction/order', json=transaction1, headers={"Authorization": f"Bearer {token}"})

        tid = 1

        response = app.test_client().put(f'/transaction/order/{tid}', json={"status": "denied"}, headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 200
        assert response.data == b"Updated successfully"

    def test_transaction_cancel_invalid(self, wrapper, transaction1, ticket1, user_info2):
        app.test_client().post('/user', json=user_info2)

        new_user = Session.query(User).filter(User.username == user_info2["username"]).first()
        new_user.isAdmin = '1'

        resp = app.test_client().get('/login', json={"username": new_user.username, "password": "beb123beb"})
        token = resp.json['token']

        app.test_client().post('/ticket', json=ticket1, headers={"Authorization": f"Bearer {token}"})

        app.test_client().post('/transaction/order', json=transaction1, headers={"Authorization": f"Bearer {token}"})

        tid = 1

        response = app.test_client().put(f'/transaction/order/{tid}', json={"status": "wrong"}, headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 200
        assert response.data == b"Updated successfully"

    def test_transaction_order_get_by_id(self, wrapper, transaction1, ticket1, user_info2):
        app.test_client().post('/user', json=user_info2)

        new_user = Session.query(User).filter(User.username == user_info2["username"]).first()
        new_user.isAdmin = '1'

        resp = app.test_client().get('/login', json={"username": new_user.username, "password": "beb123beb"})
        token = resp.json['token']

        app.test_client().post('/ticket', json=ticket1, headers={"Authorization": f"Bearer {token}"})
        app.test_client().post('/transaction/order', json=transaction1, headers={"Authorization": f"Bearer {token}"})
        tid = 1
        response = app.test_client().get(f'/transaction/order/{tid}', json=transaction1, headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 200
        ti = response.json
        assert ti["ticketId"] == 1
        assert ti["userId"] == 1
        assert ti["status"] == "placed"
        assert ti["id"] == 1

    def test_transaction_orders_get(self, wrapper, transaction1, ticket1, user_info2):
        app.test_client().post('/user', json=user_info2)

        new_user = Session.query(User).filter(User.username == user_info2["username"]).first()
        new_user.isAdmin = '1'

        resp = app.test_client().get('/login', json={"username": new_user.username, "password": "beb123beb"})
        token = resp.json['token']

        app.test_client().post('/ticket', json=ticket1, headers={"Authorization": f"Bearer {token}"})
        app.test_client().post('/transaction/order', json=transaction1, headers={"Authorization": f"Bearer {token}"})
        response = app.test_client().get('/transaction/inventory', json=transaction1, headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 200
        ti = response.json
        assert ti[0]["ticketId"] == 1
        assert ti[0]["userId"] == 1
        assert ti[0]["status"] == "placed"
        assert ti[0]["id"] == 1

    def test_transaction_order_get_by_id_invalid(self, wrapper, transaction1, ticket1, user_info2):
        app.test_client().post('/user', json=user_info2)

        new_user = Session.query(User).filter(User.username == user_info2["username"]).first()
        new_user.isAdmin = '1'

        resp = app.test_client().get('/login', json={"username": new_user.username, "password": "beb123beb"})
        token = resp.json['token']

        app.test_client().post('/ticket', json=ticket1, headers={"Authorization": f"Bearer {token}"})
        app.test_client().post('/transaction/order', json=transaction1, headers={"Authorization": f"Bearer {token}"})
        tid = 2
        response = app.test_client().get(f'/transaction/order/{tid}', json=transaction1, headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 400
        assert response.data == b"Invalid id"

    def test_transaction_order_delete_by_id(self, wrapper, transaction1, ticket1, user_info2):
        app.test_client().post('/user', json=user_info2)

        new_user = Session.query(User).filter(User.username == user_info2["username"]).first()
        new_user.isAdmin = '1'

        resp = app.test_client().get('/login', json={"username": new_user.username, "password": "beb123beb"})
        token = resp.json['token']

        app.test_client().post('/ticket', json=ticket1, headers={"Authorization": f"Bearer {token}"})
        app.test_client().post('/transaction/order', json=transaction1, headers={"Authorization": f"Bearer {token}"})
        tid = 1
        response = app.test_client().delete(f'/transaction/order/{tid}', json=transaction1, headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 200
        assert response.data == b'Deleted successfully'

    def test_transaction_order_delete_by_id_invalid(self, wrapper, transaction1, ticket1, user_info2):
        app.test_client().post('/user', json=user_info2)

        new_user = Session.query(User).filter(User.username == user_info2["username"]).first()
        new_user.isAdmin = '1'

        resp = app.test_client().get('/login', json={"username": new_user.username, "password": "beb123beb"})
        token = resp.json['token']

        app.test_client().post('/ticket', json=ticket1, headers={"Authorization": f"Bearer {token}"})
        app.test_client().post('/transaction/order', json=transaction1, headers={"Authorization": f"Bearer {token}"})
        tid = 2
        response = app.test_client().delete(f'/transaction/order/{tid}', json=transaction1, headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 400
        assert response.data == b'Invalid id'
