"""Add token column to refresh_tokens table

Revision ID: 003
Revises: 002
Create Date: 2025-11-27

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade():
    # Add the token column if it doesn't exist
    # Using raw SQL to check if column exists first
    conn = op.get_bind()
    
    # Check if the column exists
    result = conn.execute(sa.text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'refresh_tokens' AND column_name = 'token'
    """))
    
    if result.fetchone() is None:
        # Column doesn't exist, add it
        op.add_column('refresh_tokens', sa.Column('token', sa.Text(), nullable=True))
        
        # If there's a token_hash column, we might want to migrate data
        # For now, just make it nullable initially
        
        # Create unique index on token
        op.create_index('ix_refresh_tokens_token', 'refresh_tokens', ['token'], unique=True)


def downgrade():
    op.drop_index('ix_refresh_tokens_token', table_name='refresh_tokens')
    op.drop_column('refresh_tokens', 'token')
