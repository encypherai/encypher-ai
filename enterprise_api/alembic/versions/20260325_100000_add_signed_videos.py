"""add signed_videos table

Revision ID: 20260325_100000
Revises: 20260324_100000
Create Date: 2026-03-25 10:00:00

"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = "20260325_100000"
down_revision = "20260324_100000"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "signed_videos",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("organization_id", sa.String(64), nullable=False),
        sa.Column("document_id", sa.String(64), nullable=False),
        sa.Column("video_id", sa.String(64), nullable=False, unique=True),
        sa.Column("title", sa.String(500), nullable=True),
        sa.Column("mime_type", sa.String(100), nullable=False),
        sa.Column("original_hash", sa.String(128), nullable=False),
        sa.Column("signed_hash", sa.String(128), nullable=False),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("c2pa_instance_id", sa.String(255), nullable=True),
        sa.Column("c2pa_manifest_hash", sa.String(128), nullable=True),
        sa.Column("c2pa_signed", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("digital_source_type", sa.String(64), nullable=True),
        sa.Column("phash", sa.BigInteger(), nullable=True),
        sa.Column("video_metadata", postgresql.JSONB(), server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("size_bytes > 0", name="chk_signed_videos_size_positive"),
    )
    op.create_index("idx_signed_videos_org_doc", "signed_videos", ["organization_id", "document_id"])


def downgrade() -> None:
    op.drop_index("idx_signed_videos_org_doc", table_name="signed_videos")
    op.drop_table("signed_videos")
