"""
Quota enforcement system for API usage limits.

Tracks and enforces usage quotas based on organization tier.
"""

import logging
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from fastapi import HTTPException, status
from sqlalchemy import select, text, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Organization, OrganizationTier

logger = logging.getLogger(__name__)


def _coerce_tier(value: Any) -> OrganizationTier:
    if isinstance(value, OrganizationTier):
        return value
    if isinstance(value, str):
        # TEAM_145: Map legacy tier names to FREE
        legacy_map = {"starter": "free", "professional": "free", "business": "free"}
        mapped = legacy_map.get(value, value)
        try:
            return OrganizationTier(mapped)
        except ValueError:
            return OrganizationTier.FREE
    return OrganizationTier.FREE


class QuotaType(str, Enum):
    """Types of quotas that can be enforced."""

    MERKLE_ENCODING = "merkle_encoding"
    MERKLE_ATTRIBUTION = "merkle_attribution"
    MERKLE_PLAGIARISM = "merkle_plagiarism"
    FUZZY_INDEX = "fuzzy_index"
    FUZZY_SEARCH = "fuzzy_search"
    API_CALLS = "api_calls"
    SENTENCES_TRACKED = "sentences_tracked"
    BATCH_OPERATIONS = "batch_operations"
    C2PA_SIGNATURES = "c2pa_signatures"  # Soft limit for abuse prevention


# TEAM_166: Derive enum-keyed dicts from the SSOT (app.core.tier_config)
from app.core import tier_config as _tc

_TIER_ENUM_MAP = {
    "free": OrganizationTier.FREE,
    "enterprise": OrganizationTier.ENTERPRISE,
    "strategic_partner": OrganizationTier.STRATEGIC_PARTNER,
}

TIER_RATE_LIMITS: Dict[OrganizationTier, int] = {
    _TIER_ENUM_MAP[t]: _tc.TIER_RATE_LIMITS_PER_SECOND[t]
    for t in _TIER_ENUM_MAP
}

TIER_REV_SHARE: Dict[OrganizationTier, tuple] = {
    _TIER_ENUM_MAP[t]: (rs["publisher"], rs["encypher"])
    for t, rs in ((t, _tc.get_tier_rev_share(t)) for t in _TIER_ENUM_MAP)
}

TIER_FEATURES: Dict[OrganizationTier, Dict[str, bool]] = {
    _TIER_ENUM_MAP[t]: {k: v for k, v in _tc.get_tier_features(t).items() if isinstance(v, bool)}
    for t in _TIER_ENUM_MAP
}


# Quota limits by tier (per month)
# -1 means unlimited
TIER_QUOTAS: Dict[OrganizationTier, Dict[QuotaType, int]] = {
    OrganizationTier.FREE: {
        QuotaType.C2PA_SIGNATURES: 1000,  # 1K docs/month as per pricing page
        QuotaType.SENTENCES_TRACKED: 10000,
        QuotaType.MERKLE_ENCODING: 1000,
        QuotaType.MERKLE_ATTRIBUTION: 1000,
        QuotaType.MERKLE_PLAGIARISM: 0,  # Enterprise only
        QuotaType.FUZZY_INDEX: 0,  # Enterprise only
        QuotaType.FUZZY_SEARCH: 0,  # Enterprise only
        QuotaType.BATCH_OPERATIONS: 0,  # Enterprise only
        QuotaType.API_CALLS: 1000,
    },
    OrganizationTier.ENTERPRISE: {
        QuotaType.C2PA_SIGNATURES: -1,  # Unlimited
        QuotaType.SENTENCES_TRACKED: -1,
        QuotaType.MERKLE_ENCODING: -1,
        QuotaType.MERKLE_ATTRIBUTION: -1,
        QuotaType.MERKLE_PLAGIARISM: -1,
        QuotaType.FUZZY_INDEX: -1,
        QuotaType.FUZZY_SEARCH: -1,
        QuotaType.BATCH_OPERATIONS: -1,
        QuotaType.API_CALLS: -1,
    },
    OrganizationTier.STRATEGIC_PARTNER: {
        QuotaType.C2PA_SIGNATURES: -1,  # Unlimited
        QuotaType.SENTENCES_TRACKED: -1,
        QuotaType.MERKLE_ENCODING: -1,
        QuotaType.MERKLE_ATTRIBUTION: -1,
        QuotaType.MERKLE_PLAGIARISM: -1,
        QuotaType.FUZZY_INDEX: -1,
        QuotaType.FUZZY_SEARCH: -1,
        QuotaType.BATCH_OPERATIONS: -1,
        QuotaType.API_CALLS: -1,
    },
}


class QuotaManager:
    """
    Manages quota checking and enforcement.

    Tracks usage and enforces limits based on organization tier.
    """

    @staticmethod
    async def _ensure_user_organization_exists(
        db: AsyncSession,
        organization_id: str,
        tier: OrganizationTier,
    ) -> None:
        """Ensure a synthetic user-level organization exists for quota tracking."""
        limit = QuotaManager.get_quota_limit(tier, QuotaType.API_CALLS)
        await db.execute(
            text(
                """
                INSERT INTO organizations (
                    id, name, email, tier, monthly_api_limit, monthly_api_usage,
                    coalition_member, coalition_rev_share, created_at, updated_at
                ) VALUES (
                    :id, :name, :email, :tier, :monthly_api_limit, 0,
                    TRUE, 65, NOW(), NOW()
                )
                ON CONFLICT (id) DO NOTHING
                """
            ),
            {
                "id": organization_id,
                "name": "Personal Account",
                "email": f"{organization_id}@personal.local",
                "tier": tier.value,
                "monthly_api_limit": limit if limit >= 0 else 10000,
            },
        )
        await db.flush()

    @staticmethod
    async def check_quota(
        db: AsyncSession,
        organization_id: str,
        quota_type: QuotaType,
        increment: int = 1,
        tier_override: Optional[str] = None,
        features: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Check if organization has quota available and increment if so.

        Args:
            db: Database session
            organization_id: Organization identifier
            quota_type: Type of quota to check
            increment: Amount to increment (default 1)
            tier_override: Optional tier to use instead of DB lookup (for user-level keys)
            features: Optional features dict from organization context (for permission-based access)

        Returns:
            True if quota available, False if exceeded

        Raises:
            HTTPException: If quota exceeded
        """
        # Handle user-level keys (synthetic org IDs like "user_{user_id}")
        if organization_id.startswith("user_"):
            # Check if this is a super admin key (unlimited access)
            if features and features.get("is_super_admin", False):
                logger.debug(f"Super admin key {organization_id}: allowing unlimited {quota_type.value}")
                return True

            await QuotaManager._ensure_user_organization_exists(
                db=db,
                organization_id=organization_id,
                tier=OrganizationTier.FREE,
            )

        # Check if this is a demo key (doesn't require database lookup)
        # NMA starter orgs (org_nma_*) are also demo keys
        is_demo_key = (
            (features and features.get("is_demo", False))
            or organization_id.startswith("org_demo")
            or organization_id.startswith("org_encypher")
            or organization_id.startswith("org_nma_")
            or organization_id.startswith("org_starter")
            or organization_id.startswith("org_professional")
            or organization_id.startswith("org_business")
            or organization_id.startswith("org_enterprise")
        )

        if is_demo_key:
            # Demo keys use in-memory quota tracking from DEMO_KEYS config
            tier = _coerce_tier(tier_override or "free")
            quota_limit = QuotaManager.get_quota_limit(tier, quota_type)

            # NMA (News Media Alliance) members on starter tier get access to merkle features
            # Check if this is an NMA member - flag can be in features dict or at top level
            is_nma_member = features and (features.get("nma_member", False) or features.get("sentence_tracking", False))
            if is_nma_member and quota_type in (QuotaType.MERKLE_ENCODING, QuotaType.MERKLE_ATTRIBUTION):
                # NMA members get limited merkle access (same as professional tier limits)
                nma_limit = QuotaManager.get_quota_limit(OrganizationTier.FREE, quota_type)
                logger.debug(f"NMA member {organization_id}: allowing {quota_type.value} (NMA limit: {nma_limit})")
                return True

            # Demo keys with quota_limit = -1 or high limits are unlimited
            if quota_limit == -1 or quota_limit > 100000:
                logger.debug(f"Demo key {organization_id}: allowing {quota_type.value} (unlimited)")
                return True

            # Check if feature is enabled in features dict (overrides tier-based limits)
            if features and quota_limit == 0:
                feature_map = {
                    QuotaType.MERKLE_ENCODING: "merkle_enabled",
                    QuotaType.MERKLE_ATTRIBUTION: "merkle_enabled",
                    QuotaType.FUZZY_INDEX: "fuzzy_fingerprint",
                    QuotaType.FUZZY_SEARCH: "fuzzy_fingerprint",
                }
                feature_key = feature_map.get(quota_type)
                if feature_key and features.get(feature_key, False):
                    logger.debug(f"Demo key {organization_id}: allowing {quota_type.value} via feature flag")
                    return True

            # For demo keys with limits, allow without tracking (stateless)
            logger.debug(f"Demo key {organization_id}: allowing {quota_type.value} (limit: {quota_limit}, no tracking)")
            return True

        # Get organization from database for org-level keys
        result = await db.execute(select(Organization).where(Organization.organization_id == organization_id))
        org = result.scalar_one_or_none()

        if not org:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

        # Get quota limit for tier (DB stores tier as string)
        tier = _coerce_tier(tier_override or org.tier)
        quota_limit = QuotaManager.get_quota_limit(tier, quota_type)

        # Quota = 0 means feature not available for this tier
        if quota_limit == 0:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "FeatureNotAvailable",
                    "message": f"'{quota_type.value}' is not available on {tier.value} tier",
                    "current_tier": tier.value,
                    "upgrade_url": "https://dashboard.encypherai.com/billing",
                },
            )

        # Quota = -1 means unlimited - allow without tracking
        if quota_limit == -1:
            return True

        # Get current usage
        current_usage = QuotaManager._get_current_usage(org, quota_type)

        # Check if quota exceeded
        if current_usage + increment > quota_limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "QuotaExceeded",
                    "message": f"Monthly quota exceeded for {quota_type.value}",
                    "quota_limit": quota_limit,
                    "current_usage": current_usage,
                    "reset_date": QuotaManager._get_reset_date().isoformat(),
                },
            )

        # Increment usage
        await QuotaManager._increment_usage(db, org, quota_type, increment)

        return True

    @staticmethod
    def get_quota_limit(tier: OrganizationTier, quota_type: QuotaType) -> int:
        """
        Get quota limit for a tier and quota type.

        Args:
            tier: Organization tier
            quota_type: Type of quota

        Returns:
        """
        return TIER_QUOTAS.get(tier, {}).get(quota_type, 0)

    @staticmethod
    def _get_current_usage(org: Organization, quota_type: QuotaType) -> int:
        """
        Get current usage for a quota type.

        Args:
            org: Organization
            quota_type: Type of quota

        Returns:
            Current usage count
        """
        # Map quota types to organization fields
        usage_fields = {
            QuotaType.MERKLE_ENCODING: "merkle_encoding_calls_this_month",
            QuotaType.MERKLE_ATTRIBUTION: "merkle_attribution_calls_this_month",
            QuotaType.MERKLE_PLAGIARISM: "merkle_plagiarism_calls_this_month",
            QuotaType.FUZZY_INDEX: "fuzzy_index_calls_this_month",
            QuotaType.FUZZY_SEARCH: "fuzzy_search_calls_this_month",
            QuotaType.API_CALLS: "api_calls_this_month",
            QuotaType.C2PA_SIGNATURES: "documents_signed",
            QuotaType.SENTENCES_TRACKED: "sentences_tracked_this_month",
            QuotaType.BATCH_OPERATIONS: "batch_operations_this_month",
        }

        field_name = usage_fields.get(quota_type)
        if not field_name:
            return 0

        return getattr(org, field_name, 0)

    @staticmethod
    async def _increment_usage(db: AsyncSession, org: Organization, quota_type: QuotaType, increment: int):
        """
        Increment usage counter for a quota type.

        Args:
            db: Database session
            org: Organization
            quota_type: Type of quota
            increment: Amount to increment
        """
        # Map quota types to organization fields
        usage_fields = {
            QuotaType.MERKLE_ENCODING: "merkle_encoding_calls_this_month",
            QuotaType.MERKLE_ATTRIBUTION: "merkle_attribution_calls_this_month",
            QuotaType.MERKLE_PLAGIARISM: "merkle_plagiarism_calls_this_month",
            QuotaType.FUZZY_INDEX: "fuzzy_index_calls_this_month",
            QuotaType.FUZZY_SEARCH: "fuzzy_search_calls_this_month",
            QuotaType.API_CALLS: "api_calls_this_month",
            QuotaType.C2PA_SIGNATURES: "documents_signed",
            QuotaType.SENTENCES_TRACKED: "sentences_tracked_this_month",
            QuotaType.BATCH_OPERATIONS: "batch_operations_this_month",
        }

        field_name = usage_fields.get(quota_type)
        if not field_name:
            return

        # Increment the counter
        current_value = getattr(org, field_name, 0)
        setattr(org, field_name, current_value + increment)

        await db.commit()
        await db.refresh(org)

    @staticmethod
    async def get_quota_headers(db: AsyncSession, organization_id: str, quota_type: QuotaType) -> dict:
        """
        Get HTTP headers showing quota usage for a specific quota type.

        Returns headers like:
        - X-Quota-Limit: 5000
        - X-Quota-Used: 1234
        - X-Quota-Remaining: 3766
        - X-Quota-Reset: 2025-01-01T00:00:00Z
        """
        # Check if this is a demo key (doesn't require database lookup)
        is_demo_key = organization_id.startswith("org_demo") or organization_id.startswith("org_encypher")

        if is_demo_key:
            # Return generic headers for demo keys (no tracking)
            return {
                "X-Quota-Limit": "50000",
                "X-Quota-Used": "0",
                "X-Quota-Remaining": "50000",
                "X-Quota-Reset": QuotaManager._get_reset_date().isoformat(),
            }

        result = await db.execute(select(Organization).where(Organization.organization_id == organization_id))
        org = result.scalar_one_or_none()

        if not org:
            return {}

        tier = _coerce_tier(org.tier)
        limit = QuotaManager.get_quota_limit(tier, quota_type)
        used = QuotaManager._get_current_usage(org, quota_type)

        if limit == -1:
            return {
                "X-Quota-Limit": "unlimited",
                "X-Quota-Used": str(used),
                "X-Quota-Remaining": "unlimited",
                "X-Quota-Reset": QuotaManager._get_reset_date().isoformat(),
            }

        remaining = max(0, limit - used)
        return {
            "X-Quota-Limit": str(limit),
            "X-Quota-Used": str(used),
            "X-Quota-Remaining": str(remaining),
            "X-Quota-Reset": QuotaManager._get_reset_date().isoformat(),
        }

    @staticmethod
    def _get_reset_date() -> datetime:
        """
        Get the date when quotas reset (first day of next month).

        Returns:
            Reset datetime
        """
        now = datetime.utcnow()
        if now.month == 12:
            return datetime(now.year + 1, 1, 1)
        else:
            return datetime(now.year, now.month + 1, 1)

    @staticmethod
    async def get_quota_status(db: AsyncSession, organization_id: str) -> Dict[str, Any]:
        """
        Get quota status for an organization.

        Args:
            db: Database session
            organization_id: Organization identifier

        Returns:
            Dictionary with quota status for all quota types
        """
        # Get organization from database
        result = await db.execute(select(Organization).where(Organization.organization_id == organization_id))
        org = result.scalar_one_or_none()

        if not org:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

        org_quotas: Dict[str, Dict[str, Any]] = {}
        org_status: Dict[str, Any] = {
            "organization_id": organization_id,
            "tier": _coerce_tier(org.tier).value,
            "reset_date": QuotaManager._get_reset_date().isoformat(),
            "quotas": org_quotas,
        }

        for quota_type in QuotaType:
            limit = QuotaManager.get_quota_limit(_coerce_tier(org.tier), quota_type)
            usage = QuotaManager._get_current_usage(org, quota_type)

            org_quotas[quota_type.value] = {
                "limit": limit,
                "used": usage,
                "remaining": max(0, limit - usage),
                "percentage_used": round((usage / limit * 100) if limit > 0 else 0, 2),
            }

        return org_status

    @staticmethod
    async def reset_monthly_quotas(db: AsyncSession):
        """
        Reset all monthly quotas (run on first day of month).

        Args:
            db: Database session
        """
        await db.execute(
            update(Organization).values(
                merkle_encoding_calls_this_month=0,
                merkle_attribution_calls_this_month=0,
                merkle_plagiarism_calls_this_month=0,
                fuzzy_index_calls_this_month=0,
                fuzzy_search_calls_this_month=0,
                api_calls_this_month=0,
                documents_signed=0,
                sentences_tracked_this_month=0,
                batch_operations_this_month=0,
            )
        )
        await db.commit()
        logger.info("Reset monthly quotas for all organizations")


# Dependency for quota checking
async def check_quota_dependency(quota_type: QuotaType, organization_id: str, db: AsyncSession):
    """
    FastAPI dependency for quota checking.

    Usage:
        @router.post("/endpoint")
        async def endpoint(
            _: None = Depends(lambda: check_quota_dependency(QuotaType.MERKLE_ENCODING, org_id, db))
        ):
            ...

    Args:
        quota_type: Type of quota to check
        organization_id: Organization identifier
        db: Database session

    Raises:
        HTTPException: If quota exceeded
    """
    await QuotaManager.check_quota(db, organization_id, quota_type)
