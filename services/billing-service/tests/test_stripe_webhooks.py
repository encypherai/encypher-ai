"""Tests for Stripe webhook tier resolution and sync helpers."""

from pathlib import Path
import importlib
import sys

import pytest

SERVICE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SERVICE_ROOT))
sys.modules.pop("app", None)

stripe_service = importlib.import_module("app.services.stripe_service")


@pytest.mark.parametrize(
    "price_id,expected",
    [
        # Legacy professional/business price IDs now map to "free" (TEAM_145).
        ("price_prof_monthly", "free"),
        ("price_prof_annual", "free"),
        ("price_business_monthly", "free"),
        ("price_business_annual", "free"),
        # Unknown or None price IDs return None.
        ("price_unknown", None),
        (None, None),
    ],
)
def test_resolve_tier_from_price_id(monkeypatch, price_id, expected):
    monkeypatch.setattr(stripe_service.settings, "STRIPE_PRICE_PROFESSIONAL_MONTHLY", "price_prof_monthly")
    monkeypatch.setattr(stripe_service.settings, "STRIPE_PRICE_PROFESSIONAL_ANNUAL", "price_prof_annual")
    monkeypatch.setattr(stripe_service.settings, "STRIPE_PRICE_BUSINESS_MONTHLY", "price_business_monthly")
    monkeypatch.setattr(stripe_service.settings, "STRIPE_PRICE_BUSINESS_ANNUAL", "price_business_annual")

    assert stripe_service._resolve_tier_from_price_id(price_id) == expected


@pytest.mark.asyncio
async def test_handle_subscription_updated_syncs_and_persists(monkeypatch):
    """Subscription updated with a legacy professional price ID -> resolves to 'free'."""
    monkeypatch.setattr(stripe_service.settings, "STRIPE_PRICE_PROFESSIONAL_MONTHLY", "price_prof_monthly")
    monkeypatch.setattr(stripe_service.settings, "STRIPE_PRICE_PROFESSIONAL_ANNUAL", "price_prof_annual")
    monkeypatch.setattr(stripe_service.settings, "STRIPE_PRICE_BUSINESS_MONTHLY", "price_business_monthly")
    monkeypatch.setattr(stripe_service.settings, "STRIPE_PRICE_BUSINESS_ANNUAL", "price_business_annual")

    calls = {"sync": None, "upsert": None}

    async def _sync_org_tier(**kwargs):
        calls["sync"] = kwargs

    def _upsert_subscription_record(**kwargs):
        calls["upsert"] = kwargs

    monkeypatch.setattr(stripe_service, "_sync_org_tier", _sync_org_tier)
    monkeypatch.setattr(stripe_service, "_upsert_subscription_record", _upsert_subscription_record)

    subscription = {
        "id": "sub_123",
        "status": "active",
        "customer": "cus_123",
        "metadata": {"organization_id": "org_123", "user_id": "user_123"},
        "items": {"data": [{"price": {"id": "price_prof_monthly"}}]},
    }

    result = await stripe_service.StripeService._handle_subscription_updated(subscription)

    # Legacy price IDs resolve to "free" (TEAM_145: professional/business tiers removed).
    assert result["tier"] == "free"
    assert calls["sync"]["organization_id"] == "org_123"
    assert calls["sync"]["stripe_subscription_id"] == "sub_123"
    assert calls["upsert"]["organization_id"] == "org_123"
    assert calls["upsert"]["tier"] == "free"
