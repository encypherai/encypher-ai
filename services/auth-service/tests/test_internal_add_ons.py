"""Tests for internal add-ons endpoint (TEAM_255)."""

from datetime import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from app.api.v1.organizations import router as org_router
from app.core.config import settings
from app.db.session import get_db


def _org_fixture(**overrides):
    defaults = dict(
        id="org_test",
        name="Test Org",
        slug="test-org",
        email="test@encypher.com",
        tier="free",
        max_seats=1,
        subscription_status="active",
        coalition_rev_share=60,
        features={},
        add_ons={},
        has_payment_method=True,
        overage_enabled=False,
        overage_cap_cents=None,
        created_at=datetime.utcnow(),
    )
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


def _build_client(mock_db):
    app = FastAPI()
    app.include_router(org_router, prefix="/api/v1")
    app.dependency_overrides[get_db] = lambda: mock_db
    return TestClient(app)


def test_add_on_activation_requires_token():
    mock_db = MagicMock()
    client = _build_client(mock_db)
    with patch.object(settings, "INTERNAL_SERVICE_TOKEN", "secret-token"):
        response = client.post(
            "/api/v1/organizations/internal/org_test/add-ons",
            json={"add_on_id": "byok"},
        )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_add_on_activation_sets_feature_flag():
    """Activating BYOK add-on should set features.byok = True."""
    org = _org_fixture()
    mock_db = MagicMock()

    from app.services.organization_service import OrganizationService

    client = _build_client(mock_db)

    with (
        patch.object(settings, "INTERNAL_SERVICE_TOKEN", "secret-token"),
        patch.object(OrganizationService, "get_organization", return_value=org),
    ):
        response = client.post(
            "/api/v1/organizations/internal/org_test/add-ons",
            json={
                "add_on_id": "byok",
                "stripe_subscription_id": "sub_test_123",
            },
            headers={"X-Internal-Token": "secret-token"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["active"] is True
    assert data["data"]["add_ons"]["byok"]["active"] is True
    assert data["data"]["features"]["byok"] is True


def test_add_on_activation_whitelabel():
    """Activating white-label-verification should set features.whitelabel = True."""
    org = _org_fixture()
    mock_db = MagicMock()

    from app.services.organization_service import OrganizationService

    client = _build_client(mock_db)

    with (
        patch.object(settings, "INTERNAL_SERVICE_TOKEN", "secret-token"),
        patch.object(OrganizationService, "get_organization", return_value=org),
    ):
        response = client.post(
            "/api/v1/organizations/internal/org_test/add-ons",
            json={"add_on_id": "white-label-verification"},
            headers={"X-Internal-Token": "secret-token"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["data"]["features"]["whitelabel"] is True


def test_add_on_deactivation_unsets_feature_flag():
    """Deactivating BYOK add-on should set features.byok = False for non-enterprise."""
    org = _org_fixture(
        features={"byok": True},
        add_ons={"byok": {"active": True, "stripe_subscription_id": "sub_123"}},
    )
    mock_db = MagicMock()

    from app.services.organization_service import OrganizationService

    client = _build_client(mock_db)

    with (
        patch.object(settings, "INTERNAL_SERVICE_TOKEN", "secret-token"),
        patch.object(OrganizationService, "get_organization", return_value=org),
    ):
        response = client.post(
            "/api/v1/organizations/internal/org_test/add-ons",
            json={
                "add_on_id": "byok",
                "active": False,
                "stripe_subscription_id": "sub_123",
            },
            headers={"X-Internal-Token": "secret-token"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["data"]["add_ons"]["byok"]["active"] is False
    assert data["data"]["features"]["byok"] is False


def test_add_on_deactivation_preserves_enterprise_features():
    """Enterprise orgs should keep features even when add-on deactivated."""
    org = _org_fixture(
        tier="enterprise",
        features={"byok": True},
        add_ons={"byok": {"active": True}},
    )
    mock_db = MagicMock()

    from app.services.organization_service import OrganizationService

    client = _build_client(mock_db)

    with (
        patch.object(settings, "INTERNAL_SERVICE_TOKEN", "secret-token"),
        patch.object(OrganizationService, "get_organization", return_value=org),
    ):
        response = client.post(
            "/api/v1/organizations/internal/org_test/add-ons",
            json={"add_on_id": "byok", "active": False},
            headers={"X-Internal-Token": "secret-token"},
        )

    assert response.status_code == 200
    # Enterprise should keep byok feature even after add-on deactivation
    assert org.features["byok"] is True


def test_add_on_no_feature_mapping():
    """Add-ons without feature mapping (like custom-signing-identity) should only update add_ons."""
    org = _org_fixture()
    mock_db = MagicMock()

    from app.services.organization_service import OrganizationService

    client = _build_client(mock_db)

    with (
        patch.object(settings, "INTERNAL_SERVICE_TOKEN", "secret-token"),
        patch.object(OrganizationService, "get_organization", return_value=org),
    ):
        response = client.post(
            "/api/v1/organizations/internal/org_test/add-ons",
            json={"add_on_id": "custom-signing-identity"},
            headers={"X-Internal-Token": "secret-token"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["data"]["add_ons"]["custom-signing-identity"]["active"] is True
    # features should not have a custom-signing-identity key
    assert "custom-signing-identity" not in data["data"].get("features", {})


def test_add_on_with_quantity():
    """One-time add-ons (bulk-archive-backfill) should store quantity."""
    org = _org_fixture()
    mock_db = MagicMock()

    from app.services.organization_service import OrganizationService

    client = _build_client(mock_db)

    with (
        patch.object(settings, "INTERNAL_SERVICE_TOKEN", "secret-token"),
        patch.object(OrganizationService, "get_organization", return_value=org),
    ):
        response = client.post(
            "/api/v1/organizations/internal/org_test/add-ons",
            json={
                "add_on_id": "bulk-archive-backfill",
                "quantity": 500,
                "stripe_session_id": "cs_test_123",
            },
            headers={"X-Internal-Token": "secret-token"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["data"]["add_ons"]["bulk-archive-backfill"]["quantity"] == 500


def test_add_on_org_not_found():
    mock_db = MagicMock()

    from app.services.organization_service import OrganizationService

    client = _build_client(mock_db)

    with (
        patch.object(settings, "INTERNAL_SERVICE_TOKEN", "secret-token"),
        patch.object(OrganizationService, "get_organization", return_value=None),
    ):
        response = client.post(
            "/api/v1/organizations/internal/org_missing/add-ons",
            json={"add_on_id": "byok"},
            headers={"X-Internal-Token": "secret-token"},
        )

    assert response.status_code == status.HTTP_404_NOT_FOUND
