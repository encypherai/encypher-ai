"""Tests for admin service helpers."""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from app.db.models import Organization, User
from app.services.admin_service import AdminService


def test_update_user_tier_creates_org_when_missing_default_org():
    db = MagicMock()
    user = User(id="user_1", email="test@encypher.com", default_organization_id=None, is_active=True)
    org = MagicMock(spec=Organization)
    org.id = "org_1"
    org.tier = "starter"

    def query_side_effect(model):
        query = MagicMock()
        if model is Organization:
            query.filter.return_value.first.return_value = None
        elif model is User:
            query.filter.return_value.first.return_value = user
        return query

    db.query.side_effect = query_side_effect

    with patch("app.services.auth_service.AuthService._create_personal_organization", return_value=org):
        result = AdminService.update_user_tier(db=db, user_id=user.id, new_tier="enterprise")

    assert result["success"] is True
    assert user.default_organization_id == org.id
    db.commit.assert_called()


def test_list_users_handles_missing_optional_organization_columns():
    db = MagicMock()

    total_result = MagicMock()
    total_result.scalar.return_value = 1

    rows_result = MagicMock()
    rows_result.mappings.return_value.all.return_value = [
        {
            "id": "user_1",
            "email": "admin@example.com",
            "name": "Admin User",
            "is_active": True,
            "organization_id": "org_1",
            "organization_name": None,
            "tier": "starter",
            "api_access_status": "approved",
            "api_calls_this_month": 0,
            "monthly_quota": 10000,
            "created_at": datetime(2026, 3, 1, tzinfo=timezone.utc),
            "last_login_at": None,
        }
    ]

    db.execute.side_effect = [total_result, rows_result]

    with patch.object(
        AdminService,
        "_table_columns",
        side_effect=[
            {"id", "email", "name", "is_active", "created_at", "last_login_at", "default_organization_id", "api_access_status"},
            {"id"},
        ],
    ):
        result = AdminService.list_users(db=db, page=1, page_size=50)

    assert result["total"] == 1
    assert result["users"][0]["organization_id"] == "org_1"
    assert result["users"][0]["organization_name"] is None
    assert result["users"][0]["tier"] == "starter"
    assert result["users"][0]["monthly_quota"] == 10000


def test_get_setup_status_handles_missing_optional_organization_columns():
    db = MagicMock()

    user_result = MagicMock()
    user_result.mappings.return_value.first.return_value = {
        "id": "user_1",
        "default_organization_id": "org_1",
        "setup_completed_at": datetime(2026, 3, 1, tzinfo=timezone.utc),
    }

    org_result = MagicMock()
    org_result.mappings.return_value.first.return_value = {
        "account_type": None,
        "display_name": None,
        "workflow_category": None,
        "dashboard_layout": None,
        "publisher_platform": None,
        "publisher_platform_custom": None,
    }

    db.execute.side_effect = [user_result, org_result]

    with patch.object(
        AdminService,
        "_table_columns",
        side_effect=[
            {"id", "default_organization_id", "setup_completed_at"},
            {"id"},
        ],
    ):
        result = AdminService.get_setup_status(db=db, user_id="user_1")

    assert result == {
        "setup_completed": True,
        "setup_completed_at": "2026-03-01T00:00:00+00:00",
        "account_type": None,
        "display_name": None,
        "workflow_category": None,
        "dashboard_layout": None,
        "publisher_platform": None,
        "publisher_platform_custom": None,
    }
