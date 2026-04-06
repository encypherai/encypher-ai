"""add image_watermark_records table

Revision ID: 20260406_100000
Revises: f31b1cc5602e
Create Date: 2026-04-06 10:00:00

Tracks images that have had TrustMark neural watermarks applied during signing.
Signed bytes are returned to the caller, not persisted; this table stores
watermark key lookups for the verification pipeline.

Columns:
  image_id           - matches the img_<hex> value generated in _sign_image()
  organization_id    - org that signed the file
  document_id        - caller-supplied document identifier
  watermark_applied  - false when watermarking was requested but the microservice
                       was unavailable or returned an error
  watermark_key      - hex payload embedded via TrustMark; null when not applied
  watermark_method   - method identifier, "trustmark_neural_v1"
  signed_hash        - sha256 of the watermarked bytes (for integrity reference)
  mime_type          - image MIME type, e.g. "image/jpeg", "image/png"
  created_at         - timestamp of the signing operation
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = "20260406_100000"  # pragma: allowlist secret
down_revision = "f31b1cc5602e"  # pragma: allowlist secret
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "image_watermark_records",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("image_id", sa.String(64), nullable=False, unique=True),
        sa.Column("organization_id", sa.String(64), nullable=False),
        sa.Column("document_id", sa.String(64), nullable=False),
        sa.Column("watermark_applied", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("watermark_key", sa.String(64), nullable=True),
        sa.Column("watermark_method", sa.String(64), nullable=True, server_default=sa.text("'trustmark_neural_v1'")),
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
        "idx_image_watermark_org",
        "image_watermark_records",
        ["organization_id"],
    )
    op.create_index(
        "idx_image_watermark_key",
        "image_watermark_records",
        ["watermark_key"],
    )


def downgrade() -> None:
    op.drop_index("idx_image_watermark_key", table_name="image_watermark_records")
    op.drop_index("idx_image_watermark_org", table_name="image_watermark_records")
    op.drop_table("image_watermark_records")
