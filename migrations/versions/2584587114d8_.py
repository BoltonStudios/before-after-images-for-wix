"""empty message

Revision ID: 2584587114d8
Revises: 3b3ac9101ff3
Create Date: 2024-01-18 02:14:53.522349

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2584587114d8'
down_revision = '3b3ac9101ff3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('instance', schema=None) as batch_op:
        batch_op.add_column(sa.Column('did_cancel', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('instance', schema=None) as batch_op:
        batch_op.drop_column('did_cancel')

    # ### end Alembic commands ###