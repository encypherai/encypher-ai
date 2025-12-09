"""
Coalition schemas for API request/response models.
"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


# Coalition Member Schemas
class CoalitionMemberBase(BaseModel):
    """Base coalition member schema."""
    status: str = "active"


class CoalitionMemberCreate(CoalitionMemberBase):
    """Schema for creating a coalition member."""
    user_id: int


class CoalitionMemberUpdate(BaseModel):
    """Schema for updating a coalition member."""
    status: Optional[str] = None
    pending_payout: Optional[float] = None


class CoalitionMember(CoalitionMemberBase):
    """Coalition member response schema."""
    id: int
    user_id: int
    joined_date: datetime
    total_documents: int
    total_verifications: int
    total_earned: float
    pending_payout: float
    last_payout_date: Optional[datetime] = None
    next_payout_date: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Content Item Schemas
class ContentItemBase(BaseModel):
    """Base content item schema."""
    title: str
    content_type: str
    word_count: int = 0


class ContentItemCreate(ContentItemBase):
    """Schema for creating a content item."""
    user_id: int
    file_path: Optional[str] = None
    c2pa_manifest_url: Optional[str] = None


class ContentItem(ContentItemBase):
    """Content item response schema."""
    id: int
    user_id: int
    file_path: Optional[str] = None
    c2pa_manifest_url: Optional[str] = None
    verification_count: int
    access_count: int
    revenue_generated: float
    signed_at: datetime
    last_accessed: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Revenue Transaction Schemas
class RevenueTransactionBase(BaseModel):
    """Base revenue transaction schema."""
    amount: float
    transaction_type: str  # earned, paid, adjustment
    status: str = "pending"
    description: Optional[str] = None


class RevenueTransactionCreate(RevenueTransactionBase):
    """Schema for creating a revenue transaction."""
    user_id: int
    content_id: Optional[int] = None
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None


class RevenueTransaction(RevenueTransactionBase):
    """Revenue transaction response schema."""
    id: int
    user_id: int
    content_id: Optional[int] = None
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    paid_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Content Access Log Schemas
class ContentAccessLogBase(BaseModel):
    """Base content access log schema."""
    ai_company: str
    access_type: str
    revenue_amount: float = 0.0


class ContentAccessLogCreate(ContentAccessLogBase):
    """Schema for creating a content access log."""
    content_id: int
    user_id: int
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class ContentAccessLog(ContentAccessLogBase):
    """Content access log response schema."""
    id: int
    content_id: int
    user_id: int
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    accessed_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# Coalition Stats Schemas
class ContentStats(BaseModel):
    """Content statistics schema."""
    total_documents: int
    verification_count: int
    recent_documents: int  # Last 30 days
    trend_percentage: float  # Month over month


class RevenueStats(BaseModel):
    """Revenue statistics schema."""
    total_earned: float
    pending: float
    paid: float
    next_payout_date: Optional[datetime] = None
    monthly_average: float


class RevenueHistoryItem(BaseModel):
    """Revenue history item schema."""
    month: str
    earned: float
    paid: float


class TopContentItem(BaseModel):
    """Top performing content item schema."""
    id: int
    title: str
    content_type: str
    word_count: int
    verification_count: int
    access_count: int
    revenue_generated: float


class RecentAccessItem(BaseModel):
    """Recent content access item schema."""
    id: int
    ai_company: str
    content_title: str
    access_type: str
    accessed_at: datetime
    revenue_amount: float


class CoalitionStats(BaseModel):
    """Coalition dashboard statistics."""
    content_stats: ContentStats
    revenue_stats: RevenueStats
    revenue_history: List[RevenueHistoryItem]
    top_content: List[TopContentItem]
    recent_access: List[RecentAccessItem]


# Admin Schemas
class AdminCoalitionOverview(BaseModel):
    """Admin coalition overview statistics."""
    total_members: int
    active_members: int
    total_content: int
    total_revenue_mtd: float
    total_verifications: int


class MemberListItem(BaseModel):
    """Member list item for admin view."""
    id: int
    user_id: int
    email: str
    full_name: str
    status: str
    total_documents: int
    total_verifications: int
    total_earned: float
    pending_payout: float
    joined_date: datetime


class MemberListResponse(BaseModel):
    """Response schema for member list."""
    items: List[MemberListItem]
    total: int
    page: int
    limit: int
