"""
SQLAlchemy model for fuzzy fingerprint index entries.
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    TIMESTAMP,
    BigInteger,
    CheckConstraint,
    Column,
    ForeignKey,
    Index,
    Integer,
    String,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from app.database import Base


class FuzzyFingerprint(Base):
    """
    Locality-sensitive hash fingerprints for text segments.

    Stores fuzzy fingerprints (SimHash) for sentence/paragraph segments
    so we can perform similarity search when embeddings are missing.
    """

    __tablename__ = "fuzzy_fingerprints"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    organization_id = Column(
        String(64),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    document_id = Column(String(64), nullable=False, index=True)
    merkle_root_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("merkle_roots.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    segmentation_level = Column(String(20), nullable=False)
    segment_index = Column(Integer, nullable=True)
    leaf_hash = Column(String(64), nullable=True)

    fingerprint_type = Column(String(20), nullable=False, default="simhash")
    fingerprint_value = Column(BigInteger, nullable=False)
    fingerprint_bits = Column(Integer, nullable=False, default=64)
    fingerprint_bucket = Column(Integer, nullable=False)

    text_preview = Column(String(200), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint(
            "segmentation_level IN ('sentence', 'paragraph', 'document')",
            name="fuzzy_fingerprints_segmentation_level_check",
        ),
        Index("idx_fuzzy_fingerprints_doc_level", "document_id", "segmentation_level"),
        Index("idx_fuzzy_fingerprints_bucket", "fingerprint_bucket"),
        Index("idx_fuzzy_fingerprints_root", "merkle_root_id"),
    )

    def __repr__(self) -> str:
        return f"<FuzzyFingerprint(doc={self.document_id}, level={self.segmentation_level}, bucket={self.fingerprint_bucket})>"
