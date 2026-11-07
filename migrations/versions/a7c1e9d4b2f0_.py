"""Add instance.uninstalled_at and trial_history table for 30-day purge.

Revision ID: a7c1e9d4b2f0
Revises: 689915235526
Create Date: 2026-11-07 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a7c1e9d4b2f0'
down_revision = '689915235526'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('instance', schema=None) as batch_op:
        batch_op.add_column(sa.Column('uninstalled_at', sa.DateTime(timezone=True), nullable=True))

    op.create_table('trial_history',
        sa.Column('site_hash', sa.String(length=64), nullable=False),
        sa.Column('trial_started_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('site_hash')
    )


def downgrade():
    op.drop_table('trial_history')

    with op.batch_alter_table('instance', schema=None) as batch_op:
        batch_op.drop_column('uninstalled_at')
