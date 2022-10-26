from models import Session, User, Ticket, Transaction

session = Session()

user1 = User(username='denysratushniak', firstName='denys',
            lastName='ratushniak', email='denysratushniak@gmail.com',
            password='12345678den', phone='+380961515915', birthDate="2004-07-04")

user2 = User(username='denysratushniak2', firstName='denys2',
            lastName='ratushniak2', email='denysratushniak2@gmail.com',
            password='12345678den2', phone='+380961515912', birthDate="2004-07-02")

ticket1 = Ticket(name='concert1 num1', price=500)
ticket2 = Ticket(name='concert1 num2', price=500)
ticket3 = Ticket(name='concert1 num3', price=500)


session.add(user1)
session.add(user2)

session.add(ticket1)
session.add(ticket2)
session.add(ticket3)

# session.commit()

transaction1 = Transaction(ticket=ticket1, user=user1)
transaction2 = Transaction(ticket=ticket2, user=user2)
transaction3 = Transaction(ticket=ticket3, user=user2)

session.add(transaction1)
session.add(transaction2)
session.add(transaction3)

session.commit()
