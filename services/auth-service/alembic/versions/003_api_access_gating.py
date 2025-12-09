"""API Access Gating - add user approval workflow fields

Revision ID: 003
Revises: 002
Create Date: 2025-12-08

TEAM_006: API Access Gating

Adds fields to users table for API access request/approval workflow:
- api_access_status: enum (not_requested, pending, approved, denied)
- api_access_requested_at: when user requested access
- api_access_decided_at: when admin approved/denied
- api_access_decided_by: admin user_id who made decision
- api_access_use_case: user's stated use case
- api_access_denial_reason: reason if denied
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def column_exists(conn, table_name: str, column_name: str) -> bool:
    """Check if a column exists in a table."""
    sql = f"""
        SELECT EXISTS (
            SELECT FROM information_schema.columns 
            WHERE table_name = '{table_name}' AND column_name = '{column_name}'
        )
    """  # noqa: S608
    result = conn.execute(text(sql))
    return result.scalar()


def upgrade() -> None:
    """Add API access gating fields to users table."""
    conn = op.get_bind()

    # Add api_access_status column with default 'not_requested'
    if not column_exists(conn, "users", "api_access_status"):
        op.add_column("users", sa.Column("api_access_status", sa.String(32), nullable=False, server_default="not_requested"))

    # Add api_access_requested_at column
    if not column_exists(conn, "users", "api_access_requested_at"):
        op.add_column("users", sa.Column("api_access_requested_at", sa.DateTime(timezone=True), nullable=True))

    # Add api_access_decided_at column
    if not column_exists(conn, "users", "api_access_decided_at"):
        op.add_column("users", sa.Column("api_access_decided_at", sa.DateTime(timezone=True), nullable=True))

    # Add api_access_decided_by column (admin user_id)
    if not column_exists(conn, "users", "api_access_decided_by"):
        op.add_column("users", sa.Column("api_access_decided_by", sa.String(64), nullable=True))

    # Add api_access_use_case column
    if not column_exists(conn, "users", "api_access_use_case"):
        op.add_column("users", sa.Column("api_access_use_case", sa.Text(), nullable=True))

    # Add api_access_denial_reason column
    if not column_exists(conn, "users", "api_access_denial_reason"):
        op.add_column("users", sa.Column("api_access_denial_reason", sa.Text(), nullable=True))

    # Create index on api_access_status for efficient admin queries
    op.create_index("ix_users_api_access_status", "users", ["api_access_status"], if_not_exists=True)


def downgrade() -> None:
    """Remove API access gating fields from users table."""
    # Drop index first
    op.drop_index("ix_users_api_access_status", table_name="users", if_exists=True)

    # Drop columns
    op.drop_column("users", "api_access_denial_reason")
    op.drop_column("users", "api_access_use_case")
    op.drop_column("users", "api_access_decided_by")
    op.drop_column("users", "api_access_decided_at")
    op.drop_column("users", "api_access_requested_at")
    op.drop_column("users", "api_access_status")
