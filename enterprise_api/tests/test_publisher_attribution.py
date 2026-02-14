"""
Tests for Publisher Attribution Builder

TEAM_191: Tests the attribution string logic for all combinations of
individual/org, anonymous, whitelabel, and missing fields.
"""

import pytest
from app.utils.publisher_attribution import (
    build_publisher_attribution,
    build_publisher_attribution_from_org_context,
    build_publisher_identity_base,
    build_publisher_identity_base_from_org_context,
)


class TestBuildPublisherAttribution:
    """Test the core attribution builder function"""

    # --- Individual creator ---

    def test_individual_with_display_name(self):
        result = build_publisher_attribution(
            organization_id="org_abc123",
            display_name="Sarah Chen",
            account_type="individual",
        )
        assert result == "Sarah Chen · Powered by Encypher"

    def test_individual_whitelabel(self):
        result = build_publisher_attribution(
            organization_id="org_abc123",
            display_name="Sarah Chen",
            account_type="individual",
            whitelabel=True,
        )
        assert result == "Sarah Chen"

    # --- Organization ---

    def test_organization_with_display_name(self):
        result = build_publisher_attribution(
            organization_id="org_verge",
            display_name="The Verge",
            account_type="organization",
        )
        assert result == "The Verge · Powered by Encypher"

    def test_organization_whitelabel(self):
        result = build_publisher_attribution(
            organization_id="org_verge",
            display_name="The Verge",
            account_type="organization",
            whitelabel=True,
        )
        assert result == "The Verge"

    # --- Anonymous ---

    def test_anonymous_shows_org_id(self):
        result = build_publisher_attribution(
            organization_id="org_abc123",
            display_name="Sarah Chen",
            account_type="individual",
            anonymous_publisher=True,
        )
        assert result == "org_abc123"

    def test_anonymous_whitelabel(self):
        result = build_publisher_attribution(
            organization_id="org_abc123",
            display_name="Sarah Chen",
            anonymous_publisher=True,
            whitelabel=True,
        )
        assert result == "org_abc123"

    # --- Fallbacks ---

    def test_no_display_name_falls_back_to_org_name(self):
        result = build_publisher_attribution(
            organization_id="org_abc123",
            organization_name="My Org",
        )
        assert result == "My Org · Powered by Encypher"

    def test_no_names_falls_back_to_org_id(self):
        result = build_publisher_attribution(
            organization_id="org_abc123",
        )
        assert result == "org_abc123 · Powered by Encypher"

    def test_display_name_takes_precedence_over_org_name(self):
        result = build_publisher_attribution(
            organization_id="org_abc123",
            organization_name="Old Org Name",
            display_name="New Display Name",
        )
        assert result == "New Display Name · Powered by Encypher"


class TestBuildFromOrgContext:
    """Test the convenience wrapper that reads from org context dict"""

    def test_individual_free_tier(self):
        ctx = {
            "organization_id": "org_abc",
            "organization_name": "org_abc",
            "display_name": "Sarah Chen",
            "account_type": "individual",
            "anonymous_publisher": False,
            "features": {},
        }
        result = build_publisher_attribution_from_org_context(ctx)
        assert result == "Sarah Chen · Powered by Encypher"

    def test_org_with_whitelabel(self):
        ctx = {
            "organization_id": "org_verge",
            "organization_name": "The Verge",
            "display_name": "The Verge",
            "account_type": "organization",
            "anonymous_publisher": False,
            "features": {"whitelabel": True},
        }
        result = build_publisher_attribution_from_org_context(ctx)
        assert result == "The Verge"

    def test_anonymous_org(self):
        ctx = {
            "organization_id": "org_secret",
            "organization_name": "Secret Corp",
            "display_name": "Secret Corp",
            "account_type": "organization",
            "anonymous_publisher": True,
            "features": {},
        }
        result = build_publisher_attribution_from_org_context(ctx)
        assert result == "org_secret"

    def test_empty_context_defaults(self):
        ctx = {"organization_id": "org_new"}
        result = build_publisher_attribution_from_org_context(ctx)
        assert result == "org_new · Powered by Encypher"

    def test_features_not_dict(self):
        ctx = {
            "organization_id": "org_abc",
            "display_name": "Test",
            "features": "invalid",
        }
        result = build_publisher_attribution_from_org_context(ctx)
        assert result == "Test · Powered by Encypher"


class TestBuildPublisherIdentityBase:
    """Test base identity helper without branding suffix."""

    def test_base_prefers_display_name(self):
        result = build_publisher_identity_base(
            organization_id="org_abc",
            organization_name="Org Name",
            display_name="Display Name",
        )
        assert result == "Display Name"

    def test_base_falls_back_to_org_name(self):
        result = build_publisher_identity_base(
            organization_id="org_abc",
            organization_name="Org Name",
        )
        assert result == "Org Name"

    def test_base_anonymous_uses_org_id(self):
        result = build_publisher_identity_base(
            organization_id="org_abc",
            display_name="Display Name",
            anonymous_publisher=True,
        )
        assert result == "org_abc"

    def test_base_from_org_context(self):
        result = build_publisher_identity_base_from_org_context(
            {
                "organization_id": "org_abc",
                "organization_name": "Org Name",
                "display_name": "Display Name",
            }
        )
        assert result == "Display Name"
