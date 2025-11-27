"""Initial schema - creates base tables if they don't exist

Revision ID: 001
Revises: 
Create Date: 2025-11-01

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    
    # Check if users table exists
    result = conn.execute(text("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'users'
        )
    """))
    users_exists = result.scalar()
    
    if not users_exists:
        op.create_table(
            'users',
            sa.Column('id', sa.String(64), primary_key=True),
            sa.Column('email', sa.String(255), nullable=False, unique=True),
            sa.Column('password_hash', sa.String(255), nullable=False),
            sa.Column('name', sa.String(255), nullable=True),
            sa.Column('email_verified', sa.Boolean(), default=False, nullable=False),
            sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        )
        op.create_index('ix_users_email', 'users', ['email'], unique=True)
    
    # Check if refresh_tokens table exists
    result = conn.execute(text("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'refresh_tokens'
        )
    """))
    refresh_tokens_exists = result.scalar()
    
    if not refresh_tokens_exists:
        op.create_table(
            'refresh_tokens',
            sa.Column('id', sa.String(64), primary_key=True),
            sa.Column('user_id', sa.String(64), nullable=False, index=True),
            sa.Column('token', sa.Text(), nullable=False, unique=True),
            sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column('revoked', sa.Boolean(), default=False, nullable=False),
            sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('user_agent', sa.String(255), nullable=True),
            sa.Column('ip_address', sa.String(45), nullable=True),
        )
        op.create_index('ix_refresh_tokens_user_id', 'refresh_tokens', ['user_id'])
        op.create_index('ix_refresh_tokens_token', 'refresh_tokens', ['token'], unique=True)
    
    # Check if password_reset_tokens table exists
    result = conn.execute(text("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'password_reset_tokens'
        )
    """))
    password_reset_exists = result.scalar()
    
    if not password_reset_exists:
        op.create_table(
            'password_reset_tokens',
            sa.Column('id', sa.String(64), primary_key=True),
            sa.Column('user_id', sa.String(64), nullable=False, index=True),
            sa.Column('token', sa.String(64), nullable=False, unique=True),
            sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column('used', sa.Boolean(), default=False, nullable=False),
        )
        op.create_index('ix_password_reset_tokens_user_id', 'password_reset_tokens', ['user_id'])
        op.create_index('ix_password_reset_tokens_token', 'password_reset_tokens', ['token'], unique=True)
    
    # Check if email_verification_tokens table exists
    result = conn.execute(text("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'email_verification_tokens'
        )
    """))
    email_verification_exists = result.scalar()
    
    if not email_verification_exists:
        op.create_table(
            'email_verification_tokens',
            sa.Column('id', sa.String(64), primary_key=True),
            sa.Column('user_id', sa.String(64), nullable=False, index=True),
            sa.Column('token', sa.String(64), nullable=False, unique=True),
            sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column('used', sa.Boolean(), default=False, nullable=False),
        )
        op.create_index('ix_email_verification_tokens_user_id', 'email_verification_tokens', ['user_id'])
        op.create_index('ix_email_verification_tokens_token', 'email_verification_tokens', ['token'], unique=True)


def downgrade() -> None:
    op.drop_table('email_verification_tokens')
    op.drop_table('password_reset_tokens')
    op.drop_table('refresh_tokens')
    op.drop_table('users')
