"""Tests for BYOK add-on gating (TEAM_255).

Verifies that BYOK access is granted via:
1. Enterprise/strategic_partner/demo tier
2. features.byok flag
3. add_ons.byok.active flag (new)
"""

import pytest
from fastapi import HTTPException

from app.routers.byok import require_byok_business_tier


class FakeOrg:
    """Minimal dependency injection stand-in for get_current_organization."""

    def __init__(self, **kwargs):
        self._data = {
            "tier": "free",
            "features": {},
            "add_ons": {},
            "byok_enabled": False,
        }
        self._data.update(kwargs)

    def get(self, key, default=None):
        return self._data.get(key, default)


def test_byok_allowed_enterprise_tier():
    org = FakeOrg(tier="enterprise")
    result = require_byok_business_tier(org)
    assert result is org


def test_byok_allowed_features_flag():
    org = FakeOrg(features={"byok": True})
    result = require_byok_business_tier(org)
    assert result is org


def test_byok_allowed_byok_enabled_field():
    org = FakeOrg(byok_enabled=True)
    result = require_byok_business_tier(org)
    assert result is org


def test_byok_allowed_add_ons_active():
    """BYOK purchased as a subscription add-on should grant access."""
    org = FakeOrg(add_ons={"byok": {"active": True, "stripe_subscription_id": "sub_123"}})
    result = require_byok_business_tier(org)
    assert result is org


def test_byok_denied_free_tier_no_addon():
    org = FakeOrg(tier="free")
    with pytest.raises(HTTPException) as exc_info:
        require_byok_business_tier(org)
    assert exc_info.value.status_code == 403


def test_byok_denied_add_on_inactive():
    """Deactivated add-on should not grant access."""
    org = FakeOrg(add_ons={"byok": {"active": False}})
    with pytest.raises(HTTPException) as exc_info:
        require_byok_business_tier(org)
    assert exc_info.value.status_code == 403


def test_byok_denied_empty_add_ons():
    org = FakeOrg(add_ons={})
    with pytest.raises(HTTPException) as exc_info:
        require_byok_business_tier(org)
    assert exc_info.value.status_code == 403


def test_byok_allowed_strategic_partner():
    org = FakeOrg(tier="strategic_partner")
    result = require_byok_business_tier(org)
    assert result is org


def test_byok_allowed_demo():
    org = FakeOrg(tier="demo")
    result = require_byok_business_tier(org)
    assert result is org
