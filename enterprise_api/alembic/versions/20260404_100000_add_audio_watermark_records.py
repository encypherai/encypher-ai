"""add audio_watermark_records table

Revision ID: 20260404_100000
Revises: 20260401_100000
Create Date: 2026-04-04 10:00:00

Tracks audio files that have had spread-spectrum watermarks applied.
Audio signing results are ephemeral (returned to caller, not persisted),
so this table provides the persistence layer for watermark key lookups
required by the verification pipeline (task 4.2).

Columns:
  audio_id           - matches the aud_<hex> value generated in _sign_audio()
  organization_id    - org that signed the file
  document_id        - caller-supplied document identifier
  watermark_applied  - false when watermarking was requested but the microservice
                       was unavailable or returned an error
  watermark_key      - hex payload embedded in the signal (HMAC-SHA256 truncated
                       to 64 bits / 16 hex chars); null when not applied
  watermark_method   - method identifier, e.g. "spread_spectrum_v1"
  signed_hash        - sha256 of the watermarked bytes (for integrity reference)
  mime_type          - audio MIME type, e.g. "audio/mpeg", "audio/wav"
  created_at         - timestamp of the signing operation
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = "20260404_100000"
down_revision = "20260401_100000"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "audio_watermark_records",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("audio_id", sa.String(64), nullable=False, unique=True),
        sa.Column("organization_id", sa.String(64), nullable=False),
        sa.Column("document_id", sa.String(64), nullable=False),
        sa.Column("watermark_applied", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("watermark_key", sa.String(64), nullable=True),
        sa.Column("watermark_method", sa.String(64), nullable=True),
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
        "idx_audio_watermark_org",
        "audio_watermark_records",
        ["organization_id"],
    )
    op.create_index(
        "idx_audio_watermark_key",
        "audio_watermark_records",
        ["watermark_key"],
    )


def downgrade() -> None:
    op.drop_index("idx_audio_watermark_key", table_name="audio_watermark_records")
    op.drop_index("idx_audio_watermark_org", table_name="audio_watermark_records")
    op.drop_table("audio_watermark_records")
