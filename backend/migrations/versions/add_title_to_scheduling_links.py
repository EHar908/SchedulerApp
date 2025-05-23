"""Add title to scheduling links

Revision ID: add_title_to_scheduling_links
Revises: 
Create Date: 2024-03-19

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_title_to_scheduling_links'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('scheduling_links', sa.Column('title', sa.String(), nullable=True))

def downgrade():
    op.drop_column('scheduling_links', 'title') 