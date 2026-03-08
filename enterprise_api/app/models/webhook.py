"""
Webhook model for event notifications.

Stores webhook configurations for organizations to receive event notifications.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from app.database import Base
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, LargeBinary, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.sql import func


class WebhookEvent(str, Enum):
    """Available webhook events."""

    DOCUMENT_SIGNED = "document.signed"
    DOCUMENT_VERIFIED = "document.verified"
    DOCUMENT_REVOKED = "document.revoked"
    DOCUMENT_REINSTATED = "document.reinstated"
    QUOTA_WARNING = "quota.warning"
    QUOTA_EXCEEDED = "quota.exceeded"
    KEY_CREATED = "key.created"
    KEY_REVOKED = "key.revoked"
    KEY_ROTATED = "key.rotated"
    RIGHTS_PROFILE_UPDATED = "rights.profile.updated"
    RIGHTS_NOTICE_DELIVERED = "rights.notice.delivered"
    RIGHTS_LICENSING_REQUEST_RECEIVED = "rights.licensing.request_received"
    RIGHTS_LICENSING_AGREEMENT_CREATED = "rights.licensing.agreement_created"
    RIGHTS_DETECTION_EVENT = "rights.detection.event"


class Webhook(Base):
    """
    Webhook configuration for an organization.

    Organizations can register webhooks to receive notifications
    when certain events occur (document signed, revoked, etc.).
    """

    __tablename__ = "webhooks"

    id = Column(String(64), primary_key=True)
    organization_id = Column(
        String(64),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Webhook configuration
    url = Column(String(2048), nullable=False)
    events = Column(ARRAY(String), nullable=False, default=[])
    secret_hash = Column(String(128), nullable=True)  # Hashed shared secret for HMAC
    secret_encrypted = Column(LargeBinary, nullable=True)

    # Status
    is_active = Column(Boolean, nullable=False, default=True)
    is_verified = Column(Boolean, nullable=False, default=False)

    # Delivery stats
    success_count = Column(Integer, nullable=False, default=0)
    failure_count = Column(Integer, nullable=False, default=0)
    last_triggered_at = Column(DateTime(timezone=True), nullable=True)
    last_success_at = Column(DateTime(timezone=True), nullable=True)
    last_failure_at = Column(DateTime(timezone=True), nullable=True)
    last_failure_reason = Column(Text, nullable=True)

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
        return f"<Webhook {self.id} org={self.organization_id} url={self.url[:50]}...>"


class WebhookDelivery(Base):
    """
    Record of a webhook delivery attempt.

    Stores the payload, response, and status for debugging and retry purposes.
    """

    __tablename__ = "webhook_deliveries"

    id = Column(String(64), primary_key=True)
    webhook_id = Column(
        String(64),
        ForeignKey("webhooks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    organization_id = Column(String(64), nullable=False, index=True)

    # Event details
    event_type = Column(String(64), nullable=False, index=True)
    event_id = Column(String(64), nullable=False)  # Unique event ID for idempotency
    payload = Column(JSONB, nullable=False)

    # Delivery status
    status = Column(String(32), nullable=False, default="pending")  # pending, success, failed
    attempts = Column(Integer, nullable=False, default=0)
    max_attempts = Column(Integer, nullable=False, default=3)

    # Response details
    response_status_code = Column(Integer, nullable=True)
    response_body = Column(Text, nullable=True)
    response_time_ms = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        server_default=func.now(),
    )
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    next_retry_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return f"<WebhookDelivery {self.id} event={self.event_type} status={self.status}>"
