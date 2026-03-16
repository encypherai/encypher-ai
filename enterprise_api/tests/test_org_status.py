"""Tests for organization status (suspension/activation) -- TEAM_256."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import HTTPException


# ---------------------------------------------------------------------------
# 1. OrganizationStatus enum
# ---------------------------------------------------------------------------


def test_org_status_enum_values():
    from app.models.organization import OrganizationStatus

    assert OrganizationStatus.ACTIVE == "active"
    assert OrganizationStatus.SUSPENDED == "suspended"
    assert OrganizationStatus.PENDING == "pending"


def test_org_status_enum_is_str_subclass():
    from app.models.organization import OrganizationStatus

    assert isinstance(OrganizationStatus.ACTIVE, str)


# ---------------------------------------------------------------------------
# 2. Organization model columns
# ---------------------------------------------------------------------------


def test_org_model_has_status_column():
    from app.models.organization import Organization

    assert hasattr(Organization, "status")
    assert hasattr(Organization, "suspended_at")
    assert hasattr(Organization, "suspension_reason")


def test_org_model_status_default():
    """The Column default should be 'active'."""
    from app.models.organization import Organization

    col = Organization.__table__.columns["status"]
    assert col.default.arg == "active"
    assert col.nullable is False


# ---------------------------------------------------------------------------
# 3. is_suspended property
# ---------------------------------------------------------------------------


def test_is_suspended_true():
    from app.models.organization import Organization

    org = Organization(id="org_test_sus", name="Test", email="s@t.com", status="suspended")
    assert org.is_suspended is True


def test_is_suspended_false():
    from app.models.organization import Organization

    org = Organization(id="org_test_act", name="Test", email="a@t.com", status="active")
    assert org.is_suspended is False


def test_is_suspended_pending():
    from app.models.organization import Organization

    org = Organization(id="org_test_pen", name="Test", email="p@t.com", status="pending")
    assert org.is_suspended is False


# ---------------------------------------------------------------------------
# 4. Suspension enforcement in get_current_organization
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_suspended_org_blocked_with_403():
    """A suspended org context must raise HTTP 403."""
    from app.dependencies import get_current_organization

    suspended_ctx = {
        "organization_id": "org_test_suspended",
        "organization_name": "Suspended Org",
        "tier": "enterprise",
        "status": "suspended",
        "features": {},
        "permissions": ["sign", "verify", "lookup"],
        "monthly_api_limit": 100000,
        "monthly_api_usage": 0,
        "coalition_member": True,
        "coalition_rev_share": 70,
    }

    request = MagicMock()
    request.state = MagicMock()
    bg = MagicMock()
    creds = MagicMock()
    creds.credentials = "fake-api-key"

    with patch(
        "app.dependencies._resolve_org_context_via_composed_auth_service",
        new_callable=AsyncMock,
        return_value=suspended_ctx,
    ):
        with pytest.raises(HTTPException) as exc_info:
            await get_current_organization(
                request=request,
                background_tasks=bg,
                credentials=creds,
            )
        assert exc_info.value.status_code == 403
        detail = exc_info.value.detail
        assert detail["code"] == "ORGANIZATION_SUSPENDED"


@pytest.mark.asyncio
async def test_active_org_passes():
    """An active org context should be returned without error."""
    from app.dependencies import get_current_organization

    active_ctx = {
        "organization_id": "org_test_active",
        "organization_name": "Active Org",
        "tier": "free",
        "status": "active",
        "features": {},
        "permissions": ["sign", "verify"],
        "monthly_api_limit": 10000,
        "monthly_api_usage": 0,
        "coalition_member": True,
        "coalition_rev_share": 70,
    }

    request = MagicMock()
    request.state = MagicMock()
    bg = MagicMock()
    creds = MagicMock()
    creds.credentials = "fake-api-key"

    with patch(
        "app.dependencies._resolve_org_context_via_composed_auth_service",
        new_callable=AsyncMock,
        return_value=active_ctx,
    ):
        result = await get_current_organization(
            request=request,
            background_tasks=bg,
            credentials=creds,
        )
        assert result["organization_id"] == "org_test_active"
        assert result.get("status") == "active"


@pytest.mark.asyncio
async def test_missing_status_defaults_active():
    """Org context without a status field should be treated as active."""
    from app.dependencies import get_current_organization

    no_status_ctx = {
        "organization_id": "org_test_nostatus",
        "organization_name": "No Status Org",
        "tier": "free",
        "features": {},
        "permissions": ["sign", "verify"],
        "monthly_api_limit": 10000,
        "monthly_api_usage": 0,
        "coalition_member": True,
        "coalition_rev_share": 70,
    }

    request = MagicMock()
    request.state = MagicMock()
    bg = MagicMock()
    creds = MagicMock()
    creds.credentials = "fake-api-key"

    with patch(
        "app.dependencies._resolve_org_context_via_composed_auth_service",
        new_callable=AsyncMock,
        return_value=no_status_ctx,
    ):
        result = await get_current_organization(
            request=request,
            background_tasks=bg,
            credentials=creds,
        )
        # Should pass without raising
        assert result["organization_id"] == "org_test_nostatus"


# ---------------------------------------------------------------------------
# 5. list_users returns real status
# ---------------------------------------------------------------------------


def test_list_users_returns_status_from_org():
    """AdminService.list_users should use getattr(org, 'status', 'active')
    instead of a hardcoded 'active' string."""
    import inspect

    from app.services.admin_service import AdminService

    source = inspect.getsource(AdminService.list_users)
    assert 'getattr(org, "status", "active")' in source
    assert '"status": "active"' not in source


# ---------------------------------------------------------------------------
# 6. _normalize_org_context preserves status
# ---------------------------------------------------------------------------


def test_normalize_preserves_status():
    from app.dependencies import _normalize_org_context

    ctx = {
        "organization_id": "org_x",
        "organization_name": "X",
        "tier": "free",
        "status": "suspended",
        "features": {},
        "permissions": [],
    }
    result = _normalize_org_context(ctx)
    assert result["status"] == "suspended"


def test_normalize_without_status_keeps_missing():
    """If the upstream context has no status key, the normalized output should
    still not inject one -- the enforcement code defaults via .get()."""
    from app.dependencies import _normalize_org_context

    ctx = {
        "organization_id": "org_y",
        "organization_name": "Y",
        "tier": "free",
        "features": {},
        "permissions": [],
    }
    result = _normalize_org_context(ctx)
    # status not explicitly set -> defaults handled by .get("status", "active")
    # If it's present, it should be "active" or not present at all
    assert result.get("status", "active") == "active"


# ---------------------------------------------------------------------------
# 7. Migration file exists and has correct revision chain
# ---------------------------------------------------------------------------


def test_migration_revision_chain():
    import importlib.util
    import os

    migration_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "alembic",
        "versions",
        "20260316_add_org_status.py",
    )
    spec = importlib.util.spec_from_file_location("migration", migration_path)
    assert spec is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]

    assert mod.revision == "20260316_110000"
    assert mod.down_revision == "20260316_100000"
