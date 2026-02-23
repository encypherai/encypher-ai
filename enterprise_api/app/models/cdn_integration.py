"""
CDN Integration model.

Stores per-organization CDN webhook configuration for passive log ingestion
(Cloudflare Logpush and future providers). One row per (org, provider) pair.
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, String, Text, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class CdnIntegration(Base):
    """
    Configuration record for a CDN log-ingestion integration.

    The webhook_secret_hash stores a bcrypt hash of the shared secret that
    the publisher copies into Cloudflare Logpush (or equivalent). Incoming
    webhook requests carry an x-cf-secret header containing the raw secret;
    the handler verifies it with bcrypt.checkpw before processing any data.
    """

    __tablename__ = "cdn_integrations"
    __table_args__ = {"extend_existing": True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(String(64), nullable=False)

    # "cloudflare" | "fastly" | "cloudfront"
    provider = Column(Text, nullable=False, default="cloudflare")

    # Optional: Cloudflare Zone ID shown in setup instructions
    zone_id = Column(Text, nullable=True)

    # bcrypt hash of the shared secret
    webhook_secret_hash = Column(Text, nullable=False)

    enabled = Column(Boolean, nullable=False, default=True)

    created_at = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    def __repr__(self) -> str:
        return (
            f"<CdnIntegration("
            f"org={self.organization_id}, "
            f"provider={self.provider}, "
            f"enabled={self.enabled})>"
        )
