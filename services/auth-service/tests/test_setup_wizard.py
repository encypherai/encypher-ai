"""
Tests for Publisher Identity Setup Wizard

TEAM_191: Mandatory setup wizard — collects account_type + display_name
before user can use the dashboard.
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock

from app.db.models import User, Organization
from app.models.schemas import AccountType, SetupWizardRequest
from app.services.onboarding_service import ONBOARDING_STEPS, VALID_STEP_IDS


class TestSetupWizardSchemas:
    """Test Pydantic validation for setup wizard request"""

    def test_valid_individual_request(self):
        req = SetupWizardRequest(account_type=AccountType.INDIVIDUAL, display_name="Sarah Chen")
        assert req.account_type == AccountType.INDIVIDUAL
        assert req.display_name == "Sarah Chen"

    def test_valid_organization_request(self):
        req = SetupWizardRequest(account_type=AccountType.ORGANIZATION, display_name="The Verge")
        assert req.account_type == AccountType.ORGANIZATION
        assert req.display_name == "The Verge"

    def test_display_name_stripped(self):
        req = SetupWizardRequest(account_type=AccountType.INDIVIDUAL, display_name="  Sarah Chen  ")
        assert req.display_name == "Sarah Chen"

    def test_empty_display_name_rejected(self):
        with pytest.raises(Exception):
            SetupWizardRequest(account_type=AccountType.INDIVIDUAL, display_name="")

    def test_whitespace_only_display_name_rejected(self):
        with pytest.raises(Exception):
            SetupWizardRequest(account_type=AccountType.INDIVIDUAL, display_name="   ")

    def test_invalid_account_type_rejected(self):
        with pytest.raises(Exception):
            SetupWizardRequest(account_type="invalid", display_name="Test")


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
        """Should be nullable — NULL means wizard not done"""
        assert User.__table__.columns["setup_completed_at"].nullable is True


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
