"""Tests for POST /organizations/internal/bulk-provision (TEAM_222)."""

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from app.api.v1.organizations import router as org_router
from app.core.config import settings
from app.db.session import get_db


def _build_client(mock_db):
    app = FastAPI()
    app.include_router(org_router, prefix="/api/v1")
    app.dependency_overrides[get_db] = lambda: mock_db
    return TestClient(app)


def _make_org(org_id="org_new"):
    return SimpleNamespace(
        id=org_id,
        name="Test Org",
        slug=org_id,
        email="test@test.example.com",
        tier="free",
    )


def _make_invitation(token="tok_abc"):
    return SimpleNamespace(token=token)


# =============================================================================
# Authentication
# =============================================================================


def test_bulk_provision_missing_token_returns_401():
    """Missing X-Internal-Token returns 401 when token is configured."""
    mock_db = MagicMock()
    client = _build_client(mock_db)
    with patch.object(settings, "INTERNAL_SERVICE_TOKEN", "secret-token"):
        resp = client.post(
            "/api/v1/organizations/internal/bulk-provision",
            json={
                "publishers": [{"name": "Pub A", "contact_email": "a@puba.example.com"}],
                "partner_org_id": "org_partner",
                "partner_name": "Freestar",
            },
        )
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


def test_bulk_provision_wrong_token_returns_401():
    """Wrong X-Internal-Token returns 401."""
    mock_db = MagicMock()
    client = _build_client(mock_db)
    with patch.object(settings, "INTERNAL_SERVICE_TOKEN", "secret-token"):
        resp = client.post(
            "/api/v1/organizations/internal/bulk-provision",
            json={
                "publishers": [{"name": "Pub A", "contact_email": "a@puba.example.com"}],
                "partner_org_id": "org_partner",
                "partner_name": "Freestar",
            },
            headers={"X-Internal-Token": "wrong-token"},
        )
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


# =============================================================================
# Successful provisioning
# =============================================================================


def test_bulk_provision_single_publisher_success():
    """Valid request with 1 publisher returns 200 with provisioned list."""
    mock_db = MagicMock()
    client = _build_client(mock_db)

    with (
        patch.object(settings, "INTERNAL_SERVICE_TOKEN", "secret-token"),
        patch(
            "app.api.v1.organizations.OrganizationService.create_organization_without_owner",
            return_value=_make_org("org_pub_1"),
        ),
        patch(
            "app.api.v1.organizations.OrganizationService.create_invitation",
            return_value=_make_invitation("tok_001"),
        ),
    ):
        resp = client.post(
            "/api/v1/organizations/internal/bulk-provision",
            json={
                "publishers": [
                    {"name": "Daily Tribune", "contact_email": "editor@dailytribune.example.com"}
                ],
                "partner_org_id": "org_partner",
                "partner_name": "Freestar",
            },
            headers={"X-Internal-Token": "secret-token"},
        )

    assert resp.status_code == 200, resp.text
    data = resp.json()["data"]
    assert data["success_count"] == 1
    assert data["failure_count"] == 0
    assert len(data["provisioned"]) == 1
    prov = data["provisioned"][0]
    assert prov["org_id"] == "org_pub_1"
    assert prov["invitation_token"] == "tok_001"


def test_bulk_provision_three_publishers():
    """Three publishers are all provisioned with free tier."""
    mock_db = MagicMock()
    client = _build_client(mock_db)

    org_counter = [0]

    def make_org_sequential(*args, **kwargs):
        org_counter[0] += 1
        return _make_org(f"org_p{org_counter[0]}")

    inv_counter = [0]

    def make_inv_sequential(*args, **kwargs):
        inv_counter[0] += 1
        return _make_invitation(f"tok_{inv_counter[0]}")

    with (
        patch.object(settings, "INTERNAL_SERVICE_TOKEN", "secret-token"),
        patch(
            "app.api.v1.organizations.OrganizationService.create_organization_without_owner",
            side_effect=make_org_sequential,
        ),
        patch(
            "app.api.v1.organizations.OrganizationService.create_invitation",
            side_effect=make_inv_sequential,
        ),
    ):
        resp = client.post(
            "/api/v1/organizations/internal/bulk-provision",
            json={
                "publishers": [
                    {"name": f"Publisher {i}", "contact_email": f"ed{i}@pub{i}.example.com"}
                    for i in range(1, 4)
                ],
                "partner_org_id": "org_partner",
                "partner_name": "Freestar",
            },
            headers={"X-Internal-Token": "secret-token"},
        )

    assert resp.status_code == 200, resp.text
    data = resp.json()["data"]
    assert data["total"] == 3
    assert data["success_count"] == 3
    assert data["failure_count"] == 0


def test_bulk_provision_provisioned_orgs_have_free_tier():
    """create_organization_without_owner is called with tier=free."""
    mock_db = MagicMock()
    client = _build_client(mock_db)
    tier_calls: list[str] = []

    def capture_tier_call(*args, **kwargs):
        tier_calls.append(kwargs.get("tier", ""))
        return _make_org()

    with (
        patch.object(settings, "INTERNAL_SERVICE_TOKEN", "secret-token"),
        patch(
            "app.api.v1.organizations.OrganizationService.create_organization_without_owner",
            side_effect=capture_tier_call,
        ),
        patch(
            "app.api.v1.organizations.OrganizationService.create_invitation",
            return_value=_make_invitation(),
        ),
    ):
        resp = client.post(
            "/api/v1/organizations/internal/bulk-provision",
            json={
                "publishers": [
                    {"name": "Test Pub", "contact_email": "ed@testpub.example.com"}
                ],
                "partner_org_id": "org_partner",
                "partner_name": "Freestar",
            },
            headers={"X-Internal-Token": "secret-token"},
        )

    assert resp.status_code == 200, resp.text
    assert all(t == "free" for t in tier_calls), f"Expected free tier, got: {tier_calls}"


def test_bulk_provision_with_domain_creates_domain_claim():
    """Publisher with domain triggers domain claim creation."""
    mock_db = MagicMock()
    client = _build_client(mock_db)
    domain_calls: list[str] = []

    def capture_domain_call(*args, **kwargs):
        domain_calls.append(kwargs.get("domain", ""))
        return SimpleNamespace(
            id="claim_1",
            organization_id="org_pub_1",
            domain="dailytribune.example.com",
            verification_email="editor@dailytribune.example.com",
            dns_token="tok",
            email_token="etok",
        )

    with (
        patch.object(settings, "INTERNAL_SERVICE_TOKEN", "secret-token"),
        patch(
            "app.api.v1.organizations.OrganizationService.create_organization_without_owner",
            return_value=_make_org("org_pub_1"),
        ),
        patch(
            "app.api.v1.organizations.OrganizationService.create_invitation",
            return_value=_make_invitation(),
        ),
        patch(
            "app.api.v1.organizations.OrganizationService.create_domain_claim",
            side_effect=capture_domain_call,
        ),
    ):
        resp = client.post(
            "/api/v1/organizations/internal/bulk-provision",
            json={
                "publishers": [
                    {
                        "name": "Daily Tribune",
                        "contact_email": "editor@dailytribune.example.com",
                        "domain": "dailytribune.example.com",
                    }
                ],
                "partner_org_id": "org_partner",
                "partner_name": "Freestar",
            },
            headers={"X-Internal-Token": "secret-token"},
        )

    assert resp.status_code == 200, resp.text
    assert "dailytribune.example.com" in domain_calls


def test_bulk_provision_domain_failure_does_not_fail_provisioning():
    """Domain claim failure does not cause the publisher to go into failed list."""
    mock_db = MagicMock()
    client = _build_client(mock_db)

    with (
        patch.object(settings, "INTERNAL_SERVICE_TOKEN", "secret-token"),
        patch(
            "app.api.v1.organizations.OrganizationService.create_organization_without_owner",
            return_value=_make_org("org_pub_1"),
        ),
        patch(
            "app.api.v1.organizations.OrganizationService.create_invitation",
            return_value=_make_invitation(),
        ),
        patch(
            "app.api.v1.organizations.OrganizationService.create_domain_claim",
            side_effect=ValueError("Domain already claimed"),
        ),
    ):
        resp = client.post(
            "/api/v1/organizations/internal/bulk-provision",
            json={
                "publishers": [
                    {
                        "name": "Daily Tribune",
                        "contact_email": "editor@dailytribune.example.com",
                        "domain": "dailytribune.example.com",
                    }
                ],
                "partner_org_id": "org_partner",
                "partner_name": "Freestar",
            },
            headers={"X-Internal-Token": "secret-token"},
        )

    assert resp.status_code == 200, resp.text
    data = resp.json()["data"]
    # Publisher should still be in provisioned list, not failed
    assert data["success_count"] == 1
    assert data["failure_count"] == 0


def test_bulk_provision_empty_publishers_returns_422():
    """Empty publishers list returns 422 (Pydantic min_length validation)."""
    mock_db = MagicMock()
    client = _build_client(mock_db)

    with patch.object(settings, "INTERNAL_SERVICE_TOKEN", "secret-token"):
        resp = client.post(
            "/api/v1/organizations/internal/bulk-provision",
            json={
                "publishers": [],
                "partner_org_id": "org_partner",
                "partner_name": "Freestar",
            },
            headers={"X-Internal-Token": "secret-token"},
        )

    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
