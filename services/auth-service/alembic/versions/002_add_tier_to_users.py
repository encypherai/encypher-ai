"""Add tier column to users table

Revision ID: 002
Revises: 001
Create Date: 2025-11-04

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add tier column to users table
    op.add_column('users', sa.Column('tier', sa.String(20), nullable=False, server_default='free'))


def downgrade() -> None:
    # Remove tier column from users table
    op.drop_column('users', 'tier')
