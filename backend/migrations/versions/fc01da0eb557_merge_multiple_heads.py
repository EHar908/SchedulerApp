"""merge multiple heads

Revision ID: fc01da0eb557
Revises: aca63431b9d9, fix_model_relationships_v2
Create Date: 2025-05-11 18:47:55.055528

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fc01da0eb557'
down_revision = ('aca63431b9d9', 'fix_model_relationships_v2')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass 