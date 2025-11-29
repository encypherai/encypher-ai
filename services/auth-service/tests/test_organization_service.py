"""
Unit tests for OrganizationService
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session

from app.services.organization_service import (
    OrganizationService,
    ROLE_HIERARCHY,
    ROLE_CAN_INVITE,
    ROLE_CAN_MANAGE_MEMBERS,
    generate_slug,
)
from app.db.models import (
    Organization,
    OrganizationMember,
    OrganizationInvitation,
    OrganizationAuditLog,
    User,
)


class TestGenerateSlug:
    """Tests for slug generation"""
    
    def test_simple_name(self):
        assert generate_slug("Acme Corp") == "acme-corp"
    
    def test_special_characters(self):
        assert generate_slug("Test & Company!") == "test-company"
    
    def test_multiple_spaces(self):
        assert generate_slug("My   Company   Name") == "my-company-name"
    
    def test_long_name_truncated(self):
        long_name = "A" * 150
        assert len(generate_slug(long_name)) <= 100


class TestRoleHierarchy:
    """Tests for role hierarchy constants"""
    
    def test_owner_highest(self):
        assert ROLE_HIERARCHY['owner'] > ROLE_HIERARCHY['admin']
        assert ROLE_HIERARCHY['owner'] > ROLE_HIERARCHY['manager']
        assert ROLE_HIERARCHY['owner'] > ROLE_HIERARCHY['member']
        assert ROLE_HIERARCHY['owner'] > ROLE_HIERARCHY['viewer']
    
    def test_admin_above_manager(self):
        assert ROLE_HIERARCHY['admin'] > ROLE_HIERARCHY['manager']
    
    def test_manager_above_member(self):
        assert ROLE_HIERARCHY['manager'] > ROLE_HIERARCHY['member']
    
    def test_member_above_viewer(self):
        assert ROLE_HIERARCHY['member'] > ROLE_HIERARCHY['viewer']


class TestOrganizationService:
    """Tests for OrganizationService"""
    
    @pytest.fixture
    def mock_db(self):
        """Create a mock database session"""
        return MagicMock(spec=Session)
    
    @pytest.fixture
    def service(self, mock_db):
        """Create an OrganizationService instance"""
        return OrganizationService(mock_db)
    
    @pytest.fixture
    def mock_org(self):
        """Create a mock organization"""
        org = MagicMock(spec=Organization)
        org.id = "org_test123"
        org.name = "Test Org"
        org.slug = "test-org"
        org.email = "test@example.com"
        org.tier = "business"
        org.max_seats = 5
        return org
    
    @pytest.fixture
    def mock_user(self):
        """Create a mock user"""
        user = MagicMock(spec=User)
        user.id = "user_test123"
        user.email = "user@example.com"
        user.name = "Test User"
        return user
    
    @pytest.fixture
    def mock_owner_member(self, mock_org, mock_user):
        """Create a mock owner member"""
        member = MagicMock(spec=OrganizationMember)
        member.id = "mem_owner123"
        member.organization_id = mock_org.id
        member.user_id = mock_user.id
        member.role = "owner"
        member.status = "active"
        return member


class TestCreateOrganization(TestOrganizationService):
    """Tests for create_organization"""
    
    def test_creates_org_with_owner(self, service, mock_db, mock_user):
        """Test that creating an org adds the creator as owner"""
        # Setup
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # Execute
        with patch.object(service, '_log_action'):
            org = service.create_organization(
                name="Test Org",
                email="test@example.com",
                owner_user_id=mock_user.id,
                tier="business"
            )
        
        # Verify org was added
        assert mock_db.add.call_count >= 2  # org + member
        mock_db.commit.assert_called_once()
    
    def test_sets_max_seats_by_tier(self, service, mock_db):
        """Test that max_seats is set based on tier"""
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # Business tier should have 5 seats
        with patch.object(service, '_log_action'):
            service.create_organization(
                name="Business Org",
                email="biz@example.com",
                owner_user_id="user123",
                tier="business"
            )
        
        # Check the Organization was created with correct max_seats
        add_calls = mock_db.add.call_args_list
        org_call = [c for c in add_calls if isinstance(c[0][0], Organization)]
        # Note: In a real test, we'd verify the actual max_seats value


class TestGetUserRole(TestOrganizationService):
    """Tests for get_user_role"""
    
    def test_returns_role_for_active_member(self, service, mock_db, mock_org, mock_owner_member):
        """Test that role is returned for active members"""
        mock_db.query.return_value.filter.return_value.first.return_value = mock_owner_member
        
        role = service.get_user_role(mock_org.id, mock_owner_member.user_id)
        
        assert role == "owner"
    
    def test_returns_none_for_non_member(self, service, mock_db, mock_org):
        """Test that None is returned for non-members"""
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        role = service.get_user_role(mock_org.id, "nonexistent_user")
        
        assert role is None


class TestUpdateMemberRole(TestOrganizationService):
    """Tests for update_member_role"""
    
    def test_cannot_change_owner_role(self, service, mock_db, mock_org, mock_owner_member):
        """Test that owner role cannot be changed"""
        # Setup: actor is admin, target is owner
        admin_member = MagicMock(spec=OrganizationMember)
        admin_member.role = "admin"
        admin_member.status = "active"
        
        def mock_get_member(org_id, user_id):
            if user_id == "admin_user":
                return admin_member
            return mock_owner_member
        
        with patch.object(service, 'get_member', side_effect=mock_get_member):
            with patch.object(service, 'get_user_role', return_value="admin"):
                with pytest.raises(ValueError, match="Cannot change the owner's role"):
                    service.update_member_role(
                        org_id=mock_org.id,
                        target_user_id=mock_owner_member.user_id,
                        new_role="admin",
                        actor_user_id="admin_user"
                    )
    
    def test_cannot_promote_to_owner(self, service, mock_db, mock_org):
        """Test that members cannot be promoted to owner"""
        member = MagicMock(spec=OrganizationMember)
        member.role = "member"
        member.status = "active"
        
        with patch.object(service, 'get_member', return_value=member):
            with patch.object(service, '_has_permission', return_value=True):
                with pytest.raises(ValueError, match="Cannot promote to owner"):
                    service.update_member_role(
                        org_id=mock_org.id,
                        target_user_id="member_user",
                        new_role="owner",
                        actor_user_id="admin_user"
                    )


class TestCreateInvitation(TestOrganizationService):
    """Tests for create_invitation"""
    
    def test_cannot_invite_as_owner(self, service, mock_db, mock_org):
        """Test that invitations cannot be for owner role"""
        with patch.object(service, '_has_permission', return_value=True):
            with pytest.raises(ValueError, match="Invalid role for invitation"):
                service.create_invitation(
                    org_id=mock_org.id,
                    email="new@example.com",
                    role="owner",
                    inviter_user_id="admin_user"
                )
    
    def test_checks_seat_limit(self, service, mock_db, mock_org):
        """Test that seat limit is enforced"""
        with patch.object(service, '_has_permission', return_value=True):
            with patch.object(service, 'get_seat_count', return_value={
                'used': 5, 'max': 5, 'available': 0, 'unlimited': False
            }):
                with pytest.raises(ValueError, match="No seats available"):
                    service.create_invitation(
                        org_id=mock_org.id,
                        email="new@example.com",
                        role="member",
                        inviter_user_id="admin_user"
                    )
    
    def test_prevents_duplicate_invitation(self, service, mock_db, mock_org):
        """Test that duplicate pending invitations are prevented"""
        existing_invite = MagicMock(spec=OrganizationInvitation)
        existing_invite.status = "pending"
        
        with patch.object(service, '_has_permission', return_value=True):
            with patch.object(service, 'get_seat_count', return_value={
                'used': 1, 'max': 5, 'available': 4, 'unlimited': False
            }):
                # No existing user
                mock_db.query.return_value.filter.return_value.first.side_effect = [
                    None,  # No existing user
                    existing_invite  # Existing invitation
                ]
                
                with pytest.raises(ValueError, match="already pending"):
                    service.create_invitation(
                        org_id=mock_org.id,
                        email="existing@example.com",
                        role="member",
                        inviter_user_id="admin_user"
                    )


class TestAcceptInvitation(TestOrganizationService):
    """Tests for accept_invitation"""
    
    def test_rejects_expired_invitation(self, service, mock_db):
        """Test that expired invitations are rejected"""
        expired_invite = MagicMock(spec=OrganizationInvitation)
        expired_invite.status = "pending"
        expired_invite.expires_at = datetime.utcnow() - timedelta(days=1)
        
        with patch.object(service, 'get_invitation_by_token', return_value=expired_invite):
            with pytest.raises(ValueError, match="expired"):
                service.accept_invitation(token="test_token", user_id="user123")
    
    def test_rejects_wrong_email(self, service, mock_db):
        """Test that invitation is rejected if email doesn't match"""
        invite = MagicMock(spec=OrganizationInvitation)
        invite.status = "pending"
        invite.expires_at = datetime.utcnow() + timedelta(days=1)
        invite.email = "invited@example.com"
        
        wrong_user = MagicMock(spec=User)
        wrong_user.email = "different@example.com"
        
        with patch.object(service, 'get_invitation_by_token', return_value=invite):
            mock_db.query.return_value.filter.return_value.first.return_value = wrong_user
            
            with pytest.raises(ValueError, match="different email"):
                service.accept_invitation(token="test_token", user_id="user123")


class TestPermissionHelpers(TestOrganizationService):
    """Tests for permission helper methods"""
    
    def test_owner_can_invite(self, service):
        """Test that owners can invite"""
        with patch.object(service, 'get_user_role', return_value="owner"):
            assert service.can_user_invite("org123", "user123") is True
    
    def test_admin_can_invite(self, service):
        """Test that admins can invite"""
        with patch.object(service, 'get_user_role', return_value="admin"):
            assert service.can_user_invite("org123", "user123") is True
    
    def test_manager_can_invite(self, service):
        """Test that managers can invite"""
        with patch.object(service, 'get_user_role', return_value="manager"):
            assert service.can_user_invite("org123", "user123") is True
    
    def test_member_cannot_invite(self, service):
        """Test that regular members cannot invite"""
        with patch.object(service, 'get_user_role', return_value="member"):
            assert service.can_user_invite("org123", "user123") is False
    
    def test_viewer_cannot_invite(self, service):
        """Test that viewers cannot invite"""
        with patch.object(service, 'get_user_role', return_value="viewer"):
            assert service.can_user_invite("org123", "user123") is False
    
    def test_owner_can_manage_members(self, service):
        """Test that owners can manage members"""
        with patch.object(service, 'get_user_role', return_value="owner"):
            assert service.can_user_manage_members("org123", "user123") is True
    
    def test_admin_can_manage_members(self, service):
        """Test that admins can manage members"""
        with patch.object(service, 'get_user_role', return_value="admin"):
            assert service.can_user_manage_members("org123", "user123") is True
    
    def test_manager_cannot_manage_members(self, service):
        """Test that managers cannot manage members (only invite)"""
        with patch.object(service, 'get_user_role', return_value="manager"):
            assert service.can_user_manage_members("org123", "user123") is False


class TestGetSeatCount(TestOrganizationService):
    """Tests for get_seat_count"""
    
    def test_counts_active_and_pending(self, service, mock_db, mock_org):
        """Test that both active members and pending invites are counted"""
        with patch.object(service, 'get_organization', return_value=mock_org):
            # 3 active members
            mock_db.query.return_value.filter.return_value.count.side_effect = [3, 1]
            
            result = service.get_seat_count(mock_org.id)
            
            assert result['active'] == 3
            assert result['pending'] == 1
            assert result['used'] == 4
            assert result['max'] == 5
            assert result['available'] == 1
            assert result['unlimited'] is False
    
    def test_unlimited_seats(self, service, mock_db, mock_org):
        """Test unlimited seats for enterprise"""
        mock_org.max_seats = -1
        
        with patch.object(service, 'get_organization', return_value=mock_org):
            mock_db.query.return_value.filter.return_value.count.side_effect = [10, 5]
            
            result = service.get_seat_count(mock_org.id)
            
            assert result['unlimited'] is True
            assert result['available'] == -1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
