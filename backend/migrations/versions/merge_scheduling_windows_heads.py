"""merge scheduling windows heads

Revision ID: merge_windows_heads
Revises: fix_model_relationships_v2, update_windows_timestamp
Create Date: 2024-03-19 10:05:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'merge_windows_heads'
down_revision = ('fix_model_relationships_v2', 'update_windows_timestamp')
branch_labels = None
depends_on = None

def upgrade():
    pass

def downgrade():
    pass 