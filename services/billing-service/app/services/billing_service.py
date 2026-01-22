"""Billing service business logic"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..db.models import Subscription, Invoice
from ..models.schemas import SubscriptionCreate


# Pricing tier definitions (aligned with pricing strategy)
PRICING_TIERS = {
    "starter": {
        "name": "Starter",
        "price_monthly": 0,
        "price_annual": 0,
        "features": [
            "C2PA signing (1K/mo)",
            "Unlimited verifications",
            "2 API keys",
            "Community support",
            "7-day analytics",
            "Licensing coalition (65/35 rev share)",
        ],
        "limits": {
            "c2pa_signatures": 1000,
            "sentences_tracked": 0,
            "api_keys": 2,
            "rate_limit": 10,
        },
        "coalition_rev_share": {"publisher": 65, "encypher": 35},
    },
    "professional": {
        "name": "Professional",
        "price_monthly": 99,
        "price_annual": 950,
        "features": [
            "Everything in Starter",
            "Sentence-level tracking (50K/mo)",
            "Invisible embeddings",
            "10 API keys",
            "Email support (48hr SLA)",
            "90-day analytics",
            "BYOK encryption",
            "WordPress Pro (no branding)",
            "Licensing coalition (70/30 rev share)",
        ],
        "limits": {
            "c2pa_signatures": -1,
            "sentences_tracked": 50000,
            "api_keys": 10,
            "rate_limit": 50,
        },
        "coalition_rev_share": {"publisher": 70, "encypher": 30},
    },
    "business": {
        "name": "Business",
        "price_monthly": 499,
        "price_annual": 4790,
        "features": [
            "Everything in Professional",
            "Merkle tree encoding",
            "Plagiarism detection",
            "Source attribution API",
            "Batch operations (100 docs)",
            "50 API keys",
            "Priority support (24hr SLA)",
            "1-year analytics",
            "Team management (10 users)",
            "Audit logs",
            "Licensing coalition (75/25 rev share)",
        ],
        "limits": {
            "c2pa_signatures": -1,
            "sentences_tracked": 500000,
            "api_keys": 50,
            "rate_limit": 200,
        },
        "coalition_rev_share": {"publisher": 75, "encypher": 25},
    },
    "enterprise": {
        "name": "Enterprise",
        "price_monthly": 0,  # Custom
        "price_annual": 0,  # Custom
        "features": [
            "Everything in Business",
            "Unlimited everything",
            "Custom C2PA assertions",
            "SSO/SCIM",
            "Dedicated TAM + Slack",
            "Custom SLAs",
            "On-premise option",
            "Licensing coalition (80/20 rev share)",
        ],
        "limits": {
            "c2pa_signatures": -1,
            "sentences_tracked": -1,
            "api_keys": -1,
            "rate_limit": -1,
        },
        "coalition_rev_share": {"publisher": 80, "encypher": 20},
    },
    "strategic_partner": {
        "name": "Strategic Partner",
        "price_monthly": 0,  # Negotiated
        "price_annual": 0,  # Negotiated
        "features": [
            "Everything in Enterprise",
            "Best revenue share (85/15)",
            "Co-marketing",
            "Product roadmap input",
        ],
        "limits": {
            "c2pa_signatures": -1,
            "sentences_tracked": -1,
            "api_keys": -1,
            "rate_limit": -1,
        },
        "coalition_rev_share": {"publisher": 85, "encypher": 15},
    },
}

# Legacy plan mapping for backward compatibility
PLANS = {
    "free": {"name": "Starter", "monthly": 0, "yearly": 0},
    "starter": {"name": "Starter", "monthly": 0, "yearly": 0},
    "pro": {"name": "Professional", "monthly": 99, "yearly": 950},
    "professional": {"name": "Professional", "monthly": 99, "yearly": 950},
    "business": {"name": "Business", "monthly": 499, "yearly": 4790},
    "enterprise": {"name": "Enterprise", "monthly": 0, "yearly": 0},
}


class BillingService:
    """Billing and subscription service"""

    @staticmethod
    def create_subscription(
        db: Session,
        user_id: str,
        subscription_data: SubscriptionCreate,
    ) -> Subscription:
        """Create a new subscription"""
        plan = PLANS.get(subscription_data.plan_id)
        if not plan:
            raise ValueError(f"Invalid plan_id: {subscription_data.plan_id}")

        amount = plan[subscription_data.billing_cycle]

        now = datetime.utcnow()
        period_end = now + timedelta(days=365 if subscription_data.billing_cycle == "yearly" else 30)

        subscription = Subscription(
            user_id=user_id,
            plan_id=subscription_data.plan_id,
            plan_name=plan["name"],
            status="active",
            billing_cycle=subscription_data.billing_cycle,
            amount=amount,
            currency="usd",
            current_period_start=now,
            current_period_end=period_end,
        )

        db.add(subscription)
        db.commit()
        db.refresh(subscription)

        return subscription

    @staticmethod
    def get_user_subscription(db: Session, user_id: str) -> Optional[Subscription]:
        """Get active subscription for user"""
        return db.query(Subscription).filter(Subscription.user_id == user_id, Subscription.status == "active").first()

    @staticmethod
    def cancel_subscription(db: Session, subscription_id: str, user_id: str) -> bool:
        """Cancel a subscription"""
        subscription = db.query(Subscription).filter(Subscription.id == subscription_id, Subscription.user_id == user_id).first()

        if not subscription:
            return False

        subscription.cancel_at_period_end = True
        subscription.canceled_at = datetime.utcnow()
        db.commit()

        return True

    @staticmethod
    def get_invoices(db: Session, user_id: str, limit: int = 100) -> List[Invoice]:
        """Get invoices for user"""
        return db.query(Invoice).filter(Invoice.user_id == user_id).order_by(Invoice.created_at.desc()).limit(limit).all()

    @staticmethod
    def get_billing_stats(db: Session, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get billing statistics"""
        query = db.query(Subscription)
        if user_id:
            query = query.filter(Subscription.user_id == user_id)

        active_subs = query.filter(Subscription.status == "active").count()
        canceled_subs = query.filter(Subscription.status == "canceled").count()

        # Calculate MRR
        mrr = db.query(func.sum(Subscription.amount)).filter(Subscription.status == "active", Subscription.billing_cycle == "monthly").scalar() or 0.0

        # Add yearly subscriptions (divided by 12)
        yearly_mrr = (
            db.query(func.sum(Subscription.amount)).filter(Subscription.status == "active", Subscription.billing_cycle == "yearly").scalar() or 0.0
        )
        mrr += yearly_mrr / 12

        invoice_query = db.query(Invoice)
        if user_id:
            invoice_query = invoice_query.filter(Invoice.user_id == user_id)

        total_invoices = invoice_query.count()
        paid_invoices = invoice_query.filter(Invoice.status == "paid").count()
        unpaid_invoices = total_invoices - paid_invoices

        total_revenue = db.query(func.sum(Invoice.amount_paid)).scalar() or 0.0

        return {
            "total_revenue": float(total_revenue),
            "monthly_recurring_revenue": float(mrr),
            "active_subscriptions": active_subs,
            "canceled_subscriptions": canceled_subs,
            "total_invoices": total_invoices,
            "paid_invoices": paid_invoices,
            "unpaid_invoices": unpaid_invoices,
        }
