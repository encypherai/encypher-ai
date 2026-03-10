"""Add cdn_attribution_events table.

Revision ID: 20260310_110000
Revises: 20260310_100000
Create Date: 2026-03-10 11:00:00.000000

Creates the cdn_attribution_events table for per-image attribution tracking
via Cloudflare Logpush, with an index on (organization_id, created_at).
"""

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from alembic import op

revision = "20260310_110000"
down_revision = "20260310_100000"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "cdn_attribution_events",
        sa.Column("id", PGUUID(as_uuid=True), primary_key=True),
        sa.Column("organization_id", sa.String(64), nullable=False),
        sa.Column("image_url", sa.Text, nullable=True),
        sa.Column("canonical_url", sa.Text, nullable=True),
        sa.Column("matched_record_id", PGUUID(as_uuid=True), nullable=True),
        sa.Column("verdict", sa.String(32), nullable=True),
        sa.Column("http_status", sa.Integer, nullable=True),
        sa.Column("client_ip", sa.String(64), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )

    op.create_index(
        "idx_cdn_attribution_org_created",
        "cdn_attribution_events",
        ["organization_id", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("idx_cdn_attribution_org_created", table_name="cdn_attribution_events")
    op.drop_table("cdn_attribution_events")
