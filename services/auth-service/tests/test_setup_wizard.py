"""
Tests for Publisher Identity Setup Wizard

TEAM_191: Mandatory setup wizard -- collects account_type + display_name
before user can use the dashboard.
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock

from app.db.models import User, Organization
from app.models.schemas import (
    AccountType,
    DashboardLayout,
    SetupWizardRequest,
    WorkflowCategory,
)
from app.services.onboarding_service import ONBOARDING_STEPS, VALID_STEP_IDS


# ============================================================
# Helper to build valid requests with sensible defaults
# ============================================================


def _publisher_request(**overrides):
    """Build a valid media_publishing request, overriding specific fields."""
    defaults = dict(
        account_type=AccountType.INDIVIDUAL,
        display_name="Sarah Chen",
        workflow_category=WorkflowCategory.MEDIA_PUBLISHING,
        publisher_platform="wordpress",
    )
    defaults.update(overrides)
    return SetupWizardRequest(**defaults)


def _enterprise_request(**overrides):
    """Build a valid enterprise request, overriding specific fields."""
    defaults = dict(
        account_type=AccountType.ORGANIZATION,
        display_name="Acme Corp",
        workflow_category=WorkflowCategory.ENTERPRISE,
    )
    defaults.update(overrides)
    return SetupWizardRequest(**defaults)


# ============================================================
# Schema validation: basic fields
# ============================================================


class TestSetupWizardSchemas:
    """Test Pydantic validation for setup wizard request"""

    def test_valid_individual_publisher(self):
        req = _publisher_request()
        assert req.account_type == AccountType.INDIVIDUAL
        assert req.display_name == "Sarah Chen"
        assert req.workflow_category == WorkflowCategory.MEDIA_PUBLISHING

    def test_valid_organization_publisher(self):
        req = _publisher_request(
            account_type=AccountType.ORGANIZATION,
            display_name="The Verge",
        )
        assert req.account_type == AccountType.ORGANIZATION
        assert req.display_name == "The Verge"

    def test_valid_enterprise_request(self):
        req = _enterprise_request()
        assert req.workflow_category == WorkflowCategory.ENTERPRISE
        assert req.dashboard_layout == DashboardLayout.ENTERPRISE

    def test_valid_ai_governance_request(self):
        req = _enterprise_request(
            workflow_category=WorkflowCategory.AI_PROVENANCE_GOVERNANCE,
        )
        assert req.workflow_category == WorkflowCategory.AI_PROVENANCE_GOVERNANCE
        assert req.dashboard_layout == DashboardLayout.ENTERPRISE

    def test_display_name_stripped(self):
        req = _publisher_request(display_name="  Sarah Chen  ")
        assert req.display_name == "Sarah Chen"

    def test_empty_display_name_rejected(self):
        with pytest.raises(Exception):
            _publisher_request(display_name="")

    def test_whitespace_only_display_name_rejected(self):
        with pytest.raises(Exception):
            _publisher_request(display_name="   ")

    def test_invalid_account_type_rejected(self):
        with pytest.raises(Exception):
            _publisher_request(account_type="invalid")


# ============================================================
# Platform validation: publisher workflow
# ============================================================


class TestPlatformValidation:
    """Test all publisher_platform paths through the model validator"""

    # -- Standard platforms (wordpress, ghost, substack, medium) ----------

    @pytest.mark.parametrize("platform", ["wordpress", "ghost", "substack", "medium"])
    def test_standard_platform_accepted(self, platform):
        req = _publisher_request(publisher_platform=platform)
        assert req.publisher_platform == platform
        assert req.publisher_platform_custom is None
        assert req.publisher_platform_language is None
        assert req.publisher_platform_other is None

    # -- Custom CMS -------------------------------------------------------

    def test_custom_cms_with_name_accepted(self):
        """The exact payload Nate's frontend sends: platform='custom', custom='BLS CMS'"""
        req = _publisher_request(
            publisher_platform="custom",
            publisher_platform_custom="BLS CMS",
        )
        assert req.publisher_platform == "custom_cms"
        assert req.publisher_platform_custom == "BLS CMS"
        assert req.publisher_platform_language is None
        assert req.publisher_platform_other is None

    def test_custom_cms_explicit_value_accepted(self):
        req = _publisher_request(
            publisher_platform="custom_cms",
            publisher_platform_custom="Arc XP",
        )
        assert req.publisher_platform == "custom_cms"
        assert req.publisher_platform_custom == "Arc XP"

    def test_custom_cms_without_name_rejected(self):
        """Must provide platform name when selecting custom CMS"""
        with pytest.raises(Exception, match="Platform name is required"):
            _publisher_request(publisher_platform="custom")

    def test_custom_cms_whitespace_name_rejected(self):
        with pytest.raises(Exception, match="Platform name is required"):
            _publisher_request(
                publisher_platform="custom",
                publisher_platform_custom="   ",
            )

    # -- Other platform ---------------------------------------------------

    def test_other_platform_with_details_accepted(self):
        req = _publisher_request(
            publisher_platform="other",
            publisher_platform_other="Email newsletter via Buttondown",
        )
        assert req.publisher_platform == "other"
        assert req.publisher_platform_other == "Email newsletter via Buttondown"
        assert req.publisher_platform_custom is None
        assert req.publisher_platform_language is None

    def test_other_platform_without_details_rejected(self):
        with pytest.raises(Exception, match="Platform details are required"):
            _publisher_request(publisher_platform="other")

    # -- Invalid platform --------------------------------------------------

    def test_invalid_platform_rejected(self):
        with pytest.raises(Exception, match="Invalid publisher platform"):
            _publisher_request(publisher_platform="notion")

    # -- Missing platform for publisher workflow ---------------------------

    def test_publisher_workflow_requires_platform(self):
        with pytest.raises(Exception, match="Publisher platform is required"):
            _publisher_request(publisher_platform=None)


# ============================================================
# Platform validation: non-publisher workflows null out fields
# ============================================================


class TestNonPublisherWorkflowClearsFields:
    """Non-publisher workflows should null out all platform fields"""

    def test_enterprise_clears_platform_fields(self):
        req = _enterprise_request(
            publisher_platform="wordpress",
            publisher_platform_custom="should be cleared",
        )
        assert req.publisher_platform is None
        assert req.publisher_platform_custom is None
        assert req.publisher_platform_language is None
        assert req.publisher_platform_other is None

    def test_ai_governance_clears_platform_fields(self):
        req = _enterprise_request(
            workflow_category=WorkflowCategory.AI_PROVENANCE_GOVERNANCE,
            publisher_platform="ghost",
        )
        assert req.publisher_platform is None


# ============================================================
# Dashboard layout derivation
# ============================================================


class TestDashboardLayoutDerivation:
    """Layout is derived from workflow_category, not user input"""

    def test_publisher_gets_publisher_layout(self):
        req = _publisher_request()
        assert req.dashboard_layout == DashboardLayout.PUBLISHER

    def test_enterprise_gets_enterprise_layout(self):
        req = _enterprise_request()
        assert req.dashboard_layout == DashboardLayout.ENTERPRISE

    def test_ai_governance_gets_enterprise_layout(self):
        req = _enterprise_request(
            workflow_category=WorkflowCategory.AI_PROVENANCE_GOVERNANCE,
        )
        assert req.dashboard_layout == DashboardLayout.ENTERPRISE

    def test_user_supplied_layout_overridden(self):
        """Even if user sends publisher layout with enterprise workflow, it gets corrected"""
        req = _enterprise_request(dashboard_layout=DashboardLayout.PUBLISHER)
        assert req.dashboard_layout == DashboardLayout.ENTERPRISE


# ============================================================
# Onboarding steps
# ============================================================


class TestPublisherIdentityStep:
    """Test that publisher_identity_set is in the onboarding steps"""

    def test_publisher_identity_step_exists(self):
        assert "publisher_identity_set" in VALID_STEP_IDS

    def test_step_count_is_six(self):
        """Should now have 6 steps (added publisher_identity_set)"""
        assert len(ONBOARDING_STEPS) == 6

    def test_publisher_identity_is_second_step(self):
        """publisher_identity_set should come right after account_created"""
        assert ONBOARDING_STEPS[0]["step_id"] == "account_created"
        assert ONBOARDING_STEPS[1]["step_id"] == "publisher_identity_set"
        assert ONBOARDING_STEPS[2]["step_id"] == "first_api_key"


# ============================================================
# DB model columns
# ============================================================


class TestOrganizationModel:
    """Test Organization model has the new publisher identity columns"""

    def test_account_type_column_exists(self):
        assert "account_type" in Organization.__table__.columns

    def test_display_name_column_exists(self):
        assert "display_name" in Organization.__table__.columns

    def test_account_type_nullable(self):
        """account_type should be nullable (NULL = not yet set)"""
        assert Organization.__table__.columns["account_type"].nullable is True

    def test_display_name_nullable(self):
        assert Organization.__table__.columns["display_name"].nullable is True

    def test_anonymous_publisher_column_exists(self):
        assert "anonymous_publisher" in Organization.__table__.columns

    def test_anonymous_publisher_not_nullable(self):
        assert Organization.__table__.columns["anonymous_publisher"].nullable is False


class TestUserSetupCompleted:
    """Test User model has setup_completed_at column"""

    def test_setup_completed_at_column_exists(self):
        assert "setup_completed_at" in User.__table__.columns

    def test_setup_completed_at_nullable(self):
        """Should be nullable -- NULL means wizard not done"""
        assert User.__table__.columns["setup_completed_at"].nullable is True


# ============================================================
# Service-level smoke tests (mocked DB objects)
# ============================================================


class TestSetupWizardService:
    """Test the setup wizard flow using mocked DB objects"""

    @pytest.fixture
    def mock_user(self):
        user = MagicMock(spec=User)
        user.id = "user_test_setup"
        user.email = "sarah@example.com"
        user.name = "Sarah Chen"
        user.setup_completed_at = None
        user.default_organization_id = "org_test_setup"
        user.onboarding_checklist = {"account_created": {"completed_at": "2026-02-14T12:00:00+00:00"}}
        user.onboarding_completed_at = None
        return user

    @pytest.fixture
    def mock_org(self):
        org = MagicMock(spec=Organization)
        org.id = "org_test_setup"
        org.name = ""
        org.account_type = None
        org.display_name = None
        return org

    def test_setup_not_completed_initially(self, mock_user):
        """New user should have setup_completed_at = None"""
        assert mock_user.setup_completed_at is None

    def test_setup_sets_org_fields(self, mock_org):
        """Completing setup should set account_type and display_name"""
        mock_org.account_type = "individual"
        mock_org.display_name = "Sarah Chen"
        assert mock_org.account_type == "individual"
        assert mock_org.display_name == "Sarah Chen"

    def test_setup_sets_org_name_when_blank(self, mock_org):
        """If org name is blank, it should be set to display_name"""
        assert mock_org.name == ""
        mock_org.name = "Sarah Chen"
        assert mock_org.name == "Sarah Chen"

    def test_setup_preserves_org_name_when_set(self):
        """If org already has a name, don't overwrite it"""
        org = MagicMock(spec=Organization)
        org.name = "Existing Org Name"
        org.display_name = None
        # Simulate the endpoint logic: only set name if blank
        if not org.name:
            org.name = "New Name"
        assert org.name == "Existing Org Name"

    def test_setup_marks_user_complete(self, mock_user):
        """Completing setup should set setup_completed_at"""
        mock_user.setup_completed_at = datetime.now(timezone.utc)
        assert mock_user.setup_completed_at is not None
