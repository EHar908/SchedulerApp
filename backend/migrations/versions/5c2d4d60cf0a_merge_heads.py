"""merge_heads

Revision ID: 5c2d4d60cf0a
Revises: add_scheduling_link_fields, fc01da0eb557, merge_windows_heads
Create Date: 2025-05-11 20:46:38.896812

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5c2d4d60cf0a'
down_revision = ('add_scheduling_link_fields', 'fc01da0eb557', 'merge_windows_heads')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass 