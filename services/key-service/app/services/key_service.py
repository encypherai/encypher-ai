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
    def _ensure_user_has_organization(db: Session, user_id: str) -> Optional[str]:
        """
        Ensure a user has an organization. Creates one if they don't.
        This handles backfill for existing users who signed up before auto-org creation.
        
        Returns the organization_id or None if user not found.
        """
        from sqlalchemy import text
        import secrets
        
        # Get user email
        user_result = db.execute(text("""
            SELECT id, email FROM users WHERE id = :user_id
        """), {"user_id": user_id}).fetchone()
        
        if not user_result:
            return None
        
        user_email = user_result.email
        
        # Create organization with defaults
        org_id = f"org_{secrets.token_hex(8)}"
        
        db.execute(text("""
            INSERT INTO organizations (id, name, email, tier, max_seats, monthly_api_limit, monthly_api_usage, features, coalition_member, coalition_rev_share, created_at, updated_at)
            VALUES (:org_id, '', :email, 'starter', 1, 10000, 0, :features, true, 65, NOW(), NOW())
        """), {
            "org_id": org_id,
            "email": user_email,
            "features": '{"team_management": false, "audit_logs": false, "merkle_enabled": false, "bulk_operations": false, "sentence_tracking": false, "streaming": true, "byok": false, "sso": false, "custom_assertions": false}',
        })
        
        # Add user as owner
        member_id = f"mem_{secrets.token_hex(8)}"
        db.execute(text("""
            INSERT INTO organization_members (id, organization_id, user_id, role, status, accepted_at, created_at, updated_at)
            VALUES (:member_id, :org_id, :user_id, 'owner', 'active', NOW(), NOW(), NOW())
        """), {
            "member_id": member_id,
            "org_id": org_id,
            "user_id": user_id,
        })
        
        # Update user's default org
        db.execute(text("""
            UPDATE users SET default_organization_id = :org_id WHERE id = :user_id
        """), {"org_id": org_id, "user_id": user_id})
        
        return org_id

    @staticmethod
    def create_key(db: Session, user_id: str, key_data: ApiKeyCreate, organization_id: str = None) -> Tuple[ApiKey, str]:
        """
        Create a new API key
        Returns: (ApiKey model, actual key string)
        
        If organization_id is not provided, looks up user's default organization.
        """
        from sqlalchemy import text
        
        # Generate new API key
        api_key = generate_api_key()
        key_hash = hash_api_key(api_key)
        fingerprint = generate_key_fingerprint(api_key)

        # Create key prefix for display (first 12 chars)
        key_prefix = api_key[:12] + "..."
        
        # If no org provided, look up user's organization or create one
        if not organization_id:
            result = db.execute(text("""
                SELECT om.organization_id 
                FROM organization_members om
                WHERE om.user_id = :user_id AND om.status = 'active'
                ORDER BY om.role = 'owner' DESC, om.created_at ASC
                LIMIT 1
            """), {"user_id": user_id}).fetchone()
            if result:
                organization_id = result.organization_id
            else:
                # User has no organization - create one for them (backfill for existing users)
                organization_id = KeyService._ensure_user_has_organization(db, user_id)

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
        # Note: certificate_pem column will be added by auth-service migration 005
        # For now, we query without it and fetch separately if needed
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
            is_super_admin = "admin" in key_permissions or "super_admin" in key_permissions
            
            return {
                "key_id": result.key_id,
                "user_id": result.user_id,
                "organization_id": f"user_{result.user_id}",  # Synthetic org ID
                "organization_name": "Personal Account",
                "tier": "starter",  # Default tier for user keys
                "is_demo": True,  # Allow using demo private key for signing
                "certificate_pem": None,
                "features": {
                    "team_management": False,
                    "audit_logs": False,
                    "merkle_enabled": has_merkle or is_super_admin,  # Enable if key has merkle or admin permission
                    "bulk_operations": is_super_admin,
                    "sentence_tracking": is_super_admin,
                    "streaming": True,
                    "byok": False,
                    "sso": False,
                    "custom_assertions": False,
                    "max_team_members": 1,
                    "is_super_admin": is_super_admin,  # Unlimited access for super admin
                },
                "permissions": key_permissions,
                "monthly_api_limit": -1 if is_super_admin else 10000,  # Unlimited for super admin
                "monthly_api_usage": 0,
                "coalition_member": True,
                "coalition_rev_share": 65,
            }

        # Return organization context for org-level keys
        # Note: certificate_pem will be available after auth-service migration 005 deploys
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
