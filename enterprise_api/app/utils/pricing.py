"""
Pricing configuration for Encypher subscription tiers.

This module defines the official pricing tiers, features, and limits
that are used across the platform.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List

from app.core.pricing_constants import DEFAULT_COALITION_REV_SHARE
from app.core.tier_config import coerce_tier_name


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


# TEAM_145: Official pricing tiers — consolidated to free/enterprise/strategic_partner
PRICING_TIERS: Dict[str, PricingTier] = {
    "free": PricingTier(
        id="free",
        name="Free",
        display_name="Free",
        price_monthly=0,
        price_annual=0,
        description="Full signing infrastructure for publishers of any size. Prove ownership, detect copying, join the coalition.",
        features=[
            "C2PA 2.3-compliant document signing (1K/mo)",
            "Sentence-level Merkle tree authentication",
            "Invisible Unicode embeddings",
            "Unlimited verifications",
            "Coalition membership with content attribution",
            "WordPress plugin — auto-sign on publish",
            "REST API, CLI, GitHub Action",
        ],
        limits={
            "c2pa_signatures": 1000,
            "sentences_tracked": 10000,
            "merkle_encoding": 1000,
            "batch_operations": 0,
            "api_keys": 2,
            "rate_limit_per_sec": 10,
            "analytics_retention_days": 30,
            "team_members": 1,
        },
        coalition_rev_share=DEFAULT_COALITION_REV_SHARE,
        popular=True,
    ),
    "enterprise": PricingTier(
        id="enterprise",
        name="Enterprise",
        display_name="Enterprise",
        price_monthly=0,  # Custom pricing
        price_annual=0,  # Custom pricing
        description="Unlimited everything. All add-ons included. Dedicated support. Custom pricing tailored to your organization.",
        features=[
            "Unlimited signing — no caps on volume or API calls",
            "Real-time AI output monitoring",
            "Enforcement tools — formal notices and evidence packages",
            "Custom signing identity and white-label verification",
            "Streaming LLM signing",
            "Dedicated SLA, SSO, and named account manager",
            "All add-ons included",
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
        coalition_rev_share=DEFAULT_COALITION_REV_SHARE,
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
            "Co-marketing opportunities",
            "Product roadmap input",
            "Advisory board participation",
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
        coalition_rev_share=DEFAULT_COALITION_REV_SHARE,
        enterprise=True,
    ),
}


def get_tier(tier_id: str) -> PricingTier:
    """Get a pricing tier by ID"""
    tier_id = coerce_tier_name(tier_id)
    return PRICING_TIERS.get(tier_id, PRICING_TIERS["free"])


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


# Overage rates in cents per unit, keyed by QuotaType.
# A rate of 0 means the feature is hard-limited (no overage allowed).
from app.utils.quota import QuotaType

OVERAGE_RATES_CENTS = {
    QuotaType.C2PA_SIGNATURES: 2,  # $0.02/doc
    QuotaType.API_CALLS: 2,  # $0.02/call
    QuotaType.SENTENCES_TRACKED: 2,  # $0.02/unit
    QuotaType.MERKLE_ENCODING: 2,  # $0.02/call
    QuotaType.MERKLE_ATTRIBUTION: 2,  # $0.02/call
    QuotaType.BATCH_OPERATIONS: 2,  # $0.02/op
    # Hard-limited (Enterprise-only features, no overage):
    QuotaType.MERKLE_PLAGIARISM: 0,
    QuotaType.FUZZY_INDEX: 0,
    QuotaType.FUZZY_SEARCH: 0,
    QuotaType.CDN_IMAGE_REGISTRATIONS: 0,
}
