"""Tests for org-level MFA enforcement and org security settings endpoints (TEAM_224)."""

from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from app.api.v1 import endpoints as auth_endpoints
from app.models.schemas import UserLogin


def _make_org(enforce_mfa: bool = False) -> SimpleNamespace:
    return SimpleNamespace(
        id="org_123",
        features={"enforce_mfa": enforce_mfa} if enforce_mfa else {},
    )


def _make_user(totp_enabled: bool = False, org_id: str = "org_123") -> SimpleNamespace:
    return SimpleNamespace(
        id="user_abc",
        email="alice@example.com",
        email_verified=True,
        totp_enabled=totp_enabled,
        default_organization_id=org_id,
        # Fields required by UserResponse.model_validate
        name="Alice",
        is_active=True,
        is_super_admin=False,
        created_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
    )


# ─────────────────────────────────────────────────────────────────────
# Login enforcement tests
# ─────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_login_blocked_when_enforce_mfa_and_no_totp(mock_db):
    """enforce_mfa=True + totp_enabled=False -> mfa_setup_required response."""
    user = _make_user(totp_enabled=False)
    org = _make_org(enforce_mfa=True)

    mock_db.query.return_value.filter.return_value.first.return_value = org

    with patch.object(auth_endpoints.AuthService, "authenticate_user", return_value=user):
        response = await auth_endpoints.login(
            credentials=UserLogin(email="alice@example.com", password="Pass1234!"),
            db=mock_db,
            user_agent=None,
            x_forwarded_for=None,
        )

    assert response["success"] is False
    assert response["data"]["mfa_setup_required"] is True
    assert response["error"]["code"] == "E_MFA_SETUP_REQUIRED"


@pytest.mark.asyncio
async def test_login_proceeds_when_enforce_mfa_and_totp_enabled(mock_db):
    """enforce_mfa=True + totp_enabled=True -> normal MFA challenge (not blocked)."""
    user = _make_user(totp_enabled=True)
    org = _make_org(enforce_mfa=True)

    mock_db.query.return_value.filter.return_value.first.return_value = org

    with patch.object(auth_endpoints.AuthService, "authenticate_user", return_value=user):
        response = await auth_endpoints.login(
            credentials=UserLogin(email="alice@example.com", password="Pass1234!"),
            db=mock_db,
            user_agent=None,
            x_forwarded_for=None,
        )

    # Standard MFA challenge (not the setup_required block)
    assert response["success"] is True
    assert response["data"]["mfa_required"] is True
    assert "mfa_setup_required" not in response["data"]


@pytest.mark.asyncio
async def test_login_allowed_when_enforce_mfa_false_and_no_totp(mock_db):
    """enforce_mfa=False + totp_enabled=False -> full login success."""
    user = _make_user(totp_enabled=False)
    org = _make_org(enforce_mfa=False)

    mock_db.query.return_value.filter.return_value.first.return_value = org

    with (
        patch.object(auth_endpoints.AuthService, "authenticate_user", return_value=user),
        patch.object(auth_endpoints.AuthService, "create_tokens", return_value=("access", "refresh")),
        patch.object(auth_endpoints.AuthService, "store_refresh_token", return_value=MagicMock()),
        patch.object(auth_endpoints.AuthService, "mark_login_success", return_value=None),
    ):
        response = await auth_endpoints.login(
            credentials=UserLogin(email="alice@example.com", password="Pass1234!"),
            db=mock_db,
            user_agent=None,
            x_forwarded_for=None,
        )

    assert response["success"] is True
    assert response["data"]["access_token"] == "access"


@pytest.mark.asyncio
async def test_login_no_org_skips_enforcement(mock_db):
    """User with no default_organization_id: enforcement is skipped."""
    user = _make_user(totp_enabled=False, org_id=None)
    user.default_organization_id = None

    with (
        patch.object(auth_endpoints.AuthService, "authenticate_user", return_value=user),
        patch.object(auth_endpoints.AuthService, "create_tokens", return_value=("access", "refresh")),
        patch.object(auth_endpoints.AuthService, "store_refresh_token", return_value=MagicMock()),
        patch.object(auth_endpoints.AuthService, "mark_login_success", return_value=None),
    ):
        response = await auth_endpoints.login(
            credentials=UserLogin(email="alice@example.com", password="Pass1234!"),
            db=mock_db,
            user_agent=None,
            x_forwarded_for=None,
        )

    assert response["success"] is True
    mock_db.query.assert_not_called()


# ─────────────────────────────────────────────────────────────────────
# Org security settings endpoint tests
# ─────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_org_security_non_admin_returns_403():
    """Non-admin user gets 403 on GET /{org_id}/security."""
    from fastapi import HTTPException
    from app.api.v1.organizations import get_org_security_settings

    mock_db = MagicMock()
    mock_org_service = MagicMock()
    mock_org_service._has_permission.return_value = False

    with (
        patch("app.api.v1.organizations.get_current_user_id", return_value="user_xyz"),
        patch("app.api.v1.organizations.OrganizationService", return_value=mock_org_service),
    ):
        mock_request = MagicMock()
        with pytest.raises(HTTPException) as exc:
            await get_org_security_settings(org_id="org_123", request=mock_request, db=mock_db)

    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_get_org_security_returns_enforce_mfa():
    """Admin user gets correct enforce_mfa value."""
    from app.api.v1.organizations import get_org_security_settings

    mock_db = MagicMock()
    mock_org_service = MagicMock()
    mock_org_service._has_permission.return_value = True
    mock_org_service.get_organization.return_value = SimpleNamespace(
        id="org_123",
        features={"enforce_mfa": True},
    )

    with (
        patch("app.api.v1.organizations.get_current_user_id", return_value="admin_abc"),
        patch("app.api.v1.organizations.OrganizationService", return_value=mock_org_service),
    ):
        mock_request = MagicMock()
        response = await get_org_security_settings(org_id="org_123", request=mock_request, db=mock_db)

    assert response["success"] is True
    assert response["data"]["enforce_mfa"] is True


@pytest.mark.asyncio
async def test_patch_org_security_sets_enforce_mfa():
    """Admin can toggle enforce_mfa via PATCH."""
    from app.api.v1.organizations import update_org_security_settings, OrgSecuritySettingsUpdate

    mock_db = MagicMock()
    org_obj = SimpleNamespace(id="org_123", features={})
    mock_org_service = MagicMock()
    mock_org_service._has_permission.return_value = True
    mock_org_service.get_organization.return_value = org_obj

    with (
        patch("app.api.v1.organizations.get_current_user_id", return_value="admin_abc"),
        patch("app.api.v1.organizations.OrganizationService", return_value=mock_org_service),
    ):
        mock_request = MagicMock()
        response = await update_org_security_settings(
            org_id="org_123",
            payload=OrgSecuritySettingsUpdate(enforce_mfa=True),
            request=mock_request,
            db=mock_db,
        )

    assert response["success"] is True
    assert response["data"]["enforce_mfa"] is True
    assert org_obj.features == {"enforce_mfa": True}
    mock_db.commit.assert_called_once()
