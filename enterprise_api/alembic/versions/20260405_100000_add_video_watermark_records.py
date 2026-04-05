"""add video_watermark_records table

Revision ID: f31b1cc5602e
Revises: 20260404_100000
Create Date: 2026-04-05 10:00:00

Tracks video files that have had spread-spectrum watermarks applied.
Video signing results are ephemeral (returned to caller, not persisted),
so this table provides the persistence layer for watermark key lookups
required by the verification pipeline.

Columns:
  video_id           - matches the vid_<hex> value generated in _sign_video()
  organization_id    - org that signed the file
  document_id        - caller-supplied document identifier
  session_id         - optional session identifier for live stream segments
  watermark_applied  - false when watermarking was requested but the microservice
                       was unavailable or returned an error
  watermark_key      - hex payload embedded in the signal (HMAC-SHA256 truncated
                       to 64 bits / 16 hex chars); null when not applied
  watermark_method   - method identifier, e.g. "spread_spectrum_v1"
  signed_hash        - sha256 of the watermarked bytes (for integrity reference)
  mime_type          - video MIME type, e.g. "video/mp4", "video/webm"
  created_at         - timestamp of the signing operation
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = "f31b1cc5602e"  # pragma: allowlist secret
down_revision = "20260404_100000"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "video_watermark_records",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("video_id", sa.String(64), nullable=False, unique=True),
        sa.Column("organization_id", sa.String(64), nullable=False),
        sa.Column("document_id", sa.String(64), nullable=False),
        sa.Column("session_id", sa.String(64), nullable=True),
        sa.Column("watermark_applied", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("watermark_key", sa.String(64), nullable=True),
        sa.Column("watermark_method", sa.String(64), nullable=True, server_default=sa.text("'spread_spectrum_v1'")),
        sa.Column("signed_hash", sa.String(128), nullable=True),
        sa.Column("mime_type", sa.String(100), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index(
        "idx_video_watermark_org_video",
        "video_watermark_records",
        ["video_id", "organization_id"],
    )
    op.create_index(
        "idx_video_watermark_key",
        "video_watermark_records",
        ["watermark_key"],
    )


def downgrade() -> None:
    op.drop_index("idx_video_watermark_key", table_name="video_watermark_records")
    op.drop_index("idx_video_watermark_org_video", table_name="video_watermark_records")
    op.drop_table("video_watermark_records")
