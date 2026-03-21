"""
Usage record model for metering and overage billing.

Maps to the usage_records table created by migration 20251125_150700.
"""

from datetime import datetime

from sqlalchemy import BigInteger, Boolean, Column, Integer, String
from sqlalchemy import TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB

from app.database import Base


class UsageRecord(Base):
    """
    Usage record for tracking billable usage metrics per organization per period.

    Each record represents usage of a specific metric (e.g. c2pa_signatures)
    for a billing period, with overage tracking for automated billing.
    """

    __tablename__ = "usage_records"
    __table_args__ = {"extend_existing": True}

    id = Column(String(32), primary_key=True)
    organization_id = Column(String(64), nullable=False, index=True)

    # Usage metric
    metric = Column(String(64), nullable=False)  # c2pa_signatures, api_calls, etc.
    count = Column(BigInteger, nullable=False, default=0)
    unit = Column(String(32), nullable=True)  # documents, sentences, calls, operations

    # Time period
    period_start = Column(TIMESTAMP(timezone=True), nullable=False)
    period_end = Column(TIMESTAMP(timezone=True), nullable=False)
    period_type = Column(String(16), nullable=False, default="monthly")

    # Billing info
    billable = Column(Boolean, nullable=False, default=True)
    billed = Column(Boolean, nullable=False, default=False)
    invoice_id = Column(String(64), nullable=True)

    # Rate info (for overage billing)
    rate_cents = Column(Integer, nullable=True)
    included_in_plan = Column(BigInteger, nullable=True)
    overage_count = Column(BigInteger, nullable=True)
    overage_amount_cents = Column(BigInteger, nullable=True)

    # Metadata
    metadata_ = Column("metadata", JSONB, nullable=True)
    recorded_at = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<UsageRecord(id={self.id}, org={self.organization_id}, metric={self.metric}, count={self.count}, overage={self.overage_count})>"
