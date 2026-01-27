"""
Key service business logic
"""

from datetime import datetime
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.exc import ProgrammingError
import httpx
import logging

from ..db.models import ApiKey, KeyUsage, KeyRotation, Organization
from ..models.schemas import ApiKeyCreate, ApiKeyUpdate
from ..core.security import (
    generate_api_key,
    hash_api_key,
    verify_api_key_format,
    generate_key_fingerprint,
)
from ..core.config import settings

logger = logging.getLogger(__name__)


class KeyService:
    """API Key management service"""

    @staticmethod
    def _ensure_organization_exists(db: Session, organization_id: str, authorization: str) -> bool:
        """
        Ensure the organization exists in the key-service database.

        If the organization doesn't exist locally, fetch it from auth-service
        and create a local copy for foreign key integrity.

        Args:
            db: Database session
            organization_id: The organization ID to ensure exists
            authorization: Bearer token to authenticate with auth-service

        Returns:
            True if organization exists or was created, False on failure
        """
        # Check if org already exists locally
        existing_org = db.query(Organization).filter(Organization.id == organization_id).first()
        if existing_org:
            return True

        # Fetch organization info from auth-service
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(
                    f"{settings.AUTH_SERVICE_URL}/api/v1/organizations/{organization_id}",
                    headers={"Authorization": authorization},
                )

                if response.status_code != 200:
                    logger.error(f"Failed to fetch org {organization_id} from auth-service: {response.status_code}")
                    return False

                payload = response.json()
                org_data = payload.get("data") if isinstance(payload, dict) else payload

                if not org_data:
                    logger.error(f"No org data returned for {organization_id}")
                    return False

                # Create local organization record
                local_org = Organization(
                    id=org_data.get("id", organization_id),
                    name=org_data.get("name", "Unknown Organization"),
                    slug=org_data.get("slug"),
                    email=org_data.get("email", f"{organization_id}@placeholder.local"),
                    tier=org_data.get("tier", "starter"),
                    features=org_data.get("features", {}),
                    monthly_api_limit=org_data.get("monthly_api_limit", 10000),
                    monthly_api_usage=org_data.get("monthly_api_usage", 0),
                    coalition_member=org_data.get("coalition_member", True),
                    coalition_rev_share=org_data.get("coalition_rev_share", 65),
                )

                db.add(local_org)
                db.commit()
                logger.info(f"Created local org record for {organization_id}")
                return True

        except httpx.RequestError as e:
            logger.error(f"Failed to connect to auth-service: {e}")
            return False
        except Exception as e:
            logger.error(f"Error ensuring org exists: {e}")
            db.rollback()
            return False

    @staticmethod
    def _ensure_user_has_organization(db: Session, user_id: str) -> Optional[str]:
        """
        Try to find or create an organization for the user.

        Note: The key-service may be on a different database than auth-service,
        so organization_members table may not exist here. In that case, we
        return None and the key will be user-level only.

        Returns the organization_id or None if not available.
        """
        from sqlalchemy import text

        # The key-service database may not have the organization tables
        # (they're managed by auth-service on a different DB)
        # Just return None - the key will work as a user-level key
        return None

    @staticmethod
    def create_key(
        db: Session,
        user_id: str,
        key_data: ApiKeyCreate,
        organization_id: str = None,
        authorization: str = None,
    ) -> Tuple[ApiKey, str]:
        """
        Create a new API key
        Returns: (ApiKey model, actual key string)

        If organization_id is not provided, looks up user's default organization.

        Args:
            db: Database session
            user_id: ID of the user creating the key
            key_data: Key creation data (name, permissions, etc.)
            organization_id: Optional organization ID to link the key to
            authorization: Bearer token for auth-service calls (required if organization_id is set)
        """
        from sqlalchemy import text

        # If organization_id is provided, ensure it exists in our local DB
        # This syncs the org from auth-service if needed
        if organization_id and authorization:
            if not KeyService._ensure_organization_exists(db, organization_id, authorization):
                raise ValueError(f"Organization {organization_id} not found or could not be synced")

        # Generate new API key
        api_key = generate_api_key()
        key_hash = hash_api_key(api_key)
        fingerprint = generate_key_fingerprint(api_key)

        # Create key prefix for display (first 12 chars)
        key_prefix = api_key[:12] + "..."

        # If no org provided, the key will be user-level only
        # Note: Key-service uses a separate database from auth-service,
        # so we can't query organization_members here. User-level keys
        # are handled by verify_key_with_org() which returns a synthetic org context.

        # Create database record
        db_key = ApiKey(
            user_id=user_id,
            organization_id=organization_id,  # Link to user's org
            name=key_data.name,
            key_hash=key_hash,
            key_prefix=key_prefix,
            fingerprint=fingerprint,
            permissions=key_data.permissions,
            description=key_data.description,
            expires_at=key_data.expires_at,
            created_by=user_id,
        )

        db.add(db_key)
        db.commit()
        db.refresh(db_key)

        return db_key, api_key

    @staticmethod
    def get_user_keys(db: Session, user_id: str, include_revoked: bool = False) -> List[ApiKey]:
        """Get all API keys for a user"""
        query = db.query(ApiKey).filter(ApiKey.user_id == user_id)

        if not include_revoked:
            query = query.filter(ApiKey.is_revoked == False)

        return query.order_by(ApiKey.created_at.desc()).all()

    @staticmethod
    def get_org_keys(db: Session, organization_id: str, include_revoked: bool = False) -> List[ApiKey]:
        """Get all API keys for an organization"""
        query = db.query(ApiKey).filter(ApiKey.organization_id == organization_id)

        if not include_revoked:
            query = query.filter(ApiKey.is_revoked == False)

        return query.order_by(ApiKey.created_at.desc()).all()

    @staticmethod
    def get_key_by_id(
        db: Session,
        key_id: str,
        user_id: Optional[str] = None,
        organization_id: Optional[str] = None,
    ) -> Optional[ApiKey]:
        """Get a specific API key by ID"""
        query = db.query(ApiKey).filter(ApiKey.id == key_id)

        if organization_id:
            query = query.filter(ApiKey.organization_id == organization_id)
        elif user_id:
            query = query.filter(ApiKey.user_id == user_id)
        else:
            return None

        return query.first()

    @staticmethod
    def verify_key(db: Session, api_key: str) -> Optional[ApiKey]:
        """
        Verify an API key and return the key record if valid
        """
        # Check format
        if not verify_api_key_format(api_key):
            return None

        # Hash the key
        key_hash = hash_api_key(api_key)

        # Find key in database
        db_key = (
            db.query(ApiKey)
            .filter(
                ApiKey.key_hash == key_hash,
                ApiKey.is_active == True,
                ApiKey.is_revoked == False,
            )
            .first()
        )

        if not db_key:
            return None

        # Check expiration
        if db_key.expires_at and db_key.expires_at < datetime.utcnow():
            return None

        # Update last used
        db_key.last_used_at = datetime.utcnow()
        db_key.usage_count += 1
        db.commit()

        return db_key

    @staticmethod
    def verify_key_minimal(db: Session, api_key: str) -> Optional[dict]:
        """Verify an API key and return minimal key identity/permissions.

        This method is intended for the long-term architecture where each service
        owns its data and no service relies on duplicated/shared tables.

        Returns:
            dict with key_id, organization_id, user_id, permissions
            or None if invalid
        """
        from sqlalchemy import text

        if not verify_api_key_format(api_key):
            return None

        key_hash = hash_api_key(api_key)

        result = db.execute(
            text(
                """
                SELECT
                    k.id as key_id,
                    k.organization_id,
                    k.user_id,
                    k.permissions as key_permissions,
                    k.is_active,
                    k.is_revoked,
                    k.expires_at
                FROM api_keys k
                WHERE k.key_hash = :key_hash
                """
            ),
            {"key_hash": key_hash},
        ).fetchone()

        if not result:
            return None

        if not result.is_active or result.is_revoked:
            return None

        if result.expires_at and result.expires_at < datetime.utcnow():
            return None

        try:
            db.execute(
                text(
                    """
                    UPDATE api_keys
                    SET last_used_at = NOW(), usage_count = usage_count + 1
                    WHERE key_hash = :key_hash
                    """
                ),
                {"key_hash": key_hash},
            )
            db.commit()
        except Exception:
            db.rollback()

        permissions = result.key_permissions if isinstance(result.key_permissions, list) else []
        return {
            "key_id": result.key_id,
            "organization_id": result.organization_id,
            "user_id": result.user_id,
            "permissions": permissions,
        }

    @staticmethod
    def verify_key_with_org(db: Session, api_key: str) -> Optional[dict]:
        """
        Verify an API key and return full organization context.
        This is the unified auth method used by all services.

        Supports both:
        - Organization-level keys (linked to organization_id)
        - User-level keys (linked to user_id, no organization)

        Returns:
            dict with organization_id, tier, features, permissions
            or None if invalid
        """
        from sqlalchemy import text

        # Check format
        if not verify_api_key_format(api_key):
            return None

        # Hash the key
        key_hash = hash_api_key(api_key)

        # First try: Query key with organization join (org-level keys)
        # Note: certificate_pem column will be added by auth-service migration 005
        # For now, we query without it and fetch separately if needed
        query_with_certificate = text("""
            SELECT 
                k.id as key_id,
                k.organization_id,
                k.user_id,
                k.permissions as key_permissions,
                k.is_active,
                k.is_revoked,
                k.expires_at,
                o.name as organization_name,
                o.tier,
                o.features,
                o.monthly_api_limit,
                o.monthly_api_usage,
                o.coalition_member,
                o.coalition_rev_share,
                o.certificate_pem
            FROM api_keys k
            LEFT JOIN organizations o ON k.organization_id = o.id
            WHERE k.key_hash = :key_hash
        """)

        query_without_certificate = text("""
            SELECT 
                k.id as key_id,
                k.organization_id,
                k.user_id,
                k.permissions as key_permissions,
                k.is_active,
                k.is_revoked,
                k.expires_at,
                o.name as organization_name,
                o.tier,
                o.features,
                o.monthly_api_limit,
                o.monthly_api_usage,
                o.coalition_member,
                o.coalition_rev_share
            FROM api_keys k
            LEFT JOIN organizations o ON k.organization_id = o.id
            WHERE k.key_hash = :key_hash
        """)

        try:
            result = db.execute(query_with_certificate, {"key_hash": key_hash}).fetchone()
        except ProgrammingError as exc:
            message = str(getattr(exc, "orig", exc)).lower()
            if "certificate_pem" in message and ("does not exist" in message or "undefinedcolumn" in message):
                # The failed SELECT leaves the transaction in an aborted state on Postgres.
                # We must rollback before retrying any subsequent SQL.
                try:
                    db.rollback()
                except Exception:
                    pass
                result = db.execute(query_without_certificate, {"key_hash": key_hash}).fetchone()
            else:
                raise

        if not result:
            return None

        # Check key status
        if not result.is_active or result.is_revoked:
            return None

        # Check expiration
        if result.expires_at and result.expires_at < datetime.utcnow():
            return None

        # Update usage (fire and forget style - don't block on this)
        try:
            db.execute(
                text("""
                UPDATE api_keys 
                SET last_used_at = NOW(), usage_count = usage_count + 1
                WHERE key_hash = :key_hash
            """),
                {"key_hash": key_hash},
            )
            db.commit()
        except Exception:
            db.rollback()  # Don't fail auth if usage update fails

        # Handle user-level keys (no organization linked)
        if not result.organization_id:
            # User-level key - provide default starter tier context
            # Mark as demo so they can use demo signing keys for testing
            key_permissions = result.key_permissions if isinstance(result.key_permissions, list) else ["sign", "verify"]

            # Check if key has special permissions that enable features
            has_merkle = "merkle" in key_permissions
            is_super_admin = "admin" in key_permissions or "super_admin" in key_permissions

            # SHORT-TERM FIX: Hardcoded superadmin user IDs
            # TODO: Remove after shared core DB migration (see PRD_Shared_Core_DB.md)
            # These users get full enterprise access regardless of key permissions
            SUPERADMIN_USER_IDS = {
                "a1621dd6-3298-473f-b2ad-232ca72c3df5",  # erik.svilich@encypherai.com
            }
            if result.user_id in SUPERADMIN_USER_IDS:
                is_super_admin = True

            return {
                "key_id": result.key_id,
                "user_id": result.user_id,
                "organization_id": f"user_{result.user_id}",  # Synthetic org ID
                "organization_name": "Personal Account",
                "tier": "enterprise" if is_super_admin else "starter",  # Superadmins get enterprise tier
                "is_demo": True,  # Allow using demo private key for signing
                "certificate_pem": None,
                "features": {
                    "team_management": is_super_admin,
                    "audit_logs": is_super_admin,
                    "merkle_enabled": has_merkle or is_super_admin,
                    "bulk_operations": is_super_admin,
                    "sentence_tracking": is_super_admin,
                    "streaming": True,
                    "byok": is_super_admin,
                    "sso": is_super_admin,
                    "custom_assertions": is_super_admin,
                    "max_team_members": -1 if is_super_admin else 1,
                    "is_super_admin": is_super_admin,
                },
                "permissions": key_permissions,
                "monthly_api_limit": -1 if is_super_admin else 10000,  # Unlimited for super admin
                "monthly_api_usage": 0,
                "coalition_member": True,
                "coalition_rev_share": 65,
            }

        # Return organization context for org-level keys
        return {
            "key_id": result.key_id,
            "organization_id": result.organization_id,
            "organization_name": result.organization_name,
            "tier": result.tier,
            "features": result.features if isinstance(result.features, dict) else {},
            "permissions": result.key_permissions if isinstance(result.key_permissions, list) else [],
            "monthly_api_limit": result.monthly_api_limit,
            "monthly_api_usage": result.monthly_api_usage,
            "coalition_member": result.coalition_member,
            "coalition_rev_share": result.coalition_rev_share,
            "certificate_pem": getattr(result, "certificate_pem", None),
        }

    @staticmethod
    def update_key(
        db: Session,
        key_id: str,
        user_id: str,
        update_data: ApiKeyUpdate,
        organization_id: Optional[str] = None,
    ) -> Optional[ApiKey]:
        """Update an API key"""
        db_key = KeyService.get_key_by_id(db, key_id, user_id=user_id, organization_id=organization_id)

        if not db_key:
            return None

        # Update fields
        if update_data.name is not None:
            db_key.name = update_data.name

        if update_data.description is not None:
            db_key.description = update_data.description

        if update_data.permissions is not None:
            db_key.permissions = update_data.permissions

        db_key.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_key)

        return db_key

    @staticmethod
    def revoke_key(db: Session, key_id: str, user_id: str, organization_id: Optional[str] = None) -> bool:
        """Revoke an API key"""
        db_key = KeyService.get_key_by_id(db, key_id, user_id=user_id, organization_id=organization_id)

        if not db_key:
            return False

        db_key.is_revoked = True
        db_key.is_active = False
        db_key.revoked_at = datetime.utcnow()
        db.commit()

        return True

    @staticmethod
    def revoke_keys_by_user(
        db: Session,
        organization_id: str,
        target_user_id: str,
        actor_user_id: str,
    ) -> int:
        """Revoke all API keys in an organization created by a specific user"""
        query = db.query(ApiKey).filter(
            ApiKey.organization_id == organization_id,
            ApiKey.created_by == target_user_id,
            ApiKey.is_revoked == False,
        )

        revoked_count = query.update(
            {
                ApiKey.is_revoked: True,
                ApiKey.is_active: False,
                ApiKey.revoked_at: datetime.utcnow(),
                ApiKey.updated_at: datetime.utcnow(),
            },
            synchronize_session=False,
        )
        db.commit()

        return revoked_count

    @staticmethod
    def rotate_key(
        db: Session,
        key_id: str,
        user_id: str,
        reason: Optional[str] = None,
        organization_id: Optional[str] = None,
        authorization: str = None,
    ) -> Optional[Tuple[ApiKey, str]]:
        """
        Rotate an API key (create new one, revoke old one)
        Returns: (new ApiKey model, new key string) or None
        """
        old_key = KeyService.get_key_by_id(db, key_id, user_id=user_id, organization_id=organization_id)

        if not old_key:
            return None

        # Create new key with same properties
        new_key_data = ApiKeyCreate(
            name=old_key.name,
            description=old_key.description,
            permissions=old_key.permissions,
            expires_at=old_key.expires_at,
        )

        new_db_key, new_api_key = KeyService.create_key(
            db,
            user_id,
            new_key_data,
            organization_id=organization_id or old_key.organization_id,
            authorization=authorization,
        )

        # Revoke old key
        old_key.is_revoked = True
        old_key.is_active = False
        old_key.revoked_at = datetime.utcnow()

        # Record rotation
        rotation = KeyRotation(
            old_key_id=old_key.id,
            new_key_id=new_db_key.id,
            organization_id=organization_id or old_key.organization_id,
            reason=reason,
            rotated_by=user_id,
        )

        db.add(rotation)
        db.commit()

        return new_db_key, new_api_key

    @staticmethod
    def log_key_usage(
        db: Session,
        key_id: str,
        user_id: str,
        endpoint: Optional[str] = None,
        method: Optional[str] = None,
        status_code: Optional[int] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> KeyUsage:
        """Log API key usage"""
        usage = KeyUsage(
            key_id=key_id,
            user_id=user_id,
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        db.add(usage)
        db.commit()
        db.refresh(usage)

        return usage

    @staticmethod
    def get_key_usage_stats(db: Session, key_id: str, user_id: str, organization_id: Optional[str] = None) -> dict:
        """Get usage statistics for an API key"""
        # Verify key belongs to user
        db_key = KeyService.get_key_by_id(db, key_id, user_id=user_id, organization_id=organization_id)
        if not db_key:
            return {}

        # Get total requests
        total_requests = db.query(KeyUsage).filter(KeyUsage.key_id == key_id).count()

        # Get requests by endpoint
        endpoint_stats = (
            db.query(KeyUsage.endpoint, func.count(KeyUsage.id).label("count")).filter(KeyUsage.key_id == key_id).group_by(KeyUsage.endpoint).all()
        )

        requests_by_endpoint = {stat.endpoint: stat.count for stat in endpoint_stats}

        return {
            "key_id": key_id,
            "total_requests": total_requests,
            "last_used": db_key.last_used_at,
            "requests_by_endpoint": requests_by_endpoint,
        }
