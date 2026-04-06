"""Add cdn_content_records table for CDN Edge Provenance Worker

Revision ID: add_cdn_content_records
Revises: 20260407_100000
Create Date: 2026-04-06

Tracks auto-signed content from the Cloudflare Edge Provenance Worker.
Each row represents one unique (domain, content_hash) pair with a cached
embedding plan for edge marker injection.
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "add_cdn_content_records"
down_revision = "20260407_100000"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "cdn_content_records" in inspector.get_table_names():
        return

    op.create_table(
        "cdn_content_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organization_id", sa.String(64), nullable=False),
        sa.Column("domain", sa.String(255), nullable=False),
        sa.Column("canonical_url", sa.Text(), nullable=True),
        sa.Column("content_hash", sa.String(71), nullable=False),
        sa.Column("embedding_plan", postgresql.JSONB(), nullable=True),
        sa.Column("manifest_store", postgresql.JSONB(), nullable=True),
        sa.Column("manifest_url", sa.Text(), nullable=True),
        sa.Column("page_title", sa.String(500), nullable=True),
        sa.Column("signer_tier", sa.String(32), nullable=False, server_default="encypher_free"),
        sa.Column("boundary_selector", sa.String(100), nullable=True),
        sa.Column("signed_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
    )

    op.create_index(
        "idx_cdn_content_domain_hash",
        "cdn_content_records",
        ["domain", "content_hash"],
        unique=True,
    )
    op.create_index(
        "idx_cdn_content_org",
        "cdn_content_records",
        ["organization_id"],
    )


def downgrade() -> None:
    op.drop_index("idx_cdn_content_org", table_name="cdn_content_records")
    op.drop_index("idx_cdn_content_domain_hash", table_name="cdn_content_records")
    op.drop_table("cdn_content_records")
