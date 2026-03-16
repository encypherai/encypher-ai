"""Admin service for dashboard stats and user listing."""

from datetime import datetime, timedelta
from typing import Any, Dict, Optional
import httpx

from sqlalchemy import func, inspect, literal, or_, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import Organization, User
from app.utils.resilience import call_service_with_breaker

# Analytics service URL (internal service-to-service communication)
ANALYTICS_SERVICE_URL = "http://analytics-service:8003"


class AdminService:
    """Service for admin dashboard data."""

    @staticmethod
    def _table_columns(db: Session, table_name: str) -> set[str]:
        return {column["name"] for column in inspect(db.get_bind()).get_columns(table_name)}

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
            ).scalar()
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
        user_columns = AdminService._table_columns(db, User.__tablename__)
        org_columns = AdminService._table_columns(db, Organization.__tablename__)
        has_default_organization = "default_organization_id" in user_columns

        query = select(
            User.id.label("id"),
            User.email.label("email"),
            User.name.label("name"),
            User.is_active.label("is_active"),
            User.created_at.label("created_at"),
            User.last_login_at.label("last_login_at"),
            (User.default_organization_id if has_default_organization else literal(None)).label("default_organization_id"),
            (User.api_access_status if "api_access_status" in user_columns else literal("not_requested")).label("api_access_status"),
            (Organization.id if has_default_organization else literal(None)).label("organization_id"),
            ((Organization.name if "name" in org_columns else literal(None)) if has_default_organization else literal(None)).label(
                "organization_name"
            ),
            ((Organization.tier if "tier" in org_columns else literal("starter")) if has_default_organization else literal("starter")).label("tier"),
            (
                (Organization.monthly_api_usage if "monthly_api_usage" in org_columns else literal(0)) if has_default_organization else literal(0)
            ).label("api_calls_this_month"),
            (
                (Organization.monthly_api_limit if "monthly_api_limit" in org_columns else literal(10000))
                if has_default_organization
                else literal(10000)
            ).label("monthly_quota"),
        ).select_from(User)
        if has_default_organization:
            query = query.join(Organization, Organization.id == User.default_organization_id, isouter=True)

        count_query = select(func.count(User.id)).select_from(User)

        if search:
            search_filter = or_(
                User.email.ilike(f"%{search}%"),
                User.name.ilike(f"%{search}%"),
                User.id.ilike(f"%{search}%"),
            )
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)

        if tier and has_default_organization and "tier" in org_columns:
            query = query.where(Organization.tier == tier)
            count_query = count_query.join(Organization, Organization.id == User.default_organization_id, isouter=True)
            count_query = count_query.where(Organization.tier == tier)

        total = db.execute(count_query).scalar() or 0

        offset = (page - 1) * page_size
        query = query.order_by(User.created_at.desc()).offset(offset).limit(page_size)

        rows = db.execute(query).mappings().all()
        users = []
        for row in rows:
            users.append(
                {
                    "id": row["id"],
                    "email": row["email"],
                    "name": row["name"] or "",
                    "role": "member",
                    "tier": row["tier"] or "starter",
                    "status": "active" if row["is_active"] else "suspended",
                    "organization_id": row["organization_id"],
                    "organization_name": row["organization_name"],
                    "api_access_status": row["api_access_status"] or "not_requested",
                    "api_calls_this_month": row["api_calls_this_month"] or 0,
                    "monthly_quota": row["monthly_quota"] or 10000,
                    "created_at": row["created_at"].isoformat() if row["created_at"] else None,
                    "last_active_at": row["last_login_at"].isoformat() if row["last_login_at"] else None,
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
    def get_setup_status(db: Session, user_id: str) -> Dict[str, Any] | None:
        user_columns = AdminService._table_columns(db, User.__tablename__)
        org_columns = AdminService._table_columns(db, Organization.__tablename__)
        has_default_organization = "default_organization_id" in user_columns
        has_setup_completed_at = "setup_completed_at" in user_columns

        user_query = select(
            User.id.label("id"),
            (User.default_organization_id if has_default_organization else literal(None)).label("default_organization_id"),
            (User.setup_completed_at if has_setup_completed_at else literal(None)).label("setup_completed_at"),
        ).where(User.id == user_id)

        user_row = db.execute(user_query).mappings().first()
        if not user_row:
            return None

        org_row = None
        if user_row["default_organization_id"]:
            org_query = select(
                (Organization.account_type if "account_type" in org_columns else literal(None)).label("account_type"),
                (Organization.display_name if "display_name" in org_columns else literal(None)).label("display_name"),
                (Organization.workflow_category if "workflow_category" in org_columns else literal(None)).label("workflow_category"),
                (Organization.dashboard_layout if "dashboard_layout" in org_columns else literal(None)).label("dashboard_layout"),
                (Organization.publisher_platform if "publisher_platform" in org_columns else literal(None)).label("publisher_platform"),
                (Organization.publisher_platform_custom if "publisher_platform_custom" in org_columns else literal(None)).label(
                    "publisher_platform_custom"
                ),
            ).where(Organization.id == user_row["default_organization_id"])
            org_row = db.execute(org_query).mappings().first()

        return {
            "setup_completed": user_row["setup_completed_at"] is not None,
            "setup_completed_at": user_row["setup_completed_at"].isoformat() if user_row["setup_completed_at"] else None,
            "account_type": org_row["account_type"] if org_row else None,
            "display_name": org_row["display_name"] if org_row else None,
            "workflow_category": org_row["workflow_category"] if org_row else None,
            "dashboard_layout": org_row["dashboard_layout"] if org_row else None,
            "publisher_platform": org_row["publisher_platform"] if org_row else None,
            "publisher_platform_custom": org_row["publisher_platform_custom"] if org_row else None,
        }

    @staticmethod
    def is_super_admin(db: Session, user_id: str) -> bool:
        user_columns = AdminService._table_columns(db, User.__tablename__)
        if "is_super_admin" not in user_columns:
            return False

        query = select(
            User.id.label("id"),
            User.is_super_admin.label("is_super_admin"),
        ).where(User.id == user_id)
        row = db.execute(query).mappings().first()
        return bool(row and row["is_super_admin"])

    @staticmethod
    def get_basic_user_profile(db: Session, user_id: str) -> Dict[str, Any] | None:
        user_columns = AdminService._table_columns(db, User.__tablename__)
        query = select(
            User.id.label("id"),
            User.email.label("email"),
            User.name.label("name"),
            User.created_at.label("created_at"),
            User.is_active.label("is_active"),
            (User.email_verified if "email_verified" in user_columns else literal(False)).label("email_verified"),
            (User.is_super_admin if "is_super_admin" in user_columns else literal(False)).label("is_super_admin"),
            (User.default_organization_id if "default_organization_id" in user_columns else literal(None)).label("default_organization_id"),
        ).where(User.id == user_id)
        row = db.execute(query).mappings().first()
        if not row:
            return None

        return {
            "id": row["id"],
            "email": row["email"],
            "name": row["name"],
            "created_at": row["created_at"],
            "is_active": bool(row["is_active"]),
            "email_verified": bool(row["email_verified"]),
            "is_super_admin": bool(row["is_super_admin"]),
            "default_organization_id": row["default_organization_id"],
        }

    @staticmethod
    def search_organizations(
        db: Session,
        query: str,
        limit: int = 10,
    ) -> list[Dict[str, Any]]:
        org_columns = AdminService._table_columns(db, Organization.__tablename__)
        selectable_columns = {
            "id",
            "name",
            "email",
            "tier",
            "slug",
            "created_at",
        }
        if not {"id", "name", "email"}.issubset(org_columns):
            return []

        search_filter = or_(
            Organization.name.ilike(f"%{query}%"),
            Organization.email.ilike(f"%{query}%"),
            Organization.id.ilike(f"%{query}%"),
            (Organization.slug.ilike(f"%{query}%") if "slug" in org_columns else literal(False)),
        )
        order_column = (
            Organization.created_at.desc() if "created_at" in selectable_columns and "created_at" in org_columns else Organization.name.asc()
        )
        org_query = (
            select(
                Organization.id.label("id"),
                Organization.name.label("name"),
                Organization.email.label("email"),
                (Organization.tier if "tier" in org_columns else literal("free")).label("tier"),
                (Organization.slug if "slug" in org_columns else literal(None)).label("slug"),
            )
            .where(search_filter)
            .order_by(order_column)
            .limit(limit)
        )
        rows = db.execute(org_query).mappings().all()

        return [
            {
                "id": row["id"],
                "name": row["name"],
                "email": row["email"],
                "tier": row["tier"],
                "slug": row["slug"],
            }
            for row in rows
        ]

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

        # TEAM_145: Map legacy tier names
        legacy_map = {"starter": "free", "professional": "free", "business": "free"}
        new_tier = legacy_map.get(new_tier, new_tier)

        tier_config = {
            "free": {
                "max_seats": 1,
                "monthly_api_limit": 10000,
                "features": {
                    "team_management": False,
                    "audit_logs": False,
                    "merkle_enabled": True,
                    "bulk_operations": False,
                    "sentence_tracking": True,
                    "streaming": True,
                    "byok": False,
                    "sso": False,
                    "custom_assertions": False,
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

    @staticmethod
    async def get_newsletter_subscribers(
        page: int = 1,
        page_size: int = 50,
        active_only: bool = False,
    ) -> Dict[str, Any]:
        """Fetch newsletter subscriber rows from web-service internal endpoint."""
        params = {
            "page": page,
            "page_size": page_size,
            "active_only": str(active_only).lower(),
        }
        headers = {}
        if settings.INTERNAL_SERVICE_TOKEN:
            headers["X-Internal-Token"] = settings.INTERNAL_SERVICE_TOKEN

        url = f"{settings.WEB_SERVICE_URL}/api/v1/newsletter/subscribers"

        try:
            response = await call_service_with_breaker(
                service_name="web-service",
                url=url,
                method="GET",
                params=params,
                headers=headers,
                timeout=15.0,
            )
            body = response.json()
            if isinstance(body, dict) and "data" in body:
                return body["data"]
            return body
        except httpx.HTTPError as exc:
            raise RuntimeError("Failed to fetch newsletter subscribers") from exc

    @staticmethod
    async def update_newsletter_subscriber_status(
        subscriber_id: int,
        status_value: str,
        reason: str | None = None,
    ) -> Dict[str, Any]:
        headers = {}
        if settings.INTERNAL_SERVICE_TOKEN:
            headers["X-Internal-Token"] = settings.INTERNAL_SERVICE_TOKEN

        url = f"{settings.WEB_SERVICE_URL}/api/v1/newsletter/subscribers/{subscriber_id}/status"

        try:
            response = await call_service_with_breaker(
                service_name="web-service",
                url=url,
                method="POST",
                json={"status": status_value, "reason": reason},
                headers=headers,
                timeout=15.0,
            )
            body = response.json()
            if isinstance(body, dict) and "data" in body:
                return body["data"]
            return body
        except httpx.HTTPError as exc:
            raise RuntimeError("Failed to update newsletter subscriber") from exc

    @staticmethod
    async def delete_newsletter_subscriber(subscriber_id: int) -> Dict[str, Any]:
        headers = {}
        if settings.INTERNAL_SERVICE_TOKEN:
            headers["X-Internal-Token"] = settings.INTERNAL_SERVICE_TOKEN

        url = f"{settings.WEB_SERVICE_URL}/api/v1/newsletter/subscribers/{subscriber_id}"

        try:
            response = await call_service_with_breaker(
                service_name="web-service",
                url=url,
                method="DELETE",
                headers=headers,
                timeout=15.0,
            )
            body = response.json()
            if isinstance(body, dict) and "data" in body:
                return body["data"]
            return body
        except httpx.HTTPError as exc:
            raise RuntimeError("Failed to delete newsletter subscriber") from exc
