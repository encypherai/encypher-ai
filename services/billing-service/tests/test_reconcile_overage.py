"""Tests for the monthly overage reconciliation job."""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
import importlib
import sys

import pytest

SERVICE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SERVICE_ROOT))
sys.modules.pop("app", None)

reconcile = importlib.import_module("app.tasks.reconcile_overage")


@pytest.fixture
def _set_tokens(monkeypatch):
    monkeypatch.setattr(reconcile.settings, "INTERNAL_SERVICE_TOKEN", "tok_internal")
    monkeypatch.setattr(reconcile.settings, "ENTERPRISE_API_URL", "http://enterprise:8000")
    monkeypatch.setattr(reconcile.settings, "AUTH_SERVICE_URL", "http://auth:8001")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _ok_response(json_data=None, status_code=200):
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = json_data or {}
    resp.raise_for_status = MagicMock()
    return resp


def _make_unbilled_records(org_id="org_1"):
    return [
        {
            "id": "rec_1",
            "organization_id": org_id,
            "metric": "sign_requests",
            "overage_count": 150,
            "overage_amount_cents": 300,
            "rate_cents": 2,
        },
        {
            "id": "rec_2",
            "organization_id": org_id,
            "metric": "verify_requests",
            "overage_count": 50,
            "overage_amount_cents": 100,
            "rate_cents": 2,
        },
    ]


def _build_mock_client(unbilled_response, org_response=None, mark_billed_response=None, reset_response=None):
    """Build an AsyncMock httpx client that routes requests by URL pattern."""
    fallback = _ok_response()

    def _route_post(url, **kwargs):
        if "unbilled" in url:
            return unbilled_response
        if "mark-billed" in url:
            return mark_billed_response or fallback
        if "quotas/reset" in url:
            return reset_response or fallback
        return fallback

    def _route_get(url, **kwargs):
        if "/internal/" in url:
            return org_response or fallback
        return fallback

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(side_effect=_route_post)
    mock_client.get = AsyncMock(side_effect=_route_get)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    return mock_client


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
@pytest.mark.usefixtures("_set_tokens")
async def test_reconcile_creates_invoice_items():
    records = _make_unbilled_records()
    mock_client = _build_mock_client(
        unbilled_response=_ok_response({"records": records}),
        org_response=_ok_response({"data": {"stripe_customer_id": "cus_org1"}}),
    )

    mock_invoice = MagicMock()
    mock_invoice.id = "inv_test1"

    with (
        patch("httpx.AsyncClient", return_value=mock_client),
        patch("stripe.InvoiceItem.create") as mock_ii_create,
        patch("stripe.Invoice.create", return_value=mock_invoice),
    ):
        result = await reconcile.reconcile_monthly_overage()

    assert result["invoices_created"] == 1
    assert result["organizations"] == 1
    assert mock_ii_create.call_count == 2

    # Verify first InvoiceItem was created with correct customer and amount
    first_call = mock_ii_create.call_args_list[0]
    assert first_call[1]["customer"] == "cus_org1"
    assert first_call[1]["amount"] == 300


@pytest.mark.asyncio
@pytest.mark.usefixtures("_set_tokens")
async def test_reconcile_marks_records_billed():
    records = _make_unbilled_records()
    mock_client = _build_mock_client(
        unbilled_response=_ok_response({"records": records}),
        org_response=_ok_response({"data": {"stripe_customer_id": "cus_org1"}}),
    )

    mock_invoice = MagicMock()
    mock_invoice.id = "inv_test1"

    with (
        patch("httpx.AsyncClient", return_value=mock_client),
        patch("stripe.InvoiceItem.create"),
        patch("stripe.Invoice.create", return_value=mock_invoice),
    ):
        await reconcile.reconcile_monthly_overage()

    # Find the mark-billed call
    mark_calls = [c for c in mock_client.post.call_args_list if "mark-billed" in c[0][0]]
    assert len(mark_calls) == 1
    payload = mark_calls[0][1]["json"]
    assert set(payload["record_ids"]) == {"rec_1", "rec_2"}
    assert payload["invoice_id"] == "inv_test1"


@pytest.mark.asyncio
@pytest.mark.usefixtures("_set_tokens")
async def test_reconcile_no_overage_records():
    mock_client = _build_mock_client(
        unbilled_response=_ok_response({"records": []}),
    )

    with (
        patch("httpx.AsyncClient", return_value=mock_client),
        patch("stripe.InvoiceItem.create") as mock_ii,
        patch("stripe.Invoice.create") as mock_inv,
    ):
        result = await reconcile.reconcile_monthly_overage()

    assert result["invoices_created"] == 0
    assert result["organizations"] == 0
    mock_ii.assert_not_called()
    mock_inv.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.usefixtures("_set_tokens")
async def test_reconcile_triggers_quota_reset():
    records = _make_unbilled_records()
    mock_client = _build_mock_client(
        unbilled_response=_ok_response({"records": records}),
        org_response=_ok_response({"data": {"stripe_customer_id": "cus_org1"}}),
    )

    mock_invoice = MagicMock()
    mock_invoice.id = "inv_test1"

    with (
        patch("httpx.AsyncClient", return_value=mock_client),
        patch("stripe.InvoiceItem.create"),
        patch("stripe.Invoice.create", return_value=mock_invoice),
    ):
        await reconcile.reconcile_monthly_overage()

    # Verify quota reset was called
    reset_calls = [c for c in mock_client.post.call_args_list if "quotas/reset" in c[0][0]]
    assert len(reset_calls) == 1


@pytest.mark.asyncio
@pytest.mark.usefixtures("_set_tokens")
async def test_reconcile_handles_stripe_error():
    records = _make_unbilled_records()
    mock_client = _build_mock_client(
        unbilled_response=_ok_response({"records": records}),
        org_response=_ok_response({"data": {"stripe_customer_id": "cus_org1"}}),
    )

    from stripe import StripeError

    with (
        patch("httpx.AsyncClient", return_value=mock_client),
        patch("stripe.InvoiceItem.create", side_effect=StripeError("card declined")),
        patch("stripe.Invoice.create") as mock_inv,
    ):
        result = await reconcile.reconcile_monthly_overage()

    # Should handle the error gracefully -- no invoices created but no crash
    assert result["invoices_created"] == 0
    mock_inv.assert_not_called()
