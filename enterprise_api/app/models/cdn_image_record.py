"""SQLAlchemy model for cdn_image_records table.

Tracks signed images and their CDN derivatives for provenance continuity.
"""

import uuid
from datetime import datetime

from sqlalchemy import TIMESTAMP, BigInteger, Boolean, Column, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from app.database import Base


class CdnImageRecord(Base):
    """
    Metadata record for a CDN-tracked image with C2PA provenance continuity.

    Each row represents one image (or variant) registered through the CDN
    provenance pipeline. Tracks perceptual hash and SHA-256 for fuzzy and
    exact-match lookup across CDN-reprocessed derivatives.
    """

    __tablename__ = "cdn_image_records"
    __table_args__ = (
        Index("idx_cdn_image_records_org_phash", "organization_id", "phash"),
        Index("idx_cdn_image_records_org_sha256", "organization_id", "content_sha256"),
        {"extend_existing": True},
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(String(64), nullable=False)
    original_url = Column(Text, nullable=True)  # Canonical URL of the original image
    content_sha256 = Column(String(71), nullable=True)  # "sha256:" + 64 hex chars
    phash = Column(BigInteger, nullable=True)  # signed int64 average hash (8x8)
    manifest_store = Column(JSONB, nullable=True)  # Full C2PA manifest JSON

    # Derivative tracking
    is_variant = Column(Boolean, nullable=False, default=False)
    parent_record_id = Column(PGUUID(as_uuid=True), nullable=True)  # FK to self
    transform_description = Column(String(500), nullable=True)  # e.g. "resize:800x600,webp"

    created_at = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<CdnImageRecord(id={self.id!r}, org={self.organization_id!r}, is_variant={self.is_variant})>"
