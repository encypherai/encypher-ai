"""
Batch request persistence models for bulk signing and verification.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Optional

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base
from app.models.c2pa_template import JSONType

DEFAULT_RETENTION_DAYS = 30


class BatchRequestType(str, Enum):
    """Enumerates supported batch request types."""

    SIGN = "sign"
    VERIFY = "verify"

    def __str__(self):
        return self.value


class BatchStatus(str, Enum):
    """Lifecycle states for a batch request."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"


class BatchItemStatus(str, Enum):
    """Lifecycle state for individual items."""

    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


class BatchRequest(Base):
    """ORM model for persisted batch requests."""

    __tablename__ = "batch_requests"
    __table_args__ = (
        UniqueConstraint("organization_id", "idempotency_key", name="uq_batch_request_org_idempotent"),
        Index("ix_batch_requests_org_status", "organization_id", "status"),
        Index("ix_batch_requests_expires_at", "expires_at"),
    )
    RETENTION_DAYS = DEFAULT_RETENTION_DAYS

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(String(255), nullable=False)
    api_key_id = Column(String(64), nullable=True)
    request_type = Column(String(16), nullable=False)
    mode = Column(String(32), nullable=False)
    segmentation_level = Column(String(32), nullable=True)
    idempotency_key = Column(String(128), nullable=False)
    payload_hash = Column(String(64), nullable=False)
    status = Column(
        String(16),
        nullable=False,
        default="pending",
    )
    item_count = Column(Integer, nullable=False)
    success_count = Column(Integer, nullable=False, default=0)
    failure_count = Column(Integer, nullable=False, default=0)
    error_code = Column(String(64), nullable=True)
    error_message = Column(Text, nullable=True)
    request_metadata = Column(JSONType, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)

    items = relationship("BatchItem", back_populates="batch_request", cascade="all, delete-orphan")

    @staticmethod
    def default_expiry(now: Optional[datetime] = None) -> datetime:
        """Return the default expiration timestamp for batch records."""

        base = now or datetime.now(timezone.utc)
        return base + timedelta(days=DEFAULT_RETENTION_DAYS)


class BatchItem(Base):
    """ORM model for persisted batch results."""

    __tablename__ = "batch_items"
    __table_args__ = (Index("ix_batch_items_document_status", "document_id", "status"),)

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    batch_request_id = Column(
        String(36),
        ForeignKey("batch_requests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    document_id = Column(String(255), nullable=False)
    status = Column(
        String(16),
        nullable=False,
        default="pending",
    )
    mode = Column(String(32), nullable=False)
    duration_ms = Column(Integer, nullable=True)
    error_code = Column(String(64), nullable=True)
    error_message = Column(Text, nullable=True)
    statistics = Column(JSONType, nullable=True)
    result_payload = Column(JSONType, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    batch_request = relationship("BatchRequest", back_populates="items")
