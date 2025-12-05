"""
Quota enforcement system for API usage limits.

Tracks and enforces usage quotas based on organization tier.
"""
import logging
from datetime import datetime
from enum import Enum
from typing import Dict

from fastapi import HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Organization, OrganizationTier

logger = logging.getLogger(__name__)


class QuotaType(str, Enum):
    """Types of quotas that can be enforced."""
    MERKLE_ENCODING = "merkle_encoding"
    MERKLE_ATTRIBUTION = "merkle_attribution"
    MERKLE_PLAGIARISM = "merkle_plagiarism"
    API_CALLS = "api_calls"
    SENTENCES_TRACKED = "sentences_tracked"
    BATCH_OPERATIONS = "batch_operations"
    C2PA_SIGNATURES = "c2pa_signatures"  # Soft limit for abuse prevention


# Rate limits by tier (requests per second)
TIER_RATE_LIMITS: Dict[OrganizationTier, int] = {
    OrganizationTier.STARTER: 10,
    OrganizationTier.PROFESSIONAL: 50,
    OrganizationTier.BUSINESS: 200,
    OrganizationTier.ENTERPRISE: -1,  # Unlimited
    OrganizationTier.STRATEGIC_PARTNER: -1,  # Unlimited
}


# Coalition revenue share by tier (publisher_share, encypher_share)
TIER_REV_SHARE: Dict[OrganizationTier, tuple] = {
    OrganizationTier.STARTER: (65, 35),
    OrganizationTier.PROFESSIONAL: (70, 30),
    OrganizationTier.BUSINESS: (75, 25),
    OrganizationTier.ENTERPRISE: (80, 20),
    OrganizationTier.STRATEGIC_PARTNER: (85, 15),
}


# Feature availability by tier
TIER_FEATURES: Dict[OrganizationTier, Dict[str, bool]] = {
    OrganizationTier.STARTER: {
        "c2pa_signing": True,
        "verification": True,
        "sentence_tracking": False,
        "merkle": False,
        "streaming": False,
        "batch_operations": False,
        "byok": False,
        "team_management": False,
        "audit_logs": False,
        "sso": False,
        "custom_assertions": False,
        "advanced_analytics": False,
    },
    OrganizationTier.PROFESSIONAL: {
        "c2pa_signing": True,
        "verification": True,
        "sentence_tracking": True,
        "merkle": True,  # Sentence-level Merkle roots available for all paid tiers
        "streaming": True,
        "batch_operations": False,
        "byok": True,
        "team_management": False,
        "audit_logs": False,
        "sso": False,
        "custom_assertions": False,
        "advanced_analytics": True,
    },
    OrganizationTier.BUSINESS: {
        "c2pa_signing": True,
        "verification": True,
        "sentence_tracking": True,
        "merkle": True,
        "streaming": True,
        "batch_operations": True,
        "byok": True,
        "team_management": True,
        "audit_logs": True,
        "sso": False,
        "custom_assertions": False,
        "advanced_analytics": True,
    },
    OrganizationTier.ENTERPRISE: {
        "c2pa_signing": True,
        "verification": True,
        "sentence_tracking": True,
        "merkle": True,
        "streaming": True,
        "batch_operations": True,
        "byok": True,
        "team_management": True,
        "audit_logs": True,
        "sso": True,
        "custom_assertions": True,
        "advanced_analytics": True,
    },
    OrganizationTier.STRATEGIC_PARTNER: {
        "c2pa_signing": True,
        "verification": True,
        "sentence_tracking": True,
        "merkle": True,
        "streaming": True,
        "batch_operations": True,
        "byok": True,
        "team_management": True,
        "audit_logs": True,
        "sso": True,
        "custom_assertions": True,
        "advanced_analytics": True,
    },
}


# Quota limits by tier (per month)
# -1 means unlimited
TIER_QUOTAS: Dict[OrganizationTier, Dict[QuotaType, int]] = {
    OrganizationTier.STARTER: {
        QuotaType.C2PA_SIGNATURES: 10000,  # Soft cap for abuse prevention (marketed as "unlimited")
        QuotaType.SENTENCES_TRACKED: 0,  # Not available
        QuotaType.MERKLE_ENCODING: 0,  # Not available
        QuotaType.MERKLE_ATTRIBUTION: 0,
        QuotaType.MERKLE_PLAGIARISM: 0,
        QuotaType.BATCH_OPERATIONS: 0,
        QuotaType.API_CALLS: 10000,
    },
    OrganizationTier.PROFESSIONAL: {
        QuotaType.C2PA_SIGNATURES: -1,  # Unlimited
        QuotaType.SENTENCES_TRACKED: 50000,
        QuotaType.MERKLE_ENCODING: 5000,  # Sentence-level Merkle available for paid tiers
        QuotaType.MERKLE_ATTRIBUTION: 10000,
        QuotaType.MERKLE_PLAGIARISM: 0,  # Business+ only
        QuotaType.BATCH_OPERATIONS: 0,
        QuotaType.API_CALLS: 50000,
    },
    OrganizationTier.BUSINESS: {
        QuotaType.C2PA_SIGNATURES: -1,  # Unlimited
        QuotaType.SENTENCES_TRACKED: 500000,
        QuotaType.MERKLE_ENCODING: 10000,
        QuotaType.MERKLE_ATTRIBUTION: 50000,
        QuotaType.MERKLE_PLAGIARISM: 5000,
        QuotaType.BATCH_OPERATIONS: 1000,
        QuotaType.API_CALLS: 500000,
    },
    OrganizationTier.ENTERPRISE: {
        QuotaType.C2PA_SIGNATURES: -1,  # Unlimited
        QuotaType.SENTENCES_TRACKED: -1,  # Unlimited
        QuotaType.MERKLE_ENCODING: -1,  # Unlimited
        QuotaType.MERKLE_ATTRIBUTION: -1,
        QuotaType.MERKLE_PLAGIARISM: -1,
        QuotaType.BATCH_OPERATIONS: -1,
        QuotaType.API_CALLS: -1,
    },
    OrganizationTier.STRATEGIC_PARTNER: {
        QuotaType.C2PA_SIGNATURES: -1,  # Unlimited
        QuotaType.SENTENCES_TRACKED: -1,  # Unlimited
        QuotaType.MERKLE_ENCODING: -1,  # Unlimited
        QuotaType.MERKLE_ATTRIBUTION: -1,
        QuotaType.MERKLE_PLAGIARISM: -1,
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
    async def check_quota(
        db: AsyncSession,
        organization_id: str,
        quota_type: QuotaType,
        increment: int = 1,
        tier_override: str = None
    ) -> bool:
        """
        Check if organization has quota available and increment if so.
        
        Args:
            db: Database session
            organization_id: Organization identifier
            quota_type: Type of quota to check
            increment: Amount to increment (default 1)
            tier_override: Optional tier to use instead of DB lookup (for user-level keys)
        
        Returns:
            True if quota available, False if exceeded
        
        Raises:
            HTTPException: If quota exceeded
        """
        # Handle user-level keys (synthetic org IDs like "user_{user_id}")
        # These don't have a record in the organizations table
        if organization_id.startswith("user_"):
            # Use starter tier limits for user-level keys
            tier = OrganizationTier.STARTER
            quota_limit = QuotaManager.get_quota_limit(tier, quota_type)
            
            # For user-level keys, we don't track usage in DB - just check if feature is available
            if quota_limit == 0:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={
                        "error": "FeatureNotAvailable",
                        "message": f"'{quota_type.value}' is not available on starter tier",
                        "current_tier": "starter",
                        "upgrade_url": "https://dashboard.encypherai.com/billing",
                    }
                )
            # Allow the request - user-level keys have generous limits
            logger.debug(f"User-level key {organization_id}: allowing {quota_type.value} (limit: {quota_limit})")
            return True
        
        # Get organization from database for org-level keys
        result = await db.execute(
            select(Organization).where(Organization.organization_id == organization_id)
        )
        org = result.scalar_one_or_none()
        
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )
        
        # Get quota limit for tier
        quota_limit = QuotaManager.get_quota_limit(org.tier, quota_type)
        
        # Quota = 0 means feature not available for this tier
        if quota_limit == 0:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "FeatureNotAvailable",
                    "message": f"'{quota_type.value}' is not available on {org.tier.value} tier",
                    "current_tier": org.tier.value,
                    "upgrade_url": "https://dashboard.encypherai.com/billing",
                }
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
                    "reset_date": QuotaManager._get_reset_date().isoformat()
                }
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
            Quota limit (requests per month)
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
    async def _increment_usage(
        db: AsyncSession,
        org: Organization,
        quota_type: QuotaType,
        increment: int
    ):
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
    async def get_quota_headers(
        db: AsyncSession,
        organization_id: str,
        quota_type: QuotaType
    ) -> dict:
        """
        Get HTTP headers showing quota usage for a specific quota type.
        
        Returns headers like:
        - X-Quota-Limit: 5000
        - X-Quota-Used: 1234
        - X-Quota-Remaining: 3766
        - X-Quota-Reset: 2025-01-01T00:00:00Z
        """
        # Handle user-level keys (synthetic org IDs)
        if organization_id.startswith("user_"):
            limit = QuotaManager.get_quota_limit(OrganizationTier.STARTER, quota_type)
            if limit == -1:
                return {
                    "X-Quota-Limit": "unlimited",
                    "X-Quota-Used": "0",
                    "X-Quota-Remaining": "unlimited",
                    "X-Quota-Reset": QuotaManager._get_reset_date().isoformat(),
                }
            return {
                "X-Quota-Limit": str(limit),
                "X-Quota-Used": "0",  # Not tracked for user-level keys
                "X-Quota-Remaining": str(limit),
                "X-Quota-Reset": QuotaManager._get_reset_date().isoformat(),
            }
        
        result = await db.execute(
            select(Organization).where(Organization.organization_id == organization_id)
        )
        org = result.scalar_one_or_none()
        
        if not org:
            return {}
        
        limit = QuotaManager.get_quota_limit(org.tier, quota_type)
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
    async def get_quota_status(
        db: AsyncSession,
        organization_id: str
    ) -> Dict[str, any]:
        """
        Get quota status for an organization.
        
        Args:
            db: Database session
            organization_id: Organization identifier
        
        Returns:
            Dictionary with quota status for all quota types
        """
        # Handle user-level keys (synthetic org IDs)
        if organization_id.startswith("user_"):
            tier = OrganizationTier.STARTER
            status_dict = {
                "organization_id": organization_id,
                "tier": "starter",
                "reset_date": QuotaManager._get_reset_date().isoformat(),
                "quotas": {}
            }
            
            for quota_type in QuotaType:
                limit = QuotaManager.get_quota_limit(tier, quota_type)
                status_dict["quotas"][quota_type.value] = {
                    "limit": limit,
                    "used": 0,  # Not tracked for user-level keys
                    "remaining": limit if limit > 0 else 0,
                    "percentage_used": 0
                }
            
            return status_dict
        
        # Get organization from database
        result = await db.execute(
            select(Organization).where(Organization.organization_id == organization_id)
        )
        org = result.scalar_one_or_none()
        
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )
        
        status_dict = {
            "organization_id": organization_id,
            "tier": org.tier.value,
            "reset_date": QuotaManager._get_reset_date().isoformat(),
            "quotas": {}
        }
        
        for quota_type in QuotaType:
            limit = QuotaManager.get_quota_limit(org.tier, quota_type)
            usage = QuotaManager._get_current_usage(org, quota_type)
            
            status_dict["quotas"][quota_type.value] = {
                "limit": limit,
                "used": usage,
                "remaining": max(0, limit - usage),
                "percentage_used": round((usage / limit * 100) if limit > 0 else 0, 2)
            }
        
        return status_dict
    
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
                api_calls_this_month=0,
                documents_signed=0,
                sentences_tracked_this_month=0,
                batch_operations_this_month=0,
            )
        )
        await db.commit()
        logger.info("Reset monthly quotas for all organizations")


# Dependency for quota checking
async def check_quota_dependency(
    quota_type: QuotaType,
    organization_id: str,
    db: AsyncSession
):
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
