"""Tests for add-on checkout and webhook handling."""

from pathlib import Path
import importlib
import sys

import pytest

SERVICE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SERVICE_ROOT))
sys.modules.pop("app", None)

stripe_service = importlib.import_module("app.services.stripe_service")


@pytest.mark.asyncio
async def test_payment_mode_checkout_persists_add_on(monkeypatch):
    """Payment-mode checkout (bulk-archive-backfill) should POST to auth-service add-ons endpoint."""
    monkeypatch.setattr(stripe_service.settings, "AUTH_SERVICE_URL", "http://auth:8001")
    monkeypatch.setattr(stripe_service.settings, "INTERNAL_SERVICE_TOKEN", "test-token")

    http_calls = []

    class FakeResponse:
        status_code = 200

    class FakeClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def post(self, url, json=None, headers=None):
            http_calls.append({"url": url, "json": json, "headers": headers})
            return FakeResponse()

    monkeypatch.setattr(stripe_service.httpx, "AsyncClient", lambda **kw: FakeClient())

    session = {
        "id": "cs_test_123",
        "mode": "payment",
        "metadata": {
            "organization_id": "org_abc",
            "add_on": "bulk_archive_backfill",
            "quantity": "500",
        },
        "customer": "cus_123",
    }

    result = await stripe_service.StripeService._handle_checkout_completed(session)

    assert result["status"] == "success"
    assert result["action"] == "add_on_purchased"
    assert result["add_on"] == "bulk_archive_backfill"
    assert result["quantity"] == "500"

    # Verify the HTTP call to auth-service
    assert len(http_calls) == 1
    call = http_calls[0]
    assert "/add-ons" in call["url"]
    assert call["json"]["add_on_id"] == "bulk-archive-backfill"
    assert call["json"]["quantity"] == 500
    assert call["json"]["stripe_session_id"] == "cs_test_123"


@pytest.mark.asyncio
async def test_subscription_checkout_with_add_on_metadata(monkeypatch):
    """Subscription-mode checkout with add_on metadata should activate add-on via auth-service."""
    monkeypatch.setattr(stripe_service.settings, "AUTH_SERVICE_URL", "http://auth:8001")
    monkeypatch.setattr(stripe_service.settings, "INTERNAL_SERVICE_TOKEN", "test-token")
    monkeypatch.setattr(stripe_service.settings, "STRIPE_PRICE_PROFESSIONAL_MONTHLY", "")
    monkeypatch.setattr(stripe_service.settings, "STRIPE_PRICE_PROFESSIONAL_ANNUAL", "")
    monkeypatch.setattr(stripe_service.settings, "STRIPE_PRICE_BUSINESS_MONTHLY", "")
    monkeypatch.setattr(stripe_service.settings, "STRIPE_PRICE_BUSINESS_ANNUAL", "")

    http_calls = []

    class FakeResponse:
        status_code = 200

    class FakeClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def post(self, url, json=None, headers=None):
            http_calls.append({"url": url, "json": json})
            return FakeResponse()

    monkeypatch.setattr(stripe_service.httpx, "AsyncClient", lambda **kw: FakeClient())
    monkeypatch.setattr(stripe_service, "_upsert_subscription_record", lambda **kw: None)

    fake_subscription = {
        "id": "sub_addon_123",
        "status": "active",
        "customer": "cus_123",
        "metadata": {
            "organization_id": "org_abc",
            "user_id": "user_123",
            "add_on": "byok",
        },
        "items": {"data": [{"price": {"id": "price_byok_monthly"}}]},
    }

    import stripe as stripe_lib

    monkeypatch.setattr(stripe_lib.Subscription, "retrieve", lambda sid: fake_subscription)

    session = {
        "id": "cs_test_456",
        "mode": "subscription",
        "subscription": "sub_addon_123",
        "customer": "cus_123",
        "metadata": {
            "organization_id": "org_abc",
            "add_on": "byok",
        },
    }

    result = await stripe_service.StripeService._handle_checkout_completed(session)
    assert result["status"] == "success"

    # Should have called add-ons endpoint
    add_on_calls = [c for c in http_calls if "/add-ons" in c["url"]]
    assert len(add_on_calls) == 1
    assert add_on_calls[0]["json"]["add_on_id"] == "byok"
    assert add_on_calls[0]["json"]["stripe_subscription_id"] == "sub_addon_123"


@pytest.mark.asyncio
async def test_subscription_created_with_add_on(monkeypatch):
    """customer.subscription.created with add_on metadata should activate add-on."""
    monkeypatch.setattr(stripe_service.settings, "AUTH_SERVICE_URL", "http://auth:8001")
    monkeypatch.setattr(stripe_service.settings, "INTERNAL_SERVICE_TOKEN", "test-token")

    http_calls = []

    class FakeResponse:
        status_code = 200

    class FakeClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def post(self, url, json=None, headers=None):
            http_calls.append({"url": url, "json": json})
            return FakeResponse()

    monkeypatch.setattr(stripe_service.httpx, "AsyncClient", lambda **kw: FakeClient())

    subscription = {
        "id": "sub_addon_789",
        "status": "active",
        "customer": "cus_123",
        "metadata": {
            "organization_id": "org_abc",
            "user_id": "user_123",
            "add_on": "custom_signing_identity",
        },
        "items": {"data": [{"price": {"id": "price_csi"}}]},
    }

    result = await stripe_service.StripeService._handle_subscription_created(subscription)
    assert result["action"] == "add_on_subscription_created"
    assert result["add_on"] == "custom_signing_identity"

    add_on_calls = [c for c in http_calls if "/add-ons" in c["url"]]
    assert len(add_on_calls) == 1
    assert add_on_calls[0]["json"]["add_on_id"] == "custom-signing-identity"


@pytest.mark.asyncio
async def test_subscription_deleted_with_add_on(monkeypatch):
    """customer.subscription.deleted with add_on metadata should deactivate add-on."""
    monkeypatch.setattr(stripe_service.settings, "AUTH_SERVICE_URL", "http://auth:8001")
    monkeypatch.setattr(stripe_service.settings, "INTERNAL_SERVICE_TOKEN", "test-token")

    http_calls = []

    class FakeResponse:
        status_code = 200

    class FakeClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def post(self, url, json=None, headers=None):
            http_calls.append({"url": url, "json": json})
            return FakeResponse()

    monkeypatch.setattr(stripe_service.httpx, "AsyncClient", lambda **kw: FakeClient())

    subscription = {
        "id": "sub_addon_789",
        "status": "canceled",
        "customer": "cus_123",
        "metadata": {
            "organization_id": "org_abc",
            "user_id": "user_123",
            "add_on": "byok",
        },
        "items": {"data": [{"price": {"id": "price_byok"}}]},
    }

    result = await stripe_service.StripeService._handle_subscription_deleted(subscription)
    assert result["action"] == "add_on_subscription_canceled"
    assert result["add_on"] == "byok"

    add_on_calls = [c for c in http_calls if "/add-ons" in c["url"]]
    assert len(add_on_calls) == 1
    assert add_on_calls[0]["json"]["active"] is False
    assert add_on_calls[0]["json"]["add_on_id"] == "byok"


@pytest.mark.asyncio
async def test_subscription_deleted_without_add_on_downgrades_tier(monkeypatch):
    """Regular subscription deletion (no add_on) should downgrade to free tier as before."""
    monkeypatch.setattr(stripe_service.settings, "AUTH_SERVICE_URL", "http://auth:8001")
    monkeypatch.setattr(stripe_service.settings, "INTERNAL_SERVICE_TOKEN", "test-token")

    sync_calls = []

    async def mock_sync_org_tier(**kwargs):
        sync_calls.append(kwargs)

    monkeypatch.setattr(stripe_service, "_sync_org_tier", mock_sync_org_tier)
    monkeypatch.setattr(stripe_service, "_upsert_subscription_record", lambda **kw: None)

    subscription = {
        "id": "sub_regular_123",
        "status": "canceled",
        "customer": "cus_123",
        "metadata": {
            "organization_id": "org_abc",
            "user_id": "user_123",
        },
        "items": {"data": [{"price": {"id": "price_prof_monthly"}}]},
    }

    result = await stripe_service.StripeService._handle_subscription_deleted(subscription)
    assert result["action"] == "subscription_canceled"
    assert result["tier"] == "free"
    assert sync_calls[0]["tier"] == "free"
