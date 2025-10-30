"""SQLAlchemy database models for Billing Service"""
from sqlalchemy import Column, String, Integer, DateTime, JSON, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()


def generate_uuid():
    return str(uuid.uuid4())


class Subscription(Base):
    """Subscription model"""
    __tablename__ = "subscriptions"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, nullable=False, index=True)
    organization_id = Column(String, nullable=True, index=True)
    
    plan_id = Column(String, nullable=False, index=True)
    plan_name = Column(String, nullable=False)
    status = Column(String, nullable=False, index=True)  # active, canceled, past_due, trialing
    
    billing_cycle = Column(String, nullable=False)  # monthly, yearly
    amount = Column(Float, nullable=False)
    currency = Column(String, nullable=False, default="usd")
    
    current_period_start = Column(DateTime(timezone=True), nullable=False)
    current_period_end = Column(DateTime(timezone=True), nullable=False)
    cancel_at_period_end = Column(Boolean, default=False)
    canceled_at = Column(DateTime(timezone=True), nullable=True)
    
    stripe_subscription_id = Column(String, nullable=True, unique=True)
    stripe_customer_id = Column(String, nullable=True)
    
    metadata = Column(JSON, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Subscription(id={self.id}, user_id={self.user_id}, plan={self.plan_name})>"


class Invoice(Base):
    """Invoice model"""
    __tablename__ = "invoices"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    subscription_id = Column(String, nullable=False, index=True)
    user_id = Column(String, nullable=False, index=True)
    
    invoice_number = Column(String, nullable=False, unique=True, index=True)
    status = Column(String, nullable=False, index=True)  # draft, open, paid, void, uncollectible
    
    amount_due = Column(Float, nullable=False)
    amount_paid = Column(Float, nullable=False, default=0.0)
    currency = Column(String, nullable=False, default="usd")
    
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    due_date = Column(DateTime(timezone=True), nullable=True)
    paid_at = Column(DateTime(timezone=True), nullable=True)
    
    stripe_invoice_id = Column(String, nullable=True, unique=True)
    
    line_items = Column(JSON, nullable=True)
    metadata = Column(JSON, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Invoice(id={self.id}, invoice_number={self.invoice_number}, status={self.status})>"


class Payment(Base):
    """Payment model"""
    __tablename__ = "payments"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    invoice_id = Column(String, nullable=False, index=True)
    user_id = Column(String, nullable=False, index=True)
    
    amount = Column(Float, nullable=False)
    currency = Column(String, nullable=False, default="usd")
    status = Column(String, nullable=False, index=True)  # succeeded, failed, pending, refunded
    
    payment_method = Column(String, nullable=True)
    stripe_payment_intent_id = Column(String, nullable=True, unique=True)
    
    failure_message = Column(String, nullable=True)
    metadata = Column(JSON, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<Payment(id={self.id}, amount={self.amount}, status={self.status})>"
