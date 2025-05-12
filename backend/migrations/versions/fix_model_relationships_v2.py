"""fix model relationships v2

Revision ID: fix_model_relationships_v2
Revises: fix_model_relationships
Create Date: 2024-02-17 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = 'fix_model_relationships_v2'
down_revision = 'fix_model_relationships'
branch_labels = None
depends_on = None

def table_exists(table_name):
    inspector = inspect(op.get_bind())
    return table_name in inspector.get_table_names()

def upgrade():
    # Drop existing tables in the correct order to handle dependencies
    tables_to_drop = [
        'bookings',
        'meetings',
        'custom_questions',
        'scheduling_links',
        'scheduling_windows',
        'google_calendars',
        'calendars',
        'sessions',
        'cache',
        'users'
    ]
    
    for table in tables_to_drop:
        if table_exists(table):
            op.drop_table(table)

    # Recreate tables with correct relationships
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('google_id', sa.String(), nullable=True),
        sa.Column('hashed_password', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    op.create_table('google_calendars',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('access_token', sa.String(), nullable=False),
        sa.Column('refresh_token', sa.String(), nullable=False),
        sa.Column('token_uri', sa.String(), nullable=False),
        sa.Column('client_id', sa.String(), nullable=False),
        sa.Column('client_secret', sa.String(), nullable=False),
        sa.Column('scopes', sa.ARRAY(sa.String()), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_google_calendars_id'), 'google_calendars', ['id'], unique=False)

    op.create_table('scheduling_windows',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('day_of_week', sa.Integer(), nullable=True),
        sa.Column('start_hour', sa.String(), nullable=True),
        sa.Column('end_hour', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_scheduling_windows_id'), 'scheduling_windows', ['id'], unique=False)

    op.create_table('scheduling_links',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('slug', sa.String(), nullable=True),
        sa.Column('meeting_length', sa.Integer(), nullable=True),
        sa.Column('buffer_before', sa.Integer(), nullable=True),
        sa.Column('buffer_after', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_scheduling_links_id'), 'scheduling_links', ['id'], unique=False)
    op.create_index(op.f('ix_scheduling_links_slug'), 'scheduling_links', ['slug'], unique=True)

    op.create_table('custom_questions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('scheduling_link_id', sa.Integer(), nullable=True),
        sa.Column('question', sa.String(), nullable=True),
        sa.Column('required', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['scheduling_link_id'], ['scheduling_links.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_custom_questions_id'), 'custom_questions', ['id'], unique=False)

    op.create_table('meetings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('scheduling_link_id', sa.Integer(), nullable=True),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('linkedin_url', sa.String(), nullable=True),
        sa.Column('meeting_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('answers', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['scheduling_link_id'], ['scheduling_links.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_meetings_id'), 'meetings', ['id'], unique=False)

def downgrade():
    # This is a destructive migration, so we can't really downgrade
    pass 