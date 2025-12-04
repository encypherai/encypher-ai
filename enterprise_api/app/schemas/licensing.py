"""
Pydantic schemas for Licensing Agreement Management API.

Request and response models for licensing endpoints.
"""
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, validator

from app.models.licensing import AgreementStatus, AgreementType, DistributionStatus, PayoutStatus

# ============================================================================
# AI Company Schemas
# ============================================================================

class AICompanyBase(BaseModel):
    """Base schema for AI company."""
    company_name: str = Field(..., min_length=1, max_length=255)
    company_email: EmailStr


class AICompanyCreate(AICompanyBase):
    """Schema for creating AI company (internal use)."""
    pass


class AICompanyResponse(AICompanyBase):
    """Schema for AI company response."""
    id: UUID
    api_key_prefix: str
    status: AgreementStatus
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Licensing Agreement Schemas
# ============================================================================

class LicensingAgreementCreate(BaseModel):
    """Schema for creating a licensing agreement."""
    agreement_name: str = Field(..., min_length=1, max_length=255)
    ai_company_name: str = Field(..., min_length=1, max_length=255)
    ai_company_email: EmailStr
    agreement_type: AgreementType = AgreementType.SUBSCRIPTION
    total_value: Decimal = Field(..., gt=0, decimal_places=2)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    start_date: date
    end_date: date
    content_types: Optional[List[str]] = None
    min_word_count: Optional[int] = Field(None, ge=0)

    @validator('end_date')
    def end_date_after_start_date(cls, v, values):
        """Validate that end_date is after start_date."""
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('end_date must be after start_date')
        return v


class LicensingAgreementUpdate(BaseModel):
    """Schema for updating a licensing agreement."""
    agreement_name: Optional[str] = Field(None, min_length=1, max_length=255)
    total_value: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    end_date: Optional[date] = None
    content_types: Optional[List[str]] = None
    min_word_count: Optional[int] = Field(None, ge=0)
    status: Optional[AgreementStatus] = None


class LicensingAgreementResponse(BaseModel):
    """Schema for licensing agreement response."""
    id: UUID
    agreement_name: str
    ai_company_id: UUID
    agreement_type: AgreementType
    total_value: Decimal
    currency: str
    start_date: date
    end_date: date
    content_types: Optional[List[str]]
    min_word_count: Optional[int]
    status: AgreementStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LicensingAgreementCreateResponse(BaseModel):
    """Schema for licensing agreement creation response (includes API key)."""
    id: UUID
    agreement_name: str
    api_key: str  # Only shown once during creation
    api_key_prefix: str
    status: AgreementStatus
    created_at: datetime


# ============================================================================
# Content Access Schemas
# ============================================================================

class ContentMetadata(BaseModel):
    """Schema for content metadata returned to AI companies."""
    id: int  # ContentReference uses BigInteger ref_id
    content_type: str
    word_count: Optional[int]
    signed_at: datetime
    content_hash: str
    verification_url: str


class ContentListResponse(BaseModel):
    """Schema for listing available content."""
    content: List[ContentMetadata]
    total: int
    quota_remaining: Optional[int] = None


class ContentAccessTrack(BaseModel):
    """Schema for tracking content access."""
    content_id: int  # ContentReference uses BigInteger ref_id
    access_type: Optional[str] = "view"


class ContentAccessLogResponse(BaseModel):
    """Schema for content access log response."""
    id: UUID
    agreement_id: UUID
    content_id: UUID
    member_id: UUID
    accessed_at: datetime
    access_type: Optional[str]
    ai_company_name: str

    class Config:
        from_attributes = True


# ============================================================================
# Revenue Distribution Schemas
# ============================================================================

class RevenueDistributionCreate(BaseModel):
    """Schema for creating a revenue distribution."""
    agreement_id: UUID
    period_start: date
    period_end: date

    @validator('period_end')
    def period_end_after_start(cls, v, values):
        """Validate that period_end is after period_start."""
        if 'period_start' in values and v <= values['period_start']:
            raise ValueError('period_end must be after period_start')
        return v


class MemberRevenueDetail(BaseModel):
    """Schema for member revenue detail."""
    id: UUID
    member_id: UUID
    content_count: int
    access_count: int
    revenue_amount: Decimal
    status: PayoutStatus
    paid_at: Optional[datetime]
    payment_reference: Optional[str]

    class Config:
        from_attributes = True


class RevenueDistributionResponse(BaseModel):
    """Schema for revenue distribution response."""
    id: UUID
    agreement_id: UUID
    period_start: date
    period_end: date
    total_revenue: Decimal
    encypher_share: Decimal
    member_pool: Decimal
    status: DistributionStatus
    created_at: datetime
    processed_at: Optional[datetime]
    member_revenues: Optional[List[MemberRevenueDetail]] = None

    class Config:
        from_attributes = True


class PayoutCreate(BaseModel):
    """Schema for processing payouts."""
    distribution_id: UUID
    payment_method: str = "stripe"  # stripe, bank_transfer, etc.


class PayoutResponse(BaseModel):
    """Schema for payout response."""
    distribution_id: UUID
    total_members_paid: int
    total_amount_paid: Decimal
    failed_payments: List[UUID] = []


# ============================================================================
# Generic API Response Schemas
# ============================================================================

class SuccessResponse(BaseModel):
    """Generic success response."""
    success: bool = True
    message: Optional[str] = None


class ErrorResponse(BaseModel):
    """Generic error response."""
    success: bool = False
    error: dict


class PaginationParams(BaseModel):
    """Schema for pagination parameters."""
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)


class ContentFilterParams(PaginationParams):
    """Schema for content filtering parameters."""
    content_type: Optional[str] = None
    min_word_count: Optional[int] = Field(None, ge=0)
