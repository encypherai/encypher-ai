"""Tests for payment method and overage preference endpoints."""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
import importlib
import sys

import pytest

SERVICE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SERVICE_ROOT))
sys.modules.pop("app", None)

endpoints = importlib.import_module("app.api.v1.endpoints")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_current_user():
    return {
        "id": "user_test123",
        "email": "test@example.com",
        "name": "Test User",
        "organization_id": "org_test123",
    }


def _make_stripe_customer(customer_id="cus_test1", default_pm=None):
    """Build a minimal mock Stripe Customer object."""
    cust = MagicMock()
    cust.id = customer_id
    cust.get = lambda key, default=None: {
        "invoice_settings": {"default_payment_method": default_pm},
    }.get(key, default)
    return cust


def _make_payment_method(pm_id, brand="visa", last4="4242", exp_month=12, exp_year=2030):
    pm = MagicMock()
    pm.id = pm_id
    pm.get = lambda key, default=None: {
        "card": {"brand": brand, "last4": last4, "exp_month": exp_month, "exp_year": exp_year},
    }.get(key, default)
    return pm


# ---------------------------------------------------------------------------
# GET /payment-methods
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_payment_methods_returns_cards(monkeypatch, mock_current_user):
    customer = _make_stripe_customer(default_pm="pm_default")
    monkeypatch.setattr(endpoints.StripeService, "get_or_create_customer", AsyncMock(return_value=customer))

    pm1 = _make_payment_method("pm_default", brand="visa", last4="4242")
    pm2 = _make_payment_method("pm_other", brand="mastercard", last4="5555")
    pm_list = MagicMock()
    pm_list.data = [pm1, pm2]

    with patch("stripe.PaymentMethod.list", return_value=pm_list):
        result = await endpoints.list_payment_methods(current_user=mock_current_user)

    assert len(result) == 2
    assert result[0].id == "pm_default"
    assert result[0].brand == "visa"
    assert result[0].last4 == "4242"
    assert result[0].is_default is True
    assert result[1].id == "pm_other"
    assert result[1].is_default is False


@pytest.mark.asyncio
async def test_get_payment_methods_empty(monkeypatch, mock_current_user):
    customer = _make_stripe_customer()
    monkeypatch.setattr(endpoints.StripeService, "get_or_create_customer", AsyncMock(return_value=customer))

    pm_list = MagicMock()
    pm_list.data = []

    with patch("stripe.PaymentMethod.list", return_value=pm_list):
        result = await endpoints.list_payment_methods(current_user=mock_current_user)

    assert result == []


# ---------------------------------------------------------------------------
# POST /payment-methods/setup
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_payment_setup_returns_checkout_url(monkeypatch, mock_current_user):
    customer = _make_stripe_customer()
    monkeypatch.setattr(endpoints.StripeService, "get_or_create_customer", AsyncMock(return_value=customer))
    monkeypatch.setattr(endpoints.settings, "DASHBOARD_URL", "https://dashboard.example.com")

    mock_session = MagicMock()
    mock_session.url = "https://checkout.stripe.com/session_xyz"
    mock_session.id = "cs_test_abc"

    with patch("stripe.checkout.Session.create", return_value=mock_session):
        request = endpoints.PaymentSetupRequest()
        result = await endpoints.create_payment_setup_session(request=request, current_user=mock_current_user)

    assert result.checkout_url == "https://checkout.stripe.com/session_xyz"
    assert result.session_id == "cs_test_abc"


# ---------------------------------------------------------------------------
# DELETE /payment-methods/{pm_id}
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_delete_payment_method_detaches_card(monkeypatch, mock_current_user):
    customer = _make_stripe_customer()
    monkeypatch.setattr(endpoints.StripeService, "get_or_create_customer", AsyncMock(return_value=customer))

    remaining = MagicMock()
    remaining.data = [_make_payment_method("pm_other")]

    with patch("stripe.PaymentMethod.detach") as mock_detach, patch("stripe.PaymentMethod.list", return_value=remaining):
        result = await endpoints.delete_payment_method(pm_id="pm_to_delete", current_user=mock_current_user)

    mock_detach.assert_called_once_with("pm_to_delete")
    assert result["message"] == "Payment method removed"


@pytest.mark.asyncio
async def test_delete_last_payment_method_updates_auth_service(monkeypatch, mock_current_user):
    customer = _make_stripe_customer()
    monkeypatch.setattr(endpoints.StripeService, "get_or_create_customer", AsyncMock(return_value=customer))
    monkeypatch.setattr(endpoints.settings, "INTERNAL_SERVICE_TOKEN", "tok_internal")
    monkeypatch.setattr(endpoints.settings, "AUTH_SERVICE_URL", "http://auth:8001")

    remaining = MagicMock()
    remaining.data = []  # No cards left

    mock_response = MagicMock()
    mock_response.status_code = 200

    mock_http_client = AsyncMock()
    mock_http_client.post = AsyncMock(return_value=mock_response)
    mock_http_client.__aenter__ = AsyncMock(return_value=mock_http_client)
    mock_http_client.__aexit__ = AsyncMock(return_value=False)

    with (
        patch("stripe.PaymentMethod.detach"),
        patch("stripe.PaymentMethod.list", return_value=remaining),
        patch("httpx.AsyncClient", return_value=mock_http_client),
    ):
        result = await endpoints.delete_payment_method(pm_id="pm_last", current_user=mock_current_user)

    assert result["message"] == "Payment method removed"
    mock_http_client.post.assert_called_once()
    call_args = mock_http_client.post.call_args
    assert "billing-preferences" in call_args[0][0]
    payload = call_args[1]["json"]
    assert payload["has_payment_method"] is False
    assert payload["overage_enabled"] is False


# ---------------------------------------------------------------------------
# POST /payment-methods/{pm_id}/default
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_set_default_payment_method(monkeypatch, mock_current_user):
    customer = _make_stripe_customer()
    monkeypatch.setattr(endpoints.StripeService, "get_or_create_customer", AsyncMock(return_value=customer))

    with patch("stripe.Customer.modify") as mock_modify:
        result = await endpoints.set_default_payment_method(pm_id="pm_new_default", current_user=mock_current_user)

    mock_modify.assert_called_once_with(
        customer.id,
        invoice_settings={"default_payment_method": "pm_new_default"},
    )
    assert result["message"] == "Default payment method updated"


# ---------------------------------------------------------------------------
# GET /overage-preferences
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_overage_preferences(monkeypatch, mock_current_user):
    monkeypatch.setattr(endpoints.settings, "INTERNAL_SERVICE_TOKEN", "tok_internal")
    monkeypatch.setattr(endpoints.settings, "AUTH_SERVICE_URL", "http://auth:8001")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "overage_enabled": True,
        "overage_cap_cents": 50000,
        "has_payment_method": True,
    }

    mock_http_client = AsyncMock()
    mock_http_client.get = AsyncMock(return_value=mock_response)
    mock_http_client.__aenter__ = AsyncMock(return_value=mock_http_client)
    mock_http_client.__aexit__ = AsyncMock(return_value=False)

    with patch("httpx.AsyncClient", return_value=mock_http_client):
        result = await endpoints.get_overage_preferences(current_user=mock_current_user)

    assert result.overage_enabled is True
    assert result.overage_cap_cents == 50000
    assert result.has_payment_method is True


# ---------------------------------------------------------------------------
# PUT /overage-preferences
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_update_overage_preferences(monkeypatch, mock_current_user):
    monkeypatch.setattr(endpoints.settings, "INTERNAL_SERVICE_TOKEN", "tok_internal")
    monkeypatch.setattr(endpoints.settings, "AUTH_SERVICE_URL", "http://auth:8001")

    mock_response = MagicMock()
    mock_response.status_code = 200

    mock_http_client = AsyncMock()
    mock_http_client.post = AsyncMock(return_value=mock_response)
    mock_http_client.__aenter__ = AsyncMock(return_value=mock_http_client)
    mock_http_client.__aexit__ = AsyncMock(return_value=False)

    with patch("httpx.AsyncClient", return_value=mock_http_client):
        request = endpoints.OveragePreferencesUpdate(overage_enabled=True, overage_cap_cents=100000)
        result = await endpoints.update_overage_preferences(request=request, current_user=mock_current_user)

    assert result["message"] == "Overage preferences updated"
    call_args = mock_http_client.post.call_args
    payload = call_args[1]["json"]
    assert payload["overage_enabled"] is True
    assert payload["overage_cap_cents"] == 100000


# ---------------------------------------------------------------------------
# GET /payment-status
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_payment_status(monkeypatch, mock_current_user):
    customer = _make_stripe_customer()
    monkeypatch.setattr(endpoints.StripeService, "get_or_create_customer", AsyncMock(return_value=customer))
    monkeypatch.setattr(endpoints.settings, "AUTH_SERVICE_URL", "http://auth:8001")

    # Stripe customer with a default payment method
    stripe_customer = MagicMock()
    stripe_customer.invoice_settings = MagicMock()
    stripe_customer.invoice_settings.get = lambda k, d=None: "pm_test1" if k == "default_payment_method" else d
    stripe_customer.default_source = None

    pm_obj = MagicMock()
    pm_obj.card = MagicMock()
    pm_obj.card.last4 = "4242"

    # Auth-service overage preferences
    auth_response = MagicMock()
    auth_response.status_code = 200
    auth_response.json.return_value = {"overage_enabled": True}

    mock_http_client = AsyncMock()
    mock_http_client.get = AsyncMock(return_value=auth_response)
    mock_http_client.__aenter__ = AsyncMock(return_value=mock_http_client)
    mock_http_client.__aexit__ = AsyncMock(return_value=False)

    with (
        patch("stripe.Customer.retrieve", return_value=stripe_customer),
        patch("stripe.PaymentMethod.retrieve", return_value=pm_obj),
        patch("httpx.AsyncClient", return_value=mock_http_client),
    ):
        result = await endpoints.get_payment_status(current_user=mock_current_user)

    assert result.has_payment_method is True
    assert result.default_card_last4 == "4242"
    assert result.overage_enabled is True
