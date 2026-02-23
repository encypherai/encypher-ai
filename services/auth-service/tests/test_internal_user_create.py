"""Tests for the internal user creation endpoint (TEAM_224 magic link invite flow)."""

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from app.api.v1 import endpoints as auth_endpoints
from app.api.v1.endpoints import InternalCreateUserRequest


# ─────────────────────────────────────────────────────────────────────
# Helper: a minimal User-like object returned after db.add/commit/refresh
# ─────────────────────────────────────────────────────────────────────


def _make_created_user() -> SimpleNamespace:
    return SimpleNamespace(
        id="user_new_001",
        email="invited@example.com",
        name="Invited User",
        email_verified=True,
        totp_enabled=False,
        is_super_admin=False,
        is_active=True,
        created_at=None,
        default_organization_id=None,
    )


# ─────────────────────────────────────────────────────────────────────
# Tests
# ─────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_user_internal_no_token_returns_401(mock_db):
    """Missing internal token should return 401."""
    with patch("app.api.v1.endpoints.settings", INTERNAL_SERVICE_TOKEN="secret-abc"):
        with pytest.raises(HTTPException) as exc:
            await auth_endpoints.create_user_internal(
                payload=InternalCreateUserRequest(
                    email="x@example.com",
                    name="X",
                    password="Pass1234!",
                ),
                internal_token=None,
                db=mock_db,
            )

    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_create_user_internal_wrong_token_returns_401(mock_db):
    """Wrong internal token should return 401."""
    with patch("app.api.v1.endpoints.settings", INTERNAL_SERVICE_TOKEN="secret-abc"):
        with pytest.raises(HTTPException) as exc:
            await auth_endpoints.create_user_internal(
                payload=InternalCreateUserRequest(
                    email="x@example.com",
                    name="X",
                    password="Pass1234!",
                ),
                internal_token="wrong-token",
                db=mock_db,
            )

    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_create_user_internal_duplicate_email_returns_409(mock_db):
    """Duplicate email should return 409."""
    existing_user = SimpleNamespace(id="existing", email="alice@example.com")
    mock_db.query.return_value.filter.return_value.first.return_value = existing_user

    with patch("app.api.v1.endpoints.settings", INTERNAL_SERVICE_TOKEN=""):
        with pytest.raises(HTTPException) as exc:
            await auth_endpoints.create_user_internal(
                payload=InternalCreateUserRequest(
                    email="alice@example.com",
                    name="Alice",
                    password="Pass1234!",
                ),
                internal_token=None,
                db=mock_db,
            )

    assert exc.value.status_code == 409


@pytest.mark.asyncio
async def test_create_user_internal_success_returns_tokens(mock_db):
    """Valid request with no token requirement creates user and returns tokens."""
    mock_db.query.return_value.filter.return_value.first.return_value = None

    created_user = _make_created_user()

    def _db_refresh(obj):
        obj.id = created_user.id

    mock_db.refresh.side_effect = _db_refresh

    with (
        patch("app.api.v1.endpoints.settings", INTERNAL_SERVICE_TOKEN=""),
        patch("app.api.v1.endpoints.AuthService.create_tokens", return_value=("acc_tok", "ref_tok")),
        patch("app.api.v1.endpoints.AuthService.store_refresh_token", return_value=MagicMock()),
    ):
        response = await auth_endpoints.create_user_internal(
            payload=InternalCreateUserRequest(
                email="invited@example.com",
                name="Invited User",
                password="Pass1234!",
            ),
            internal_token=None,
            db=mock_db,
        )

    assert response["success"] is True
    assert response["data"]["access_token"] == "acc_tok"
    assert response["data"]["refresh_token"] == "ref_tok"
    assert "user_id" in response["data"]
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
