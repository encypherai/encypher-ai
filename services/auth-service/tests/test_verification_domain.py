"""Tests for custom verification domain management (TEAM_255).

Verifies:
1. Add-on gating -- cannot set domain without add-on
2. Domain validation -- rejects invalid formats
3. Set domain returns CNAME/TXT instructions
4. DNS verify succeeds with correct records
5. DNS verify fails with missing records
6. Internal context returns domain only when active
7. Domain removal clears all fields
"""

from datetime import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import dns.resolver
from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from app.api.v1.organizations import router as org_router
from app.core.config import settings
from app.db.session import get_db
from encypher_commercial_shared.core.pricing_constants import DEFAULT_COALITION_PUBLISHER_PERCENT


def _org_fixture(**overrides):
    defaults = dict(
        id="org_cvd",
        name="Test Org",
        slug="test-org",
        email="test@encypherai.com",
        account_type="organization",
        display_name="Test Publisher",
        anonymous_publisher=False,
        tier="free",
        features={"custom_verification_domain": True},
        add_ons={"custom-verification-domain": {"active": True}},
        monthly_api_limit=100000,
        monthly_api_usage=0,
        coalition_member=True,
        coalition_rev_share=DEFAULT_COALITION_PUBLISHER_PERCENT,
        certificate_pem=None,
        verification_domain=None,
        verification_domain_status=None,
        verification_domain_dns_token=None,
        verification_domain_verified_at=None,
        has_payment_method=False,
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


def _mock_user_auth(monkeypatch, user_id="usr_admin"):
    """Patch get_current_user_id to return a fixed user."""

    async def _fake_user_id(request, db):
        return user_id

    monkeypatch.setattr("app.api.v1.organizations.get_current_user_id", _fake_user_id)


def _mock_has_permission(monkeypatch, allowed=True):
    """Patch permission check."""
    monkeypatch.setattr(
        "app.api.v1.organizations.OrganizationService._has_permission",
        lambda self, org_id, user_id, role: allowed,
    )


def test_set_domain_requires_addon(monkeypatch):
    """Cannot set domain without the custom-verification-domain add-on."""
    mock_db = MagicMock()
    client = _build_client(mock_db)
    _mock_user_auth(monkeypatch)
    _mock_has_permission(monkeypatch)

    org = _org_fixture(features={}, add_ons={})
    with (
        patch.object(settings, "INTERNAL_SERVICE_TOKEN", ""),
        patch("app.api.v1.organizations.OrganizationService.get_organization", return_value=org),
    ):
        response = client.post(
            "/api/v1/organizations/org_cvd/verification-domain",
            json={"domain": "verify.example.com"},
        )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "add-on required" in response.json()["detail"].lower()


def test_set_domain_rejects_bare_domain(monkeypatch):
    """Rejects bare domains without a subdomain."""
    mock_db = MagicMock()
    client = _build_client(mock_db)
    _mock_user_auth(monkeypatch)
    _mock_has_permission(monkeypatch)

    org = _org_fixture()
    with (
        patch.object(settings, "INTERNAL_SERVICE_TOKEN", ""),
        patch("app.api.v1.organizations.OrganizationService.get_organization", return_value=org),
    ):
        response = client.post(
            "/api/v1/organizations/org_cvd/verification-domain",
            json={"domain": "example.com"},
        )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "subdomain" in response.json()["detail"].lower()


def test_set_domain_success(monkeypatch):
    """Setting a valid domain returns CNAME/TXT instructions."""
    mock_db = MagicMock()
    client = _build_client(mock_db)
    _mock_user_auth(monkeypatch)
    _mock_has_permission(monkeypatch)

    org = _org_fixture()
    with (
        patch.object(settings, "INTERNAL_SERVICE_TOKEN", ""),
        patch("app.api.v1.organizations.OrganizationService.get_organization", return_value=org),
    ):
        response = client.post(
            "/api/v1/organizations/org_cvd/verification-domain",
            json={"domain": "verify.acmenews.com"},
        )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["domain"] == "verify.acmenews.com"
    assert data["status"] == "pending_dns"
    assert data["instructions"]["cname"]["target"] == "verify.encypherai.com"
    assert "encypher-verify=" in data["instructions"]["txt"]["value"]


def test_verify_dns_success(monkeypatch):
    """DNS verification succeeds with correct CNAME + TXT records."""
    mock_db = MagicMock()
    client = _build_client(mock_db)
    _mock_user_auth(monkeypatch)
    _mock_has_permission(monkeypatch)

    org = _org_fixture(
        verification_domain="verify.acmenews.com",
        verification_domain_status="pending_dns",
        verification_domain_dns_token="test-token-123",
    )

    mock_cname = MagicMock()
    mock_cname_rdata = MagicMock()
    mock_cname_rdata.target = "verify.encypherai.com."
    mock_cname.__iter__ = lambda self: iter([mock_cname_rdata])

    mock_txt = MagicMock()
    mock_txt_rdata = MagicMock()
    mock_txt_rdata.__str__ = lambda self: '"encypher-verify=test-token-123"'
    mock_txt.__iter__ = lambda self: iter([mock_txt_rdata])

    def _mock_resolve(name, rtype):
        if rtype == "CNAME":
            return mock_cname
        if rtype == "TXT":
            return mock_txt
        raise dns.resolver.NoAnswer()

    mock_resolver_instance = MagicMock()
    mock_resolver_instance.resolve = MagicMock(side_effect=_mock_resolve)

    with (
        patch.object(settings, "INTERNAL_SERVICE_TOKEN", ""),
        patch("app.api.v1.organizations.OrganizationService.get_organization", return_value=org),
        patch("app.api.v1.organizations.dns.resolver.Resolver", return_value=mock_resolver_instance),
    ):
        response = client.post("/api/v1/organizations/org_cvd/verification-domain/verify")

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["verified"] is True
    assert data["status"] == "active"


def test_verify_dns_fails_missing_cname(monkeypatch):
    """DNS verification fails when CNAME is missing."""
    mock_db = MagicMock()
    client = _build_client(mock_db)
    _mock_user_auth(monkeypatch)
    _mock_has_permission(monkeypatch)

    org = _org_fixture(
        verification_domain="verify.acmenews.com",
        verification_domain_status="pending_dns",
        verification_domain_dns_token="test-token-123",
    )

    mock_resolver_instance = MagicMock()
    mock_resolver_instance.resolve = MagicMock(side_effect=dns.resolver.NoAnswer())

    with (
        patch.object(settings, "INTERNAL_SERVICE_TOKEN", ""),
        patch("app.api.v1.organizations.OrganizationService.get_organization", return_value=org),
        patch("app.api.v1.organizations.dns.resolver.Resolver", return_value=mock_resolver_instance),
    ):
        response = client.post("/api/v1/organizations/org_cvd/verification-domain/verify")

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["verified"] is False
    assert len(data["errors"]) > 0


def test_internal_context_returns_domain_when_active(monkeypatch):
    """Internal context includes verification_domain only when status is active."""
    mock_db = MagicMock()
    client = _build_client(mock_db)

    org = _org_fixture(
        verification_domain="verify.acmenews.com",
        verification_domain_status="active",
        verification_domain_verified_at=datetime.utcnow(),
    )
    with (
        patch.object(settings, "INTERNAL_SERVICE_TOKEN", "secret-token"),
        patch("app.api.v1.organizations.OrganizationService.get_organization", return_value=org),
    ):
        response = client.get(
            "/api/v1/organizations/internal/org_cvd/context",
            headers={"X-Internal-Token": "secret-token"},
        )

    assert response.status_code == 200
    assert response.json()["data"]["verification_domain"] == "verify.acmenews.com"


def test_internal_context_returns_none_when_pending(monkeypatch):
    """Internal context returns None for verification_domain when pending_dns."""
    mock_db = MagicMock()
    client = _build_client(mock_db)

    org = _org_fixture(
        verification_domain="verify.acmenews.com",
        verification_domain_status="pending_dns",
    )
    with (
        patch.object(settings, "INTERNAL_SERVICE_TOKEN", "secret-token"),
        patch("app.api.v1.organizations.OrganizationService.get_organization", return_value=org),
    ):
        response = client.get(
            "/api/v1/organizations/internal/org_cvd/context",
            headers={"X-Internal-Token": "secret-token"},
        )

    assert response.status_code == 200
    assert response.json()["data"]["verification_domain"] is None


def test_remove_domain(monkeypatch):
    """Removing domain clears all verification_domain fields."""
    mock_db = MagicMock()
    client = _build_client(mock_db)
    _mock_user_auth(monkeypatch)
    _mock_has_permission(monkeypatch)

    org = _org_fixture(
        verification_domain="verify.acmenews.com",
        verification_domain_status="active",
        verification_domain_dns_token="tok",
        verification_domain_verified_at=datetime.utcnow(),
    )
    with (
        patch.object(settings, "INTERNAL_SERVICE_TOKEN", ""),
        patch("app.api.v1.organizations.OrganizationService.get_organization", return_value=org),
    ):
        response = client.delete("/api/v1/organizations/org_cvd/verification-domain")

    assert response.status_code == 200
    assert response.json()["data"]["removed"] is True
    assert org.verification_domain is None
    assert org.verification_domain_status is None
    assert org.verification_domain_dns_token is None
    assert org.verification_domain_verified_at is None


def test_enterprise_bypasses_addon_check(monkeypatch):
    """Enterprise tier can set domain without purchasing the add-on."""
    mock_db = MagicMock()
    client = _build_client(mock_db)
    _mock_user_auth(monkeypatch)
    _mock_has_permission(monkeypatch)

    org = _org_fixture(tier="enterprise", features={}, add_ons={})
    with (
        patch.object(settings, "INTERNAL_SERVICE_TOKEN", ""),
        patch("app.api.v1.organizations.OrganizationService.get_organization", return_value=org),
    ):
        response = client.post(
            "/api/v1/organizations/org_cvd/verification-domain",
            json={"domain": "verify.enterprise.com"},
        )

    assert response.status_code == 200
    assert response.json()["data"]["domain"] == "verify.enterprise.com"


def test_addon_cancellation_deactivates_domain_status(monkeypatch):
    """Canceling custom-verification-domain add-on sets verification_domain_status to None."""
    mock_db = MagicMock()
    client = _build_client(mock_db)

    org = _org_fixture(
        verification_domain="verify.acmenews.com",
        verification_domain_status="active",
        verification_domain_dns_token="tok-abc",
        verification_domain_verified_at=datetime.utcnow(),
    )
    with (
        patch.object(settings, "INTERNAL_SERVICE_TOKEN", "secret-token"),
        patch("app.api.v1.organizations.OrganizationService.get_organization", return_value=org),
    ):
        response = client.post(
            "/api/v1/organizations/internal/org_cvd/add-ons",
            json={"add_on_id": "custom-verification-domain", "active": False},
            headers={"X-Internal-Token": "secret-token"},
        )

    assert response.status_code == 200
    # Status should be cleared so internal context returns None
    assert org.verification_domain_status is None
    # Domain and dns_token preserved for re-subscription
    assert org.verification_domain == "verify.acmenews.com"
    assert org.verification_domain_dns_token == "tok-abc"


def test_blocked_domain_rejected(monkeypatch):
    """Reserved domains like localhost and encypherai.com are rejected."""
    mock_db = MagicMock()
    client = _build_client(mock_db)
    _mock_user_auth(monkeypatch)
    _mock_has_permission(monkeypatch)

    org = _org_fixture()
    with (
        patch.object(settings, "INTERNAL_SERVICE_TOKEN", ""),
        patch("app.api.v1.organizations.OrganizationService.get_organization", return_value=org),
    ):
        response = client.post(
            "/api/v1/organizations/org_cvd/verification-domain",
            json={"domain": "verify.test.localhost"},
        )

    assert response.status_code == 400
    assert "reserved" in response.json()["detail"].lower()
