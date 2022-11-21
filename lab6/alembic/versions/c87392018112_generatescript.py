"""generatescript

Revision ID: c87392018112
Revises: 
Create Date: 2022-10-24 18:36:29.181375

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c87392018112'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'user',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('username', sa.VARCHAR(32), ),
        sa.Column('firstName', sa.VARCHAR(32)),
        sa.Column('lastName', sa.VARCHAR(32)),
        sa.Column('email', sa.VARCHAR(128)),
        sa.Column('password', sa.VARCHAR(100)),
        sa.Column('phone', sa.VARCHAR(32)),
        sa.Column('birthDate', sa.DATE),
        sa.Column('status', sa.Enum('0', '1'), default='1'),
        sa.Column('isAdmin', sa.Enum('0', '1'), default='0')
    )
    op.create_table(
        'ticket',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.VARCHAR(128)),
        sa.Column('status', sa.Enum('free', 'booked', 'sold'), default='free'),
        sa.Column('price', sa.Integer),
    )
    op.create_table(
        'transaction',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('ticketId', sa.Integer, sa.ForeignKey('ticket.id')),
        sa.Column('userId', sa.Integer, sa.ForeignKey('user.id')),
        sa.Column('status', sa.Enum('placed', 'approved', 'denied'), default='placed'),
    )
    pass


def downgrade() -> None:
    op.drop_table('transaction')
    op.drop_table('user')
    op.drop_table('ticket')

    pass
