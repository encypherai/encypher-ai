"""Billing service business logic"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func

from encypher_commercial_shared.core.pricing_constants import DEFAULT_COALITION_REV_SHARE

from ..db.models import Subscription, Invoice
from ..models.schemas import SubscriptionCreate


# TEAM_145: Pricing tier definitions — consolidated to free/enterprise/strategic_partner
PRICING_TIERS = {
    "free": {
        "name": "Free",
        "price_monthly": 0,
        "price_annual": 0,
        "features": [
            "C2PA 2.3-compliant document signing (1K/mo)",
            "Sentence-level Merkle tree authentication",
            "Invisible Unicode embeddings",
            "Unlimited verifications",
            "Coalition membership with content attribution",
            "WordPress plugin — auto-sign on publish",
            "REST API, CLI, GitHub Action",
        ],
        "limits": {
            "c2pa_signatures": 1000,
            "sentences_tracked": 10000,
            "api_keys": 2,
            "rate_limit": 10,
        },
        "coalition_rev_share": DEFAULT_COALITION_REV_SHARE,
    },
    "enterprise": {
        "name": "Enterprise",
        "price_monthly": 0,  # Custom pricing
        "price_annual": 0,  # Custom pricing
        "features": [
            "Unlimited signing — no caps on volume or API calls",
            "Real-time AI output monitoring",
            "Enforcement tools — formal notices and evidence packages",
            "Custom signing identity and white-label verification",
            "Streaming LLM signing",
            "Dedicated SLA, SSO, and named account manager",
            "All add-ons included",
        ],
        "limits": {
            "c2pa_signatures": -1,
            "sentences_tracked": -1,
            "api_keys": -1,
            "rate_limit": -1,
        },
        "coalition_rev_share": DEFAULT_COALITION_REV_SHARE,
    },
    "strategic_partner": {
        "name": "Strategic Partner",
        "price_monthly": 0,  # Negotiated
        "price_annual": 0,  # Negotiated
        "features": [
            "Everything in Enterprise",
            "Co-marketing",
            "Product roadmap input",
            "Advisory board participation",
        ],
        "limits": {
            "c2pa_signatures": -1,
            "sentences_tracked": -1,
            "api_keys": -1,
            "rate_limit": -1,
        },
        "coalition_rev_share": DEFAULT_COALITION_REV_SHARE,
    },
}

# Legacy plan mapping for backward compatibility
PLANS = {
    "free": {"name": "Free", "monthly": 0, "yearly": 0},
    "starter": {"name": "Free", "monthly": 0, "yearly": 0},
    "pro": {"name": "Free", "monthly": 0, "yearly": 0},
    "professional": {"name": "Free", "monthly": 0, "yearly": 0},
    "business": {"name": "Free", "monthly": 0, "yearly": 0},
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
    def create_trial_subscription(
        *,
        db: Session,
        user_id: str,
        organization_id: str,
        tier: str,
        trial_months: int,
    ) -> Subscription:
        """Create a trial subscription record for an organization."""
        plan = PRICING_TIERS.get(tier)
        if not plan:
            raise ValueError(f"Invalid tier: {tier}")

        now = datetime.utcnow()
        period_end = now + timedelta(days=trial_months * 30)

        subscription = Subscription(
            user_id=user_id,
            organization_id=organization_id,
            plan_id=tier,
            plan_name=plan["name"],
            status="trialing",
            billing_cycle="monthly",
            amount=plan["price_monthly"],
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
        """Get active subscription for user, preferring ones with valid Stripe data"""
        # First try to find a subscription with a valid stripe_subscription_id and known tier
        sub = (
            db.query(Subscription)
            .filter(
                Subscription.user_id == user_id,
                Subscription.status == "active",
                Subscription.stripe_subscription_id.isnot(None),
                Subscription.plan_id != "unknown",
            )
            .order_by(Subscription.created_at.desc())
            .first()
        )
        if sub:
            return sub
        # Fall back to any active subscription
        return (
            db.query(Subscription)
            .filter(Subscription.user_id == user_id, Subscription.status == "active")
            .order_by(Subscription.created_at.desc())
            .first()
        )

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
