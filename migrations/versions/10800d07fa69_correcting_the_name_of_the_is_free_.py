"""Correcting the name of the is_free column.

Revision ID: 10800d07fa69
Revises: f4f75bde1a45
Create Date: 2023-11-24 14:37:10.913778

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '10800d07fa69'
down_revision = 'f4f75bde1a45'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_free', sa.String(length=200), nullable=True))
        batch_op.drop_column('if_free')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('if_free', sa.VARCHAR(length=200), nullable=True))
        batch_op.drop_column('is_free')

    # ### end Alembic commands ###
