"""Add fields to scheduling links

Revision ID: add_scheduling_link_fields
Revises: add_title_to_scheduling_links
Create Date: 2024-03-19

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_scheduling_link_fields'
down_revision = 'add_title_to_scheduling_links'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('scheduling_links', sa.Column('max_uses', sa.Integer(), nullable=True))
    op.add_column('scheduling_links', sa.Column('expiration_date', sa.DateTime(timezone=True), nullable=True))
    op.add_column('scheduling_links', sa.Column('max_days_ahead', sa.Integer(), nullable=False, server_default='30'))

def downgrade():
    op.drop_column('scheduling_links', 'max_days_ahead')
    op.drop_column('scheduling_links', 'expiration_date')
    op.drop_column('scheduling_links', 'max_uses') 