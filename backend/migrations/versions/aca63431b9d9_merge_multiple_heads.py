"""merge multiple heads

Revision ID: aca63431b9d9
Revises: 7e85f4ab61d3, fix_model_relationships
Create Date: 2025-05-11 18:42:30.045583

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'aca63431b9d9'
down_revision = ('7e85f4ab61d3', 'fix_model_relationships')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass 