"""Initial schema for encoding-service

Revision ID: 001
Revises:
Create Date: 2024-11-28

Tables: encoded_documents, signing_operations
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Encoded documents table
    op.create_table(
        "encoded_documents",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("user_id", sa.String(64), nullable=False, index=True),
        sa.Column("organization_id", sa.String(64), nullable=True, index=True),
        # Document information
        sa.Column("document_id", sa.String(64), nullable=False, unique=True, index=True),
        sa.Column("original_content", sa.Text, nullable=False),
        sa.Column("encoded_content", sa.Text, nullable=False),
        sa.Column("content_hash", sa.String(64), nullable=False, index=True),
        # Signature information
        sa.Column("signature", sa.Text, nullable=False),
        sa.Column("signer_id", sa.String(64), nullable=False),
        sa.Column("signing_key_id", sa.String(64), nullable=True),
        # Manifest (C2PA)
        sa.Column("manifest", postgresql.JSONB, nullable=False),
        # Metadata
        sa.Column("extra_metadata", postgresql.JSONB, nullable=True),
        sa.Column("format", sa.String(50), server_default="text"),
        sa.Column("encoding_method", sa.String(50), server_default="unicode"),
        sa.Column("word_count", sa.Integer, nullable=True),
        # Status
        sa.Column("is_active", sa.Boolean, server_default="true", nullable=False),
        # Timestamps
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )

    # Signing operations audit log
    op.create_table(
        "signing_operations",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("document_id", sa.String(64), nullable=False, index=True),
        sa.Column("user_id", sa.String(64), nullable=False, index=True),
        sa.Column("organization_id", sa.String(64), nullable=True, index=True),
        # Operation details
        sa.Column("operation_type", sa.String(50), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("error_message", sa.Text, nullable=True),
        # Performance metrics
        sa.Column("processing_time_ms", sa.Integer, nullable=True),
        sa.Column("content_size_bytes", sa.Integer, nullable=True),
        # Client information
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.String(500), nullable=True),
        # Timestamp
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), index=True),
    )


def downgrade() -> None:
    op.drop_table("signing_operations")
    op.drop_table("encoded_documents")
