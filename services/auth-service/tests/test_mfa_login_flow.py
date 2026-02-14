"""Tests for MFA login challenge flow endpoints."""

from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from app.api.v1 import endpoints as auth_endpoints
from app.models.schemas import MfaLoginCompleteRequest, UserLogin


@pytest.mark.asyncio
async def test_login_returns_mfa_challenge_when_totp_enabled(mock_db):
    user = SimpleNamespace(
        id="user_123",
        email="user@example.com",
        email_verified=True,
        totp_enabled=True,
    )

    with patch.object(auth_endpoints.AuthService, "authenticate_user", return_value=user):
        response = await auth_endpoints.login(
            credentials=UserLogin(email="user@example.com", password="SecurePass123!"),
            db=mock_db,
            user_agent=None,
            x_forwarded_for=None,
        )

    assert response["success"] is True
    assert response["data"]["mfa_required"] is True
    assert response["data"]["mfa_token"]


@pytest.mark.asyncio
async def test_login_rejects_invalid_totp_code(mock_db):
    user = SimpleNamespace(
        id="user_123",
        email="user@example.com",
        email_verified=True,
        totp_enabled=True,
    )

    with (
        patch.object(auth_endpoints.AuthService, "authenticate_user", return_value=user),
        patch.object(auth_endpoints.AuthFactorsService, "verify_totp_or_backup", return_value=None),
    ):
        with pytest.raises(HTTPException) as exc:
            await auth_endpoints.login(
                credentials=UserLogin(email="user@example.com", password="SecurePass123!", mfa_code="000000"),
                db=mock_db,
                user_agent=None,
                x_forwarded_for=None,
            )

    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_complete_mfa_login_returns_tokens(mock_db):
    user = SimpleNamespace(
        id="user_123",
        email="user@example.com",
        name="Test User",
        created_at=datetime.now(timezone.utc),
        is_active=True,
        email_verified=True,
        is_super_admin=False,
        default_organization_id=None,
        totp_enabled=True,
    )
    mock_db.query.return_value.filter.return_value.first.return_value = user

    with (
        patch.object(auth_endpoints, "verify_jwt_token", return_value={"sub": user.id, "email": user.email}),
        patch.object(auth_endpoints.AuthFactorsService, "verify_totp_or_backup", return_value="totp"),
        patch.object(auth_endpoints.AuthService, "create_tokens", return_value=("access", "refresh")),
        patch.object(auth_endpoints.AuthService, "store_refresh_token", return_value=MagicMock()),
        patch.object(auth_endpoints.AuthService, "mark_login_success", return_value=None),
    ):
        response = await auth_endpoints.complete_mfa_login(
            request=MfaLoginCompleteRequest(mfa_token="challenge-token", mfa_code="123456"),
            db=mock_db,
            user_agent=None,
            x_forwarded_for=None,
        )

    assert response["success"] is True
    assert response["data"]["access_token"] == "access"
    assert response["data"]["mfa_method"] == "totp"
