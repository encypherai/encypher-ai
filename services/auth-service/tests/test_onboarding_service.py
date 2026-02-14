"""
Tests for Onboarding Checklist Service

TEAM_191: Server-side onboarding checklist
TDD: Tests written for onboarding service + auto-approve behavior
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock, PropertyMock
from sqlalchemy.orm import Session

from app.db.models import User, ApiAccessStatus
from app.services.onboarding_service import (
    OnboardingService,
    ONBOARDING_STEPS,
    VALID_STEP_IDS,
)
from app.models.schemas import OnboardingStatusResponse


class TestAutoApproveOnSignup:
    """TEAM_191: Verify new users get auto-approved API access"""

    def test_user_model_default_is_approved(self):
        """New users should default to APPROVED api_access_status"""
        user = User(
            email="new@example.com",
            name="New User",
        )
        # SQLAlchemy Column default is APPROVED
        assert User.__table__.columns["api_access_status"].default.arg == ApiAccessStatus.APPROVED.value

    def test_suspended_users_unaffected(self):
        """Suspended users should remain suspended (not auto-approved)"""
        user = User(
            email="suspended@example.com",
            name="Suspended User",
            api_access_status=ApiAccessStatus.SUSPENDED.value,
        )
        assert user.api_access_status == ApiAccessStatus.SUSPENDED.value


class TestOnboardingSteps:
    """Test onboarding step definitions"""

    def test_all_steps_defined(self):
        """Verify all expected onboarding steps exist"""
        expected_ids = {
            "account_created",
            "publisher_identity_set",
            "first_api_key",
            "first_api_call",
            "first_document_signed",
            "first_verification",
        }
        assert VALID_STEP_IDS == expected_ids

    def test_steps_have_required_fields(self):
        """Each step must have step_id, title, description"""
        for step in ONBOARDING_STEPS:
            assert "step_id" in step
            assert "title" in step
            assert "description" in step
            assert "action_url" in step

    def test_step_count(self):
        """Should have exactly 6 onboarding steps"""
        assert len(ONBOARDING_STEPS) == 6


class TestOnboardingService:
    """Tests for OnboardingService business logic"""

    @pytest.fixture
    def service(self, mock_db):
        return OnboardingService(mock_db)

    @pytest.fixture
    def mock_user(self):
        user = MagicMock(spec=User)
        user.id = "user_test_123"
        user.email = "test@example.com"
        user.onboarding_checklist = {}
        user.onboarding_completed_at = None
        return user

    def _setup_user_query(self, mock_db, user):
        mock_db.query.return_value.filter.return_value.first.return_value = user

    # --- get_onboarding_status ---

    def test_get_status_empty_checklist(self, service, mock_db, mock_user):
        """New user with empty checklist should show all steps incomplete"""
        self._setup_user_query(mock_db, mock_user)

        result = service.get_onboarding_status(mock_user.id)

        assert isinstance(result, OnboardingStatusResponse)
        assert result.total_count == 6
        assert result.completed_count == 0
        assert result.all_completed is False
        assert result.dismissed is False
        assert len(result.steps) == 6
        for step in result.steps:
            assert step.completed is False

    def test_get_status_with_some_completed(self, service, mock_db, mock_user):
        """User with some steps completed should show partial progress"""
        mock_user.onboarding_checklist = {
            "account_created": {"completed_at": "2026-02-14T12:00:00+00:00"},
            "first_api_key": {"completed_at": "2026-02-14T12:05:00+00:00"},
        }
        self._setup_user_query(mock_db, mock_user)

        result = service.get_onboarding_status(mock_user.id)

        assert result.completed_count == 2
        assert result.total_count == 6
        assert result.all_completed is False

        # Check specific steps
        step_map = {s.step_id: s for s in result.steps}
        assert step_map["account_created"].completed is True
        assert step_map["first_api_key"].completed is True
        assert step_map["first_api_call"].completed is False

    def test_get_status_all_completed(self, service, mock_db, mock_user):
        """User with all steps completed should show all_completed=True"""
        mock_user.onboarding_checklist = {
            step["step_id"]: {"completed_at": "2026-02-14T12:00:00+00:00"}
            for step in ONBOARDING_STEPS
        }
        mock_user.onboarding_completed_at = datetime(2026, 2, 14, 12, 0, tzinfo=timezone.utc)
        self._setup_user_query(mock_db, mock_user)

        result = service.get_onboarding_status(mock_user.id)

        assert result.completed_count == 6
        assert result.all_completed is True
        assert result.completed_at is not None

    def test_get_status_dismissed(self, service, mock_db, mock_user):
        """Dismissed checklist should show dismissed=True"""
        mock_user.onboarding_checklist = {"_dismissed": True}
        self._setup_user_query(mock_db, mock_user)

        result = service.get_onboarding_status(mock_user.id)

        assert result.dismissed is True

    def test_get_status_user_not_found(self, service, mock_db):
        """Should raise ValueError for non-existent user"""
        mock_db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(ValueError, match="User not found"):
            service.get_onboarding_status("nonexistent_user")

    # --- complete_step ---

    def test_complete_step_success(self, service, mock_db, mock_user):
        """Completing a valid step should mark it done"""
        self._setup_user_query(mock_db, mock_user)

        result = service.complete_step(mock_user.id, "first_api_key")

        assert mock_user.onboarding_checklist["first_api_key"]["completed_at"] is not None
        mock_db.commit.assert_called()

    def test_complete_step_idempotent(self, service, mock_db, mock_user):
        """Completing an already-completed step should not change the timestamp"""
        original_time = "2026-02-14T12:00:00+00:00"
        mock_user.onboarding_checklist = {
            "first_api_key": {"completed_at": original_time},
        }
        self._setup_user_query(mock_db, mock_user)

        result = service.complete_step(mock_user.id, "first_api_key")

        # Should NOT have been overwritten
        assert mock_user.onboarding_checklist["first_api_key"]["completed_at"] == original_time
        # commit should NOT be called for idempotent no-op
        mock_db.commit.assert_not_called()

    def test_complete_step_invalid_step_id(self, service, mock_db):
        """Should raise ValueError for invalid step ID"""
        with pytest.raises(ValueError, match="Invalid onboarding step"):
            service.complete_step("user_123", "nonexistent_step")

    def test_complete_step_user_not_found(self, service, mock_db):
        """Should raise ValueError for non-existent user"""
        mock_db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(ValueError, match="User not found"):
            service.complete_step("nonexistent_user", "first_api_key")

    def test_complete_all_steps_sets_completed_at(self, service, mock_db, mock_user):
        """Completing the last step should set onboarding_completed_at"""
        # Pre-complete all steps except one
        mock_user.onboarding_checklist = {
            step["step_id"]: {"completed_at": "2026-02-14T12:00:00+00:00"}
            for step in ONBOARDING_STEPS[:-1]
        }
        self._setup_user_query(mock_db, mock_user)

        last_step_id = ONBOARDING_STEPS[-1]["step_id"]
        result = service.complete_step(mock_user.id, last_step_id)

        assert mock_user.onboarding_completed_at is not None

    # --- dismiss_checklist ---

    def test_dismiss_checklist(self, service, mock_db, mock_user):
        """Dismissing should set _dismissed flag"""
        self._setup_user_query(mock_db, mock_user)

        result = service.dismiss_checklist(mock_user.id)

        assert mock_user.onboarding_checklist["_dismissed"] is True
        mock_db.commit.assert_called()

    def test_dismiss_user_not_found(self, service, mock_db):
        """Should raise ValueError for non-existent user"""
        mock_db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(ValueError, match="User not found"):
            service.dismiss_checklist("nonexistent_user")

    # --- initialize_for_new_user ---

    def test_initialize_for_new_user(self, service, mock_db, mock_user):
        """Should mark account_created step as complete"""
        self._setup_user_query(mock_db, mock_user)

        service.initialize_for_new_user(mock_user.id)

        assert "account_created" in mock_user.onboarding_checklist
        assert mock_user.onboarding_checklist["account_created"]["completed_at"] is not None

    def test_initialize_does_not_commit(self, service, mock_db, mock_user):
        """initialize_for_new_user should NOT commit (caller manages transaction)"""
        self._setup_user_query(mock_db, mock_user)

        service.initialize_for_new_user(mock_user.id)

        mock_db.commit.assert_not_called()

    def test_initialize_idempotent(self, service, mock_db, mock_user):
        """Calling initialize twice should not overwrite the first timestamp"""
        original_time = "2026-02-14T12:00:00+00:00"
        mock_user.onboarding_checklist = {
            "account_created": {"completed_at": original_time},
        }
        self._setup_user_query(mock_db, mock_user)

        service.initialize_for_new_user(mock_user.id)

        assert mock_user.onboarding_checklist["account_created"]["completed_at"] == original_time

    def test_initialize_user_not_found(self, service, mock_db):
        """Should silently return for non-existent user (not raise)"""
        mock_db.query.return_value.filter.return_value.first.return_value = None

        # Should not raise
        service.initialize_for_new_user("nonexistent_user")
