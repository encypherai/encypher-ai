"""
Auto-provisioning service for organizations and API keys.

Handles automatic creation of organizations, users, and API keys
from external services (SDK, WordPress plugin, CLI, etc.)
"""
import hashlib
import logging
import secrets
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Organization, OrganizationTier
from app.utils.feature_flags import TIER_FEATURES
from app.utils.quota import TIER_QUOTAS, QuotaType

logger = logging.getLogger(__name__)


class ProvisioningService:
    """
    Service for auto-provisioning organizations and API keys.
    
    Provides methods to automatically create organizations, users,
    and API keys from external services.
    """
    
    @staticmethod
    def generate_api_key(prefix: str = "ency_live") -> str:
        """
        Generate a secure API key.
        
        Format: {prefix}_{random_string}
        Example: ency_live_1a2b3c4d5e6f7g8h9i0j
        
        Args:
            prefix: Key prefix (default: ency_live)
        
        Returns:
            Generated API key
        """
        # Generate 32 bytes of random data
        random_bytes = secrets.token_bytes(32)
        # Convert to hex string
        random_hex = random_bytes.hex()
        # Take first 40 characters for readability
        key_suffix = random_hex[:40]
        
        return f"{prefix}_{key_suffix}"
    
    @staticmethod
    def generate_organization_id(email: str) -> str:
        """
        Generate organization ID from email.
        
        Args:
            email: User email
        
        Returns:
            Organization ID (org_xxxxx)
        """
        # Create hash from email
        email_hash = hashlib.sha256(email.encode()).hexdigest()[:12]
        return f"org_{email_hash}"
    
    @staticmethod
    def generate_user_id(email: str) -> str:
        """
        Generate user ID from email.
        
        Args:
            email: User email
        
        Returns:
            User ID (user_xxxxx)
        """
        email_hash = hashlib.sha256(email.encode()).hexdigest()[:12]
        return f"user_{email_hash}"
    
    @staticmethod
    async def auto_provision(
        db: AsyncSession,
        email: str,
        organization_name: Optional[str],
        source: str,
        source_metadata: Optional[Dict[str, Any]],
        tier: str = "free",
        auto_activate: bool = True
    ) -> Tuple[Organization, str, str]:
        """
        Auto-provision an organization, user, and API key.
        
        Args:
            db: Database session
            email: User email
            organization_name: Organization name (auto-generated if None)
            source: Provisioning source (api/sdk/wordpress/etc)
            source_metadata: Additional metadata from source
            tier: Initial tier (default: free)
            auto_activate: Whether to auto-activate (default: True)
        
        Returns:
            Tuple of (Organization, api_key, user_id)
        """
        # Generate IDs
        org_id = ProvisioningService.generate_organization_id(email)
        user_id = ProvisioningService.generate_user_id(email)
        
        # Check if organization already exists
        result = await db.execute(
            select(Organization).where(Organization.organization_id == org_id)
        )
        existing_org = result.scalar_one_or_none()
        
        if existing_org:
            logger.info(f"Organization {org_id} already exists for {email}")
            # Generate new API key for existing org
            api_key = ProvisioningService.generate_api_key()
            return existing_org, api_key, user_id
        
        # Generate organization name if not provided
        if not organization_name:
            # Use email domain as organization name
            domain = email.split('@')[1]
            organization_name = domain.split('.')[0].title()
        
        # Map tier string to enum
        tier_map = {
            "free": OrganizationTier.FREE,
            "professional": OrganizationTier.PROFESSIONAL,
            "enterprise": OrganizationTier.ENTERPRISE
        }
        tier_enum = tier_map.get(tier.lower(), OrganizationTier.FREE)
        
        # Create organization
        org = Organization(
            organization_id=org_id,
            name=organization_name,
            tier=tier_enum,
            merkle_enabled=(tier_enum == OrganizationTier.ENTERPRISE),
            advanced_analytics_enabled=(tier_enum in [OrganizationTier.PROFESSIONAL, OrganizationTier.ENTERPRISE]),
            bulk_operations_enabled=(tier_enum in [OrganizationTier.PROFESSIONAL, OrganizationTier.ENTERPRISE]),
            api_calls_this_month=0,
            merkle_encoding_calls_this_month=0,
            merkle_attribution_calls_this_month=0,
            merkle_plagiarism_calls_this_month=0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(org)
        await db.commit()
        await db.refresh(org)
        
        # Generate API key
        api_key = ProvisioningService.generate_api_key()
        
        # TODO: Store API key in database (api_keys table)
        # For now, we just return it
        
        # Log provisioning event
        logger.info(
            f"Auto-provisioned organization {org_id} for {email} "
            f"from {source} with tier {tier}"
        )
        
        # TODO: Send welcome email
        # TODO: Trigger webhook
        
        return org, api_key, user_id
    
    @staticmethod
    def get_features_for_tier(tier: OrganizationTier) -> Dict[str, bool]:
        """
        Get enabled features for a tier.
        
        Args:
            tier: Organization tier
        
        Returns:
            Dictionary of feature names and enabled status
        """
        TIER_FEATURES.get(tier, set())
        
        return {
            "merkle_trees": tier == OrganizationTier.ENTERPRISE,
            "bulk_operations": tier in [OrganizationTier.PROFESSIONAL, OrganizationTier.ENTERPRISE],
            "advanced_analytics": tier in [OrganizationTier.PROFESSIONAL, OrganizationTier.ENTERPRISE],
            "custom_segmentation": tier in [OrganizationTier.PROFESSIONAL, OrganizationTier.ENTERPRISE],
            "api_webhooks": tier in [OrganizationTier.PROFESSIONAL, OrganizationTier.ENTERPRISE],
            "priority_processing": tier == OrganizationTier.ENTERPRISE,
            "dedicated_resources": tier == OrganizationTier.ENTERPRISE,
            "premium_support": tier in [OrganizationTier.PROFESSIONAL, OrganizationTier.ENTERPRISE],
            "sla_guarantee": tier == OrganizationTier.ENTERPRISE,
        }
    
    @staticmethod
    def get_quota_limits_for_tier(tier: OrganizationTier) -> Dict[str, int]:
        """
        Get quota limits for a tier.
        
        Args:
            tier: Organization tier
        
        Returns:
            Dictionary of quota types and limits
        """
        quotas = TIER_QUOTAS.get(tier, {})
        
        return {
            "api_calls_per_month": quotas.get(QuotaType.API_CALLS, 0),
            "merkle_encoding_per_month": quotas.get(QuotaType.MERKLE_ENCODING, 0),
            "merkle_attribution_per_month": quotas.get(QuotaType.MERKLE_ATTRIBUTION, 0),
            "merkle_plagiarism_per_month": quotas.get(QuotaType.MERKLE_PLAGIARISM, 0),
        }
    
    @staticmethod
    def get_next_steps() -> Dict[str, str]:
        """
        Get next steps and documentation links.
        
        Returns:
            Dictionary of next step links
        """
        return {
            "documentation": "https://docs.encypher.ai/getting-started",
            "api_reference": "https://docs.encypher.ai/api",
            "sdk_guide": "https://docs.encypher.ai/sdk",
            "wordpress_plugin": "https://docs.encypher.ai/wordpress",
            "upgrade": "https://encypher.ai/pricing",
            "support": "https://encypher.ai/support"
        }
    
    @staticmethod
    async def revoke_api_key(
        db: AsyncSession,
        key_id: str,
        reason: Optional[str] = None
    ) -> bool:
        """
        Revoke an API key.
        
        Args:
            db: Database session
            key_id: API key identifier
            reason: Revocation reason
        
        Returns:
            True if revoked, False if not found
        """
        # TODO: Implement API key revocation in database
        logger.info(f"Revoking API key {key_id}: {reason}")
        return True
    
    @staticmethod
    async def list_api_keys(
        db: AsyncSession,
        organization_id: str
    ) -> list[Dict[str, Any]]:
        """
        List API keys for an organization.
        
        Args:
            db: Database session
            organization_id: Organization identifier
        
        Returns:
            List of API key information
        """
        # TODO: Implement API key listing from database
        return []
    
    @staticmethod
    async def validate_api_key(
        db: AsyncSession,
        api_key: str
    ) -> Optional[Organization]:
        """
        Validate an API key and return associated organization.
        
        Args:
            db: Database session
            api_key: API key to validate
        
        Returns:
            Organization if valid, None otherwise
        """
        # TODO: Implement API key validation
        # For now, extract org_id from key and look up
        
        # This is a placeholder - in production, you'd:
        # 1. Hash the API key
        # 2. Look up in api_keys table
        # 3. Check expiration
        # 4. Return associated organization
        
        return None
