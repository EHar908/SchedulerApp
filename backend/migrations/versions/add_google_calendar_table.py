"""add google calendar table

Revision ID: add_google_calendar_table
Revises: make_user_id_nullable
Create Date: 2024-03-19 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY

# revision identifiers, used by Alembic.
revision = 'add_google_calendar_table'
down_revision = 'make_user_id_nullable'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'google_calendars',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('access_token', sa.String(), nullable=False),
        sa.Column('refresh_token', sa.String(), nullable=False),
        sa.Column('token_uri', sa.String(), nullable=False),
        sa.Column('client_id', sa.String(), nullable=False),
        sa.Column('client_secret', sa.String(), nullable=False),
        sa.Column('scopes', ARRAY(sa.String()), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_google_calendars_id'), 'google_calendars', ['id'], unique=False)

def downgrade():
    op.drop_index(op.f('ix_google_calendars_id'), table_name='google_calendars')
    op.drop_table('google_calendars') 