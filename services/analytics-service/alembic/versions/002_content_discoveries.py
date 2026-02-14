"""Add content_discoveries and discovery_domain_summaries tables

Revision ID: 002
Revises: 001
Create Date: 2026-02-13

Tables: content_discoveries, discovery_domain_summaries
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Content discoveries table (raw discovery events)
    op.create_table(
        "content_discoveries",
        sa.Column("id", sa.String(64), primary_key=True),
        # Where the content was found
        sa.Column("page_url", sa.String(2048), nullable=False),
        sa.Column("page_domain", sa.String(255), nullable=False, index=True),
        sa.Column("page_title", sa.String(512), nullable=True),
        # Who signed the content (the content owner)
        sa.Column("signer_id", sa.String(255), nullable=True, index=True),
        sa.Column("signer_name", sa.String(255), nullable=True),
        sa.Column("organization_id", sa.String(255), nullable=True, index=True),
        sa.Column("document_id", sa.String(255), nullable=True, index=True),
        # The domain where the content was originally signed/published
        sa.Column("original_domain", sa.String(255), nullable=True, index=True),
        # Verification outcome
        sa.Column("verified", sa.Integer, nullable=False, server_default="0"),
        sa.Column("verification_status", sa.String(50), nullable=True),
        sa.Column("marker_type", sa.String(50), nullable=True),
        # Domain-mismatch flag
        sa.Column("is_external_domain", sa.Integer, nullable=False, server_default="0"),
        # Anonymized reporter context (no PII)
        sa.Column("session_id", sa.String(100), nullable=True),
        sa.Column("extension_version", sa.String(50), nullable=True),
        sa.Column("source", sa.String(50), nullable=False, server_default="chrome_extension"),
        # Timestamps
        sa.Column("discovered_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False, index=True),
        sa.Column("date", sa.String(10), nullable=False, index=True),
    )

    # Composite indexes for common queries
    op.create_index(
        "idx_discovery_org_domain",
        "content_discoveries",
        ["organization_id", "page_domain"],
    )
    op.create_index(
        "idx_discovery_org_date",
        "content_discoveries",
        ["organization_id", "date"],
    )
    op.create_index(
        "idx_discovery_external",
        "content_discoveries",
        ["organization_id", "is_external_domain"],
    )

    # Discovery domain summaries table (aggregated per org+domain)
    op.create_table(
        "discovery_domain_summaries",
        sa.Column("id", sa.String(64), primary_key=True),
        # The org whose content was found
        sa.Column("organization_id", sa.String(255), nullable=False, index=True),
        # The domain where content was found
        sa.Column("page_domain", sa.String(255), nullable=False),
        # Counts
        sa.Column("discovery_count", sa.Integer, nullable=False, server_default="1"),
        sa.Column("verified_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("invalid_count", sa.Integer, nullable=False, server_default="0"),
        # Whether this domain belongs to the org
        sa.Column("is_owned_domain", sa.Integer, nullable=False, server_default="0"),
        # Alert tracking
        sa.Column("alert_sent", sa.Integer, nullable=False, server_default="0"),
        sa.Column("alert_sent_at", sa.DateTime(timezone=True), nullable=True),
        # Timestamps
        sa.Column("first_seen_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Unique constraint: one summary row per org+domain
    op.create_index(
        "idx_domain_summary_org_domain",
        "discovery_domain_summaries",
        ["organization_id", "page_domain"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("idx_domain_summary_org_domain")
    op.drop_table("discovery_domain_summaries")
    op.drop_index("idx_discovery_external")
    op.drop_index("idx_discovery_org_date")
    op.drop_index("idx_discovery_org_domain")
    op.drop_table("content_discoveries")
