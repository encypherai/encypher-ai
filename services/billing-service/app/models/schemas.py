"""Pydantic schemas for Billing Service"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class SubscriptionCreate(BaseModel):
    """Schema for creating a subscription"""
    plan_id: str
    billing_cycle: str = Field(pattern="^(monthly|yearly)$")


class SubscriptionResponse(BaseModel):
    """Schema for subscription response"""
    id: str
    user_id: str
    plan_id: str
    plan_name: str
    status: str
    billing_cycle: str
    amount: float
    currency: str
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class SubscriptionUpdate(BaseModel):
    """Schema for updating subscription"""
    plan_id: Optional[str] = None
    billing_cycle: Optional[str] = None


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
