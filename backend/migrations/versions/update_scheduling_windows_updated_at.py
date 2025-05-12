"""update scheduling windows updated_at

Revision ID: update_windows_timestamp
Revises: fix_model_relationships_v2
Create Date: 2024-03-19 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func

# revision identifiers, used by Alembic.
revision = 'update_windows_timestamp'
down_revision = 'fix_model_relationships_v2'
branch_labels = None
depends_on = None

def upgrade():
    # Update existing records to set updated_at to created_at
    op.execute("""
        UPDATE scheduling_windows 
        SET updated_at = created_at 
        WHERE updated_at IS NULL
    """)

def downgrade():
    # No downgrade needed as this is just a data fix
    pass 