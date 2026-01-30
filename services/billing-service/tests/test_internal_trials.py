"""Tests for internal trial provisioning endpoint."""

from datetime import datetime, timedelta
from pathlib import Path
import importlib
import sys
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

SERVICE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SERVICE_ROOT))
sys.modules.pop("app", None)

endpoints = importlib.import_module("app.api.v1.endpoints")


@pytest.mark.asyncio
async def test_internal_trial_requires_token(monkeypatch):
    monkeypatch.setattr(endpoints.settings, "INTERNAL_SERVICE_TOKEN", "secret")
    payload = endpoints.InternalTrialRequest(
        organization_id="org_123",
        user_id="user_123",
        tier=endpoints.TierName.BUSINESS,
        trial_months=2,
    )

    with pytest.raises(HTTPException) as excinfo:
        await endpoints.create_trial_subscription_internal(payload, internal_token="bad", db=SimpleNamespace())

    assert excinfo.value.status_code == 401


@pytest.mark.asyncio
async def test_internal_trial_creates_subscription(monkeypatch):
    monkeypatch.setattr(endpoints.settings, "INTERNAL_SERVICE_TOKEN", "secret")

    subscription = SimpleNamespace(
        id="sub_123",
        user_id="user_123",
        organization_id="org_123",
        plan_id="business",
        plan_name="Business",
        status="trialing",
        billing_cycle="monthly",
        amount=499,
        currency="usd",
        current_period_start=datetime.utcnow(),
        current_period_end=datetime.utcnow() + timedelta(days=60),
        cancel_at_period_end=False,
        created_at=datetime.utcnow(),
    )

    def _create_trial_subscription(**_kwargs):
        return subscription

    monkeypatch.setattr(endpoints.BillingService, "create_trial_subscription", _create_trial_subscription)

    payload = endpoints.InternalTrialRequest(
        organization_id="org_123",
        user_id="user_123",
        tier=endpoints.TierName.BUSINESS,
        trial_months=2,
    )

    response = await endpoints.create_trial_subscription_internal(payload, internal_token="secret", db=SimpleNamespace())

    assert response.success is True
    assert response.data.plan_id == "business"
    assert response.data.status == "trialing"
