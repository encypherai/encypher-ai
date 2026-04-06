"""add article_audios, article_videos tables and composite_manifests media count columns

Revision ID: 20260407_100000
Revises: 20260406_100000
Create Date: 2026-04-07 10:00:00

Adds persistence tables for audio and video files embedded in rich articles
(article_audios, article_videos), mirroring the existing article_images table.
Also adds per-media-type count columns to composite_manifests.
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = "20260407_100000"  # pragma: allowlist secret
down_revision = "20260406_100000"  # pragma: allowlist secret
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- article_audios table ---
    op.create_table(
        "article_audios",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("organization_id", sa.String(64), nullable=False),
        sa.Column("document_id", sa.String(64), nullable=False),
        sa.Column("audio_id", sa.String(64), nullable=False, unique=True),
        sa.Column("position", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("filename", sa.String(500), nullable=True),
        sa.Column("mime_type", sa.String(100), nullable=False),
        sa.Column("original_hash", sa.String(128), nullable=False),
        sa.Column("signed_hash", sa.String(128), nullable=False),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("c2pa_instance_id", sa.String(255), nullable=True),
        sa.Column("c2pa_manifest_hash", sa.String(128), nullable=True),
        sa.Column("watermark_applied", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("watermark_key", sa.String(100), nullable=True),
        sa.Column("audio_metadata", postgresql.JSONB(), nullable=True, server_default=sa.text("'{}'::jsonb")),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint("position >= 0", name="chk_article_audios_position_positive"),
        sa.CheckConstraint("size_bytes > 0", name="chk_article_audios_size_positive"),
    )
    op.create_index("idx_article_audios_org_doc", "article_audios", ["organization_id", "document_id"])

    # --- article_videos table ---
    op.create_table(
        "article_videos",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("organization_id", sa.String(64), nullable=False),
        sa.Column("document_id", sa.String(64), nullable=False),
        sa.Column("video_id", sa.String(64), nullable=False, unique=True),
        sa.Column("position", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("filename", sa.String(500), nullable=True),
        sa.Column("mime_type", sa.String(100), nullable=False),
        sa.Column("original_hash", sa.String(128), nullable=False),
        sa.Column("signed_hash", sa.String(128), nullable=False),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("c2pa_instance_id", sa.String(255), nullable=True),
        sa.Column("c2pa_manifest_hash", sa.String(128), nullable=True),
        sa.Column("watermark_applied", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("watermark_key", sa.String(100), nullable=True),
        sa.Column("video_metadata", postgresql.JSONB(), nullable=True, server_default=sa.text("'{}'::jsonb")),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint("position >= 0", name="chk_article_videos_position_positive"),
        sa.CheckConstraint("size_bytes > 0", name="chk_article_videos_size_positive"),
    )
    op.create_index("idx_article_videos_org_doc", "article_videos", ["organization_id", "document_id"])

    # --- Add media count columns to composite_manifests ---
    op.add_column("composite_manifests", sa.Column("image_count", sa.Integer(), nullable=False, server_default=sa.text("0")))
    op.add_column("composite_manifests", sa.Column("audio_count", sa.Integer(), nullable=False, server_default=sa.text("0")))
    op.add_column("composite_manifests", sa.Column("video_count", sa.Integer(), nullable=False, server_default=sa.text("0")))


def downgrade() -> None:
    op.drop_column("composite_manifests", "video_count")
    op.drop_column("composite_manifests", "audio_count")
    op.drop_column("composite_manifests", "image_count")
    op.drop_index("idx_article_videos_org_doc", table_name="article_videos")
    op.drop_table("article_videos")
    op.drop_index("idx_article_audios_org_doc", table_name="article_audios")
    op.drop_table("article_audios")
