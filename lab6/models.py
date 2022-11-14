from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum
import json

DB_URL = "mysql://root:password@localhost:3306/ap_project"

engine = create_engine(DB_URL)
SessionFactory = sessionmaker(bind=engine)
Session = scoped_session(SessionFactory)

BaseModel = declarative_base()


class User(BaseModel):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    username = Column(String)
    firstName = Column(String)
    lastName = Column(String)
    email = Column(String)
    password = Column(String)
    phone = Column(String)
    birthDate = Column(Date)
    status = Column(Enum('0', '1'), default='1')


class Ticket(BaseModel):
    __tablename__ = "ticket"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    status = Column(Enum('free', 'booked', 'sold'), default='free')
    price = Column(Integer)


class Transaction(BaseModel):
    __tablename__ = "transaction"
    id = Column(Integer, primary_key=True)

    ticketId = Column(Integer, ForeignKey('ticket.id'))
    userId = Column(Integer, ForeignKey('user.id'))

    ticket = relationship(Ticket, foreign_keys=[ticketId], backref='ticket', lazy="joined")
    user = relationship(User, foreign_keys=[userId], backref='user', lazy="joined")

    status = Column(Enum('placed', 'approved', 'denied'), default='placed')
