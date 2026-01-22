"""Admin service for dashboard stats and user listing."""

from datetime import datetime, timedelta
from typing import Any, Dict, Optional
import httpx

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.db.models import Organization, User

# Analytics service URL (internal service-to-service communication)
ANALYTICS_SERVICE_URL = "http://analytics-service:8003"


class AdminService:
    """Service for admin dashboard data."""

    @staticmethod
    def get_platform_stats(db: Session) -> Dict[str, Any]:
        tier_query = select(Organization.tier, func.count(Organization.id).label("count")).group_by(Organization.tier)
        tier_rows = db.execute(tier_query).fetchall()
        tier_counts = {str(row.tier): int(row.count or 0) for row in tier_rows}

        total_users = db.execute(select(func.count(User.id))).scalar() or 0
        paying_customers = sum(count for tier, count in tier_counts.items() if tier not in {"starter", "free"})

        tier_prices = {
            "professional": 99,
            "business": 499,
            "enterprise": 999,
            "strategic_partner": 0,
        }
        mrr = sum(tier_prices.get(tier, 0) * count for tier, count in tier_counts.items())

        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        active_users = (
            db.execute(
                select(func.count(User.id)).where(
                    User.last_login_at.is_not(None),
                    User.last_login_at >= thirty_days_ago,
                )
            )
            .scalar()
            or 0
        )

        total_api_calls = db.execute(select(func.sum(Organization.monthly_api_usage))).scalar() or 0

        return {
            "total_users": total_users,
            "active_users": active_users,
            "paying_customers": paying_customers,
            "mrr": mrr,
            "total_api_calls": total_api_calls,
            "users_by_tier": tier_counts,
        }

    @staticmethod
    def list_users(
        db: Session,
        search: Optional[str] = None,
        tier: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Dict[str, Any]:
        query = select(User, Organization).join(
            Organization, Organization.id == User.default_organization_id, isouter=True
        )
        count_query = select(func.count(User.id))

        if search:
            search_filter = or_(
                User.email.ilike(f"%{search}%"),
                User.name.ilike(f"%{search}%"),
                User.id.ilike(f"%{search}%"),
            )
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)

        if tier:
            query = query.where(Organization.tier == tier)
            count_query = count_query.where(Organization.tier == tier)

        total = db.execute(count_query).scalar() or 0

        offset = (page - 1) * page_size
        query = query.order_by(User.created_at.desc()).offset(offset).limit(page_size)

        rows = db.execute(query).all()
        users = []
        for user, org in rows:
            users.append(
                {
                    "id": user.id,
                    "email": user.email,
                    "name": user.name or "",
                    "role": "member",
                    "tier": org.tier if org else "starter",
                    "status": "active" if user.is_active else "suspended",
                    "organization_id": org.id if org else None,
                    "organization_name": org.name if org else None,
                    "api_calls_this_month": org.monthly_api_usage if org else 0,
                    "monthly_quota": org.monthly_api_limit if org else 10000,
                    "created_at": user.created_at.isoformat() if user.created_at else None,
                    "last_active_at": user.last_login_at.isoformat() if user.last_login_at else None,
                }
            )

        return {
            "users": users,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }

    @staticmethod
    def update_user_tier(
        db: Session,
        user_id: str,
        new_tier: str,
        reason: Optional[str] = None,
        admin_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        org = db.query(Organization).filter(Organization.id == user_id).first()
        if not org:
            user = db.query(User).filter(User.id == user_id).first()
            org_id = user.default_organization_id if user else None
            if not org_id and user:
                from app.services.auth_service import AuthService

                org = AuthService._create_personal_organization(db, user)
                user.default_organization_id = org.id
                org_id = org.id
            if not org_id:
                return {"success": False, "error": f"Organization not found for user: {user_id}"}
            if not org:
                org = db.query(Organization).filter(Organization.id == org_id).first()
            if not org:
                return {"success": False, "error": f"Organization not found: {org_id}"}

        previous_tier = org.tier

        tier_config = {
            "starter": {
                "max_seats": 1,
                "monthly_api_limit": 10000,
                "features": {
                    "team_management": False,
                    "audit_logs": False,
                    "merkle_enabled": False,
                    "bulk_operations": False,
                    "sentence_tracking": False,
                    "streaming": True,
                    "byok": False,
                    "sso": False,
                    "custom_assertions": False,
                },
            },
            "professional": {
                "max_seats": 1,
                "monthly_api_limit": 100000,
                "features": {
                    "team_management": False,
                    "audit_logs": False,
                    "merkle_enabled": False,
                    "bulk_operations": False,
                    "sentence_tracking": True,
                    "streaming": True,
                    "byok": False,
                    "sso": False,
                    "custom_assertions": False,
                },
            },
            "business": {
                "max_seats": 5,
                "monthly_api_limit": 500000,
                "features": {
                    "team_management": True,
                    "audit_logs": True,
                    "merkle_enabled": True,
                    "bulk_operations": True,
                    "sentence_tracking": True,
                    "streaming": True,
                    "byok": True,
                    "sso": False,
                    "custom_assertions": True,
                },
            },
            "enterprise": {
                "max_seats": -1,
                "monthly_api_limit": -1,
                "features": {
                    "team_management": True,
                    "audit_logs": True,
                    "merkle_enabled": True,
                    "bulk_operations": True,
                    "sentence_tracking": True,
                    "streaming": True,
                    "byok": True,
                    "sso": True,
                    "custom_assertions": True,
                },
            },
            "strategic_partner": {
                "max_seats": -1,
                "monthly_api_limit": -1,
                "features": {
                    "team_management": True,
                    "audit_logs": True,
                    "merkle_enabled": True,
                    "bulk_operations": True,
                    "sentence_tracking": True,
                    "streaming": True,
                    "byok": True,
                    "sso": True,
                    "custom_assertions": True,
                },
            },
        }

        config = tier_config.get(new_tier)
        if not config:
            return {"success": False, "error": f"Invalid tier: {new_tier}"}

        org.tier = new_tier
        org.max_seats = config["max_seats"]
        org.monthly_api_limit = config["monthly_api_limit"]
        org.features = config["features"]
        org.updated_at = datetime.utcnow()

        db.commit()

        return {
            "success": True,
            "user_id": user_id,
            "previous_tier": previous_tier,
            "new_tier": new_tier,
            "updated_at": org.updated_at.isoformat() if org.updated_at else None,
            "reason": reason,
            "admin_id": admin_id,
        }

    @staticmethod
    def update_user_status(
        db: Session,
        user_id: str,
        status: str,
        reason: Optional[str] = None,
        admin_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"success": False, "error": f"User not found: {user_id}"}

        previous_status = "active" if user.is_active else "suspended"
        user.is_active = status == "active"
        user.updated_at = datetime.utcnow()

        db.commit()

        return {
            "success": True,
            "user_id": user_id,
            "previous_status": previous_status,
            "new_status": status,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
            "reason": reason,
            "admin_id": admin_id,
        }

    @staticmethod
    def update_user_role(
        db: Session,
        user_id: str,
        new_role: str,
        admin_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update a user's role within their default organization."""
        from ...db.models import OrganizationMember

        valid_roles = ["member", "manager", "admin"]
        if new_role.lower() not in valid_roles:
            return {"success": False, "error": f"Invalid role: {new_role}. Must be one of: {valid_roles}"}

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"success": False, "error": f"User not found: {user_id}"}

        org_id = user.default_organization_id
        if not org_id:
            return {"success": False, "error": f"User has no default organization: {user_id}"}

        membership = (
            db.query(OrganizationMember)
            .filter(
                OrganizationMember.organization_id == org_id,
                OrganizationMember.user_id == user_id,
            )
            .first()
        )

        if not membership:
            return {"success": False, "error": "User is not a member of their default organization"}

        previous_role = membership.role
        membership.role = new_role.lower()
        membership.updated_at = datetime.utcnow()

        db.commit()

        return {
            "success": True,
            "user_id": user_id,
            "organization_id": str(org_id),
            "previous_role": previous_role,
            "new_role": new_role.lower(),
            "updated_at": membership.updated_at.isoformat() if membership.updated_at else None,
            "admin_id": admin_id,
        }
