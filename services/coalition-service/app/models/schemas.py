"""
Pydantic schemas for Coalition Service API
"""

from pydantic import BaseModel, Field, UUID4
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal


# Coalition Member Schemas
class CoalitionJoinRequest(BaseModel):
    """Request to join coalition"""

    user_id: UUID4
    organization_id: Optional[UUID4] = None
    tier: str = Field(..., pattern="^(free|pro|enterprise)$")
    accept_terms: bool = True


class CoalitionMemberResponse(BaseModel):
    """Coalition member response"""

    member_id: UUID4
    user_id: UUID4
    organization_id: Optional[UUID4] = None
    joined_at: datetime
    status: str
    tier: str

    class Config:
        from_attributes = True


class CoalitionLeaveRequest(BaseModel):
    """Request to leave coalition"""

    user_id: UUID4
    reason: Optional[str] = None


# Coalition Stats Schemas
class ContentStats(BaseModel):
    """Content statistics"""

    total_documents: int
    total_word_count: int
    verification_count: int
    last_signed: Optional[datetime] = None


class RevenueStats(BaseModel):
    """Revenue statistics"""

    total_earned: Decimal
    pending: Decimal
    paid: Decimal
    currency: str = "USD"
    next_payout_date: Optional[date] = None


class CoalitionStats(BaseModel):
    """Overall coalition statistics"""

    total_members: int
    total_content_pool: int
    active_agreements: int


class CoalitionStatsResponse(BaseModel):
    """Complete coalition stats response"""

    member_id: UUID4
    status: str
    joined_at: datetime
    content_stats: ContentStats
    revenue_stats: RevenueStats
    coalition_stats: CoalitionStats


# Revenue Schemas
class RevenueDistributionDetail(BaseModel):
    """Revenue distribution detail"""

    period: str
    amount: Decimal
    status: str
    agreement_name: Optional[str] = None
    content_accessed: Optional[int] = None
    access_count: Optional[int] = None
    paid_at: Optional[datetime] = None
    payment_method: Optional[str] = None
    payment_reference: Optional[str] = None


class RevenueResponse(BaseModel):
    """Revenue breakdown response"""

    total_earned: Decimal
    currency: str = "USD"
    distributions: List[RevenueDistributionDetail]


# Licensing Agreement Schemas
class LicensingAgreementCreate(BaseModel):
    """Create licensing agreement"""

    agreement_name: str
    ai_company_name: str
    ai_company_id: Optional[str] = None
    agreement_type: str = Field(..., pattern="^(bulk_access|per_document|subscription)$")
    total_value: Decimal
    currency: str = "USD"
    payment_frequency: Optional[str] = Field(None, pattern="^(monthly|quarterly|annual|one_time)$")
    content_types: Optional[List[str]] = None
    min_word_count: Optional[int] = None
    date_range_start: Optional[date] = None
    date_range_end: Optional[date] = None
    start_date: date
    end_date: date
    signed_date: Optional[date] = None
    created_by: Optional[UUID4] = None


class LicensingAgreementResponse(BaseModel):
    """Licensing agreement response"""

    id: UUID4
    agreement_name: str
    ai_company_name: str
    ai_company_id: Optional[str]
    agreement_type: str
    status: str
    total_value: Decimal
    currency: str
    payment_frequency: Optional[str]
    content_types: Optional[List[str]]
    min_word_count: Optional[int]
    date_range_start: Optional[date]
    date_range_end: Optional[date]
    start_date: date
    end_date: date
    signed_date: Optional[date]
    created_by: Optional[UUID4]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class LicensingAgreementUpdate(BaseModel):
    """Update licensing agreement"""

    agreement_name: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(draft|active|expired|terminated)$")
    total_value: Optional[Decimal] = None
    payment_frequency: Optional[str] = None
    signed_date: Optional[date] = None


# Content Access Schemas
class ContentAccessTrack(BaseModel):
    """Track content access by AI company"""

    agreement_id: UUID4
    content_id: UUID4
    member_id: UUID4
    access_type: Optional[str] = Field(None, pattern="^(training|inference|verification)$")
    ai_company_name: str
    metadata: Optional[dict] = None


class ContentAccessResponse(BaseModel):
    """Content access log response"""

    id: UUID4
    agreement_id: UUID4
    content_id: UUID4
    member_id: UUID4
    accessed_at: datetime
    access_type: Optional[str]
    ai_company_name: str
    metadata: Optional[dict]

    class Config:
        from_attributes = True


# Coalition Content Schemas
class CoalitionContentCreate(BaseModel):
    """Index content for coalition"""

    member_id: UUID4
    document_id: UUID4
    content_hash: str
    content_type: Optional[str] = None
    word_count: Optional[int] = None
    signed_at: datetime


class CoalitionContentResponse(BaseModel):
    """Coalition content response"""

    id: UUID4
    member_id: UUID4
    document_id: UUID4
    content_hash: str
    content_type: Optional[str]
    word_count: Optional[int]
    signed_at: datetime
    verification_count: int
    last_verified_at: Optional[datetime]
    indexed_at: datetime

    class Config:
        from_attributes = True


# Settings Schemas
class CoalitionSettingCreate(BaseModel):
    """Create or update coalition setting"""

    setting_key: str
    setting_value: dict
    description: Optional[str] = None


class CoalitionSettingResponse(BaseModel):
    """Coalition setting response"""

    id: UUID4
    setting_key: str
    setting_value: dict
    description: Optional[str]
    updated_at: datetime

    class Config:
        from_attributes = True


# Generic Response Wrappers
class SuccessResponse(BaseModel):
    """Generic success response"""

    success: bool = True
    message: Optional[str] = None
    data: Optional[dict] = None


class ErrorResponse(BaseModel):
    """Generic error response"""

    success: bool = False
    error: str
    detail: Optional[str] = None
