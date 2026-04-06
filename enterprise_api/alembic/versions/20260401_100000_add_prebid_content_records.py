"""add prebid_content_records table

Revision ID: 20260401_100000
Revises: 20260325_100000
Create Date: 2026-04-01 10:00:00

"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = "20260401_100000"
down_revision = "20260325_100000"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "prebid_content_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("organization_id", sa.String(64), nullable=False),
        sa.Column("domain", sa.String(255), nullable=False),
        sa.Column("canonical_url", sa.Text(), nullable=True),
        sa.Column("content_hash", sa.String(71), nullable=False),
        sa.Column("manifest_store", postgresql.JSONB(), nullable=True),
        sa.Column("manifest_url", sa.Text(), nullable=True),
        sa.Column("page_title", sa.String(500), nullable=True),
        sa.Column("signer_tier", sa.String(32), nullable=False, server_default="encypher_free"),
        sa.Column("signed_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index(
        "idx_prebid_content_domain_hash",
        "prebid_content_records",
        ["domain", "content_hash"],
        unique=True,
    )
    op.create_index(
        "idx_prebid_content_org",
        "prebid_content_records",
        ["organization_id"],
    )


def downgrade() -> None:
    op.drop_index("idx_prebid_content_org", table_name="prebid_content_records")
    op.drop_index("idx_prebid_content_domain_hash", table_name="prebid_content_records")
    op.drop_table("prebid_content_records")
