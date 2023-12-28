"""Changed name of table User to Instance.

Revision ID: 835a2d55ee82
Revises: 563177877571
Create Date: 2023-12-26 22:33:45.924972

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '835a2d55ee82'
down_revision = '563177877571'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('instance',
    sa.Column('instance_id', sa.String(length=200), nullable=False),
    sa.Column('site_id', sa.String(length=200), nullable=True),
    sa.Column('refresh_token', sa.String(length=200), nullable=True),
    sa.Column('is_free', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('instance_id'),
    sa.UniqueConstraint('instance_id'),
    sa.UniqueConstraint('site_id')
    )
    op.drop_table('user')
    with op.batch_alter_table('extension', schema=None) as batch_op:
        batch_op.create_unique_constraint(None, ['extension_id'])
        # batch_op.drop_constraint('extension_instance_id_fkey', type_='foreignkey')
        batch_op.create_foreign_key(None, 'instance', ['instance_id'], ['instance_id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('extension', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('extension_instance_id_fkey', 'user', ['instance_id'], ['instance_id'])
        batch_op.drop_constraint(None, type_='unique')

    op.create_table('user',
    sa.Column('instance_id', sa.VARCHAR(length=200), autoincrement=False, nullable=False),
    sa.Column('site_id', sa.VARCHAR(length=200), autoincrement=False, nullable=True),
    sa.Column('refresh_token', sa.VARCHAR(length=200), autoincrement=False, nullable=True),
    sa.Column('is_free', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('instance_id', name='user_pkey'),
    sa.UniqueConstraint('site_id', name='user_site_id_key')
    )
    op.drop_table('instance')
    # ### end Alembic commands ###
