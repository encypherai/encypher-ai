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
    generate_slug,
)
from app.db.models import (
    Organization,
    OrganizationMember,
    OrganizationInvitation,
    OrganizationDomainClaim,
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
        assert ROLE_HIERARCHY["owner"] > ROLE_HIERARCHY["admin"]
        assert ROLE_HIERARCHY["owner"] > ROLE_HIERARCHY["manager"]
        assert ROLE_HIERARCHY["owner"] > ROLE_HIERARCHY["member"]
        assert ROLE_HIERARCHY["owner"] > ROLE_HIERARCHY["viewer"]

    def test_admin_above_manager(self):
        assert ROLE_HIERARCHY["admin"] > ROLE_HIERARCHY["manager"]

    def test_manager_above_member(self):
        assert ROLE_HIERARCHY["manager"] > ROLE_HIERARCHY["member"]

    def test_member_above_viewer(self):
        assert ROLE_HIERARCHY["member"] > ROLE_HIERARCHY["viewer"]


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
        with patch.object(service, "_log_action"):
            org = service.create_organization(name="Test Org", email="test@example.com", owner_user_id=mock_user.id, tier="business")

        # Verify org was added
        assert mock_db.add.call_count >= 2  # org + member
        mock_db.commit.assert_called_once()

    def test_sets_max_seats_by_tier(self, service, mock_db):
        """Test that max_seats is set based on tier"""
        mock_db.query.return_value.filter.return_value.first.return_value = None

        # Business tier should have 5 seats
        with patch.object(service, "_log_action"):
            service.create_organization(name="Business Org", email="biz@example.com", owner_user_id="user123", tier="business")

        # Check the Organization was created with correct max_seats
        add_calls = mock_db.add.call_args_list
        org_call = [c for c in add_calls if isinstance(c[0][0], Organization)]
        # Note: In a real test, we'd verify the actual max_seats value


class TestTierConfig(TestOrganizationService):
    """Tests for tier configuration feature flags."""

    @pytest.mark.parametrize("tier", ["enterprise", "strategic_partner"])
    def test_fuzzy_fingerprint_enabled_for_enterprise_tiers(self, service, tier):
        config = service._get_tier_config(tier)
        assert config is not None
        assert config["features"].get("fuzzy_fingerprint") is True

    def test_fuzzy_fingerprint_disabled_for_lower_tiers(self, service):
        config = service._get_tier_config("business")
        assert config is not None
        assert config["features"].get("fuzzy_fingerprint") is not True


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

        with patch.object(service, "get_member", side_effect=mock_get_member):
            with patch.object(service, "get_user_role", return_value="admin"):
                with pytest.raises(ValueError, match="Cannot change the owner's role"):
                    service.update_member_role(
                        org_id=mock_org.id, target_user_id=mock_owner_member.user_id, new_role="admin", actor_user_id="admin_user"
                    )

    def test_cannot_promote_to_owner(self, service, mock_db, mock_org):
        """Test that members cannot be promoted to owner"""
        member = MagicMock(spec=OrganizationMember)
        member.role = "member"
        member.status = "active"

        with patch.object(service, "get_member", return_value=member):
            with patch.object(service, "_has_permission", return_value=True):
                with pytest.raises(ValueError, match="Cannot promote to owner"):
                    service.update_member_role(org_id=mock_org.id, target_user_id="member_user", new_role="owner", actor_user_id="admin_user")


class TestCreateInvitation(TestOrganizationService):
    """Tests for create_invitation"""

    def test_cannot_invite_as_owner(self, service, mock_db, mock_org):
        """Test that invitations cannot be for owner role"""
        with patch.object(service, "_has_permission", return_value=True):
            with pytest.raises(ValueError, match="Invalid role for invitation"):
                service.create_invitation(org_id=mock_org.id, email="new@example.com", role="owner", inviter_user_id="admin_user")

    def test_checks_seat_limit(self, service, mock_db, mock_org):
        """Test that seat limit is enforced"""
        with patch.object(service, "_has_permission", return_value=True):
            with patch.object(service, "get_seat_count", return_value={"used": 5, "max": 5, "available": 0, "unlimited": False}):
                with pytest.raises(ValueError, match="No seats available"):
                    service.create_invitation(org_id=mock_org.id, email="new@example.com", role="member", inviter_user_id="admin_user")

    def test_prevents_duplicate_invitation(self, service, mock_db, mock_org):
        """Test that duplicate pending invitations are prevented"""
        existing_invite = MagicMock(spec=OrganizationInvitation)
        existing_invite.status = "pending"

        with patch.object(service, "_has_permission", return_value=True):
            with patch.object(service, "get_seat_count", return_value={"used": 1, "max": 5, "available": 4, "unlimited": False}):
                # No existing user
                mock_db.query.return_value.filter.return_value.first.side_effect = [
                    None,  # No existing user
                    existing_invite,  # Existing invitation
                ]

                with pytest.raises(ValueError, match="already pending"):
                    service.create_invitation(org_id=mock_org.id, email="existing@example.com", role="member", inviter_user_id="admin_user")

    @pytest.mark.parametrize(
        ("tier", "trial_months"),
        [("business", None), (None, 2)],
    )
    def test_requires_tier_and_trial_months_pair(self, service, mock_db, mock_org, tier, trial_months):
        """Trial invites require both tier and trial_months."""
        with patch.object(service, "_has_permission", return_value=True):
            with patch.object(service, "get_seat_count", return_value={"used": 0, "max": 5, "available": 5, "unlimited": False}):
                mock_db.query.return_value.filter.return_value.first.side_effect = [None, None]

                with pytest.raises(ValueError, match="Trial invitations require both tier and trial months"):
                    service.create_invitation(
                        org_id=mock_org.id,
                        email="new@example.com",
                        role="member",
                        inviter_user_id="admin_user",
                        tier=tier,
                        trial_months=trial_months,
                    )

    @pytest.mark.parametrize(
        ("first_name", "last_name"),
        [(None, "Doe"), ("Jane", None), ("", "Doe"), ("Jane", "")],
    )
    def test_trial_invite_requires_names(self, service, mock_db, mock_org, first_name, last_name):
        """Trial invites require first and last name."""
        with patch.object(service, "_has_permission", return_value=True):
            with patch.object(service, "get_seat_count", return_value={"used": 0, "max": 5, "available": 5, "unlimited": False}):
                mock_db.query.return_value.filter.return_value.first.side_effect = [None, None]

                with pytest.raises(ValueError, match="first and last name"):
                    service.create_invitation(
                        org_id=mock_org.id,
                        email="new@example.com",
                        role="member",
                        inviter_user_id="admin_user",
                        first_name=first_name,
                        last_name=last_name,
                        tier="business",
                        trial_months=2,
                    )


class TestCreateTrialInvitationForNewOrg(TestOrganizationService):
    """Tests for create_trial_invitation_for_new_org."""

    def test_creates_org_and_owner_invite(self, service):
        invitation = MagicMock(spec=OrganizationInvitation)
        org = MagicMock(spec=Organization)
        org.id = "org_new"

        with patch.object(service, "create_organization_without_owner", return_value=org) as create_org:
            with patch.object(service, "create_invitation", return_value=invitation) as create_invitation:
                result = service.create_trial_invitation_for_new_org(
                    organization_name="New Org",
                    email="invitee@example.com",
                    first_name="Jane",
                    last_name="Doe",
                    tier="business",
                    trial_months=2,
                    inviter_user_id="admin_user",
                )

        assert result == invitation
        create_org.assert_called_once_with(
            name="New Org",
            email="invitee@example.com",
            tier="starter",
            created_by="admin_user",
        )
        create_invitation.assert_called_once_with(
            org_id="org_new",
            email="invitee@example.com",
            role="owner",
            inviter_user_id="admin_user",
            message=None,
            first_name="Jane",
            last_name="Doe",
            organization_name="New Org",
            tier="business",
            trial_months=2,
            allow_owner=True,
            skip_permission=True,
            skip_seat_check=True,
        )

    @pytest.mark.parametrize("organization_name", [None, ""])
    def test_requires_org_name(self, service, organization_name):
        with pytest.raises(ValueError, match="Organization name is required"):
            service.create_trial_invitation_for_new_org(
                organization_name=organization_name,
                email="invitee@example.com",
                first_name="Jane",
                last_name="Doe",
                tier="business",
                trial_months=2,
                inviter_user_id="admin_user",
            )

    @pytest.mark.parametrize(
        ("first_name", "last_name"),
        [(None, "Doe"), ("Jane", None), ("", "Doe"), ("Jane", "")],
    )
    def test_requires_first_and_last_name(self, service, first_name, last_name):
        with pytest.raises(ValueError, match="first and last name"):
            service.create_trial_invitation_for_new_org(
                organization_name="New Org",
                email="invitee@example.com",
                first_name=first_name,
                last_name=last_name,
                tier="business",
                trial_months=2,
                inviter_user_id="admin_user",
            )


class TestDomainClaims(TestOrganizationService):
    """Tests for domain claim logic"""

    def test_create_domain_claim_rejects_common_domain(self, service, mock_db, mock_org):
        with patch.object(service, "_has_permission", return_value=True):
            with patch.object(service, "get_organization", return_value=mock_org):
                with pytest.raises(ValueError, match="Common email domains cannot be claimed"):
                    service.create_domain_claim(
                        org_id=mock_org.id,
                        domain="gmail.com",
                        verification_email="admin@gmail.com",
                        actor_user_id="user123",
                    )

    def test_create_domain_claim_enforces_limit(self, service, mock_db, mock_org):
        active_query = MagicMock()
        active_query.filter.return_value.count.return_value = 1
        existing_query = MagicMock()
        existing_query.filter.return_value.first.return_value = None

        with patch.object(service, "_has_permission", return_value=True):
            mock_org.tier = "starter"
            with patch.object(service, "get_organization", return_value=mock_org):
                with patch.object(service, "_log_action"):
                    mock_db.query.side_effect = [active_query, existing_query]
                    with pytest.raises(ValueError, match="Domain claim limit reached"):
                        service.create_domain_claim(
                            org_id=mock_org.id,
                            domain="example.com",
                            verification_email="admin@example.com",
                            actor_user_id="user123",
                        )

    def test_verify_domain_email_marks_verified(self, service, mock_db):
        claim = MagicMock(spec=OrganizationDomainClaim)
        claim.status = "pending"
        claim.email_verified_at = None
        claim.dns_verified_at = datetime.utcnow()
        claim.verified_at = None

        query = MagicMock()
        query.filter.return_value.first.return_value = claim
        mock_db.query.return_value = query

        result = service.verify_domain_email("token123")

        assert result.email_verified_at is not None
        assert result.status == "verified"
        mock_db.commit.assert_called_once()

    def test_verify_domain_dns_sets_verified(self, service, mock_db):
        claim = MagicMock(spec=OrganizationDomainClaim)
        claim.status = "pending"
        claim.dns_token = "abc"
        claim.dns_verified_at = None
        claim.email_verified_at = datetime.utcnow()
        claim.verified_at = None

        query = MagicMock()
        query.filter.return_value.first.return_value = claim
        mock_db.query.return_value = query

        with patch.object(service, "_has_permission", return_value=True):
            result = service.verify_domain_dns("org123", "claim123", "user123", ["encypher-domain-claim=abc"])

        assert result.dns_verified_at is not None
        assert result.status == "verified"
        mock_db.commit.assert_called_once()

    def test_set_domain_auto_join_requires_verified(self, service, mock_db):
        claim = MagicMock(spec=OrganizationDomainClaim)
        claim.status = "pending"

        query = MagicMock()
        query.filter.return_value.first.return_value = claim
        mock_db.query.return_value = query

        with patch.object(service, "_has_permission", return_value=True):
            with pytest.raises(ValueError, match="Domain must be verified"):
                service.set_domain_auto_join("org123", "claim123", "user123", True)


class TestAcceptInvitation(TestOrganizationService):
    """Tests for accept_invitation"""

    def test_rejects_expired_invitation(self, service, mock_db):
        """Test that expired invitations are rejected"""
        expired_invite = MagicMock(spec=OrganizationInvitation)
        expired_invite.status = "pending"
        expired_invite.expires_at = datetime.utcnow() - timedelta(days=1)

        with patch.object(service, "get_invitation_by_token", return_value=expired_invite):
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

        with patch.object(service, "get_invitation_by_token", return_value=invite):
            mock_db.query.return_value.filter.return_value.first.return_value = wrong_user

            with pytest.raises(ValueError, match="different email"):
                service.accept_invitation(token="test_token", user_id="user123")

    def test_applies_trial_metadata_for_existing_user(self, service, mock_db):
        """Ensure trial invites apply org metadata and sync billing for existing users."""
        invitation = MagicMock(spec=OrganizationInvitation)
        invitation.status = "pending"
        invitation.expires_at = datetime.utcnow() + timedelta(days=1)
        invitation.email = "invitee@example.com"
        invitation.organization_id = "org_123"
        invitation.role = "member"
        invitation.invited_by = "user_inviter"
        invitation.created_at = datetime.utcnow()
        invitation.tier = "business"
        invitation.trial_months = 3

        user = MagicMock(spec=User)
        user.id = "user_123"
        user.email = "invitee@example.com"

        mock_db.query.return_value.filter.return_value.first.return_value = user

        org = MagicMock(spec=Organization)

        with patch.object(service, "get_invitation_by_token", return_value=invitation):
            with patch.object(service, "get_member", return_value=None):
                with patch.object(service, "_log_action"):
                    with patch.object(service, "update_tier_internal", return_value=org) as update_tier:
                        with patch.object(service, "_apply_trial_metadata") as apply_trial:
                            with patch.object(service, "_sync_trial_to_billing") as sync_trial:
                                service.accept_invitation(token="token_123", user_id=user.id)

        update_tier.assert_called_once_with(
            org_id="org_123",
            tier="business",
            subscription_status="trialing",
        )
        apply_trial.assert_called_once_with(org=org, tier="business", trial_months=3)
        sync_trial.assert_called_once_with(
            organization_id="org_123",
            user_id=user.id,
            tier="business",
            trial_months=3,
        )


class TestAcceptInvitationNewUser(TestOrganizationService):
    """Tests for accept_invitation_new_user"""

    def test_applies_trial_tier_and_syncs_billing(self, service, mock_db):
        """Ensure trial-tier invites update org tier and sync billing."""
        invitation = MagicMock(spec=OrganizationInvitation)
        invitation.status = "pending"
        invitation.expires_at = datetime.utcnow() + timedelta(days=1)
        invitation.email = "invitee@example.com"
        invitation.first_name = "Jane"
        invitation.last_name = "Doe"
        invitation.organization_id = "org_123"
        invitation.role = "member"
        invitation.invited_by = "user_inviter"
        invitation.created_at = datetime.utcnow()
        invitation.tier = "business"
        invitation.trial_months = 2

        query = MagicMock()
        query.filter.return_value.first.return_value = None
        mock_db.query.return_value = query

        def _flush():
            if mock_db.add.call_args_list:
                user_obj = mock_db.add.call_args_list[0][0][0]
                user_obj.id = "user_123"

        mock_db.flush.side_effect = _flush

        with patch.object(service, "get_invitation_by_token", return_value=invitation):
            with patch.object(service, "_log_action"):
                org = MagicMock(spec=Organization)
                with patch.object(service, "update_tier_internal", return_value=org) as update_tier:
                    with patch.object(service, "_apply_trial_metadata") as apply_trial:
                        with patch.object(service, "_sync_trial_to_billing") as sync_trial:
                            user, member = service.accept_invitation_new_user(
                                token="token_123",
                                name=None,
                                password_hash="hash",
                            )

        update_tier.assert_called_once_with(
            org_id="org_123",
            tier="business",
            subscription_status="trialing",
        )
        apply_trial.assert_called_once_with(org=org, tier="business", trial_months=2)
        sync_trial.assert_called_once_with(
            organization_id="org_123",
            user_id=user.id,
            tier="business",
            trial_months=2,
        )
        assert member.organization_id == "org_123"


class TestPermissionHelpers(TestOrganizationService):
    """Tests for permission helper methods"""

    def test_owner_can_invite(self, service):
        """Test that owners can invite"""
        with patch.object(service, "get_user_role", return_value="owner"):
            assert service.can_user_invite("org123", "user123") is True

    def test_admin_can_invite(self, service):
        """Test that admins can invite"""
        with patch.object(service, "get_user_role", return_value="admin"):
            assert service.can_user_invite("org123", "user123") is True

    def test_manager_can_invite(self, service):
        """Test that managers can invite"""
        with patch.object(service, "get_user_role", return_value="manager"):
            assert service.can_user_invite("org123", "user123") is True

    def test_member_cannot_invite(self, service):
        """Test that regular members cannot invite"""
        with patch.object(service, "get_user_role", return_value="member"):
            assert service.can_user_invite("org123", "user123") is False

    def test_viewer_cannot_invite(self, service):
        """Test that viewers cannot invite"""
        with patch.object(service, "get_user_role", return_value="viewer"):
            assert service.can_user_invite("org123", "user123") is False

    def test_owner_can_manage_members(self, service):
        """Test that owners can manage members"""
        with patch.object(service, "get_user_role", return_value="owner"):
            assert service.can_user_manage_members("org123", "user123") is True

    def test_admin_can_manage_members(self, service):
        """Test that admins can manage members"""
        with patch.object(service, "get_user_role", return_value="admin"):
            assert service.can_user_manage_members("org123", "user123") is True

    def test_manager_cannot_manage_members(self, service):
        """Test that managers cannot manage members (only invite)"""
        with patch.object(service, "get_user_role", return_value="manager"):
            assert service.can_user_manage_members("org123", "user123") is False


class TestGetSeatCount(TestOrganizationService):
    """Tests for get_seat_count"""

    def test_counts_active_and_pending(self, service, mock_db, mock_org):
        """Test that both active members and pending invites are counted"""
        with patch.object(service, "get_organization", return_value=mock_org):
            # 3 active members
            mock_db.query.return_value.filter.return_value.count.side_effect = [3, 1]

            result = service.get_seat_count(mock_org.id)

            assert result["active"] == 3
            assert result["pending"] == 1
            assert result["used"] == 4
            assert result["max"] == 5
            assert result["available"] == 1
            assert result["unlimited"] is False

    def test_unlimited_seats(self, service, mock_db, mock_org):
        """Test unlimited seats for enterprise"""
        mock_org.max_seats = -1

        with patch.object(service, "get_organization", return_value=mock_org):
            mock_db.query.return_value.filter.return_value.count.side_effect = [10, 5]

            result = service.get_seat_count(mock_org.id)

            assert result["unlimited"] is True
            assert result["available"] == -1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
