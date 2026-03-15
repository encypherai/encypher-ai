"""Add overage billing columns to organizations

Revision ID: 017
Revises: 016
Create Date: 2026-03-15

Adds has_payment_method, overage_enabled, overage_cap_cents to organizations
for overage billing support.
"""

import sqlalchemy as sa
from alembic import op

revision = "017"
down_revision = "016"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "organizations",
        sa.Column("has_payment_method", sa.Boolean(), nullable=False, server_default="false"),
    )
    op.add_column(
        "organizations",
        sa.Column("overage_enabled", sa.Boolean(), nullable=False, server_default="false"),
    )
    op.add_column(
        "organizations",
        sa.Column("overage_cap_cents", sa.Integer(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("organizations", "overage_cap_cents")
    op.drop_column("organizations", "overage_enabled")
    op.drop_column("organizations", "has_payment_method")
