"""
Coalition models for tracking members, content, and revenue.
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, Index
from sqlalchemy.sql import func

from app.core.database import Base


class CoalitionMember(Base):
    """Coalition member information."""
    __tablename__ = "coalition_members"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    status = Column(String, default="active")  # active, inactive, suspended
    joined_date = Column(DateTime(timezone=True), server_default=func.now())
    total_documents = Column(Integer, default=0)
    total_verifications = Column(Integer, default=0)
    total_earned = Column(Float, default=0.0)
    pending_payout = Column(Float, default=0.0)
    last_payout_date = Column(DateTime(timezone=True), nullable=True)
    next_payout_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship to user
    # user = relationship("User", back_populates="coalition_member")

    __table_args__ = (
        Index('idx_coalition_member_user', 'user_id'),
        Index('idx_coalition_member_status', 'status'),
    )


class ContentItem(Base):
    """Signed content items tracked for coalition members."""
    __tablename__ = "content_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    content_type = Column(String)  # document, image, video, etc.
    word_count = Column(Integer, default=0)
    file_path = Column(Text, nullable=True)
    c2pa_manifest_url = Column(Text, nullable=True)
    verification_count = Column(Integer, default=0)
    access_count = Column(Integer, default=0)
    revenue_generated = Column(Float, default=0.0)
    signed_at = Column(DateTime(timezone=True), server_default=func.now())
    last_accessed = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index('idx_content_user', 'user_id'),
        Index('idx_content_type', 'content_type'),
        Index('idx_content_signed', 'signed_at'),
    )


class RevenueTransaction(Base):
    """Revenue transactions for coalition members."""
    __tablename__ = "revenue_transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content_id = Column(Integer, ForeignKey("content_items.id"), nullable=True)
    amount = Column(Float, nullable=False)
    transaction_type = Column(String)  # earned, paid, adjustment
    status = Column(String)  # pending, completed, cancelled
    description = Column(Text, nullable=True)
    period_start = Column(DateTime(timezone=True), nullable=True)
    period_end = Column(DateTime(timezone=True), nullable=True)
    paid_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index('idx_revenue_user', 'user_id'),
        Index('idx_revenue_type', 'transaction_type'),
        Index('idx_revenue_status', 'status'),
        Index('idx_revenue_created', 'created_at'),
    )


class ContentAccessLog(Base):
    """Logs of AI companies accessing coalition member content."""
    __tablename__ = "content_access_logs"

    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(Integer, ForeignKey("content_items.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    ai_company = Column(String, nullable=False)  # OpenAI, Anthropic, Google, etc.
    access_type = Column(String)  # view, download, verify, license
    ip_address = Column(String, nullable=True)
    user_agent = Column(Text, nullable=True)
    revenue_amount = Column(Float, default=0.0)
    accessed_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('idx_access_content', 'content_id'),
        Index('idx_access_user', 'user_id'),
        Index('idx_access_company', 'ai_company'),
        Index('idx_access_date', 'accessed_at'),
    )
