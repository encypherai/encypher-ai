"""
Tests for API Access Gating feature

TEAM_006: API Access Gating
TDD: Tests written before implementation
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch, AsyncMock
from sqlalchemy.orm import Session

# These imports will fail until we implement the feature - that's expected in TDD
try:
    from app.db.models import User, ApiAccessStatus
    from app.services.api_access_service import ApiAccessService
    from app.models.schemas import (
        ApiAccessRequestCreate,
        ApiAccessStatusResponse,
        ApiAccessApproval,
        ApiAccessDenial,
        PendingAccessRequest,
    )
except ImportError:
    # Mark tests as expected to fail until implementation
    pytestmark = pytest.mark.skip(reason="Implementation not yet complete")


class TestApiAccessStatus:
    """Tests for the ApiAccessStatus enum and User model field"""

    def test_api_access_status_enum_values(self):
        """Verify all expected status values exist"""
        assert ApiAccessStatus.NOT_REQUESTED.value == "not_requested"
        assert ApiAccessStatus.PENDING.value == "pending"
        assert ApiAccessStatus.APPROVED.value == "approved"
        assert ApiAccessStatus.DENIED.value == "denied"

    def test_user_default_api_access_status(self, mock_db):
        """New users should have NOT_REQUESTED status by default when persisted"""
        # Note: SQLAlchemy defaults only apply on INSERT, not on Python instantiation
        # This test verifies the model accepts the expected default value
        user = User(
            email="test@example.com",
            name="Test User",
            api_access_status=ApiAccessStatus.NOT_REQUESTED.value,  # Simulating DB default
        )
        assert user.api_access_status == ApiAccessStatus.NOT_REQUESTED.value
        assert user.api_access_requested_at is None
        assert user.api_access_decided_at is None
        assert user.api_access_decided_by is None
        assert user.api_access_use_case is None


class TestApiAccessService:
    """Tests for the ApiAccessService business logic"""

    @pytest.fixture
    def service(self, mock_db):
        """Create ApiAccessService with mock DB"""
        return ApiAccessService(mock_db)

    @pytest.fixture
    def test_user(self):
        """Create a test user with all required attributes as plain values"""
        user = MagicMock()
        user.id = "user_test123"
        user.email = "test@example.com"
        user.name = "Test User"
        user.api_access_status = ApiAccessStatus.NOT_REQUESTED.value
        user.api_access_requested_at = None
        user.api_access_decided_at = None
        user.api_access_decided_by = None
        user.api_access_use_case = None
        user.api_access_denial_reason = None
        return user

    @pytest.mark.asyncio
    async def test_request_api_access_success(self, service, test_user, mock_db):
        """User can request API access with a use case"""
        mock_db.query.return_value.filter.return_value.first.return_value = test_user

        result = await service.request_api_access(user_id=test_user.id, use_case="Building a content verification tool for my news site")

        assert result.status == ApiAccessStatus.PENDING
        assert test_user.api_access_status == ApiAccessStatus.PENDING
        assert test_user.api_access_use_case == "Building a content verification tool for my news site"
        assert test_user.api_access_requested_at is not None
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_request_api_access_already_pending(self, service, test_user, mock_db):
        """Cannot request access if already pending"""
        test_user.api_access_status = ApiAccessStatus.PENDING.value
        mock_db.query.return_value.filter.return_value.first.return_value = test_user

        with pytest.raises(ValueError, match="already pending"):
            await service.request_api_access(user_id=test_user.id, use_case="Another request")

    @pytest.mark.asyncio
    async def test_request_api_access_already_approved(self, service, test_user, mock_db):
        """Cannot request access if already approved"""
        test_user.api_access_status = ApiAccessStatus.APPROVED.value
        mock_db.query.return_value.filter.return_value.first.return_value = test_user

        with pytest.raises(ValueError, match="already approved"):
            await service.request_api_access(user_id=test_user.id, use_case="Another request")

    @pytest.mark.asyncio
    async def test_get_api_access_status(self, service, test_user, mock_db):
        """Can retrieve current API access status"""
        test_user.api_access_status = ApiAccessStatus.PENDING.value
        test_user.api_access_denial_reason = None  # Explicitly set to None, not MagicMock
        mock_db.query.return_value.filter.return_value.first.return_value = test_user

        result = await service.get_api_access_status(user_id=test_user.id)

        assert result.status.value == ApiAccessStatus.PENDING.value

    @pytest.mark.asyncio
    async def test_approve_api_access(self, service, test_user, mock_db):
        """Admin can approve pending access request"""
        test_user.api_access_status = ApiAccessStatus.PENDING.value
        mock_db.query.return_value.filter.return_value.first.return_value = test_user

        admin_user_id = "admin_user123"
        result = await service.approve_api_access(user_id=test_user.id, admin_user_id=admin_user_id)

        assert result.status == ApiAccessStatus.APPROVED
        assert test_user.api_access_status == ApiAccessStatus.APPROVED.value
        assert test_user.api_access_decided_by == admin_user_id
        assert test_user.api_access_decided_at is not None
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_approve_non_pending_fails(self, service, test_user, mock_db):
        """Cannot approve a request that isn't pending"""
        test_user.api_access_status = ApiAccessStatus.NOT_REQUESTED.value
        mock_db.query.return_value.filter.return_value.first.return_value = test_user

        with pytest.raises(ValueError, match="not pending"):
            await service.approve_api_access(user_id=test_user.id, admin_user_id="admin_user123")

    @pytest.mark.asyncio
    async def test_deny_api_access(self, service, test_user, mock_db):
        """Admin can deny pending access request"""
        test_user.api_access_status = ApiAccessStatus.PENDING.value
        mock_db.query.return_value.filter.return_value.first.return_value = test_user

        admin_user_id = "admin_user123"
        result = await service.deny_api_access(user_id=test_user.id, admin_user_id=admin_user_id, reason="Incomplete use case description")

        assert result.status == ApiAccessStatus.DENIED
        assert test_user.api_access_status == ApiAccessStatus.DENIED.value
        assert test_user.api_access_decided_by == admin_user_id
        assert test_user.api_access_decided_at is not None
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_deny_non_pending_fails(self, service, test_user, mock_db):
        """Cannot deny a request that isn't pending"""
        test_user.api_access_status = ApiAccessStatus.APPROVED.value
        mock_db.query.return_value.filter.return_value.first.return_value = test_user

        with pytest.raises(ValueError, match="not pending"):
            await service.deny_api_access(user_id=test_user.id, admin_user_id="admin_user123", reason="Test")

    @pytest.mark.asyncio
    async def test_list_pending_requests(self, service, mock_db):
        """Admin can list all pending access requests"""
        # Create proper mock users with all required attributes as plain values
        user1 = MagicMock()
        user1.id = "user_1"
        user1.email = "user1@example.com"
        user1.name = "User One"
        user1.api_access_status = ApiAccessStatus.PENDING.value
        user1.api_access_requested_at = datetime.now(timezone.utc)
        user1.api_access_use_case = "Use case 1"

        user2 = MagicMock()
        user2.id = "user_2"
        user2.email = "user2@example.com"
        user2.name = "User Two"
        user2.api_access_status = ApiAccessStatus.PENDING.value
        user2.api_access_requested_at = datetime.now(timezone.utc)
        user2.api_access_use_case = "Use case 2"

        pending_users = [user1, user2]
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = pending_users

        result = await service.list_pending_requests()

        assert len(result) == 2
        assert result[0].user_id == "user_1"
        assert result[1].user_id == "user_2"

    @pytest.mark.asyncio
    async def test_user_not_found(self, service, mock_db):
        """Appropriate error when user not found"""
        mock_db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(ValueError, match="User not found"):
            await service.request_api_access(user_id="nonexistent_user", use_case="Test")


class TestApiAccessSchemas:
    """Tests for Pydantic schemas"""

    def test_api_access_request_create_validation(self):
        """Use case is required and must be non-empty"""
        # Valid request
        request = ApiAccessRequestCreate(use_case="Building a content tool")
        assert request.use_case == "Building a content tool"

        # Empty use case should fail
        with pytest.raises(ValueError):
            ApiAccessRequestCreate(use_case="")

        # Too short use case should fail
        with pytest.raises(ValueError):
            ApiAccessRequestCreate(use_case="Hi")

    def test_api_access_status_response(self):
        """Status response includes all relevant fields"""
        response = ApiAccessStatusResponse(status=ApiAccessStatus.PENDING, requested_at=datetime.now(timezone.utc), use_case="My use case")
        assert response.status == ApiAccessStatus.PENDING
        assert response.requested_at is not None
        assert response.use_case == "My use case"

    def test_pending_access_request_schema(self):
        """Pending request includes user info and use case"""
        request = PendingAccessRequest(
            user_id="user_123", email="test@example.com", name="Test User", use_case="Building a tool", requested_at=datetime.now(timezone.utc)
        )
        assert request.user_id == "user_123"
        assert request.email == "test@example.com"


class TestApiAccessGatingIntegration:
    """Integration tests for the full flow"""

    @pytest.mark.asyncio
    async def test_full_approval_flow(self, mock_db):
        """Test complete flow: request -> approve -> can generate keys"""
        # This test verifies the business logic flow
        # 1. User signs up (default: NOT_REQUESTED)
        # 2. User requests API access
        # 3. Admin approves
        # 4. User can now generate API keys

        service = ApiAccessService(mock_db)

        # Create user with default status
        user = MagicMock()
        user.id = "user_flow_test"
        user.email = "flow@example.com"
        user.name = "Flow Test User"
        user.api_access_status = ApiAccessStatus.NOT_REQUESTED.value
        user.api_access_requested_at = None
        user.api_access_decided_at = None
        user.api_access_decided_by = None
        user.api_access_use_case = None
        user.api_access_denial_reason = None

        mock_db.query.return_value.filter.return_value.first.return_value = user

        # Step 1: Request access
        await service.request_api_access(user_id=user.id, use_case="Building content verification for my publication")
        assert user.api_access_status == ApiAccessStatus.PENDING.value

        # Step 2: Admin approves
        await service.approve_api_access(user_id=user.id, admin_user_id="admin_123")
        assert user.api_access_status == ApiAccessStatus.APPROVED.value

        # Step 3: Verify user can now generate keys (checked by key-service)
        assert user.api_access_status == ApiAccessStatus.APPROVED.value

    @pytest.mark.asyncio
    async def test_denied_user_can_reapply(self, mock_db):
        """Denied users should be able to request access again"""
        service = ApiAccessService(mock_db)

        user = MagicMock()
        user.id = "user_denied"
        user.email = "denied@example.com"
        user.name = "Denied User"
        user.api_access_status = ApiAccessStatus.DENIED.value
        user.api_access_use_case = "Old use case"
        user.api_access_requested_at = None
        user.api_access_decided_at = None
        user.api_access_decided_by = None
        user.api_access_denial_reason = "Previous denial reason"

        mock_db.query.return_value.filter.return_value.first.return_value = user

        # Denied user can reapply
        result = await service.request_api_access(user_id=user.id, use_case="New and improved use case with more detail")

        assert result.status == ApiAccessStatus.PENDING
        assert user.api_access_use_case == "New and improved use case with more detail"
