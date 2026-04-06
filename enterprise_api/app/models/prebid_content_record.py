"""SQLAlchemy model for prebid_content_records table.

Tracks auto-signed content from the Prebid RTD module pipeline.
Each row represents one unique (domain, content_hash) pair.
Content text is never stored -- only hashes, metadata, and C2PA manifests.
"""

import uuid
from datetime import datetime

from sqlalchemy import TIMESTAMP, Column, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from app.database import Base


class PrebidContentRecord(Base):
    """Signed content record for Prebid auto-provenance pipeline.

    One row per unique (domain, content_hash). Re-requests for the same
    content return the existing manifest without charging quota.
    """

    __tablename__ = "prebid_content_records"
    __table_args__ = (
        Index("idx_prebid_content_domain_hash", "domain", "content_hash", unique=True),
        Index("idx_prebid_content_org", "organization_id"),
        {"extend_existing": True},
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(String(64), nullable=False)
    domain = Column(String(255), nullable=False)
    canonical_url = Column(Text, nullable=True)
    content_hash = Column(String(71), nullable=False)  # "sha256:" + 64 hex chars
    manifest_store = Column(JSONB, nullable=True)
    manifest_url = Column(Text, nullable=True)
    page_title = Column(String(500), nullable=True)
    signer_tier = Column(String(32), nullable=False, default="encypher_free")
    signed_at = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<PrebidContentRecord(id={self.id!r}, domain={self.domain!r}, org={self.organization_id!r})>"
