"""Tests for internal organization tier update endpoint."""

from datetime import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from app.api.v1.organizations import router as org_router
from app.core.config import settings
from app.db.session import get_db
from encypher_commercial_shared.core.pricing_constants import DEFAULT_COALITION_PUBLISHER_PERCENT


def _org_fixture():
    return SimpleNamespace(
        id="org_test",
        name="Test Org",
        slug="test-org",
        email="test@encypher.com",
        tier="professional",
        max_seats=1,
        subscription_status="active",
        coalition_rev_share=DEFAULT_COALITION_PUBLISHER_PERCENT,
        created_at=datetime.utcnow(),
    )


def _build_client(mock_db):
    app = FastAPI()
    app.include_router(org_router, prefix="/api/v1")
    app.dependency_overrides[get_db] = lambda: mock_db
    return TestClient(app)


def test_internal_tier_update_requires_token():
    mock_db = MagicMock()
    client = _build_client(mock_db)
    with patch.object(settings, "INTERNAL_SERVICE_TOKEN", "secret-token"):
        response = client.post(
            "/api/v1/organizations/internal/org_test/tier",
            json={"tier": "professional"},
        )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_internal_tier_update_success():
    mock_db = MagicMock()
    client = _build_client(mock_db)
    with (
        patch.object(settings, "INTERNAL_SERVICE_TOKEN", "secret-token"),
        patch("app.api.v1.organizations.OrganizationService.update_tier_internal", return_value=_org_fixture()),
    ):
        response = client.post(
            "/api/v1/organizations/internal/org_test/tier",
            json={"tier": "professional"},
            headers={"X-Internal-Token": "secret-token"},
        )

    assert response.status_code == status.HTTP_200_OK
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["tier"] == "professional"
    assert payload["data"]["id"] == "org_test"
