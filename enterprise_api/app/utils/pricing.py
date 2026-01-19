"""
Pricing configuration for Encypher subscription tiers.

This module defines the official pricing tiers, features, and limits
that are used across the platform.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List


class BillingCycle(str, Enum):
    """Billing cycle options"""

    MONTHLY = "monthly"
    ANNUAL = "annual"


@dataclass
class PricingTier:
    """Definition of a pricing tier"""

    id: str
    name: str
    display_name: str
    price_monthly: float
    price_annual: float
    description: str
    features: List[str]
    limits: Dict[str, Any]
    coalition_rev_share: Dict[str, int]
    popular: bool = False
    enterprise: bool = False


# Official pricing tiers
PRICING_TIERS: Dict[str, PricingTier] = {
    "starter": PricingTier(
        id="starter",
        name="Starter",
        display_name="Starter (Free)",
        price_monthly=0,
        price_annual=0,
        description="Perfect for individual bloggers and small publishers getting started with content authentication.",
        features=[
            "Unlimited C2PA signing",
            "Unlimited verifications",
            "2 API keys",
            "Community support (GitHub/Discord)",
            "7-day analytics retention",
            "WordPress plugin (with Encypher branding)",
            "Auto-join licensing coalition",
        ],
        limits={
            "c2pa_signatures": 10000,  # Soft cap for abuse prevention
            "sentences_tracked": 0,
            "merkle_encoding": 0,
            "batch_operations": 0,
            "api_keys": 2,
            "rate_limit_per_sec": 10,
            "analytics_retention_days": 7,
            "team_members": 1,
        },
        coalition_rev_share={"publisher": 65, "encypher": 35},
    ),
    "professional": PricingTier(
        id="professional",
        name="Professional",
        display_name="Professional",
        price_monthly=99,
        price_annual=950,  # ~20% discount
        description="For growing publishers who need sentence-level tracking and better coalition revenue share.",
        features=[
            "Everything in Starter",
            "Sentence-level tracking (50K/month)",
            "Invisible embeddings (Unicode VS)",
            "Streaming signing (WebSocket/SSE)",
            "Sentence lookup API",
            "10 API keys",
            "Email support (48hr SLA)",
            "90-day analytics retention",
            "BYOK (Bring Your Own Keys)",
            "WordPress Pro (no branding)",
        ],
        limits={
            "c2pa_signatures": -1,  # Unlimited
            "sentences_tracked": 50000,
            "merkle_encoding": 0,
            "batch_operations": 0,
            "api_keys": 10,
            "rate_limit_per_sec": 50,
            "analytics_retention_days": 90,
            "team_members": 1,
        },
        coalition_rev_share={"publisher": 70, "encypher": 30},
        popular=True,
    ),
    "business": PricingTier(
        id="business",
        name="Business",
        display_name="Business",
        price_monthly=499,
        price_annual=4790,  # ~20% discount
        description="For major publishers who need Merkle infrastructure, plagiarism detection, and team features.",
        features=[
            "Everything in Professional",
            "Merkle tree encoding",
            "Source attribution API",
            "Plagiarism detection API",
            "Batch operations (100 docs)",
            "500K tracked sentences/month",
            "50 API keys",
            "Priority support (24hr SLA)",
            "1-year analytics retention",
            "Team management (10 users)",
            "Audit logs",
            "WordPress multi-site (5 sites)",
        ],
        limits={
            "c2pa_signatures": -1,  # Unlimited
            "sentences_tracked": 500000,
            "merkle_encoding": 10000,
            "batch_operations": 1000,
            "api_keys": 50,
            "rate_limit_per_sec": 200,
            "analytics_retention_days": 365,
            "team_members": 10,
        },
        coalition_rev_share={"publisher": 75, "encypher": 25},
    ),
    "enterprise": PricingTier(
        id="enterprise",
        name="Enterprise",
        display_name="Enterprise",
        price_monthly=0,  # Custom pricing
        price_annual=0,  # Custom pricing
        description="For global media organizations with custom requirements, SLAs, and dedicated support.",
        features=[
            "Everything in Business",
            "Unlimited everything",
            "Custom C2PA assertion schemas",
            "Assertion templates",
            "Provenance chain (edit history)",
            "Unlimited API keys",
            "Unlimited team members",
            "SSO/SCIM integration",
            "Dedicated TAM + Slack channel",
            "Custom SLAs",
            "On-premise deployment option",
            "WordPress unlimited sites + white-label",
        ],
        limits={
            "c2pa_signatures": -1,
            "sentences_tracked": -1,
            "merkle_encoding": -1,
            "batch_operations": -1,
            "api_keys": -1,
            "rate_limit_per_sec": -1,
            "analytics_retention_days": -1,  # Custom
            "team_members": -1,
        },
        coalition_rev_share={"publisher": 80, "encypher": 20},
        enterprise=True,
    ),
    "strategic_partner": PricingTier(
        id="strategic_partner",
        name="Strategic Partner",
        display_name="Strategic Partner",
        price_monthly=0,  # Negotiated
        price_annual=0,  # Negotiated
        description="Invite-only tier for founding coalition members and strategic partners.",
        features=[
            "Everything in Enterprise",
            "Best-in-class revenue share (85/15)",
            "Co-marketing opportunities",
            "Product roadmap input",
            "Early access to new features",
            "Dedicated engineering support",
        ],
        limits={
            "c2pa_signatures": -1,
            "sentences_tracked": -1,
            "merkle_encoding": -1,
            "batch_operations": -1,
            "api_keys": -1,
            "rate_limit_per_sec": -1,
            "analytics_retention_days": -1,
            "team_members": -1,
        },
        coalition_rev_share={"publisher": 85, "encypher": 15},
        enterprise=True,
    ),
}


def get_tier(tier_id: str) -> PricingTier:
    """Get a pricing tier by ID"""
    return PRICING_TIERS.get(tier_id, PRICING_TIERS["starter"])


def get_price(tier_id: str, billing_cycle: BillingCycle) -> float:
    """Get the price for a tier and billing cycle"""
    tier = get_tier(tier_id)
    if billing_cycle == BillingCycle.ANNUAL:
        return tier.price_annual
    return tier.price_monthly


def get_all_tiers() -> List[Dict[str, Any]]:
    """Get all tiers as a list of dictionaries (for API responses)"""
    return [
        {
            "id": tier.id,
            "name": tier.name,
            "display_name": tier.display_name,
            "price_monthly": tier.price_monthly,
            "price_annual": tier.price_annual,
            "description": tier.description,
            "features": tier.features,
            "limits": tier.limits,
            "coalition_rev_share": tier.coalition_rev_share,
            "popular": tier.popular,
            "enterprise": tier.enterprise,
        }
        for tier in PRICING_TIERS.values()
    ]


def get_public_tiers() -> List[Dict[str, Any]]:
    """Get tiers that should be shown on public pricing page (excludes strategic partner)"""
    return [tier_dict for tier_dict in get_all_tiers() if tier_dict["id"] != "strategic_partner"]
