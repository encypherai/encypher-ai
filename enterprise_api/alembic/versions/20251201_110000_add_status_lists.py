"""Add bitstring status lists for per-document revocation.

Revision ID: 20251201_110000
Revises: 20251125_150700
Create Date: 2025-12-01 11:00:00.000000

Implements W3C StatusList2021 for internet-scale document revocation.
Supports 10+ billion documents with O(1) status lookups.
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = "20251201_110000"
down_revision = "20251125_150700"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create status_list_entries table
    op.create_table(
        "status_list_entries",
        sa.Column("organization_id", sa.String(64), nullable=False),
        sa.Column("list_index", sa.Integer(), nullable=False),
        sa.Column("bit_index", sa.Integer(), nullable=False),
        sa.Column("document_id", sa.String(64), nullable=False),
        sa.Column("revoked", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("revoked_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("revoked_reason", sa.String(50), nullable=True),
        sa.Column("revoked_reason_detail", sa.Text(), nullable=True),
        sa.Column("revoked_by", sa.String(64), nullable=True),
        sa.Column("reinstated_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("reinstated_by", sa.String(64), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("organization_id", "list_index", "bit_index"),
    )

    # Create indexes for status_list_entries
    op.create_index("idx_status_entry_document", "status_list_entries", ["document_id"])
    op.create_index("idx_status_entry_org_revoked", "status_list_entries", ["organization_id", "revoked"])
    op.create_index("idx_status_entry_list", "status_list_entries", ["organization_id", "list_index"])

    # Create status_list_metadata table
    op.create_table(
        "status_list_metadata",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", sa.String(64), nullable=False),
        sa.Column("list_index", sa.Integer(), nullable=False),
        sa.Column("next_bit_index", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_full", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("current_version", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_generated_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("generation_duration_ms", sa.Integer(), nullable=True),
        sa.Column("cdn_url", sa.String(500), nullable=True),
        sa.Column("cdn_etag", sa.String(64), nullable=True),
        sa.Column("total_documents", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("revoked_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes for status_list_metadata
    op.create_index("idx_status_meta_org_list", "status_list_metadata", ["organization_id", "list_index"], unique=True)
    op.create_index("idx_status_meta_stale", "status_list_metadata", ["organization_id", "last_generated_at"])

    # Add status_list columns to content_references for linking
    op.add_column("content_references", sa.Column("status_list_index", sa.Integer(), nullable=True))
    op.add_column("content_references", sa.Column("status_bit_index", sa.Integer(), nullable=True))
    op.add_column("content_references", sa.Column("status_list_url", sa.String(500), nullable=True))


def downgrade() -> None:
    # Remove columns from content_references
    op.drop_column("content_references", "status_list_url")
    op.drop_column("content_references", "status_bit_index")
    op.drop_column("content_references", "status_list_index")

    # Drop status_list_metadata
    op.drop_index("idx_status_meta_stale", table_name="status_list_metadata")
    op.drop_index("idx_status_meta_org_list", table_name="status_list_metadata")
    op.drop_table("status_list_metadata")

    # Drop status_list_entries
    op.drop_index("idx_status_entry_list", table_name="status_list_entries")
    op.drop_index("idx_status_entry_org_revoked", table_name="status_list_entries")
    op.drop_index("idx_status_entry_document", table_name="status_list_entries")
    op.drop_table("status_list_entries")
