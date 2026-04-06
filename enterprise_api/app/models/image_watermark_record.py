"""SQLAlchemy model for image_watermark_records table.

Stores metadata for images that had TrustMark neural watermarks applied
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

WATERMARK_METHOD = "trustmark_neural_v1"


class ImageWatermarkRecord(Base):
    """Metadata record for an image with an embedded TrustMark neural watermark.

    Rows are written by the _sign_image() pipeline in media_signing.py after
    a successful (or attempted) watermark application. The watermark_key field
    enables payload-to-image_id lookups during verification.
    """

    __tablename__ = "image_watermark_records"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    image_id = Column(String(64), nullable=False, unique=True)
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
        Index("idx_image_watermark_org", "organization_id"),
        Index("idx_image_watermark_key", "watermark_key"),
    )

    def __repr__(self) -> str:
        return f"<ImageWatermarkRecord(image_id={self.image_id!r}, applied={self.watermark_applied}, key={self.watermark_key!r})>"
