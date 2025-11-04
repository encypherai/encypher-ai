"""
Database models for Coalition Service
"""
import uuid
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    Text,
    Date,
    ARRAY,
    DECIMAL,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from .session import Base


class CoalitionMember(Base):
    """Coalition member model"""

    __tablename__ = "coalition_members"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, unique=True, index=True)
    organization_id = Column(UUID(as_uuid=True), nullable=True)
    joined_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    status = Column(String(20), nullable=False, default="active", index=True)  # active, opted_out
    tier = Column(String(20), nullable=False, index=True)  # free, pro, enterprise
    opt_out_reason = Column(Text, nullable=True)
    opted_out_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)

    # Relationships
    content = relationship("CoalitionContent", back_populates="member")
    revenue = relationship("MemberRevenue", back_populates="member")


class CoalitionContent(Base):
    """Coalition content (aggregated signed content)"""

    __tablename__ = "coalition_content"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    member_id = Column(UUID(as_uuid=True), ForeignKey("coalition_members.id"), nullable=False, index=True)
    document_id = Column(UUID(as_uuid=True), nullable=False, unique=True, index=True)
    content_hash = Column(String(64), nullable=False, index=True)
    content_type = Column(String(50), nullable=True)  # article, blog, social_post
    word_count = Column(Integer, nullable=True)
    signed_at = Column(DateTime, nullable=False, index=True)
    verification_count = Column(Integer, default=0)
    last_verified_at = Column(DateTime, nullable=True)
    indexed_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    member = relationship("CoalitionMember", back_populates="content")
    access_logs = relationship("ContentAccessLog", back_populates="content")


class LicensingAgreement(Base):
    """Licensing agreements with AI companies"""

    __tablename__ = "licensing_agreements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agreement_name = Column(String(255), nullable=False)
    ai_company_name = Column(String(255), nullable=False, index=True)
    ai_company_id = Column(String(255), nullable=True)  # External ID
    agreement_type = Column(String(50), nullable=False)  # bulk_access, per_document, subscription
    status = Column(String(20), nullable=False, default="draft", index=True)  # draft, active, expired, terminated

    # Financial terms
    total_value = Column(DECIMAL(12, 2), nullable=False)
    currency = Column(String(3), default="USD")
    payment_frequency = Column(String(20), nullable=True)  # monthly, quarterly, annual, one_time

    # Content scope
    content_types = Column(ARRAY(Text), nullable=True)  # ['article', 'blog']
    min_word_count = Column(Integer, nullable=True)
    date_range_start = Column(Date, nullable=True)
    date_range_end = Column(Date, nullable=True)

    # Dates
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    signed_date = Column(Date, nullable=True)

    # Metadata
    created_by = Column(UUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)

    # Relationships
    access_logs = relationship("ContentAccessLog", back_populates="agreement")
    distributions = relationship("RevenueDistribution", back_populates="agreement")


class ContentAccessLog(Base):
    """Content access tracking (AI company usage)"""

    __tablename__ = "content_access_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agreement_id = Column(UUID(as_uuid=True), ForeignKey("licensing_agreements.id"), nullable=False, index=True)
    content_id = Column(UUID(as_uuid=True), ForeignKey("coalition_content.id"), nullable=False, index=True)
    member_id = Column(UUID(as_uuid=True), ForeignKey("coalition_members.id"), nullable=False, index=True)
    accessed_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    access_type = Column(String(50), nullable=True)  # training, inference, verification
    ai_company_name = Column(String(255), nullable=False)
    metadata = Column(JSONB, nullable=True)

    # Relationships
    agreement = relationship("LicensingAgreement", back_populates="access_logs")
    content = relationship("CoalitionContent", back_populates="access_logs")


class RevenueDistribution(Base):
    """Revenue distribution calculations"""

    __tablename__ = "revenue_distributions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agreement_id = Column(UUID(as_uuid=True), ForeignKey("licensing_agreements.id"), nullable=False, index=True)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    total_revenue = Column(DECIMAL(12, 2), nullable=False)
    encypher_share = Column(DECIMAL(12, 2), nullable=False)  # 30%
    member_pool = Column(DECIMAL(12, 2), nullable=False)  # 70%

    # Distribution calculation
    total_content_count = Column(Integer, nullable=False)
    total_access_count = Column(Integer, nullable=False)
    calculation_method = Column(String(50), nullable=True)  # equal_split, usage_based, weighted

    # Status
    status = Column(String(20), nullable=False, default="pending", index=True)  # pending, calculated, paid
    calculated_at = Column(DateTime, nullable=True)
    paid_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    agreement = relationship("LicensingAgreement", back_populates="distributions")
    member_revenues = relationship("MemberRevenue", back_populates="distribution")


class MemberRevenue(Base):
    """Individual member revenue (payouts)"""

    __tablename__ = "member_revenue"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    distribution_id = Column(UUID(as_uuid=True), ForeignKey("revenue_distributions.id"), nullable=False, index=True)
    member_id = Column(UUID(as_uuid=True), ForeignKey("coalition_members.id"), nullable=False, index=True)

    # Content contribution
    content_count = Column(Integer, nullable=False)
    access_count = Column(Integer, nullable=False)
    contribution_percentage = Column(DECIMAL(5, 2), nullable=False)

    # Revenue
    revenue_amount = Column(DECIMAL(12, 2), nullable=False)
    currency = Column(String(3), default="USD")

    # Payment
    status = Column(String(20), nullable=False, default="pending", index=True)  # pending, paid, failed
    payment_method = Column(String(50), nullable=True)
    payment_reference = Column(String(255), nullable=True)
    paid_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    distribution = relationship("RevenueDistribution", back_populates="member_revenues")
    member = relationship("CoalitionMember", back_populates="revenue")


class CoalitionSettings(Base):
    """Coalition settings and configuration"""

    __tablename__ = "coalition_settings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    setting_key = Column(String(100), nullable=False, unique=True, index=True)
    setting_value = Column(JSONB, nullable=False)
    description = Column(Text, nullable=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
