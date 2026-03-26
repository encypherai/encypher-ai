"""SQLAlchemy model for signed_videos table.

Stores metadata for signed videos produced by the C2PA video signing pipeline.
Mirrors the ArticleImage pattern: signed bytes are returned directly in the API
response; this table records only hashes, pHash, and C2PA instance references.
"""

import uuid
from datetime import datetime

from sqlalchemy import (
    TIMESTAMP,
    BigInteger,
    Boolean,
    CheckConstraint,
    Column,
    Index,
    String,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from app.database import Base


class SignedVideo(Base):
    """Metadata record for a C2PA-signed video.

    Each row represents one video that was signed and returned to the caller.
    The signed bytes are NOT stored here; only verification metadata is kept.
    """

    __tablename__ = "signed_videos"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(String(64), nullable=False)
    document_id = Column(String(64), nullable=False)
    video_id = Column(String(64), nullable=False, unique=True)
    title = Column(String(500), nullable=True)
    mime_type = Column(String(100), nullable=False)

    # Hashes (sign-and-return model, no binary storage)
    original_hash = Column(String(128), nullable=False)
    signed_hash = Column(String(128), nullable=False)
    size_bytes = Column(BigInteger, nullable=False)

    # C2PA manifest references
    c2pa_instance_id = Column(String(255), nullable=True)
    c2pa_manifest_hash = Column(String(128), nullable=True)
    c2pa_signed = Column(Boolean, nullable=False, default=False)

    # C2PA digital source type
    digital_source_type = Column(String(64), nullable=True)

    # Perceptual hash (first-frame average hash, 64-bit)
    phash = Column(BigInteger, nullable=True)

    # Metadata
    video_metadata = Column(JSONB, default=dict)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("size_bytes > 0", name="chk_signed_videos_size_positive"),
        Index("idx_signed_videos_org_doc", "organization_id", "document_id"),
    )

    def __repr__(self) -> str:
        return f"<SignedVideo(video_id={self.video_id!r}, doc={self.document_id!r})>"
