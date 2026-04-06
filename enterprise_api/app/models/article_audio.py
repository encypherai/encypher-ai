"""SQLAlchemy model for article_audios table.

Stores metadata for signed audio files produced by the rich article signing
pipeline. Signed audio bytes are returned directly in the API response (base64).
This table records only hashes, C2PA instance references, and watermark metadata.
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
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from app.database import Base


class ArticleAudio(Base):
    """Metadata record for a C2PA-signed audio file within a rich article.

    Each row represents one audio file that was signed and returned to the
    publisher. The signed bytes are NOT stored here; only verification
    metadata is kept.
    """

    __tablename__ = "article_audios"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(String(64), nullable=False)
    document_id = Column(String(64), nullable=False)
    audio_id = Column(String(64), nullable=False, unique=True)
    position = Column(Integer, nullable=False, default=0)
    filename = Column(String(500), nullable=True)
    mime_type = Column(String(100), nullable=False)

    # Hashes (no binary storage - sign-and-return model)
    original_hash = Column(String(128), nullable=False)
    signed_hash = Column(String(128), nullable=False)
    size_bytes = Column(BigInteger, nullable=False)

    # C2PA manifest references
    c2pa_instance_id = Column(String(255), nullable=True)
    c2pa_manifest_hash = Column(String(128), nullable=True)

    # Spread-spectrum watermark (Enterprise only)
    watermark_applied = Column(Boolean, nullable=False, default=False)
    watermark_key = Column(String(100), nullable=True)

    # Metadata
    audio_metadata = Column(JSONB, default=dict)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("position >= 0", name="chk_article_audios_position_positive"),
        CheckConstraint("size_bytes > 0", name="chk_article_audios_size_positive"),
        Index("idx_article_audios_org_doc", "organization_id", "document_id"),
    )

    def __repr__(self) -> str:
        return f"<ArticleAudio(audio_id={self.audio_id!r}, doc={self.document_id!r}, pos={self.position})>"
