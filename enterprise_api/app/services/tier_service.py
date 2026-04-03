"""
Tier enforcement service for API access control.

Handles feature gating, quota enforcement, and tier-based access control.
"""

import logging
from datetime import datetime
from typing import Any, Dict, cast

from fastapi import HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.tier_config import LEGACY_TIER_MAP
from app.models.organization import Organization, OrganizationTier
from app.utils.quota import (
    QUOTA_FIELD_MAPPING,
    TIER_FEATURES,
    TIER_QUOTAS,
    TIER_RATE_LIMITS,
    TIER_REV_SHARE,
    QuotaType,
)

logger = logging.getLogger(__name__)


def _coerce_tier(value: Any) -> OrganizationTier:
    if isinstance(value, OrganizationTier):
        return value
    if isinstance(value, str):
        mapped = LEGACY_TIER_MAP.get(value, value)
        try:
            return OrganizationTier(mapped)
        except ValueError:
            return OrganizationTier.FREE
    return OrganizationTier.FREE


class TierService:
    """
    Service for tier-based access control and feature enforcement.

    Provides methods to check feature availability, enforce quotas,
    and manage tier-specific functionality.
    """

    @staticmethod
    def get_tier_features(tier: OrganizationTier) -> Dict[str, bool]:
        """
        Get all features available for a tier.

        Args:
            tier: Organization tier

        Returns:
            Dictionary of feature name -> enabled status
        """
        return TIER_FEATURES.get(_coerce_tier(tier), TIER_FEATURES[OrganizationTier.FREE])

    @staticmethod
    def is_feature_available(tier: OrganizationTier, feature: str) -> bool:
        """
        Check if a feature is available for a tier.

        Args:
            tier: Organization tier
            feature: Feature name (e.g., "merkle", "sentence_tracking")

        Returns:
            True if feature is available, False otherwise
        """
        features = TIER_FEATURES.get(_coerce_tier(tier), {})
        return features.get(feature, False)

    @staticmethod
    def get_rate_limit(tier: OrganizationTier) -> int:
        """
        Get rate limit for a tier.

        Args:
            tier: Organization tier

        Returns:
            Rate limit in requests per second (-1 for unlimited)
        """
        return TIER_RATE_LIMITS.get(_coerce_tier(tier), 10)

    @staticmethod
    def get_rev_share(tier: OrganizationTier) -> tuple:
        """
        Get coalition revenue share for a tier.

        Args:
            tier: Organization tier

        Returns:
            Tuple of (publisher_share, encypher_share) as percentages
        """
        return TIER_REV_SHARE.get(_coerce_tier(tier), (60, 40))

    @staticmethod
    def get_quota_limit(tier: OrganizationTier, quota_type: QuotaType) -> int:
        """
        Get quota limit for a tier and quota type.

        Args:
            tier: Organization tier
            quota_type: Type of quota

        Returns:
            Quota limit (-1 for unlimited, 0 for not available)
        """
        tier_quotas = TIER_QUOTAS.get(_coerce_tier(tier), {})
        return tier_quotas.get(quota_type, 0)

    @staticmethod
    async def check_feature_access(db: AsyncSession, organization_id: str, feature: str, raise_on_denied: bool = True) -> bool:
        """
        Check if an organization has access to a feature.

        Args:
            db: Database session
            organization_id: Organization identifier
            feature: Feature name to check
            raise_on_denied: If True, raise HTTPException on denied access

        Returns:
            True if access granted, False if denied (when raise_on_denied=False)

        Raises:
            HTTPException: If access denied and raise_on_denied=True
        """
        # Handle user-level keys (synthetic org IDs like "user_{user_id}")
        if organization_id.startswith("user_"):
            # Use free tier for user-level keys
            tier = OrganizationTier.FREE
            is_available = TierService.is_feature_available(tier, feature)

            if not is_available and raise_on_denied:
                upgrade_tier = TierService._get_upgrade_tier_for_feature(feature)
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={
                        "error": "FeatureNotAvailable",
                        "message": f"The '{feature}' feature is not available on free tier",
                        "current_tier": "free",
                        "required_tier": upgrade_tier,
                        "upgrade_url": "https://dashboard.encypher.com/billing",
                        "features_available": TierService.get_tier_features(tier),
                    },
                )
            return is_available

        # Get organization from database
        result = await db.execute(select(Organization).where(Organization.organization_id == organization_id))
        org = result.scalar_one_or_none()

        if not org:
            if raise_on_denied:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
            return False

        # Check feature availability for tier
        tier = _coerce_tier(org.tier)
        is_available = TierService.is_feature_available(tier, feature)

        if not is_available and raise_on_denied:
            # Get upgrade tier suggestion
            upgrade_tier = TierService._get_upgrade_tier_for_feature(feature)

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "FeatureNotAvailable",
                    "message": f"The '{feature}' feature is not available on your current plan ({tier.value})",
                    "current_tier": tier.value,
                    "required_tier": upgrade_tier,
                    "upgrade_url": "https://dashboard.encypher.com/billing",
                    "features_available": TierService.get_tier_features(tier),
                },
            )

        return is_available

    @staticmethod
    def _get_upgrade_tier_for_feature(feature: str) -> str:
        """
        Get the minimum tier required for a feature.

        Args:
            feature: Feature name

        Returns:
            Tier name that provides the feature
        """
        tier_order = [
            OrganizationTier.FREE,
            OrganizationTier.ENTERPRISE,
            OrganizationTier.STRATEGIC_PARTNER,
        ]

        for tier in tier_order:
            if TierService.is_feature_available(tier, feature):
                return str(tier.value)

        return str(OrganizationTier.ENTERPRISE.value)

    @staticmethod
    async def get_organization_tier_info(db: AsyncSession, organization_id: str) -> Dict[str, Any]:
        """
        Get comprehensive tier information for an organization.

        Args:
            db: Database session
            organization_id: Organization identifier

        Returns:
            Dictionary with tier info, features, quotas, and usage
        """
        # Handle user-level keys (synthetic org IDs)
        if organization_id.startswith("user_"):
            tier = OrganizationTier.FREE
            features = TierService.get_tier_features(tier)
            rate_limit = TierService.get_rate_limit(tier)

            quotas = {}
            for quota_type in QuotaType:
                limit = TierService.get_quota_limit(tier, quota_type)
                quotas[quota_type.value] = {
                    "limit": limit if limit >= 0 else "unlimited",
                    "used": 0,
                    "remaining": "unlimited" if limit < 0 else limit,
                    "available": limit != 0,
                }

            return {
                "organization_id": organization_id,
                "organization_name": "Personal Account",
                "tier": "free",
                "tier_display_name": "Free",
                "features": features,
                "rate_limit": rate_limit if rate_limit >= 0 else "unlimited",
                "quotas": quotas,
                "coalition": {
                    "member": True,
                    "opted_out": False,
                    "publisher_share": 60,
                    "encypher_share": 40,
                },
                "reset_date": TierService._get_reset_date().isoformat(),
            }

        # Get organization from database
        result = await db.execute(select(Organization).where(Organization.organization_id == organization_id))
        org = result.scalar_one_or_none()

        if not org:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

        tier = _coerce_tier(org.tier)

        # Get tier info
        features = TierService.get_tier_features(tier)
        rate_limit = TierService.get_rate_limit(tier)

        # Build quota status
        quotas = {}
        for quota_type in QuotaType:
            limit = TierService.get_quota_limit(tier, quota_type)
            usage = TierService._get_current_usage(org, quota_type)

            quotas[quota_type.value] = {
                "limit": limit if limit >= 0 else "unlimited",
                "used": usage,
                "remaining": "unlimited" if limit < 0 else max(0, limit - usage),
                "available": limit != 0,
            }

        return {
            "organization_id": organization_id,
            "organization_name": org.organization_name,
            "tier": tier.value,
            "tier_display_name": TierService._get_tier_display_name(tier),
            "features": features,
            "rate_limit": rate_limit if rate_limit >= 0 else "unlimited",
            "quotas": quotas,
            "coalition": {
                "member": org.coalition_member,
                "opted_out": org.coalition_opted_out,
                "publisher_share": org.coalition_rev_share_publisher,
                "encypher_share": org.coalition_rev_share_encypher,
            },
            "reset_date": TierService._get_reset_date().isoformat(),
        }

    @staticmethod
    def _get_tier_display_name(tier: OrganizationTier) -> str:
        """Get human-readable tier name."""
        tier = _coerce_tier(tier)
        display_names = {
            OrganizationTier.FREE: "Free",
            OrganizationTier.ENTERPRISE: "Enterprise",
            OrganizationTier.STRATEGIC_PARTNER: "Strategic Partner",
        }
        return str(display_names.get(tier, tier.value))

    @staticmethod
    def _get_current_usage(org: Organization, quota_type: QuotaType) -> int:
        """Get current usage for a quota type."""
        field_name = QUOTA_FIELD_MAPPING.get(quota_type)
        if not field_name:
            return 0

        return getattr(org, field_name, 0)

    @staticmethod
    def _get_reset_date() -> datetime:
        """Get the date when quotas reset (first day of next month)."""
        now = datetime.utcnow()
        if now.month == 12:
            return datetime(now.year + 1, 1, 1)
        else:
            return datetime(now.year, now.month + 1, 1)

    @staticmethod
    async def set_organization_tier(db: AsyncSession, organization_id: str, new_tier: OrganizationTier, update_features: bool = True) -> Organization:
        """
        Update an organization's tier and optionally sync feature flags.

        Args:
            db: Database session
            organization_id: Organization identifier
            new_tier: New tier to set
            update_features: If True, update feature flags to match tier

        Returns:
            Updated organization
        """
        # Get organization
        result = await db.execute(select(Organization).where(Organization.organization_id == organization_id))
        org = result.scalar_one_or_none()

        if not org:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

        old_tier = _coerce_tier(org.tier)
        new_tier = _coerce_tier(new_tier)
        org_any = cast(Any, org)
        org_any.tier = new_tier.value

        # Update feature flags if requested
        if update_features:
            features = TierService.get_tier_features(new_tier)
            org_any.merkle_enabled = features.get("merkle", False)
            org_any.sentence_tracking_enabled = features.get("sentence_tracking", False)
            org_any.streaming_enabled = features.get("streaming", False)
            org_any.bulk_operations_enabled = features.get("batch_operations", False)
            org_any.byok_enabled = features.get("byok", False)
            org_any.team_management_enabled = features.get("team_management", False)
            org_any.audit_logs_enabled = features.get("audit_logs", False)
            org_any.sso_enabled = features.get("sso", False)
            org_any.custom_assertions_enabled = features.get("custom_assertions", False)
            org_any.fuzzy_fingerprint_enabled = features.get("fuzzy_fingerprint", False)
            org_any.advanced_analytics_enabled = features.get("advanced_analytics", False)

        # Update coalition rev share
        pub_share, enc_share = TierService.get_rev_share(new_tier)
        org_any.coalition_rev_share_publisher = pub_share
        org_any.coalition_rev_share_encypher = enc_share

        await db.commit()
        await db.refresh(org)

        logger.info(f"Organization {organization_id} tier changed from {old_tier.value} to {new_tier.value}")

        return org


# FastAPI dependency for feature access checking
def require_feature(feature: str):
    """
    FastAPI dependency that requires a specific feature.

    Usage:
        @router.post("/merkle/encode")
        async def encode(
            _: None = Depends(require_feature("merkle")),
            org_id: str = Depends(get_current_org_id),
            db: AsyncSession = Depends(get_db)
        ):
            ...
    """

    async def _check_feature(request: Request, db: AsyncSession, organization_id: str):
        await TierService.check_feature_access(db, organization_id, feature)

    return _check_feature
