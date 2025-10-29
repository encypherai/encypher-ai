"""
Quota enforcement system for API usage limits.

Tracks and enforces usage quotas based on organization tier.
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict
from enum import Enum

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from fastapi import HTTPException, status

from app.models.organization import Organization, OrganizationTier

logger = logging.getLogger(__name__)


class QuotaType(str, Enum):
    """Types of quotas that can be enforced."""
    MERKLE_ENCODING = "merkle_encoding"
    MERKLE_ATTRIBUTION = "merkle_attribution"
    MERKLE_PLAGIARISM = "merkle_plagiarism"
    API_CALLS = "api_calls"


# Quota limits by tier (per month)
TIER_QUOTAS: Dict[OrganizationTier, Dict[QuotaType, int]] = {
    OrganizationTier.FREE: {
        QuotaType.MERKLE_ENCODING: 0,  # Not available
        QuotaType.MERKLE_ATTRIBUTION: 0,
        QuotaType.MERKLE_PLAGIARISM: 0,
        QuotaType.API_CALLS: 1000,
    },
    OrganizationTier.PROFESSIONAL: {
        QuotaType.MERKLE_ENCODING: 0,  # Not available
        QuotaType.MERKLE_ATTRIBUTION: 0,
        QuotaType.MERKLE_PLAGIARISM: 0,
        QuotaType.API_CALLS: 10000,
    },
    OrganizationTier.ENTERPRISE: {
        QuotaType.MERKLE_ENCODING: 1000,
        QuotaType.MERKLE_ATTRIBUTION: 5000,
        QuotaType.MERKLE_PLAGIARISM: 500,
        QuotaType.API_CALLS: 100000,
    }
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
        increment: int = 1
    ) -> bool:
        """
        Check if organization has quota available and increment if so.
        
        Args:
            db: Database session
            organization_id: Organization identifier
            quota_type: Type of quota to check
            increment: Amount to increment (default 1)
        
        Returns:
            True if quota available, False if exceeded
        
        Raises:
            HTTPException: If quota exceeded
        """
        # Get organization
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
        # Get organization
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
                api_calls_this_month=0
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
