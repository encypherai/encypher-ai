"""Add token column to refresh_tokens table

Revision ID: 003
Revises: 002
Create Date: 2025-11-27

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade():
    # Add the token column if it doesn't exist
    conn = op.get_bind()
    
    # Check if the column exists
    result = conn.execute(text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'refresh_tokens' AND column_name = 'token'
    """))
    
    if result.fetchone() is None:
        # Column doesn't exist, add it
        op.add_column('refresh_tokens', sa.Column('token', sa.Text(), nullable=True))
        
        # Check if index exists before creating
        result = conn.execute(text("""
            SELECT indexname FROM pg_indexes 
            WHERE tablename = 'refresh_tokens' AND indexname = 'ix_refresh_tokens_token'
        """))
        if result.fetchone() is None:
            op.create_index('ix_refresh_tokens_token', 'refresh_tokens', ['token'], unique=True)


def downgrade():
    conn = op.get_bind()
    
    # Check if index exists before dropping
    result = conn.execute(text("""
        SELECT indexname FROM pg_indexes 
        WHERE tablename = 'refresh_tokens' AND indexname = 'ix_refresh_tokens_token'
    """))
    if result.fetchone() is not None:
        op.drop_index('ix_refresh_tokens_token', table_name='refresh_tokens')
    
    # Check if column exists before dropping
    result = conn.execute(text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'refresh_tokens' AND column_name = 'token'
    """))
    if result.fetchone() is not None:
        op.drop_column('refresh_tokens', 'token')
