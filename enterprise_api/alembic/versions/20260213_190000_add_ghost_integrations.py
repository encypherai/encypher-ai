"""Add ghost_integrations table for hosted Ghost CMS webhook endpoint.

Revision ID: 20260213_190000
Revises: 20251201_110000
Create Date: 2026-02-13 19:00:00.000000

Stores per-organization Ghost credentials and signing preferences
so the hosted webhook endpoint can sign content on behalf of the org.
"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "20260213_190000"
down_revision = "20251201_110000"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ghost_integrations",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column(
            "organization_id",
            sa.String(64),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("ghost_url", sa.String(1000), nullable=False),
        sa.Column("ghost_admin_api_key", sa.String(500), nullable=False),
        sa.Column("webhook_token_hash", sa.String(128), nullable=False, unique=True),
        sa.Column("auto_sign_on_publish", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("auto_sign_on_update", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("manifest_mode", sa.String(50), nullable=False, server_default="micro_ecc_c2pa"),
        sa.Column("segmentation_level", sa.String(50), nullable=False, server_default="sentence"),
        sa.Column("badge_enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("last_webhook_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_sign_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sign_count", sa.String(20), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_ghost_integrations_organization_id", "ghost_integrations", ["organization_id"])
    op.create_index("ix_ghost_integrations_webhook_token_hash", "ghost_integrations", ["webhook_token_hash"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_ghost_integrations_webhook_token_hash")
    op.drop_index("ix_ghost_integrations_organization_id")
    op.drop_table("ghost_integrations")
