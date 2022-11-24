from sqlalchemy import desc, exists

from total.models import Session, User, Ticket, Transaction


def is_id_taken(model_class, id):
    session = Session()
    print(session.query(exists().where(model_class.id == id)).scalar())
    return session.query(exists().where(model_class.id == id)).scalar()


def create_entry(model_class, *, commit=True, **kwargs):
    session = Session()
    entry = model_class(**kwargs)
    session.add(entry)
    if commit:
        session.commit()
    return entry


def get_entry_by_id(model_class, id, **kwargs):
    session = Session()
    if session.query(model_class).filter_by(id=id, **kwargs).all() == []:
        return 400
    return session.query(model_class).filter_by(id=id, **kwargs).one()


def get_entry_by_username(model_class, username, **kwargs):
    session = Session()
    if session.query(model_class).filter_by(username=username, **kwargs).all() == []:
        return 400
    return session.query(model_class).filter_by(username=username, **kwargs).one()


def get_entry_all(model_class):
    session = Session()
    return session.query(model_class).all()


def get_entry_all_ticket_by_status(model_class, status, **kwargs):
    session = Session()
    if session.query(model_class).filter_by(status=status, **kwargs).all() == []:
        return 400
    return session.query(model_class).filter_by(status=status, **kwargs).all()

def get_entry_all_transaction_by_id(model_class, id, **kwargs):
    session = Session()
    if session.query(model_class).filter_by(userId=id, **kwargs).all() == []:
        return 400
    return session.query(model_class).filter_by(userId=id, **kwargs).all()


def get_entry_self(model_class, id=1, **kwargs):
    session = Session()
    return session.query(model_class).filter_by(id=id, **kwargs).one()


def delete_entry(model_class, id, commit=True, **kwargs):
    session = Session()
    session.query(model_class).filter_by(id=id, **kwargs).delete()
    if commit:
        session.commit()


def update_entry(entry, *, commit=True, **kwargs):
    session = Session()
    for key, value in kwargs.items():
        setattr(entry, key, value)
    if commit:
        session.commit()
    return entry


def create_order(commit=True, **orderinfo):
    session = Session()

    userid = orderinfo.get('userId')
    ticketid = orderinfo.get('ticketId')

    user = get_entry_by_id(User, userid)
    ticket = get_entry_by_id(Ticket, ticketid)

    order = Transaction(**orderinfo, user=user, ticket=ticket)

    session.add(order)
    if commit:
        session.commit()
    return order


def is_ticket_taken(model_class, id):
    session = Session()
    return session.query(exists().where(model_class.status != "free", model_class.id == id)).scalar()


def does_ticket_exist(model_class, id):
    session = Session()
    return session.query(exists().where(model_class.id == id)).scalar()


def is_name_taken(model_class, name):
    session = Session()
    return session.query(exists().where(model_class.username == name)).scalar()




