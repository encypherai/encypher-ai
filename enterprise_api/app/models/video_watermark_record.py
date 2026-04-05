"""SQLAlchemy model for video_watermark_records table.

Stores metadata for video files that had spread-spectrum watermarks applied
during signing. The signed bytes are returned directly to the caller and are
not stored here; this table provides the persistence layer for watermark key
lookups used by the verification pipeline.
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


class VideoWatermarkRecord(Base):
    """Metadata record for a video file with an embedded spread-spectrum watermark.

    Rows are written by the _sign_video() pipeline in media_signing.py after
    a successful (or attempted) watermark application. The watermark_key field
    enables payload-to-video_id lookups during verification.
    """

    __tablename__ = "video_watermark_records"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_id = Column(String(64), nullable=False, unique=True)
    organization_id = Column(String(64), nullable=False)
    document_id = Column(String(64), nullable=False)
    session_id = Column(String(64), nullable=True)  # For live stream segments

    # Watermark tracking columns
    watermark_applied = Column(Boolean, nullable=False, default=False)
    watermark_key = Column(String(64), nullable=True)
    watermark_method = Column(String(64), nullable=True, default=WATERMARK_METHOD)

    # Signed file reference (hash only -- bytes returned to caller, not stored)
    signed_hash = Column(String(128), nullable=True)
    mime_type = Column(String(100), nullable=True)

    created_at = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_video_watermark_org_video", "video_id", "organization_id"),
        Index("idx_video_watermark_key", "watermark_key"),
    )

    def __repr__(self) -> str:
        return f"<VideoWatermarkRecord(video_id={self.video_id!r}, applied={self.watermark_applied}, key={self.watermark_key!r})>"
