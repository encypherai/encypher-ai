"""Add parent_org_id column to organizations

Revision ID: 20260316_100000
Revises: 20260315_100000
Create Date: 2026-03-16

Adds parent_org_id column (VARCHAR(64), nullable) to organizations table
for partner portal parent-child org relationships.
"""

import sqlalchemy as sa
from alembic import op

revision = "20260316_100000"
down_revision = "20260315_100000"
branch_labels = None
depends_on = None


def _has_column(table_name: str, column_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {col["name"] for col in inspector.get_columns(table_name)}
    return column_name in columns


def upgrade() -> None:
    if not _has_column("organizations", "parent_org_id"):
        op.add_column(
            "organizations",
            sa.Column("parent_org_id", sa.String(64), nullable=True),
        )
        op.create_index(
            "ix_organizations_parent_org_id",
            "organizations",
            ["parent_org_id"],
        )
        op.create_foreign_key(
            "fk_organizations_parent_org_id",
            "organizations",
            "organizations",
            ["parent_org_id"],
            ["id"],
            ondelete="SET NULL",
        )


def downgrade() -> None:
    if _has_column("organizations", "parent_org_id"):
        op.drop_constraint("fk_organizations_parent_org_id", "organizations", type_="foreignkey")
        op.drop_index("ix_organizations_parent_org_id", table_name="organizations")
        op.drop_column("organizations", "parent_org_id")
