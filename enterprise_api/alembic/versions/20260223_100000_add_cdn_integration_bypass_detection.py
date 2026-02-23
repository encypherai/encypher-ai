"""add cdn_integrations table and robots_txt_bypassed column

Revision ID: 20260223_100000
Revises: 20260221_120000
Create Date: 2026-02-23 10:00:00

Adds:
- cdn_integrations table (Cloudflare Logpush + future CDN providers)
- robots_txt_bypassed column on content_detection_events
"""

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

from alembic import op

revision = "20260223_100000"
down_revision = "20260221_120000"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # -------------------------------------------------------------------------
    # cdn_integrations table
    # -------------------------------------------------------------------------
    op.create_table(
        "cdn_integrations",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("organization_id", sa.String(64), nullable=False),
        # Provider slug: "cloudflare" | "fastly" | "cloudfront"
        sa.Column("provider", sa.Text(), nullable=False, server_default="cloudflare"),
        # Cloudflare Zone ID (optional — for display / Logpush setup instructions)
        sa.Column("zone_id", sa.Text(), nullable=True),
        # Shared secret stored as bcrypt hash; Logpush signs with HMAC-SHA256
        sa.Column("webhook_secret_hash", sa.Text(), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index(
        "ix_cdn_integrations_org_provider",
        "cdn_integrations",
        ["organization_id", "provider"],
        unique=True,
    )

    # -------------------------------------------------------------------------
    # content_detection_events — add robots_txt_bypassed column
    # -------------------------------------------------------------------------
    op.add_column(
        "content_detection_events",
        sa.Column("robots_txt_bypassed", sa.Boolean(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("content_detection_events", "robots_txt_bypassed")
    op.drop_index("ix_cdn_integrations_org_provider", table_name="cdn_integrations")
    op.drop_table("cdn_integrations")
