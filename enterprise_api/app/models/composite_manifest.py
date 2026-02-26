"""SQLAlchemy model for composite_manifests table.

Stores the article-level C2PA manifest that references each signed image as an
ingredient and binds them to the signed text via the ZWC/Merkle pipeline.
"""

import uuid
from datetime import datetime

from sqlalchemy import (
    TIMESTAMP,
    CheckConstraint,
    Column,
    Index,
    Integer,
    String,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from app.database import Base


class CompositeManifest(Base):
    """
    Article-level C2PA manifest binding signed text and signed images.

    Created after all images in a rich article are signed. The manifest_data
    JSONB field holds the full C2PA manifest with c2pa.ingredient.v3 entries
    for each image and a reference to the text Merkle root.
    """

    __tablename__ = "composite_manifests"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(String(64), nullable=False)
    document_id = Column(String(64), nullable=False, unique=True)
    instance_id = Column(String(255), nullable=False)

    # Full C2PA manifest JSON (ingredient references, assertions, hashes)
    manifest_data = Column(JSONB, nullable=False)
    # String(128) accommodates "sha256:" prefix (7 chars) + 64 hex chars = 71 total
    manifest_hash = Column(String(128), nullable=False)

    # Link to text signing Merkle root (null if text-only article had no Merkle)
    text_merkle_root = Column(String(128), nullable=True)

    # Number of image ingredients in this composite manifest
    ingredient_count = Column(Integer, nullable=False, default=0)

    created_at = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint(
            "ingredient_count >= 0",
            name="chk_composite_manifests_ingredient_count_non_negative",
        ),
        Index("idx_composite_manifests_org", "organization_id"),
        Index("idx_composite_manifests_instance", "instance_id"),
    )

    def __repr__(self) -> str:
        return (
            f"<CompositeManifest(document_id={self.document_id!r}, "
            f"ingredients={self.ingredient_count})>"
        )
