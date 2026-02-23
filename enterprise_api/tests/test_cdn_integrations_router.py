"""
Tests for the CDN integrations router.

Covers: config CRUD and webhook authentication.
Uses httpx TestClient with dependency overrides.
"""

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.dependencies import get_current_organization_dep
from app.database import get_db


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

TEST_ORG_ID = "test-org-cdn-001"
TEST_SECRET = "supersecretvalue1234"


def mock_org_dep():
    """Override get_current_organization_dep to return a test org context."""
    return {"organization_id": TEST_ORG_ID}


def mock_db():
    """Minimal AsyncSession mock."""
    db = AsyncMock()
    db.execute = AsyncMock()
    db.add = MagicMock()
    db.flush = AsyncMock()
    db.delete = AsyncMock()
    db.refresh = AsyncMock()
    return db


@pytest.fixture
def client():
    app.dependency_overrides[get_current_organization_dep] = mock_org_dep
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Config CRUD tests
# ---------------------------------------------------------------------------


def test_get_cdn_integration_not_found(client):
    """GET /cdn/cloudflare when no row exists should return 404."""
    with patch("app.routers.cdn_integrations.get_db") as mock_get_db:
        db = mock_db()
        # scalar_one_or_none returns None (not configured)
        exec_result = MagicMock()
        exec_result.scalar_one_or_none.return_value = None
        db.execute = AsyncMock(return_value=exec_result)
        mock_get_db.return_value = db

        # Override get_db with async generator
        async def override_db():
            yield db

        app.dependency_overrides[get_db] = override_db

        response = client.get("/api/v1/cdn/cloudflare")
        assert response.status_code == 404


def test_create_cdn_integration(client):
    """POST /cdn/cloudflare should return config with webhook_url and no secret."""
    from datetime import datetime, timezone

    fake_id = uuid4()

    # Build a fake ORM instance with the fields the router reads after flush+refresh
    instance = MagicMock()
    instance.id = fake_id
    instance.provider = "cloudflare"
    instance.zone_id = "abc123"
    instance.enabled = True
    instance.created_at = datetime.now(timezone.utc)
    instance.updated_at = datetime.now(timezone.utc)

    # no-existing-row result
    none_result = MagicMock()
    none_result.scalar_one_or_none.return_value = None

    async def override_db():
        db = AsyncMock()
        db.execute = AsyncMock(return_value=none_result)
        db.add = MagicMock()
        db.flush = AsyncMock()
        # refresh sets the fields on the integration object passed to it
        async def do_refresh(obj):
            obj.id = instance.id
            obj.provider = instance.provider
            obj.zone_id = instance.zone_id
            obj.enabled = instance.enabled
            obj.created_at = instance.created_at
            obj.updated_at = instance.updated_at
        db.refresh = do_refresh
        yield db

    app.dependency_overrides[get_db] = override_db

    response = client.post(
        "/api/v1/cdn/cloudflare",
        json={
            "provider": "cloudflare",
            "zone_id": "abc123",
            "webhook_secret": TEST_SECRET,
            "enabled": True,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["provider"] == "cloudflare"
    assert data["zone_id"] == "abc123"
    assert "webhook_url" in data
    assert "cloudflare/webhook" in data["webhook_url"]
    # Secret must NOT appear in response
    assert TEST_SECRET not in response.text


# ---------------------------------------------------------------------------
# Webhook authentication tests
# ---------------------------------------------------------------------------


def test_webhook_missing_secret_rejected():
    """POST webhook without x-cf-secret header should return 401."""
    with TestClient(app) as c:
        response = c.post(
            f"/api/v1/cdn/cloudflare/webhook/{TEST_ORG_ID}",
            content=b"{}",
        )
    assert response.status_code == 401


def test_webhook_invalid_secret_rejected():
    """POST webhook with wrong secret should return 401."""
    import bcrypt

    correct_hash = bcrypt.hashpw(TEST_SECRET.encode(), bcrypt.gensalt()).decode()
    fake_integration = MagicMock()
    fake_integration.webhook_secret_hash = correct_hash
    fake_integration.enabled = True

    exec_result = MagicMock()
    exec_result.scalar_one_or_none.return_value = fake_integration

    async def override_db():
        db = AsyncMock()
        db.execute = AsyncMock(return_value=exec_result)
        yield db

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides.pop(get_current_organization_dep, None)

    with TestClient(app) as c:
        response = c.post(
            f"/api/v1/cdn/cloudflare/webhook/{TEST_ORG_ID}",
            content=b"{}",
            headers={"x-cf-secret": "wrong-secret"},
        )
    app.dependency_overrides.clear()
    assert response.status_code == 401


def test_webhook_valid_secret_empty_body_accepted():
    """POST webhook with correct secret and empty NDJSON body should return 200."""
    import bcrypt

    correct_hash = bcrypt.hashpw(TEST_SECRET.encode(), bcrypt.gensalt()).decode()
    fake_integration = MagicMock()
    fake_integration.webhook_secret_hash = correct_hash
    fake_integration.enabled = True
    fake_integration.organization_id = TEST_ORG_ID

    exec_result = MagicMock()
    exec_result.scalar_one_or_none.return_value = fake_integration

    async def override_db():
        db = AsyncMock()
        db.execute = AsyncMock(return_value=exec_result)
        db.add = MagicMock()
        db.flush = AsyncMock()
        yield db

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides.pop(get_current_organization_dep, None)

    # Patch ingest to avoid full DB queries
    with patch("app.routers.cdn_integrations.ingest_logpush_batch") as mock_ingest:
        from app.schemas.cdn_schemas import LogpushIngestResult
        mock_ingest.return_value = LogpushIngestResult(
            lines_received=0,
            bots_detected=0,
            bypass_flags=0,
            events_created=0,
            errors=0,
        )
        with TestClient(app) as c:
            response = c.post(
                f"/api/v1/cdn/cloudflare/webhook/{TEST_ORG_ID}",
                content=b"",
                headers={"x-cf-secret": TEST_SECRET},
            )

    app.dependency_overrides.clear()
    assert response.status_code == 200
    data = response.json()
    assert data["lines_received"] == 0
    assert data["events_created"] == 0


def test_webhook_no_integration_returns_401():
    """POST webhook for an org with no CDN integration configured returns 401."""
    exec_result = MagicMock()
    exec_result.scalar_one_or_none.return_value = None

    async def override_db():
        db = AsyncMock()
        db.execute = AsyncMock(return_value=exec_result)
        yield db

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides.pop(get_current_organization_dep, None)

    with TestClient(app) as c:
        response = c.post(
            f"/api/v1/cdn/cloudflare/webhook/{TEST_ORG_ID}",
            content=b"{}",
            headers={"x-cf-secret": TEST_SECRET},
        )
    app.dependency_overrides.clear()
    assert response.status_code == 401
