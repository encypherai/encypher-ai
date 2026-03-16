"""Add status, suspended_at, suspension_reason to organizations

Revision ID: 20260316_110000
Revises: 20260316_100000
Create Date: 2026-03-16

Adds organization suspension/activation support columns.
"""

import sqlalchemy as sa
from alembic import op

revision = "20260316_110000"
down_revision = "20260316_100000"
branch_labels = None
depends_on = None


def _has_column(table_name: str, column_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {col["name"] for col in inspector.get_columns(table_name)}
    return column_name in columns


def upgrade() -> None:
    if not _has_column("organizations", "status"):
        op.add_column(
            "organizations",
            sa.Column("status", sa.String(32), nullable=False, server_default="active"),
        )
        op.create_index("ix_organizations_status", "organizations", ["status"])
    if not _has_column("organizations", "suspended_at"):
        op.add_column(
            "organizations",
            sa.Column("suspended_at", sa.TIMESTAMP(timezone=True), nullable=True),
        )
    if not _has_column("organizations", "suspension_reason"):
        op.add_column(
            "organizations",
            sa.Column("suspension_reason", sa.Text(), nullable=True),
        )


def downgrade() -> None:
    if _has_column("organizations", "suspension_reason"):
        op.drop_column("organizations", "suspension_reason")
    if _has_column("organizations", "suspended_at"):
        op.drop_column("organizations", "suspended_at")
    if _has_column("organizations", "status"):
        op.drop_index("ix_organizations_status", table_name="organizations")
        op.drop_column("organizations", "status")
