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


def upgrade() -> None:
    op.add_column(
        "organizations",
        sa.Column(
            "certificate_status",
            certificate_status_enum,
            nullable=False,
            server_default="active",
        ),
    )
    op.add_column(
        "organizations",
        sa.Column("certificate_rotated_at", sa.TIMESTAMP(timezone=True), nullable=True),
    )
    op.alter_column("organizations", "certificate_status", server_default=None)


def downgrade() -> None:
    op.drop_column("organizations", "certificate_rotated_at")
    op.drop_column("organizations", "certificate_status")
