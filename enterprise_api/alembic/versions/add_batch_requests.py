"""add batch request persistence tables

Revision ID: add_batch_requests
Revises: add_org_certificate_metadata
Create Date: 2025-11-12
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "add_batch_requests"
down_revision = "add_org_certificate_metadata"
branch_labels = None
depends_on = None


batch_request_type = sa.Enum("sign", "verify", name="batch_request_type")
batch_status_enum = sa.Enum(
    "pending",
    "running",
    "completed",
    "failed",
    "canceled",
    name="batch_request_status",
)
batch_item_status_enum = sa.Enum(
    "pending",
    "processing",
    "success",
    "failed",
    "skipped",
    name="batch_item_status",
)


def upgrade() -> None:
    batch_request_type.create(op.get_bind(), checkfirst=True)
    batch_status_enum.create(op.get_bind(), checkfirst=True)
    batch_item_status_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "batch_requests",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("organization_id", sa.String(length=255), nullable=False),
        sa.Column("api_key", sa.String(length=64), nullable=False),
        sa.Column("request_type", batch_request_type, nullable=False),
        sa.Column("mode", sa.String(length=32), nullable=False),
        sa.Column("segmentation_level", sa.String(length=32), nullable=True),
        sa.Column("idempotency_key", sa.String(length=128), nullable=False),
        sa.Column("payload_hash", sa.String(length=64), nullable=False),
        sa.Column(
            "status",
            batch_status_enum,
            nullable=False,
            server_default="pending",
        ),
        sa.Column("item_count", sa.Integer(), nullable=False),
        sa.Column("success_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("failure_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_code", sa.String(length=64), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("request_metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("started_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("completed_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("expires_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.UniqueConstraint("organization_id", "idempotency_key", name="uq_batch_request_org_idempotent"),
    )

    op.create_index(
        "ix_batch_requests_org_status",
        "batch_requests",
        ["organization_id", "status"],
    )
    op.create_index("ix_batch_requests_expires_at", "batch_requests", ["expires_at"])

    op.create_table(
        "batch_items",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("batch_request_id", sa.String(length=36), nullable=False),
        sa.Column("document_id", sa.String(length=255), nullable=False),
        sa.Column("status", batch_item_status_enum, nullable=False, server_default="pending"),
        sa.Column("mode", sa.String(length=32), nullable=False),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("error_code", sa.String(length=64), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("statistics", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("result_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(
            ["batch_request_id"],
            ["batch_requests.id"],
            ondelete="CASCADE",
        ),
    )

    op.create_index("ix_batch_items_batch_request_id", "batch_items", ["batch_request_id"])
    op.create_index(
        "ix_batch_items_document_status",
        "batch_items",
        ["document_id", "status"],
    )


def downgrade() -> None:
    op.drop_index("ix_batch_items_document_status", table_name="batch_items")
    op.drop_index("ix_batch_items_batch_request_id", table_name="batch_items")
    op.drop_table("batch_items")

    op.drop_index("ix_batch_requests_expires_at", table_name="batch_requests")
    op.drop_index("ix_batch_requests_org_status", table_name="batch_requests")
    op.drop_table("batch_requests")

    batch_item_status_enum.drop(op.get_bind(), checkfirst=True)
    batch_status_enum.drop(op.get_bind(), checkfirst=True)
    batch_request_type.drop(op.get_bind(), checkfirst=True)

