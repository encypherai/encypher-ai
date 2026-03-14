"""Consolidate pricing tiers to free/enterprise/strategic_partner and add add_ons column.

Revision ID: 009
Revises: 008
Create Date: 2026-02-11

TEAM_145: Backend tier consolidation.
- Coerce legacy tier values (starter, professional, business) to 'free'
- Add add_ons JSON column to organizations table
- Update default coalition rev share to 60/40
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "009"
down_revision = "008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Coerce legacy tier values to 'free'
    #    Auth-service uses a VARCHAR tier column, not a PG enum.
    op.execute("UPDATE organizations SET tier = 'free' WHERE tier IN ('starter', 'professional', 'business')")

    # 2. Add add_ons JSON column (default empty dict)
    op.add_column(
        "organizations",
        sa.Column("add_ons", sa.JSON(), nullable=False, server_default="{}"),
    )

    # 3. Update coalition rev share defaults for existing orgs on old 65/35 split
    op.execute("UPDATE organizations SET coalition_rev_share = 60 WHERE coalition_rev_share = 65")


def downgrade() -> None:
    # Remove add_ons column
    op.drop_column("organizations", "add_ons")

    # Revert 'free' tier back to 'starter'
    op.execute("UPDATE organizations SET tier = 'starter' WHERE tier = 'free'")
