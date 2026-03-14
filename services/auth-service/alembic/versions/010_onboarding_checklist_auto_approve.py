"""Add onboarding checklist columns and auto-approve API access for new users.

Revision ID: 010
Revises: 009
Create Date: 2026-02-14

TEAM_191: Remove manual API access gate, add server-side onboarding checklist.
- Change default api_access_status from 'not_requested' to 'approved'
- Migrate existing 'not_requested' users to 'approved'
- Add onboarding_checklist JSON column to users table
- Add onboarding_completed_at timestamp column to users table
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "010"
down_revision = "009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Auto-approve all existing users who haven't requested access yet
    #    (they were stuck at 'not_requested' under the old gate)
    #    Do NOT touch suspended or denied users — admins set those intentionally.
    op.execute("UPDATE users SET api_access_status = 'approved' WHERE api_access_status = 'not_requested'")

    # 2. Also auto-approve pending users (no more manual review)
    op.execute("UPDATE users SET api_access_status = 'approved' WHERE api_access_status = 'pending'")

    # 3. Change the column default to 'approved' for new signups
    op.alter_column(
        "users",
        "api_access_status",
        server_default="approved",
    )

    # 4. Add onboarding checklist JSON column
    op.add_column(
        "users",
        sa.Column("onboarding_checklist", sa.JSON(), nullable=False, server_default="{}"),
    )

    # 5. Add onboarding completed timestamp
    op.add_column(
        "users",
        sa.Column("onboarding_completed_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    # Remove onboarding columns
    op.drop_column("users", "onboarding_completed_at")
    op.drop_column("users", "onboarding_checklist")

    # Revert default back to 'not_requested'
    op.alter_column(
        "users",
        "api_access_status",
        server_default="not_requested",
    )
