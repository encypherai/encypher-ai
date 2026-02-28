"""SQLAlchemy model for article_images table.

Stores metadata for signed images produced by the C2PA image signing pipeline.
Signed image bytes are returned directly in the API response (base64).
Publishers host signed images on their own CDN. This table records only
hashes, pHash, and C2PA instance references.
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
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from app.database import Base


class ArticleImage(Base):
    """
    Metadata record for a C2PA-signed image within a rich article.

    Each row represents one image that was signed and returned to the publisher.
    The signed bytes are NOT stored here; only verification metadata is kept.
    """

    __tablename__ = "article_images"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(String(64), nullable=False)
    document_id = Column(String(64), nullable=False)
    image_id = Column(String(64), nullable=False, unique=True)
    position = Column(Integer, nullable=False, default=0)
    filename = Column(String(500), nullable=True)
    mime_type = Column(String(100), nullable=False)
    alt_text = Column(Text, nullable=True)

    # Hashes (no binary storage - sign-and-return model)
    # String(128) accommodates "sha256:" prefix (7 chars) + 64 hex chars = 71 total
    original_hash = Column(String(128), nullable=False)
    signed_hash = Column(String(128), nullable=False)
    size_bytes = Column(BigInteger, nullable=False)

    # C2PA manifest references
    c2pa_instance_id = Column(String(255), nullable=True)
    c2pa_manifest_hash = Column(String(128), nullable=True)

    # Perceptual hash for fuzzy attribution lookup
    phash = Column(BigInteger, nullable=True)
    phash_algorithm = Column(String(20), default="average_hash")

    # TrustMark neural watermark (Enterprise only)
    trustmark_applied = Column(Boolean, nullable=False, default=False)
    trustmark_key = Column(String(100), nullable=True)

    # Metadata
    exif_metadata = Column(JSONB, nullable=True)
    image_metadata = Column(JSONB, default=dict)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("position >= 0", name="chk_article_images_position_positive"),
        CheckConstraint("size_bytes > 0", name="chk_article_images_size_positive"),
        Index("idx_article_images_org_doc", "organization_id", "document_id"),
    )

    def __repr__(self) -> str:
        return (
            f"<ArticleImage(image_id={self.image_id!r}, "
            f"doc={self.document_id!r}, "
            f"pos={self.position})>"
        )
