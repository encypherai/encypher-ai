"""Pydantic schemas for Billing Service"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import datetime
from enum import Enum


class TierName(str, Enum):
    """Available subscription tiers"""
    STARTER = "starter"
    PROFESSIONAL = "professional"
    BUSINESS = "business"
    ENTERPRISE = "enterprise"
    STRATEGIC_PARTNER = "strategic_partner"


class PlanInfo(BaseModel):
    """Information about a subscription plan"""
    id: str
    name: str
    tier: TierName
    price_monthly: float
    price_annual: float
    features: List[str]
    limits: Dict[str, Any]
    coalition_rev_share: Dict[str, int]  # {"publisher": 65, "encypher": 35}
    enterprise: bool = False  # True for enterprise/custom pricing plans
    popular: bool = False  # True for the recommended plan


class SubscriptionCreate(BaseModel):
    """Schema for creating a subscription"""
    plan_id: str
    billing_cycle: str = Field(pattern="^(monthly|annual)$")


class SubscriptionResponse(BaseModel):
    """Schema for subscription response"""
    id: str
    user_id: str
    organization_id: Optional[str] = None
    plan_id: str
    plan_name: str
    tier: str
    status: str
    billing_cycle: str
    amount: float
    currency: str
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool
    created_at: datetime
    features: Optional[Dict[str, bool]] = None
    coalition_rev_share: Optional[Dict[str, int]] = None

    class Config:
        from_attributes = True


class SubscriptionUpdate(BaseModel):
    """Schema for updating subscription"""
    plan_id: Optional[str] = None
    billing_cycle: Optional[str] = None


class UsageMetric(BaseModel):
    """Single usage metric"""
    name: str
    limit: Any  # int or "unlimited"
    used: int
    remaining: Any  # int or "unlimited"
    percentage_used: float
    available: bool


class UsageResponse(BaseModel):
    """Current usage statistics"""
    organization_id: str
    tier: str
    period_start: datetime
    period_end: datetime
    metrics: Dict[str, UsageMetric]
    reset_date: datetime


class CoalitionEarnings(BaseModel):
    """Coalition earnings for a period"""
    period: str  # e.g., "2025-11"
    gross_revenue: float
    publisher_share: float
    encypher_share: float
    content_count: int
    access_count: int
    status: str  # pending, calculated, paid


class CoalitionSummary(BaseModel):
    """Coalition membership summary"""
    member: bool
    opted_out: bool
    publisher_share_percent: int
    encypher_share_percent: int
    total_content: int
    total_earnings: float
    pending_earnings: float
    last_payout_date: Optional[datetime] = None
    earnings_history: List[CoalitionEarnings] = []


class UpgradeRequest(BaseModel):
    """Request to upgrade subscription"""
    target_tier: TierName
    billing_cycle: str = Field(pattern="^(monthly|annual)$")


class UpgradeResponse(BaseModel):
    """Response for upgrade request"""
    success: bool
    checkout_url: Optional[str] = None  # Stripe checkout URL (when integrated)
    message: str
    new_tier: Optional[str] = None
    effective_date: Optional[datetime] = None


class InvoiceResponse(BaseModel):
    """Schema for invoice response"""
    id: str
    invoice_number: str
    status: str
    amount_due: float
    amount_paid: float
    currency: str
    period_start: datetime
    period_end: datetime
    due_date: Optional[datetime]
    paid_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class PaymentResponse(BaseModel):
    """Schema for payment response"""
    id: str
    invoice_id: str
    amount: float
    currency: str
    status: str
    payment_method: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class BillingStats(BaseModel):
    """Schema for billing statistics"""
    total_revenue: float
    monthly_recurring_revenue: float
    active_subscriptions: int
    canceled_subscriptions: int
    total_invoices: int
    paid_invoices: int
    unpaid_invoices: int


class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
