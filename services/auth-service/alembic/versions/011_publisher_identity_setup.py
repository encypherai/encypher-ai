"""Add publisher identity columns and mandatory setup wizard.

Revision ID: 011
Revises: 010
Create Date: 2026-02-14

TEAM_191: Publisher identity setup wizard.
- Add account_type and display_name to organizations table
- Add setup_completed_at to users table
- Add whitelabel feature flag default
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "011"
down_revision = "010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Add account_type to organizations (individual vs organization)
    op.add_column(
        "organizations",
        sa.Column("account_type", sa.String(32), nullable=True),
    )

    # 2. Add display_name to organizations (human-readable publisher name)
    op.add_column(
        "organizations",
        sa.Column("display_name", sa.String(255), nullable=True),
    )

    # 3. Add setup_completed_at to users (NULL = wizard not done yet)
    op.add_column(
        "users",
        sa.Column("setup_completed_at", sa.DateTime(timezone=True), nullable=True),
    )

    # 4. Mark existing users as setup-complete (they were already using the system)
    op.execute("UPDATE users SET setup_completed_at = created_at WHERE setup_completed_at IS NULL")


def downgrade() -> None:
    op.drop_column("users", "setup_completed_at")
    op.drop_column("organizations", "display_name")
    op.drop_column("organizations", "account_type")
