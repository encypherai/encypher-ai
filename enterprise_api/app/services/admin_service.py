"""
Admin Service - Business logic for admin operations.

Handles:
- User listing with stats
- Tier upgrades/downgrades
- Error log retrieval
- BYOK public key management
"""

import hashlib
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, cast
from uuid import uuid4

from sqlalchemy import desc, func, or_, select, text, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.error_log import ErrorLog
from app.models.organization import Organization
from app.models.public_key import PublicKey

logger = logging.getLogger(__name__)


class AdminService:
    """Service for admin operations."""

    @staticmethod
    async def get_platform_stats(db: AsyncSession) -> Dict[str, Any]:
        """
        Get platform-wide statistics for admin dashboard.

        Returns:
            Dict with total_users, active_users, paying_customers, mrr, etc.
        """
        try:
            # Get organization counts by tier
            tier_query = select(Organization.tier, func.count(Organization.id).label("count")).group_by(Organization.tier)

            result = await db.execute(tier_query)
            tier_counts: Dict[str, int] = {
                str(row.tier): int(row._mapping.get("count") or 0) for row in result.fetchall()
            }

            total_users = sum(tier_counts.values())

            # TEAM_145: Paying customers = enterprise or strategic_partner tiers
            paying_customers = sum(count for tier, count in tier_counts.items() if tier not in ("starter", "free"))

            # Calculate MRR (Monthly Recurring Revenue) - rough estimate
            # Enterprise is custom pricing; tracked separately
            tier_prices = {
                "enterprise": 999,
                "strategic_partner": 0,  # Custom pricing
            }
            mrr = sum(tier_prices.get(tier, 0) * count for tier, count in tier_counts.items())

            # Get active users (API calls in last 30 days)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            active_query = select(func.count(Organization.id)).where(Organization.api_calls_this_month > 0)
            active_result = await db.execute(active_query)
            active_users = active_result.scalar() or 0

            # Get total API calls this month
            api_calls_query = select(func.sum(Organization.api_calls_this_month))
            api_calls_result = await db.execute(api_calls_query)
            total_api_calls = api_calls_result.scalar() or 0

            # Get total documents signed
            docs_query = select(func.sum(Organization.documents_signed))
            docs_result = await db.execute(docs_query)
            total_documents = docs_result.scalar() or 0

            return {
                "total_users": total_users,
                "active_users": active_users,
                "paying_customers": paying_customers,
                "mrr": mrr,
                "total_api_calls": total_api_calls,
                "total_documents_signed": total_documents,
                "users_by_tier": tier_counts,
            }
        except Exception as e:
            logger.error(f"Error getting platform stats: {e}")
            return {
                "total_users": 0,
                "active_users": 0,
                "paying_customers": 0,
                "mrr": 0,
                "total_api_calls": 0,
                "users_by_tier": {},
            }

    @staticmethod
    async def list_users(
        db: AsyncSession,
        search: Optional[str] = None,
        tier: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Dict[str, Any]:
        """
        List users/organizations with optional filtering.

        Args:
            db: Database session
            search: Search term for name/email
            tier: Filter by tier
            page: Page number (1-indexed)
            page_size: Items per page

        Returns:
            Dict with users list, total count, pagination info
        """
        try:
            # Base query
            query = select(Organization)
            count_query = select(func.count(Organization.id))

            # Apply filters
            if search:
                search_filter = or_(
                    Organization.name.ilike(f"%{search}%"),
                    Organization.email.ilike(f"%{search}%"),
                    Organization.id.ilike(f"%{search}%"),
                )
                query = query.where(search_filter)
                count_query = count_query.where(search_filter)

            if tier:
                query = query.where(Organization.tier == tier)
                count_query = count_query.where(Organization.tier == tier)

            # Get total count
            total_result = await db.execute(count_query)
            total = total_result.scalar() or 0

            # Apply pagination and ordering
            offset = (page - 1) * page_size
            query = query.order_by(desc(Organization.created_at)).offset(offset).limit(page_size)

            result = await db.execute(query)
            organizations = result.scalars().all()

            # Format response
            users = []
            for org in organizations:
                users.append(
                    {
                        "id": org.id,
                        "email": org.email,
                        "name": org.name,
                        "tier": org.tier,
                        "status": "active",  # TODO: Add status field to Organization
                        "organization_id": org.id,
                        "organization_name": org.name,
                        "api_calls_this_month": org.api_calls_this_month or 0,
                        "documents_signed": org.documents_signed or 0,
                        "monthly_quota": org.monthly_quota or 10000,
                        "api_key_count": 0,  # TODO: Join with api_keys table
                        "created_at": org.created_at.isoformat() if org.created_at else None,
                        "last_active_at": None,  # TODO: Track last activity
                        "features": {
                            "merkle_enabled": org.merkle_enabled,
                            "bulk_operations": org.bulk_operations_enabled,
                            "sentence_tracking": org.sentence_tracking_enabled,
                            "streaming": org.streaming_enabled,
                            "byok": org.byok_enabled,
                            "team_management": org.team_management_enabled,
                            "audit_logs": org.audit_logs_enabled,
                            "sso": org.sso_enabled,
                            "custom_assertions": org.custom_assertions_enabled,
                        },
                    }
                )

            return {
                "users": users,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size,
            }
        except Exception as e:
            logger.error(f"Error listing users: {e}")
            return {
                "users": [],
                "total": 0,
                "page": page,
                "page_size": page_size,
                "total_pages": 0,
            }

    @staticmethod
    async def update_user_tier(
        db: AsyncSession,
        user_id: str,
        new_tier: str,
        reason: Optional[str] = None,
        admin_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Update a user's tier.

        Args:
            db: Database session
            user_id: User/Organization ID to update
            new_tier: New tier value
            reason: Reason for change (audit log)
            admin_id: Admin making the change

        Returns:
            Dict with update result
        """
        try:
            # Get current organization
            query = select(Organization).where(Organization.id == user_id)
            result = await db.execute(query)
            org = result.scalar_one_or_none()

            if not org:
                return {"success": False, "error": f"User/Organization not found: {user_id}"}

            previous_tier = org.tier

            # TEAM_166: Use SSOT tier config
            from app.core.tier_config import coerce_tier_name, get_tier_features, get_tier_limits
            new_tier = coerce_tier_name(new_tier)

            raw_features = get_tier_features(new_tier)
            raw_limits = get_tier_limits(new_tier)
            # Build the _enabled suffix dict that the ORM columns expect
            features = {
                "merkle_enabled": raw_features.get("merkle_enabled", False),
                "bulk_operations_enabled": raw_features.get("bulk_operations", False),
                "sentence_tracking_enabled": raw_features.get("sentence_tracking", False),
                "streaming_enabled": raw_features.get("streaming", False),
                "byok_enabled": raw_features.get("byok", False),
                "team_management_enabled": raw_features.get("team_management", False),
                "audit_logs_enabled": raw_features.get("audit_logs", False),
                "sso_enabled": raw_features.get("sso", False),
                "custom_assertions_enabled": raw_features.get("custom_assertions", False),
                "monthly_quota": raw_limits.get("api_calls", 10000),
            }

            # Update organization
            org_any = cast(Any, org)
            org_any.tier = new_tier
            for feature, value in features.items():
                if hasattr(org, feature):
                    setattr(org_any, feature, value)
            org_any.updated_at = datetime.utcnow()

            await db.commit()
            await db.refresh(org)

            logger.info(f"Admin {admin_id} updated user {user_id} tier: {previous_tier} -> {new_tier}. Reason: {reason}")

            return {
                "success": True,
                "user_id": user_id,
                "previous_tier": previous_tier,
                "new_tier": new_tier,
                "updated_at": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            logger.error(f"Error updating user tier: {e}")
            await db.rollback()
            return {"success": False, "error": str(e)}

    @staticmethod
    async def update_user_status(
        db: AsyncSession,
        user_id: str,
        status: str,
        reason: Optional[str] = None,
        admin_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Update a user's status (suspend/activate).

        Note: This requires adding a 'status' column to organizations table.
        For now, we'll log the action but the actual suspension logic
        would need to be implemented in the auth flow.
        """
        try:
            # Get current organization
            query = select(Organization).where(Organization.id == user_id)
            result = await db.execute(query)
            org = result.scalar_one_or_none()

            if not org:
                return {"success": False, "error": f"User/Organization not found: {user_id}"}

            # TODO: Add status column to Organization model
            # For now, just log the action
            logger.info(f"Admin {admin_id} changed user {user_id} status to: {status}. Reason: {reason}")

            return {
                "success": True,
                "user_id": user_id,
                "new_status": status,
                "updated_at": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            logger.error(f"Error updating user status: {e}")
            return {"success": False, "error": str(e)}

    @staticmethod
    async def get_error_logs(
        db: AsyncSession,
        user_id: Optional[str] = None,
        status_code: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Dict[str, Any]:
        """
        Get error logs with optional filtering.

        Args:
            db: Database session
            user_id: Filter by user ID
            status_code: Filter by HTTP status code
            start_date: Filter by start date
            end_date: Filter by end date
            page: Page number
            page_size: Items per page

        Returns:
            Dict with logs list and pagination info
        """
        try:
            # Base query
            query = select(ErrorLog)
            count_query = select(func.count(ErrorLog.id))

            # Apply filters
            if user_id:
                query = query.where(ErrorLog.user_id == user_id)
                count_query = count_query.where(ErrorLog.user_id == user_id)

            if status_code:
                query = query.where(ErrorLog.status_code == status_code)
                count_query = count_query.where(ErrorLog.status_code == status_code)

            if start_date:
                query = query.where(ErrorLog.timestamp >= start_date)
                count_query = count_query.where(ErrorLog.timestamp >= start_date)

            if end_date:
                query = query.where(ErrorLog.timestamp <= end_date)
                count_query = count_query.where(ErrorLog.timestamp <= end_date)

            # Get total count
            total_result = await db.execute(count_query)
            total = total_result.scalar() or 0

            # Apply pagination and ordering
            offset = (page - 1) * page_size
            query = query.order_by(desc(ErrorLog.timestamp)).offset(offset).limit(page_size)

            result = await db.execute(query)
            logs = result.scalars().all()

            # Format response
            log_entries = []
            for log in logs:
                log_entries.append(
                    {
                        "id": log.id,
                        "user_id": log.user_id,
                        "organization_id": log.organization_id,
                        "endpoint": log.endpoint,
                        "method": log.method,
                        "status_code": log.status_code,
                        "error_code": log.error_code,
                        "error_message": log.error_message,
                        "request_id": log.request_id,
                        "ip_address": log.ip_address,
                        "user_agent": log.user_agent,
                        "timestamp": log.timestamp.isoformat() if log.timestamp else None,
                    }
                )

            return {
                "logs": log_entries,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size,
            }
        except Exception as e:
            logger.error(f"Error getting error logs: {e}")
            # Table might not exist yet
            return {
                "logs": [],
                "total": 0,
                "page": page,
                "page_size": page_size,
                "total_pages": 0,
                "note": "Error logs table may not be initialized yet",
            }

    @staticmethod
    async def log_error(
        db: AsyncSession,
        endpoint: str,
        method: str,
        status_code: int,
        error_message: str,
        error_code: Optional[str] = None,
        user_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        api_key_id: Optional[str] = None,
        request_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        error_details: Optional[str] = None,
    ) -> None:
        """
        Log an error to the error_logs table.

        Called by error handling middleware.
        """
        try:
            error_log = ErrorLog(
                id=f"err_{uuid4().hex[:16]}",
                endpoint=endpoint,
                method=method,
                status_code=status_code,
                error_message=error_message,
                error_code=error_code,
                user_id=user_id,
                organization_id=organization_id,
                api_key_id=api_key_id,
                request_id=request_id,
                ip_address=ip_address,
                user_agent=user_agent,
                error_details=error_details,
                timestamp=datetime.utcnow(),
            )
            db.add(error_log)
            await db.commit()
        except Exception as e:
            logger.warning(f"Failed to log error: {e}")
            # Don't raise - error logging should not break the app


class PublicKeyService:
    """Service for BYOK public key management."""

    @staticmethod
    def compute_key_fingerprint(public_key_pem: str) -> str:
        """
        Compute SHA-256 fingerprint of a public key.

        Args:
            public_key_pem: PEM-encoded public key

        Returns:
            SHA256 fingerprint string
        """
        # Normalize the PEM (remove headers, whitespace)
        lines = public_key_pem.strip().split("\n")
        key_data = "".join(line for line in lines if not line.startswith("-----"))

        # Hash the base64-encoded key data
        key_hash = hashlib.sha256(key_data.encode()).hexdigest()
        return f"SHA256:{key_hash}"

    @staticmethod
    async def register_public_key(
        db: AsyncSession,
        organization_id: str,
        public_key_pem: str,
        key_name: Optional[str] = None,
        key_algorithm: str = "Ed25519",
    ) -> Dict[str, Any]:
        """
        Register a public key for BYOK verification.

        Args:
            db: Database session
            organization_id: Organization registering the key
            public_key_pem: PEM-encoded public key
            key_name: Friendly name for the key
            key_algorithm: Key algorithm (Ed25519, RSA-2048, RSA-4096)

        Returns:
            Dict with registration result
        """
        try:
            # Validate the public key format
            try:
                from cryptography.hazmat.primitives.serialization import load_pem_public_key

                load_pem_public_key(public_key_pem.encode())
            except Exception as e:
                return {"success": False, "error": f"Invalid public key format: {e}"}

            # Compute fingerprint
            fingerprint = PublicKeyService.compute_key_fingerprint(public_key_pem)

            # Check if key already exists
            existing_query = select(PublicKey).where(PublicKey.key_fingerprint == fingerprint)
            existing_result = await db.execute(existing_query)
            existing = existing_result.scalar_one_or_none()

            if existing:
                return {"success": False, "error": "This public key is already registered", "existing_key_id": existing.id}

            # Create new public key record
            key_id = f"pk_{uuid4().hex[:16]}"
            public_key = PublicKey(
                id=key_id,
                organization_id=organization_id,
                key_name=key_name,
                key_algorithm=key_algorithm,
                key_fingerprint=fingerprint,
                public_key_pem=public_key_pem,
                is_active=True,
                is_primary=False,
                created_at=datetime.utcnow(),
            )

            db.add(public_key)
            await db.commit()
            await db.refresh(public_key)

            logger.info(f"Registered public key {key_id} for org {organization_id}")

            return {
                "success": True,
                "data": {
                    "id": public_key.id,
                    "organization_id": public_key.organization_id,
                    "key_name": public_key.key_name,
                    "key_algorithm": public_key.key_algorithm,
                    "key_fingerprint": public_key.key_fingerprint,
                    "public_key_pem": public_key.public_key_pem,
                    "is_active": public_key.is_active,
                    "created_at": public_key.created_at.isoformat() if public_key.created_at else None,
                },
            }
        except Exception as e:
            logger.error(f"Error registering public key: {e}")
            await db.rollback()
            return {"success": False, "error": str(e)}

    @staticmethod
    async def list_public_keys(
        db: AsyncSession,
        organization_id: str,
        include_revoked: bool = False,
    ) -> Dict[str, Any]:
        """
        List public keys for an organization.

        Args:
            db: Database session
            organization_id: Organization ID
            include_revoked: Include revoked keys

        Returns:
            Dict with keys list
        """
        try:
            query = select(PublicKey).where(PublicKey.organization_id == organization_id)

            if not include_revoked:
                query = query.where(PublicKey.is_active == True)

            query = query.order_by(desc(PublicKey.created_at))

            result = await db.execute(query)
            keys = result.scalars().all()

            key_list = []
            for key in keys:
                key_list.append(
                    {
                        "id": key.id,
                        "organization_id": key.organization_id,
                        "key_name": key.key_name,
                        "key_algorithm": key.key_algorithm,
                        "key_fingerprint": key.key_fingerprint,
                        "public_key_pem": key.public_key_pem,
                        "is_active": key.is_active,
                        "is_primary": key.is_primary,
                        "verification_count": key.verification_count,
                        "created_at": key.created_at.isoformat() if key.created_at else None,
                        "last_used_at": key.last_used_at.isoformat() if key.last_used_at else None,
                    }
                )

            return {
                "success": True,
                "data": {
                    "keys": key_list,
                    "total": len(key_list),
                },
            }
        except Exception as e:
            logger.error(f"Error listing public keys: {e}")
            return {"success": False, "error": str(e), "data": {"keys": [], "total": 0}}

    @staticmethod
    async def revoke_public_key(
        db: AsyncSession,
        organization_id: str,
        key_id: str,
        reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Revoke a public key.

        Args:
            db: Database session
            organization_id: Organization ID (for authorization)
            key_id: Key ID to revoke
            reason: Reason for revocation

        Returns:
            Dict with revocation result
        """
        try:
            query = select(PublicKey).where(PublicKey.id == key_id, PublicKey.organization_id == organization_id)
            result = await db.execute(query)
            key = result.scalar_one_or_none()

            if not key:
                return {"success": False, "error": "Public key not found or not owned by organization"}

            key_any = cast(Any, key)
            key_any.is_active = False
            key_any.revoked_at = datetime.utcnow()
            key_any.revoked_reason = reason

            await db.commit()

            logger.info(f"Revoked public key {key_id} for org {organization_id}. Reason: {reason}")

            return {
                "success": True,
                "data": {
                    "key_id": key_id,
                    "revoked_at": key.revoked_at.isoformat(),
                },
            }
        except Exception as e:
            logger.error(f"Error revoking public key: {e}")
            await db.rollback()
            return {"success": False, "error": str(e)}

    @staticmethod
    async def get_public_key_by_fingerprint(
        db: AsyncSession,
        fingerprint: str,
    ) -> Optional[PublicKey]:
        """
        Get a public key by its fingerprint.

        Used during verification to look up the signer's public key.

        Args:
            db: Database session
            fingerprint: Key fingerprint

        Returns:
            PublicKey or None
        """
        try:
            query = select(PublicKey).where(PublicKey.key_fingerprint == fingerprint, PublicKey.is_active == True)
            result = await db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting public key by fingerprint: {e}")
            return None
