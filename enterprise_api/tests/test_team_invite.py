"""
Tests for the public team invite endpoints (TEAM_224).

Tests:
- GET /api/v1/org/invites/public/{token}  -> invite metadata (no auth)
- GET /api/v1/org/invites/public/bad-token -> 404
- POST /api/v1/org/invites/public/{token}/accept-new -> creates user+member (mocked auth_svc)
- POST .../accept-new with existing email -> 409
- POST .../accept-new with expired invite -> 410
"""

from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────

_ORG_ID = "org_enterprise"  # Seeded by conftest
_INVITE_EMAIL = "invited-test-user@example-team.com"


def _iso(dt: datetime) -> str:
    return dt.isoformat()


@pytest_asyncio.fixture
async def pending_invite(db: AsyncSession) -> dict:
    """Insert a pending invite into organization_invites and return its details."""
    invite_id = "inv_teamtest001234"
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)

    await db.execute(
        text("""
            INSERT INTO organization_invites (
                id, organization_id, email, role, invited_by,
                token, status, expires_at
            )
            VALUES (
                :id, :org_id, :email, :role, :invited_by,
                :token, 'pending', :expires_at
            )
            ON CONFLICT (id) DO UPDATE SET
                token = EXCLUDED.token,
                status = 'pending',
                expires_at = EXCLUDED.expires_at;
        """),
        {
            "id": invite_id,
            "org_id": _ORG_ID,
            "email": _INVITE_EMAIL,
            "role": "member",
            "invited_by": "user_inviter",
            "token": token,
            "expires_at": expires_at,
        },
    )
    await db.commit()

    return {"id": invite_id, "token": token, "email": _INVITE_EMAIL, "org_id": _ORG_ID}


@pytest_asyncio.fixture
async def expired_invite(db: AsyncSession) -> dict:
    """Insert an expired invite (expires_at in the past)."""
    invite_id = "inv_expiredtest000"
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) - timedelta(days=1)

    await db.execute(
        text("""
            INSERT INTO organization_invites (
                id, organization_id, email, role, invited_by,
                token, status, expires_at
            )
            VALUES (
                :id, :org_id, :email, :role, :invited_by,
                :token, 'pending', :expires_at
            )
            ON CONFLICT (id) DO UPDATE SET
                token = EXCLUDED.token,
                status = 'pending',
                expires_at = EXCLUDED.expires_at;
        """),
        {
            "id": invite_id,
            "org_id": _ORG_ID,
            "email": "expired-invite@example.com",
            "role": "viewer",
            "invited_by": "user_inviter",
            "token": token,
            "expires_at": expires_at,
        },
    )
    await db.commit()

    return {"id": invite_id, "token": token}


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/v1/org/invites/public/{token}
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_public_invite_returns_metadata(client: AsyncClient, pending_invite: dict):
    """Valid pending token returns invite metadata."""
    r = await client.get(f"/api/v1/org/invites/public/{pending_invite['token']}")
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    assert data["data"]["email"] == _INVITE_EMAIL
    assert data["data"]["role"] == "member"
    assert data["data"]["status"] == "pending"
    # org_name comes from organizations.name JOIN
    assert data["data"]["org_name"]  # non-empty string


@pytest.mark.asyncio
async def test_get_public_invite_bad_token_returns_404(client: AsyncClient):
    """Non-existent token returns 404."""
    r = await client.get("/api/v1/org/invites/public/no-such-token-xyz")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_get_public_invite_expired_returns_410(client: AsyncClient, expired_invite: dict):
    """Token for an invite with expires_at in the past returns 410."""
    r = await client.get(f"/api/v1/org/invites/public/{expired_invite['token']}")
    assert r.status_code == 410


# ─────────────────────────────────────────────────────────────────────────────
# POST /api/v1/org/invites/public/{token}/accept-new
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_accept_invite_new_user_creates_member(client: AsyncClient, pending_invite: dict):
    """New user registers via invite: user created, member record inserted, invite marked accepted."""
    mock_result = {
        "user_id": "usr_freshlyinvited",
        "access_token": "acc_token_xyz",
        "refresh_token": "ref_token_xyz",
    }

    mock_set_default_org = AsyncMock()

    with (
        patch(
            "app.routers.team.auth_service_client.create_user_internal",
            new=AsyncMock(return_value=mock_result),
        ),
        patch(
            "app.routers.team.auth_service_client.set_default_organization",
            new=mock_set_default_org,
        ),
    ):
        r = await client.post(
            f"/api/v1/org/invites/public/{pending_invite['token']}/accept-new",
            json={"name": "New Member", "password": "SecurePass123!"},
        )

    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    assert data["data"]["access_token"] == "acc_token_xyz"
    assert data["data"]["refresh_token"] == "ref_token_xyz"
    assert data["data"]["organization_id"] == _ORG_ID
    assert data["data"]["role"] == "member"

    # Verify default org was set in auth-service
    mock_set_default_org.assert_called_once_with(
        user_id="usr_freshlyinvited",
        organization_id=_ORG_ID,
    )


@pytest.mark.asyncio
async def test_accept_invite_new_user_duplicate_email_returns_409(client: AsyncClient, pending_invite: dict):
    """If auth-service returns 409 (email taken), endpoint returns 409."""
    with patch(
        "app.routers.team.auth_service_client.create_user_internal",
        new=AsyncMock(side_effect=RuntimeError("create_user_internal failed: 409 Email already registered")),
    ):
        r = await client.post(
            f"/api/v1/org/invites/public/{pending_invite['token']}/accept-new",
            json={"name": "Existing User", "password": "SecurePass123!"},
        )

    assert r.status_code == 409


@pytest.mark.asyncio
async def test_accept_invite_new_user_expired_invite_returns_410(client: AsyncClient, expired_invite: dict):
    """Expired invite token returns 410."""
    r = await client.post(
        f"/api/v1/org/invites/public/{expired_invite['token']}/accept-new",
        json={"name": "Late User", "password": "SecurePass123!"},
    )
    assert r.status_code == 410


@pytest.mark.asyncio
async def test_accept_invite_new_user_bad_token_returns_404(client: AsyncClient):
    """Bad token returns 404 even on accept-new."""
    r = await client.post(
        "/api/v1/org/invites/public/totally-fake-token/accept-new",
        json={"name": "Ghost", "password": "SecurePass123!"},
    )
    assert r.status_code == 404
