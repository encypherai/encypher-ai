"""Tests for internal organization context endpoint."""

from datetime import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from app.api.v1.organizations import router as org_router
from app.core.config import settings
from app.db.session import get_db


def _org_fixture():
    return SimpleNamespace(
        id="org_test",
        name="Test Org",
        slug="test-org",
        email="test@encypherai.com",
        tier="professional",
        features={"byok": True},
        monthly_api_limit=100000,
        monthly_api_usage=12,
        coalition_member=True,
        coalition_rev_share=70,
        certificate_pem="-----BEGIN PUBLIC KEY-----\nZm9v\n-----END PUBLIC KEY-----\n",
        created_at=datetime.utcnow(),
    )


def _build_client(mock_db):
    app = FastAPI()
    app.include_router(org_router, prefix="/api/v1")
    app.dependency_overrides[get_db] = lambda: mock_db
    return TestClient(app)


def test_internal_org_context_requires_token():
    mock_db = MagicMock()
    client = _build_client(mock_db)
    with patch.object(settings, "INTERNAL_SERVICE_TOKEN", "secret-token"):
        response = client.get("/api/v1/organizations/internal/org_test/context")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_internal_org_context_success():
    mock_db = MagicMock()
    client = _build_client(mock_db)
    with (
        patch.object(settings, "INTERNAL_SERVICE_TOKEN", "secret-token"),
        patch("app.api.v1.organizations.OrganizationService.get_organization", return_value=_org_fixture()),
    ):
        response = client.get(
            "/api/v1/organizations/internal/org_test/context",
            headers={"X-Internal-Token": "secret-token"},
        )

    assert response.status_code == status.HTTP_200_OK
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["id"] == "org_test"
    assert payload["data"]["tier"] == "professional"
    assert payload["data"]["certificate_pem"].startswith("-----BEGIN PUBLIC KEY-----")
