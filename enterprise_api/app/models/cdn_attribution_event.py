"""
CDN image attribution event — one row per image request tracked via Logpush.
"""

import uuid
from datetime import datetime

from sqlalchemy import TIMESTAMP, Column, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from app.database import Base


class CdnAttributionEvent(Base):
    __tablename__ = "cdn_attribution_events"
    __table_args__ = (
        Index("idx_cdn_attribution_org_created", "organization_id", "created_at"),
        {"extend_existing": True},
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(String(64), nullable=False)
    image_url = Column(Text, nullable=True)  # Full URL from Logpush log
    canonical_url = Column(Text, nullable=True)  # URL with CDN transforms stripped
    matched_record_id = Column(PGUUID(as_uuid=True), nullable=True)  # CdnImageRecord.id if matched
    verdict = Column(String(32), nullable=True)  # ORIGINAL_SIGNED | VERIFIED_DERIVATIVE | PROVENANCE_LOST
    http_status = Column(Integer, nullable=True)
    client_ip = Column(String(64), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow)
