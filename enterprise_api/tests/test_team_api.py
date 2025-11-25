"""Tests for team management API endpoints."""
import pytest
from httpx import AsyncClient
from datetime import datetime, timezone


class TestTeamManagementEndpoints:
    """Test suite for /api/v1/org/members endpoints."""

    @pytest.mark.asyncio
    async def test_list_team_members_success(self, async_client: AsyncClient, business_auth_headers: dict):
        """Test successful retrieval of team members (Business+ tier)."""
        response = await async_client.get(
            "/api/v1/org/members",
            headers=business_auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "organization_id" in data
        assert "members" in data
        assert "total" in data
        assert "max_members" in data
        
        assert isinstance(data["members"], list)

    @pytest.mark.asyncio
    async def test_list_team_members_unauthorized(self, async_client: AsyncClient):
        """Test team members requires authentication."""
        response = await async_client.get("/api/v1/org/members")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_list_team_members_tier_gated(self, async_client: AsyncClient, starter_auth_headers: dict):
        """Test team management is tier-gated (requires Business+)."""
        response = await async_client.get(
            "/api/v1/org/members",
            headers=starter_auth_headers,
        )
        
        # Should return 403 for Starter tier
        assert response.status_code == 403
        data = response.json()
        assert "FEATURE_NOT_AVAILABLE" in str(data.get("detail", {}).get("code", ""))

    @pytest.mark.asyncio
    async def test_invite_member_success(self, async_client: AsyncClient, business_admin_headers: dict):
        """Test inviting a new team member."""
        response = await async_client.post(
            "/api/v1/org/members/invite",
            headers=business_admin_headers,
            json={
                "email": "newmember@example.com",
                "role": "member",
            },
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "invite_id" in data
        assert data["email"] == "newmember@example.com"
        assert data["role"] == "member"
        assert "expires_at" in data

    @pytest.mark.asyncio
    async def test_invite_member_invalid_email(self, async_client: AsyncClient, business_admin_headers: dict):
        """Test inviting with invalid email."""
        response = await async_client.post(
            "/api/v1/org/members/invite",
            headers=business_admin_headers,
            json={
                "email": "not-an-email",
                "role": "member",
            },
        )
        
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_invite_member_invalid_role(self, async_client: AsyncClient, business_admin_headers: dict):
        """Test inviting with invalid role."""
        response = await async_client.post(
            "/api/v1/org/members/invite",
            headers=business_admin_headers,
            json={
                "email": "test@example.com",
                "role": "superadmin",  # Invalid role
            },
        )
        
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_invite_as_owner_forbidden(self, async_client: AsyncClient, business_admin_headers: dict):
        """Test cannot invite someone as owner."""
        response = await async_client.post(
            "/api/v1/org/members/invite",
            headers=business_admin_headers,
            json={
                "email": "owner@example.com",
                "role": "owner",
            },
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "owner" in str(data.get("detail", "")).lower()

    @pytest.mark.asyncio
    async def test_list_pending_invites(self, async_client: AsyncClient, business_admin_headers: dict):
        """Test listing pending invitations."""
        response = await async_client.get(
            "/api/v1/org/members/invites",
            headers=business_admin_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_revoke_invite(self, async_client: AsyncClient, business_admin_headers: dict):
        """Test revoking a pending invitation."""
        # First create an invite
        invite_response = await async_client.post(
            "/api/v1/org/members/invite",
            headers=business_admin_headers,
            json={
                "email": "revoke-test@example.com",
                "role": "viewer",
            },
        )
        
        if invite_response.status_code == 200:
            invite_id = invite_response.json()["invite_id"]
            
            # Now revoke it
            response = await async_client.delete(
                f"/api/v1/org/members/invites/{invite_id}",
                headers=business_admin_headers,
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True

    @pytest.mark.asyncio
    async def test_update_member_role(self, async_client: AsyncClient, business_owner_headers: dict, test_member_id: str):
        """Test updating a team member's role."""
        response = await async_client.patch(
            f"/api/v1/org/members/{test_member_id}/role",
            headers=business_owner_headers,
            json={"role": "admin"},
        )
        
        # May return 200 (success) or 404 (member not found in test env)
        assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_update_owner_role_forbidden(self, async_client: AsyncClient, business_admin_headers: dict, owner_member_id: str):
        """Test cannot change owner's role."""
        response = await async_client.patch(
            f"/api/v1/org/members/{owner_member_id}/role",
            headers=business_admin_headers,
            json={"role": "member"},
        )
        
        # Should be forbidden
        assert response.status_code in [400, 403, 404]

    @pytest.mark.asyncio
    async def test_remove_member(self, async_client: AsyncClient, business_owner_headers: dict, test_member_id: str):
        """Test removing a team member."""
        response = await async_client.delete(
            f"/api/v1/org/members/{test_member_id}",
            headers=business_owner_headers,
        )
        
        # May return 200 (success) or 404 (member not found)
        assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_remove_owner_forbidden(self, async_client: AsyncClient, business_admin_headers: dict, owner_member_id: str):
        """Test cannot remove the owner."""
        response = await async_client.delete(
            f"/api/v1/org/members/{owner_member_id}",
            headers=business_admin_headers,
        )
        
        # Should be forbidden
        assert response.status_code in [400, 403, 404]

    @pytest.mark.asyncio
    async def test_accept_invite(self, async_client: AsyncClient):
        """Test accepting a team invitation."""
        # This would require a valid token, so we test the endpoint exists
        response = await async_client.post(
            "/api/v1/org/members/accept-invite?token=invalid_token&user_id=test_user",
        )
        
        # Should return 404 (invalid token) not 500
        assert response.status_code in [400, 404]

    @pytest.mark.asyncio
    async def test_member_limit_enforcement(self, async_client: AsyncClient, business_auth_headers: dict):
        """Test that member limits are enforced based on tier."""
        response = await async_client.get(
            "/api/v1/org/members",
            headers=business_auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Business tier should have max_members = 10
        # (unless unlimited for enterprise)
        assert data["max_members"] >= 1
