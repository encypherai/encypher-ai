"""
Auto-provisioning service for organizations and API keys.

Handles automatic creation of organizations, users, and API keys
from external services (SDK, WordPress plugin, CLI, etc.)
"""

import hashlib
import json
import logging
import secrets
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple

import httpx
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
from cryptography import x509
from cryptography.x509.oid import NameOID
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Organization, OrganizationTier
from app.utils.feature_flags import TIER_FEATURES
from app.utils.quota import TIER_QUOTAS, QuotaType
from app.core.config import settings

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
        auto_activate: bool = True,
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
        result = await db.execute(select(Organization).where(Organization.organization_id == org_id))
        existing_org = result.scalar_one_or_none()

        if existing_org:
            logger.info(f"Organization {org_id} already exists for {email}")
            org = existing_org
        else:
            # Generate organization name if not provided
            if not organization_name:
                # Use email domain as organization name
                domain = email.split("@")[1]
                organization_name = domain.split(".")[0].title()

            # Map tier string to enum
            tier_map = {
                "free": OrganizationTier.FREE,
                "professional": OrganizationTier.PROFESSIONAL,
                "enterprise": OrganizationTier.ENTERPRISE,
            }
            tier_enum = tier_map.get(tier.lower(), OrganizationTier.FREE)

            # Create organization
            org = Organization(
                organization_id=org_id,
                name=organization_name,
                email=email,
                tier=tier_enum,
                merkle_enabled=(tier_enum == OrganizationTier.ENTERPRISE),
                advanced_analytics_enabled=(tier_enum in [OrganizationTier.PROFESSIONAL, OrganizationTier.ENTERPRISE]),
                bulk_operations_enabled=(tier_enum in [OrganizationTier.PROFESSIONAL, OrganizationTier.ENTERPRISE]),
                api_calls_this_month=0,
                merkle_encoding_calls_this_month=0,
                merkle_attribution_calls_this_month=0,
                merkle_plagiarism_calls_this_month=0,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )

            db.add(org)
            await db.commit()
            await db.refresh(org)

        # Auto-provision certificate if needed
        await ProvisioningService._ensure_organization_certificate(
            organization_id=org.organization_id,
            organization_name=org.name,
            authorization=None,
        )

        # Generate API key
        api_key = ProvisioningService.generate_api_key()
        key_hash = hashlib.sha256(api_key.encode("utf-8")).hexdigest()
        key_prefix = api_key[:12]
        key_id = f"key_{api_key[-12:]}"
        scopes = ["sign", "verify", "lookup"]

        await db.execute(
            text(
                """
                INSERT INTO api_keys (
                    id, organization_id, name, key_hash, key_prefix,
                    scopes, created_at, expires_at, is_active
                ) VALUES (
                    :id, :org_id, :name, :key_hash, :key_prefix,
                    CAST(:scopes AS jsonb), :created_at, :expires_at, true
                )
                """
            ),
            {
                "id": key_id,
                "org_id": org.organization_id,
                "name": "Provisioned Key",
                "key_hash": key_hash,
                "key_prefix": key_prefix,
                "scopes": json.dumps(scopes),
                "created_at": datetime.utcnow(),
                "expires_at": None,
            },
        )
        await db.commit()

        # Log provisioning event
        logger.info(f"Auto-provisioned organization {org_id} for {email} from {source} with tier {tier}")

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
            "support": "https://encypher.ai/support",
        }

    @staticmethod
    async def _ensure_organization_certificate(
        organization_id: str,
        organization_name: str,
        authorization: Optional[str] = None,
    ) -> bool:
        """
        Ensure organization has a signing certificate.
        
        If the organization doesn't have a certificate, auto-provision a self-signed
        Ed25519 certificate via auth-service.
        
        Args:
            organization_id: Organization identifier
            organization_name: Organization name for certificate CN
            authorization: Optional auth header to pass to auth-service
            
        Returns:
            True if certificate exists or was created, False on failure
        """
        try:
            headers = {}
            if authorization:
                headers["Authorization"] = authorization
                
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Check if org already has certificate
                context_response = await client.get(
                    f"{settings.AUTH_SERVICE_URL}/api/v1/organizations/internal/{organization_id}/context",
                    headers=headers,
                )
                
                if context_response.status_code == 200:
                    context_data = context_response.json()
                    if context_data.get("data", {}).get("certificate_pem"):
                        logger.debug(f"Organization {organization_id} already has certificate")
                        return True
                
                # Generate self-signed Ed25519 certificate
                private_key = ed25519.Ed25519PrivateKey.generate()
                public_key = private_key.public_key()
                
                # Create certificate
                subject = issuer = x509.Name([
                    x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
                    x509.NameAttribute(NameOID.ORGANIZATION_NAME, organization_name or organization_id),
                    x509.NameAttribute(NameOID.COMMON_NAME, organization_id),
                ])
                
                cert = (
                    x509.CertificateBuilder()
                    .subject_name(subject)
                    .issuer_name(issuer)
                    .public_key(public_key)
                    .serial_number(x509.random_serial_number())
                    .not_valid_before(datetime.utcnow())
                    .not_valid_after(datetime.utcnow() + timedelta(days=3650))  # 10 years
                    .sign(private_key, algorithm=None)  # Ed25519 doesn't need hash algorithm
                )
                
                # Serialize certificate to PEM
                cert_pem = cert.public_bytes(serialization.Encoding.PEM).decode("utf-8")
                
                # Update organization certificate via auth-service internal endpoint
                update_response = await client.patch(
                    f"{settings.AUTH_SERVICE_URL}/api/v1/organizations/internal/{organization_id}/certificate",
                    json={"certificate_pem": cert_pem},
                    headers=headers,
                )
                
                if update_response.status_code in (200, 201):
                    logger.info(f"Auto-provisioned self-signed certificate for organization {organization_id}")
                    return True
                else:
                    logger.warning(
                        f"Failed to provision certificate for {organization_id}: "
                        f"{update_response.status_code} {update_response.text}"
                    )
                    return False
                    
        except Exception as e:
            logger.error(f"Error ensuring certificate for {organization_id}: {e}", exc_info=True)
            return False

    @staticmethod
    async def create_api_key(
        db: AsyncSession,
        organization_id: str,
        name: Optional[str] = None,
        scopes: Optional[list[str]] = None,
        expires_in_days: Optional[int] = None,
        authorization: Optional[str] = None,
    ) -> Dict[str, Any]:
        # Get organization name for certificate provisioning
        org_result = await db.execute(
            text("SELECT name FROM organizations WHERE organization_id = :org_id"),
            {"org_id": organization_id},
        )
        org_row = org_result.fetchone()
        org_name = org_row.name if org_row else organization_id
        
        # Auto-provision certificate if needed
        await ProvisioningService._ensure_organization_certificate(
            organization_id=organization_id,
            organization_name=org_name,
            authorization=authorization,
        )
        
        api_key = ProvisioningService.generate_api_key()
        key_hash = hashlib.sha256(api_key.encode("utf-8")).hexdigest()
        key_prefix = api_key[:12]
        key_id = f"key_{api_key[-12:]}"

        permissions = scopes or ["sign", "verify", "lookup"]
        created_at = datetime.utcnow()
        expires_at = None
        if expires_in_days:
            expires_at = created_at + timedelta(days=expires_in_days)

        await db.execute(
            text(
                """
                INSERT INTO api_keys (
                    id, organization_id, name, key_hash, key_prefix,
                    scopes, created_at, expires_at, is_active
                ) VALUES (
                    :id, :org_id, :name, :key_hash, :key_prefix,
                    CAST(:scopes AS jsonb), :created_at, :expires_at, true
                )
                """
            ),
            {
                "id": key_id,
                "org_id": organization_id,
                "name": name or "Provisioned Key",
                "key_hash": key_hash,
                "key_prefix": key_prefix,
                "scopes": json.dumps(permissions),
                "created_at": created_at,
                "expires_at": expires_at,
            },
        )
        await db.commit()

        return {
            "api_key": api_key,
            "key_id": key_id,
            "organization_id": organization_id,
            "created_at": created_at,
            "expires_at": expires_at,
            "scopes": permissions,
        }

    @staticmethod
    async def revoke_api_key(db: AsyncSession, key_id: str, organization_id: str, reason: Optional[str] = None) -> bool:
        """
        Revoke an API key.

        Args:
            db: Database session
            key_id: API key identifier
            reason: Revocation reason

        Returns:
            True if revoked, False if not found
        """
        result = await db.execute(
            text(
                """
                UPDATE api_keys
                SET is_active = false, revoked_at = :revoked_at, updated_at = :updated_at
                WHERE id = :key_id AND organization_id = :org_id AND revoked_at IS NULL
                RETURNING id
                """
            ),
            {
                "key_id": key_id,
                "org_id": organization_id,
                "revoked_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            },
        )
        row = result.fetchone()
        await db.commit()
        if not row:
            return False

        logger.info(f"Revoked API key {key_id} for org {organization_id}: {reason}")
        return True

    @staticmethod
    async def list_api_keys(db: AsyncSession, organization_id: str) -> list[Dict[str, Any]]:
        """
        List API keys for an organization.

        Args:
            db: Database session
            organization_id: Organization identifier

        Returns:
            List of API key information
        """
        result = await db.execute(
            text(
                """
                SELECT id, name, key_prefix, scopes, created_at, expires_at, last_used_at, is_active, revoked_at
                FROM api_keys
                WHERE organization_id = :org_id
                ORDER BY created_at DESC
                """
            ),
            {"org_id": organization_id},
        )
        rows = result.fetchall()
        keys: list[Dict[str, Any]] = []
        for row in rows:
            scopes = row.scopes or []
            if isinstance(scopes, str):
                scopes = json.loads(scopes)
            keys.append(
                {
                    "id": row.id,
                    "name": row.name,
                    "key_prefix": row.key_prefix,
                    "scopes": scopes,
                    "created_at": row.created_at,
                    "expires_at": row.expires_at,
                    "last_used_at": row.last_used_at,
                    "is_active": bool(row.is_active) and row.revoked_at is None,
                    "revoked_at": row.revoked_at,
                }
            )
        return keys

    @staticmethod
    async def validate_api_key(db: AsyncSession, api_key: str) -> Optional[Organization]:
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
