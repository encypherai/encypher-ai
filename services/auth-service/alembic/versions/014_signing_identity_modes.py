"""Add controlled signing identity mode columns to organizations.

Revision ID: 014
Revises: 013
Create Date: 2026-02-16
"""

from alembic import op
import sqlalchemy as sa

revision = "014"
down_revision = "013"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "organizations",
        sa.Column(
            "signing_identity_mode",
            sa.String(length=64),
            nullable=False,
            server_default="organization_name",
        ),
    )
    op.add_column(
        "organizations",
        sa.Column("signing_identity_custom_label", sa.String(length=255), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("organizations", "signing_identity_custom_label")
    op.drop_column("organizations", "signing_identity_mode")
