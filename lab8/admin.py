from lab6.models import Session, User, Transaction, Ticket
from flask_bcrypt import generate_password_hash

session = Session()

user1 = User(username="admin", firstName="admin", lastName="admin", email="admin@gmail.com",
             password=generate_password_hash("admin_admin"), phone="+380689098277",
             birthDate="1998-04-12", isAdmin='1')

session.add(user1)
session.commit()