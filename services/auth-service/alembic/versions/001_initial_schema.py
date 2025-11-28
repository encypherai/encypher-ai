"""Initial schema - creates base tables if they don't exist

Revision ID: 001
Revises: 
Create Date: 2025-11-01

This migration is idempotent - it checks if tables/columns exist before creating.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def table_exists(conn, table_name: str) -> bool:
    """Check if a table exists in the database."""
    # Note: table_name is always a hardcoded string from this migration, not user input
    sql = f"""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = '{table_name}'
        )
    """  # noqa: S608
    result = conn.execute(text(sql))
    return result.scalar()


def column_exists(conn, table_name: str, column_name: str) -> bool:
    """Check if a column exists in a table."""
    # Note: table_name/column_name are always hardcoded strings from this migration
    sql = f"""
        SELECT EXISTS (
            SELECT FROM information_schema.columns 
            WHERE table_name = '{table_name}' AND column_name = '{column_name}'
        )
    """  # noqa: S608
    result = conn.execute(text(sql))
    return result.scalar()


def index_exists(conn, index_name: str) -> bool:
    """Check if an index exists."""
    # Note: index_name is always a hardcoded string from this migration
    sql = f"""
        SELECT EXISTS (
            SELECT FROM pg_indexes WHERE indexname = '{index_name}'
        )
    """  # noqa: S608
    result = conn.execute(text(sql))
    return result.scalar()


def upgrade() -> None:
    conn = op.get_bind()

    # =========================================
    # USERS TABLE
    # =========================================
    if not table_exists(conn, 'users'):
        op.create_table(
            'users',
            sa.Column('id', sa.String(64), primary_key=True),
            sa.Column('email', sa.String(255), nullable=False, unique=True),
            sa.Column('password_hash', sa.String(255), nullable=True),  # NULL for OAuth users
            sa.Column('name', sa.String(255), nullable=True),
            sa.Column('avatar_url', sa.String(500), nullable=True),
            sa.Column('email_verified', sa.Boolean(), default=False, nullable=False),
            sa.Column('email_verified_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('google_id', sa.String(255), unique=True, nullable=True),
            sa.Column('github_id', sa.String(255), unique=True, nullable=True),
            sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
            sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        )

    if not index_exists(conn, 'ix_users_email'):
        op.create_index('ix_users_email', 'users', ['email'], unique=True)

    # =========================================
    # REFRESH TOKENS TABLE
    # =========================================
    if not table_exists(conn, 'refresh_tokens'):
        op.create_table(
            'refresh_tokens',
            sa.Column('id', sa.String(64), primary_key=True),
            sa.Column('user_id', sa.String(64), nullable=False),
            sa.Column('token', sa.Text(), nullable=False),
            sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column('revoked', sa.Boolean(), default=False, nullable=False),
            sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('user_agent', sa.String(500), nullable=True),
            sa.Column('ip_address', sa.String(45), nullable=True),
        )
    
    # Always check for missing columns (handles schema drift)
    missing_columns = [
        ('token', sa.Text(), True),
        ('revoked', sa.Boolean(), False),
        ('revoked_at', sa.DateTime(timezone=True), True),
        ('user_agent', sa.String(500), True),
        ('ip_address', sa.String(45), True),
        ('created_at', sa.DateTime(timezone=True), True),
    ]
    for col_name, col_type, nullable in missing_columns:
        if not column_exists(conn, 'refresh_tokens', col_name):
            default_val = False if col_name == 'revoked' else None
            op.add_column('refresh_tokens', sa.Column(col_name, col_type, nullable=nullable, server_default=str(default_val) if default_val is not None else None))

    if not index_exists(conn, 'ix_refresh_tokens_user_id'):
        op.create_index('ix_refresh_tokens_user_id', 'refresh_tokens', ['user_id'])
    if not index_exists(conn, 'ix_refresh_tokens_token'):
        op.create_index('ix_refresh_tokens_token', 'refresh_tokens', ['token'], unique=True)

    # =========================================
    # PASSWORD RESET TOKENS TABLE
    # =========================================
    if not table_exists(conn, 'password_reset_tokens'):
        op.create_table(
            'password_reset_tokens',
            sa.Column('id', sa.String(64), primary_key=True),
            sa.Column('user_id', sa.String(64), nullable=False),
            sa.Column('token', sa.String(64), nullable=False),
            sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column('used', sa.Boolean(), default=False, nullable=False),
            sa.Column('used_at', sa.DateTime(timezone=True), nullable=True),
        )

    if not index_exists(conn, 'ix_password_reset_tokens_user_id'):
        op.create_index('ix_password_reset_tokens_user_id', 'password_reset_tokens', ['user_id'])
    if not index_exists(conn, 'ix_password_reset_tokens_token'):
        op.create_index('ix_password_reset_tokens_token', 'password_reset_tokens', ['token'], unique=True)

    # =========================================
    # EMAIL VERIFICATION TOKENS TABLE
    # =========================================
    if not table_exists(conn, 'email_verification_tokens'):
        op.create_table(
            'email_verification_tokens',
            sa.Column('id', sa.String(64), primary_key=True),
            sa.Column('user_id', sa.String(64), nullable=False),
            sa.Column('token', sa.String(64), nullable=False),
            sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column('used', sa.Boolean(), default=False, nullable=False),
            sa.Column('used_at', sa.DateTime(timezone=True), nullable=True),
        )

    if not index_exists(conn, 'ix_email_verification_tokens_user_id'):
        op.create_index('ix_email_verification_tokens_user_id', 'email_verification_tokens', ['user_id'])
    if not index_exists(conn, 'ix_email_verification_tokens_token'):
        op.create_index('ix_email_verification_tokens_token', 'email_verification_tokens', ['token'], unique=True)


def downgrade() -> None:
    op.drop_table('email_verification_tokens')
    op.drop_table('password_reset_tokens')
    op.drop_table('refresh_tokens')
    op.drop_table('users')
