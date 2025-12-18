"""
Key service business logic
"""
from datetime import datetime
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..db.models import ApiKey, KeyUsage, KeyRotation
from ..models.schemas import ApiKeyCreate, ApiKeyUpdate
from ..core.security import (
    generate_api_key,
    hash_api_key,
    verify_api_key_format,
    generate_key_fingerprint,
)


class KeyService:
    """API Key management service"""

    @staticmethod
    def create_key(db: Session, user_id: str, key_data: ApiKeyCreate) -> Tuple[ApiKey, str]:
        """
        Create a new API key
        Returns: (ApiKey model, actual key string)
        """
        # Generate new API key
        api_key = generate_api_key()
        key_hash = hash_api_key(api_key)
        fingerprint = generate_key_fingerprint(api_key)

        # Create key prefix for display (first 12 chars)
        key_prefix = api_key[:12] + "..."

        # Create database record
        db_key = ApiKey(
            user_id=user_id,
            name=key_data.name,
            key_hash=key_hash,
            key_prefix=key_prefix,
            fingerprint=fingerprint,
            permissions=key_data.permissions,
            description=key_data.description,
            expires_at=key_data.expires_at,
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
    def get_key_by_id(db: Session, key_id: str, user_id: str) -> Optional[ApiKey]:
        """Get a specific API key by ID"""
        return db.query(ApiKey).filter(
            ApiKey.id == key_id,
            ApiKey.user_id == user_id
        ).first()

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
        db_key = db.query(ApiKey).filter(
            ApiKey.key_hash == key_hash,
            ApiKey.is_active == True,
            ApiKey.is_revoked == False,
        ).first()

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
        result = db.execute(text("""
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
        """), {"key_hash": key_hash}).fetchone()

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
            db.execute(text("""
                UPDATE api_keys 
                SET last_used_at = NOW(), usage_count = usage_count + 1
                WHERE key_hash = :key_hash
            """), {"key_hash": key_hash})
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
            
            return {
                "key_id": result.key_id,
                "user_id": result.user_id,
                "organization_id": f"user_{result.user_id}",  # Synthetic org ID
                "organization_name": "Personal Account",
                "tier": "starter",  # Default tier for user keys
                "is_demo": True,  # Allow using demo private key for signing
                "features": {
                    "team_management": False,
                    "audit_logs": False,
                    "merkle_enabled": has_merkle,  # Enable if key has merkle permission
                    "bulk_operations": False,
                    "sentence_tracking": False,
                    "streaming": True,
                    "byok": False,
                    "sso": False,
                    "custom_assertions": False,
                    "max_team_members": 1,
                },
                "permissions": key_permissions,
                "monthly_api_limit": 10000,  # Starter tier limit
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
        }

    @staticmethod
    def update_key(db: Session, key_id: str, user_id: str, update_data: ApiKeyUpdate) -> Optional[ApiKey]:
        """Update an API key"""
        db_key = KeyService.get_key_by_id(db, key_id, user_id)

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
    def revoke_key(db: Session, key_id: str, user_id: str) -> bool:
        """Revoke an API key"""
        db_key = KeyService.get_key_by_id(db, key_id, user_id)

        if not db_key:
            return False

        db_key.is_revoked = True
        db_key.is_active = False
        db_key.revoked_at = datetime.utcnow()
        db.commit()

        return True

    @staticmethod
    def rotate_key(
        db: Session,
        key_id: str,
        user_id: str,
        reason: Optional[str] = None
    ) -> Optional[Tuple[ApiKey, str]]:
        """
        Rotate an API key (create new one, revoke old one)
        Returns: (new ApiKey model, new key string) or None
        """
        old_key = KeyService.get_key_by_id(db, key_id, user_id)

        if not old_key:
            return None

        # Create new key with same properties
        new_key_data = ApiKeyCreate(
            name=old_key.name,
            description=old_key.description,
            permissions=old_key.permissions,
            expires_at=old_key.expires_at,
        )

        new_db_key, new_api_key = KeyService.create_key(db, user_id, new_key_data)

        # Revoke old key
        old_key.is_revoked = True
        old_key.is_active = False
        old_key.revoked_at = datetime.utcnow()

        # Record rotation
        rotation = KeyRotation(
            old_key_id=old_key.id,
            new_key_id=new_db_key.id,
            user_id=user_id,
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
    def get_key_usage_stats(db: Session, key_id: str, user_id: str) -> dict:
        """Get usage statistics for an API key"""
        # Verify key belongs to user
        db_key = KeyService.get_key_by_id(db, key_id, user_id)
        if not db_key:
            return {}

        # Get total requests
        total_requests = db.query(KeyUsage).filter(KeyUsage.key_id == key_id).count()

        # Get requests by endpoint
        endpoint_stats = db.query(
            KeyUsage.endpoint,
            func.count(KeyUsage.id).label('count')
        ).filter(
            KeyUsage.key_id == key_id
        ).group_by(KeyUsage.endpoint).all()

        requests_by_endpoint = {stat.endpoint: stat.count for stat in endpoint_stats}

        return {
            "key_id": key_id,
            "total_requests": total_requests,
            "last_used": db_key.last_used_at,
            "requests_by_endpoint": requests_by_endpoint,
        }
