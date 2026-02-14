"""add certificate metadata columns for organizations

Revision ID: add_org_certificate_metadata
Revises: add_licensing_mgmt
Create Date: 2025-11-11
"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "add_org_certificate_metadata"
down_revision = "add_licensing_mgmt"
branch_labels = None
depends_on = None

certificate_status_enum = sa.Enum(
    "active",
    "inactive",
    "revoked",
    "expired",
    name="organization_certificate_status",
    native_enum=False,
)


def _has_column(table_name: str, column_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = inspector.get_columns(table_name)
    return any(col.get("name") == column_name for col in columns)


def upgrade() -> None:
    if not _has_column("organizations", "certificate_status"):
        op.add_column(
            "organizations",
            sa.Column(
                "certificate_status",
                certificate_status_enum,
                nullable=False,
                server_default="active",
            ),
        )
    if not _has_column("organizations", "certificate_rotated_at"):
        op.add_column(
            "organizations",
            sa.Column("certificate_rotated_at", sa.TIMESTAMP(timezone=True), nullable=True),
        )
    op.alter_column("organizations", "certificate_status", server_default=None)


def downgrade() -> None:
    op.drop_column("organizations", "certificate_rotated_at")
    op.drop_column("organizations", "certificate_status")
