"""Added four new columns tol ComponentSlider table.

Revision ID: efdfdd2c106e
Revises: de1b0cb5e87c
Create Date: 2023-12-21 13:44:47.731332

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'efdfdd2c106e'
down_revision = 'de1b0cb5e87c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('component_slider', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_vertical', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('mouseover_action', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('handle_animation', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('is_move_on_click_enabled', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('component_slider', schema=None) as batch_op:
        batch_op.drop_column('is_move_on_click_enabled')
        batch_op.drop_column('handle_animation')
        batch_op.drop_column('mouseover_action')
        batch_op.drop_column('is_vertical')

    # ### end Alembic commands ###