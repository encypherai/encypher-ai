"""
Licensing Agreement Management Models.

Database models for managing licensing agreements with AI companies,
tracking content access, and revenue distribution.
"""
from enum import Enum
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import (
    Column, String, Integer, TIMESTAMP, Enum as SQLEnum,
    DECIMAL, DATE, ForeignKey, ARRAY
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.database import Base


class AgreementStatus(str, Enum):
    """Licensing agreement status."""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"
    EXPIRED = "expired"


class AgreementType(str, Enum):
    """Type of licensing agreement."""
    SUBSCRIPTION = "subscription"
    ONE_TIME = "one_time"
    USAGE_BASED = "usage_based"


class DistributionStatus(str, Enum):
    """Revenue distribution status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class PayoutStatus(str, Enum):
    """Member payout status."""
    PENDING = "pending"
    PROCESSING = "processing"
    PAID = "paid"
    FAILED = "failed"


class AICompany(Base):
    """
    AI Company profile with API key authentication.

    Represents an AI company that has licensing agreements with Encypher.
    """
    __tablename__ = "ai_companies"
    __table_args__ = {'extend_existing': True}

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Company details
    company_name = Column(String(255), nullable=False, unique=True)
    company_email = Column(String(255), nullable=False)

    # API key authentication
    api_key_hash = Column(String(255), nullable=False, unique=True)
    api_key_prefix = Column(String(20), nullable=False)  # For display (e.g., "lic_abc1")

    # Status
    status = Column(
        SQLEnum(AgreementStatus),
        nullable=False,
        default=AgreementStatus.ACTIVE
    )

    # Timestamps
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    agreements = relationship("LicensingAgreement", back_populates="ai_company")

    def __repr__(self):
        return f"<AICompany(id={self.id}, name={self.company_name}, status={self.status.value})>"


class LicensingAgreement(Base):
    """
    Licensing agreement between Encypher and an AI company.

    Defines terms, pricing, content types, and duration of the agreement.
    """
    __tablename__ = "licensing_agreements"
    __table_args__ = {'extend_existing': True}

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Agreement details
    agreement_name = Column(String(255), nullable=False)
    ai_company_id = Column(UUID(as_uuid=True), ForeignKey("ai_companies.id"), nullable=False)

    # Agreement type and pricing
    agreement_type = Column(
        SQLEnum(AgreementType),
        nullable=False,
        default=AgreementType.SUBSCRIPTION
    )
    total_value = Column(DECIMAL(12, 2), nullable=False)
    currency = Column(String(3), nullable=False, default="USD")

    # Duration
    start_date = Column(DATE, nullable=False)
    end_date = Column(DATE, nullable=False)

    # Content filters
    content_types = Column(ARRAY(String), nullable=True)  # e.g., ["article", "blog"]
    min_word_count = Column(Integer, nullable=True)

    # Status
    status = Column(
        SQLEnum(AgreementStatus),
        nullable=False,
        default=AgreementStatus.ACTIVE
    )

    # Timestamps
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    ai_company = relationship("AICompany", back_populates="agreements")
    access_logs = relationship("ContentAccessLog", back_populates="agreement")
    distributions = relationship("RevenueDistribution", back_populates="agreement")

    def __repr__(self):
        return f"<LicensingAgreement(id={self.id}, name={self.agreement_name}, status={self.status.value})>"

    def is_active(self) -> bool:
        """Check if agreement is currently active."""
        today = date.today()
        return (
            self.status == AgreementStatus.ACTIVE and
            self.start_date <= today <= self.end_date
        )

    def get_monthly_value(self) -> Decimal:
        """Calculate monthly value of the agreement."""
        if self.agreement_type == AgreementType.SUBSCRIPTION:
            # Calculate number of months in agreement
            months = ((self.end_date.year - self.start_date.year) * 12 +
                     (self.end_date.month - self.start_date.month))
            if months == 0:
                months = 1
            return self.total_value / Decimal(months)
        return self.total_value


class ContentAccessLog(Base):
    """
    Log of content access by AI companies.

    Tracks when AI companies access content for revenue attribution.
    """
    __tablename__ = "content_access_logs"
    __table_args__ = {'extend_existing': True}

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # References
    agreement_id = Column(UUID(as_uuid=True), ForeignKey("licensing_agreements.id"), nullable=False)
    content_id = Column(UUID(as_uuid=True), nullable=False)  # References coalition_content.id
    member_id = Column(UUID(as_uuid=True), nullable=False)   # References coalition_members.id

    # Access details
    accessed_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    access_type = Column(String(50), nullable=True)  # e.g., "view", "download", "train"
    ai_company_name = Column(String(255), nullable=False)

    # Relationships
    agreement = relationship("LicensingAgreement", back_populates="access_logs")

    def __repr__(self):
        return f"<ContentAccessLog(id={self.id}, content_id={self.content_id}, accessed_at={self.accessed_at})>"


class RevenueDistribution(Base):
    """
    Revenue distribution for a specific period.

    Tracks how revenue is distributed between Encypher and coalition members.
    """
    __tablename__ = "revenue_distributions"
    __table_args__ = {'extend_existing': True}

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # References
    agreement_id = Column(UUID(as_uuid=True), ForeignKey("licensing_agreements.id"), nullable=False)

    # Period
    period_start = Column(DATE, nullable=False)
    period_end = Column(DATE, nullable=False)

    # Revenue breakdown
    total_revenue = Column(DECIMAL(12, 2), nullable=False)
    encypher_share = Column(DECIMAL(12, 2), nullable=False)  # 30%
    member_pool = Column(DECIMAL(12, 2), nullable=False)     # 70%

    # Status
    status = Column(
        SQLEnum(DistributionStatus),
        nullable=False,
        default=DistributionStatus.PENDING
    )

    # Timestamps
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    processed_at = Column(TIMESTAMP, nullable=True)

    # Relationships
    agreement = relationship("LicensingAgreement", back_populates="distributions")
    member_revenues = relationship("MemberRevenue", back_populates="distribution")

    def __repr__(self):
        return f"<RevenueDistribution(id={self.id}, period={self.period_start} to {self.period_end}, status={self.status.value})>"


class MemberRevenue(Base):
    """
    Individual member revenue from a distribution period.

    Tracks revenue owed to each coalition member based on content usage.
    """
    __tablename__ = "member_revenue"
    __table_args__ = {'extend_existing': True}

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # References
    distribution_id = Column(UUID(as_uuid=True), ForeignKey("revenue_distributions.id"), nullable=False)
    member_id = Column(UUID(as_uuid=True), nullable=False)  # References coalition_members.id

    # Contribution metrics
    content_count = Column(Integer, nullable=False, default=0)
    access_count = Column(Integer, nullable=False, default=0)

    # Revenue
    revenue_amount = Column(DECIMAL(12, 2), nullable=False)

    # Status
    status = Column(
        SQLEnum(PayoutStatus),
        nullable=False,
        default=PayoutStatus.PENDING
    )

    # Payment details
    paid_at = Column(TIMESTAMP, nullable=True)
    payment_reference = Column(String(255), nullable=True)  # Stripe payment ID, etc.

    # Timestamps
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    distribution = relationship("RevenueDistribution", back_populates="member_revenues")

    def __repr__(self):
        return f"<MemberRevenue(id={self.id}, member_id={self.member_id}, amount={self.revenue_amount}, status={self.status.value})>"
