"""Add cdn_image_records table and CDN provenance columns to organizations.

Revision ID: 20260310_100000
Revises: 20260308_120000
Create Date: 2026-03-10 10:00:00.000000

Creates the cdn_image_records table for CDN provenance continuity tracking
and adds cdn_provenance_enabled + cdn_image_registrations_this_month columns
to the organizations table.
"""

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from alembic import op

revision = "20260310_100000"
down_revision = "20260308_120000"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Create cdn_image_records table
    op.create_table(
        "cdn_image_records",
        sa.Column("id", PGUUID(as_uuid=True), primary_key=True),
        sa.Column("organization_id", sa.String(64), nullable=False),
        sa.Column("original_url", sa.Text, nullable=True),
        sa.Column("content_sha256", sa.String(71), nullable=True),
        sa.Column("phash", sa.BigInteger, nullable=True),
        sa.Column("manifest_store", JSONB, nullable=True),
        sa.Column("is_variant", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("parent_record_id", PGUUID(as_uuid=True), nullable=True),
        sa.Column("transform_description", sa.String(500), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )

    # 2. Create indexes
    op.create_index(
        "idx_cdn_image_records_org_phash",
        "cdn_image_records",
        ["organization_id", "phash"],
    )
    op.create_index(
        "idx_cdn_image_records_org_sha256",
        "cdn_image_records",
        ["organization_id", "content_sha256"],
    )

    # 3. Add CDN provenance columns to organizations
    op.add_column(
        "organizations",
        sa.Column("cdn_provenance_enabled", sa.Boolean, nullable=True, server_default="false"),
    )
    op.add_column(
        "organizations",
        sa.Column(
            "cdn_image_registrations_this_month",
            sa.Integer,
            nullable=True,
            server_default="0",
        ),
    )


def downgrade() -> None:
    # Remove columns from organizations
    op.drop_column("organizations", "cdn_image_registrations_this_month")
    op.drop_column("organizations", "cdn_provenance_enabled")

    # Drop indexes and table
    op.drop_index("idx_cdn_image_records_org_sha256", table_name="cdn_image_records")
    op.drop_index("idx_cdn_image_records_org_phash", table_name="cdn_image_records")
    op.drop_table("cdn_image_records")
