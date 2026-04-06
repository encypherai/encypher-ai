"""SQLAlchemy model for audio_watermark_records table.

Stores metadata for audio files that had spread-spectrum watermarks applied
during signing. The signed bytes are returned directly to the caller and are
not stored here; this table provides the persistence layer for watermark key
lookups used by the verification pipeline (task 4.2).
"""

import uuid
from datetime import datetime

from sqlalchemy import (
    TIMESTAMP,
    Boolean,
    Column,
    Index,
    String,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from app.database import Base

WATERMARK_METHOD = "spread_spectrum_v1"


class AudioWatermarkRecord(Base):
    """Metadata record for an audio file with an embedded spread-spectrum watermark.

    Rows are written by the _sign_audio() pipeline in media_signing.py after
    a successful (or attempted) watermark application. The watermark_key field
    enables payload-to-audio_id lookups during verification.
    """

    __tablename__ = "audio_watermark_records"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    audio_id = Column(String(64), nullable=False, unique=True)
    organization_id = Column(String(64), nullable=False)
    document_id = Column(String(64), nullable=False)

    # Watermark tracking columns
    watermark_applied = Column(Boolean, nullable=False, default=False)
    watermark_key = Column(String(64), nullable=True)
    watermark_method = Column(String(64), nullable=True, default=WATERMARK_METHOD)

    # Signed file reference (hash only -- bytes returned to caller, not stored)
    signed_hash = Column(String(128), nullable=True)
    mime_type = Column(String(100), nullable=True)

    created_at = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_audio_watermark_org", "organization_id"),
        Index("idx_audio_watermark_key", "watermark_key"),
    )

    def __repr__(self) -> str:
        return f"<AudioWatermarkRecord(audio_id={self.audio_id!r}, applied={self.watermark_applied}, key={self.watermark_key!r})>"
