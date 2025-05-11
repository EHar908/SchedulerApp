"""make user_id nullable

Revision ID: make_user_id_nullable
Revises: add_title_to_scheduling_links
Create Date: 2024-05-11 21:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'make_user_id_nullable'
down_revision = 'add_title_to_scheduling_links'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Make user_id nullable in scheduling_links table
    op.alter_column('scheduling_links', 'user_id',
               existing_type=sa.Integer(),
               nullable=True)


def downgrade() -> None:
    # Make user_id non-nullable again
    op.alter_column('scheduling_links', 'user_id',
               existing_type=sa.Integer(),
               nullable=False) 