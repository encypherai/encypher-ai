"""
Ghost CMS integration model.

Stores per-organization Ghost credentials and signing preferences
for the hosted Ghost webhook endpoint.
"""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String
from sqlalchemy.sql import func

from app.database import Base


class GhostIntegration(Base):
    """
    Ghost CMS integration configuration for an organization.

    Stores the Ghost instance URL, Admin API key, and signing preferences
    so the hosted webhook endpoint can sign content on behalf of the org.
    """

    __tablename__ = "ghost_integrations"

    id = Column(String(64), primary_key=True)
    organization_id = Column(
        String(64),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    # Ghost connection
    ghost_url = Column(String(1000), nullable=False)
    ghost_admin_api_key = Column(String(500), nullable=False)

    # Webhook authentication — opaque token (ghwh_...) scoped to this integration
    # Only the SHA-256 hash is stored; the plaintext token is returned once on creation.
    webhook_token_hash = Column(String(128), nullable=False, unique=True, index=True)

    # Signing preferences
    auto_sign_on_publish = Column(Boolean, nullable=False, default=True)
    auto_sign_on_update = Column(Boolean, nullable=False, default=True)
    manifest_mode = Column(String(50), nullable=False, default="micro")
    segmentation_level = Column(String(50), nullable=False, default="sentence")
    ecc = Column(Boolean, nullable=False, default=True)
    embed_c2pa = Column(Boolean, nullable=False, default=True)
    badge_enabled = Column(Boolean, nullable=False, default=True)

    # Status
    is_active = Column(Boolean, nullable=False, default=True)
    last_webhook_at = Column(DateTime(timezone=True), nullable=True)
    last_sign_at = Column(DateTime(timezone=True), nullable=True)
    sign_count = Column(String(20), nullable=False, default="0")

    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        server_default=func.now(),
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=True,
        onupdate=datetime.utcnow,
    )

    def __repr__(self) -> str:
        return f"<GhostIntegration {self.id} org={self.organization_id} url={self.ghost_url[:50]}>"
