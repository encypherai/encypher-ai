"""Add overage billing columns to organizations

Revision ID: 20260315_100000
Revises: 20260310_110000
Create Date: 2026-03-15

Adds has_payment_method, overage_enabled, overage_cap_cents to organizations
for overage billing support.
"""

import sqlalchemy as sa
from alembic import op

revision = "20260315_100000"
down_revision = "20260310_110000"
branch_labels = None
depends_on = None


def _has_column(table_name: str, column_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {col["name"] for col in inspector.get_columns(table_name)}
    return column_name in columns


def upgrade() -> None:
    if not _has_column("organizations", "has_payment_method"):
        op.add_column(
            "organizations",
            sa.Column("has_payment_method", sa.Boolean(), nullable=False, server_default="false"),
        )
    if not _has_column("organizations", "overage_enabled"):
        op.add_column(
            "organizations",
            sa.Column("overage_enabled", sa.Boolean(), nullable=False, server_default="false"),
        )
    if not _has_column("organizations", "overage_cap_cents"):
        op.add_column(
            "organizations",
            sa.Column("overage_cap_cents", sa.Integer(), nullable=True),
        )


def downgrade() -> None:
    if _has_column("organizations", "overage_cap_cents"):
        op.drop_column("organizations", "overage_cap_cents")
    if _has_column("organizations", "overage_enabled"):
        op.drop_column("organizations", "overage_enabled")
    if _has_column("organizations", "has_payment_method"):
        op.drop_column("organizations", "has_payment_method")
