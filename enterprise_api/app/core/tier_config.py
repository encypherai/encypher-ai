"""
Single Source of Truth for tier configuration.

TEAM_166: All tier-related constants (features, limits, rates, rev share, hierarchy)
live here. Every other module imports from this file instead of hardcoding.

Tiers: free, enterprise, strategic_partner
Legacy names (starter, professional, business) map to free via coerce_tier_name().
"""

from __future__ import annotations

from typing import Any, Dict, Set

# ---------------------------------------------------------------------------
# Tier names
# ---------------------------------------------------------------------------

TIERS = ("free", "enterprise", "strategic_partner")

LEGACY_TIER_MAP: Dict[str, str] = {
    "starter": "free",
    "professional": "free",
    "business": "free",
}


def coerce_tier_name(tier: str) -> str:
    """Map any tier string (including legacy names) to a canonical tier."""
    return LEGACY_TIER_MAP.get(tier, tier)


# ---------------------------------------------------------------------------
# Tier hierarchy  (higher number = more access)
# ---------------------------------------------------------------------------

TIER_HIERARCHY: Dict[str, int] = {
    "free": 0,
    "starter": 0,       # legacy alias
    "professional": 0,  # legacy alias
    "business": 0,      # legacy alias
    "enterprise": 1,
    "strategic_partner": 2,
    "demo": 2,           # demo has full access
}


def is_enterprise_tier(tier: str) -> bool:
    """Return True if tier is enterprise, strategic_partner, or demo."""
    return tier in {"enterprise", "strategic_partner", "demo"}


# ---------------------------------------------------------------------------
# Feature flags per tier
# ---------------------------------------------------------------------------
# These are the *default* feature flags applied when an org is created or
# its tier is changed.  Individual orgs can override via the DB features
# column or add_ons JSON.

FREE_FEATURES: Dict[str, Any] = {
    "c2pa_signing": True,
    "verification": True,
    "merkle_enabled": True,
    "sentence_tracking": True,
    "streaming": True,
    "custom_assertions": True,
    "audit_logs": True,
    # --- enterprise-only below ---
    "fuzzy_fingerprint": False,
    "bulk_operations": False,
    "byok": False,
    "byok_enabled": False,
    "team_management": False,
    "sso": False,
    "advanced_analytics": False,
    "max_team_members": 1,
}

ENTERPRISE_FEATURES: Dict[str, Any] = {
    "c2pa_signing": True,
    "verification": True,
    "merkle_enabled": True,
    "sentence_tracking": True,
    "streaming": True,
    "custom_assertions": True,
    "audit_logs": True,
    "fuzzy_fingerprint": True,
    "bulk_operations": True,
    "byok": True,
    "byok_enabled": True,
    "team_management": True,
    "sso": True,
    "advanced_analytics": True,
    "max_team_members": -1,  # Unlimited
}

# Strategic partners get the same features as enterprise
STRATEGIC_PARTNER_FEATURES: Dict[str, Any] = {**ENTERPRISE_FEATURES}

TIER_FEATURES: Dict[str, Dict[str, Any]] = {
    "free": FREE_FEATURES,
    "enterprise": ENTERPRISE_FEATURES,
    "strategic_partner": STRATEGIC_PARTNER_FEATURES,
}


def get_tier_features(tier: str) -> Dict[str, Any]:
    """Get feature dict for a tier, coercing legacy names."""
    return TIER_FEATURES.get(coerce_tier_name(tier), FREE_FEATURES)


# ---------------------------------------------------------------------------
# Quota / usage limits per tier  (per month, -1 = unlimited)
# ---------------------------------------------------------------------------

TIER_LIMITS: Dict[str, Dict[str, int]] = {
    "free": {
        "c2pa_signatures": 1000,
        "sentences_tracked": 10000,
        "batch_operations": 0,
        "api_keys": 2,
        "api_calls": 10000,
    },
    "enterprise": {
        "c2pa_signatures": -1,
        "sentences_tracked": -1,
        "batch_operations": -1,
        "api_keys": -1,
        "api_calls": -1,
    },
    "strategic_partner": {
        "c2pa_signatures": -1,
        "sentences_tracked": -1,
        "batch_operations": -1,
        "api_keys": -1,
        "api_calls": -1,
    },
}


def get_tier_limits(tier: str) -> Dict[str, int]:
    """Get usage limits for a tier, coercing legacy names."""
    return TIER_LIMITS.get(coerce_tier_name(tier), TIER_LIMITS["free"])


# ---------------------------------------------------------------------------
# Rate limits  (requests per second, -1 = unlimited)
# ---------------------------------------------------------------------------

TIER_RATE_LIMITS_PER_SECOND: Dict[str, int] = {
    "free": 10,
    "starter": 10,       # legacy alias
    "professional": 10,  # legacy alias
    "business": 10,      # legacy alias
    "enterprise": -1,
    "strategic_partner": -1,
    "demo": -1,
}


# ---------------------------------------------------------------------------
# Coalition revenue share  (publisher %, encypher %)
# ---------------------------------------------------------------------------

TIER_REV_SHARE: Dict[str, Dict[str, int]] = {
    "free": {"publisher": 60, "encypher": 40},
    "enterprise": {"publisher": 85, "encypher": 15},
    "strategic_partner": {"publisher": 85, "encypher": 15},
}


def get_tier_rev_share(tier: str) -> Dict[str, int]:
    """Get rev share for a tier, coercing legacy names."""
    return TIER_REV_SHARE.get(coerce_tier_name(tier), TIER_REV_SHARE["free"])


# ---------------------------------------------------------------------------
# Team member limits
# ---------------------------------------------------------------------------

TIER_MEMBER_LIMITS: Dict[str, int] = {
    "free": 1,
    "enterprise": -1,
    "strategic_partner": -1,
}


def get_team_member_limit(tier: str) -> int:
    """Get max team members for a tier, coercing legacy names."""
    return TIER_MEMBER_LIMITS.get(coerce_tier_name(tier), 1)


# ---------------------------------------------------------------------------
# Batch size limits  (for /sign endpoint)
# ---------------------------------------------------------------------------

BATCH_LIMITS: Dict[str, int] = {
    "free": 10,
    "starter": 10,       # legacy alias
    "professional": 10,  # legacy alias
    "business": 10,      # legacy alias
    "enterprise": 100,
    "strategic_partner": 100,
    "demo": 100,
}


def get_batch_limit(tier: str) -> int:
    """Get batch size limit for a tier."""
    return BATCH_LIMITS.get(coerce_tier_name(tier), 10)


# ---------------------------------------------------------------------------
# API key limits per tier
# ---------------------------------------------------------------------------

TIER_KEY_LIMITS: Dict[str, int] = {
    "free": 2,
    "starter": 2,       # legacy alias
    "professional": 2,  # legacy alias
    "business": 2,      # legacy alias
    "enterprise": -1,
    "strategic_partner": -1,
}
