"""
Integration tests for Organization API endpoints.
Requires a running auth-service at localhost:8001.
"""

import pytest
import httpx
from datetime import datetime
import secrets


BASE_URL = "http://localhost:8001"


pytestmark = pytest.mark.e2e


class TestOrganizationAPI:
    """Integration tests for organization endpoints"""

    @pytest.fixture
    async def auth_headers(self):
        """Create a test user and return auth headers"""
        async with httpx.AsyncClient() as client:
            # Create unique test user
            email = f"test_org_{datetime.now().timestamp()}_{secrets.token_hex(4)}@example.com"

            # Register
            response = await client.post(
                f"{BASE_URL}/api/v1/auth/signup", json={"email": email, "password": "SecurePass123!", "name": "Test Org User"}
            )

            if response.status_code != 201:
                pytest.skip(f"Could not create test user: {response.text}")

            # Login (may fail if email verification required)
            login_response = await client.post(f"{BASE_URL}/api/v1/auth/login", json={"email": email, "password": "SecurePass123!"})

            if login_response.status_code != 200:
                pytest.skip(f"Could not login test user: {login_response.text}")

            tokens = login_response.json()
            return {"Authorization": f"Bearer {tokens['data']['access_token']}", "email": email}

    @pytest.mark.asyncio
    async def test_create_organization(self, auth_headers):
        """Test creating a new organization"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/api/v1/organizations",
                headers={"Authorization": auth_headers["Authorization"]},
                json={"name": f"Test Org {datetime.now().timestamp()}", "email": f"org_{secrets.token_hex(4)}@example.com"},
            )

            assert response.status_code == 201
            data = response.json()
            assert data["success"] is True
            assert "id" in data["data"]
            assert data["data"]["tier"] == "starter"

    @pytest.mark.asyncio
    async def test_list_organizations(self, auth_headers):
        """Test listing user's organizations"""
        async with httpx.AsyncClient() as client:
            # First create an org
            await client.post(
                f"{BASE_URL}/api/v1/organizations",
                headers={"Authorization": auth_headers["Authorization"]},
                json={"name": "List Test Org", "email": f"listorg_{secrets.token_hex(4)}@example.com"},
            )

            # List orgs
            response = await client.get(f"{BASE_URL}/api/v1/organizations", headers={"Authorization": auth_headers["Authorization"]})

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert isinstance(data["data"], list)
            assert len(data["data"]) >= 1

    @pytest.mark.asyncio
    async def test_get_organization(self, auth_headers):
        """Test getting organization details"""
        async with httpx.AsyncClient() as client:
            # Create org
            create_response = await client.post(
                f"{BASE_URL}/api/v1/organizations",
                headers={"Authorization": auth_headers["Authorization"]},
                json={"name": "Get Test Org", "email": f"getorg_{secrets.token_hex(4)}@example.com"},
            )
            org_id = create_response.json()["data"]["id"]

            # Get org
            response = await client.get(f"{BASE_URL}/api/v1/organizations/{org_id}", headers={"Authorization": auth_headers["Authorization"]})

            assert response.status_code == 200
            data = response.json()
            assert data["data"]["id"] == org_id
            assert data["data"]["name"] == "Get Test Org"

    @pytest.mark.asyncio
    async def test_update_organization(self, auth_headers):
        """Test updating organization settings"""
        async with httpx.AsyncClient() as client:
            # Create org
            create_response = await client.post(
                f"{BASE_URL}/api/v1/organizations",
                headers={"Authorization": auth_headers["Authorization"]},
                json={"name": "Update Test Org", "email": f"updateorg_{secrets.token_hex(4)}@example.com"},
            )
            org_id = create_response.json()["data"]["id"]

            # Update org
            response = await client.patch(
                f"{BASE_URL}/api/v1/organizations/{org_id}",
                headers={"Authorization": auth_headers["Authorization"]},
                json={"name": "Updated Org Name"},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["data"]["name"] == "Updated Org Name"

    @pytest.mark.asyncio
    async def test_get_members(self, auth_headers):
        """Test listing organization members"""
        async with httpx.AsyncClient() as client:
            # Create org
            create_response = await client.post(
                f"{BASE_URL}/api/v1/organizations",
                headers={"Authorization": auth_headers["Authorization"]},
                json={"name": "Members Test Org", "email": f"membersorg_{secrets.token_hex(4)}@example.com"},
            )
            org_id = create_response.json()["data"]["id"]

            # Get members
            response = await client.get(f"{BASE_URL}/api/v1/organizations/{org_id}/members", headers={"Authorization": auth_headers["Authorization"]})

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert isinstance(data["data"], list)
            # Should have at least the owner
            assert len(data["data"]) >= 1
            # First member should be owner
            assert data["data"][0]["role"] == "owner"

    @pytest.mark.asyncio
    async def test_get_seats(self, auth_headers):
        """Test getting seat information"""
        async with httpx.AsyncClient() as client:
            # Create org
            create_response = await client.post(
                f"{BASE_URL}/api/v1/organizations",
                headers={"Authorization": auth_headers["Authorization"]},
                json={"name": "Seats Test Org", "email": f"seatsorg_{secrets.token_hex(4)}@example.com"},
            )
            org_id = create_response.json()["data"]["id"]

            # Get seats
            response = await client.get(f"{BASE_URL}/api/v1/organizations/{org_id}/seats", headers={"Authorization": auth_headers["Authorization"]})

            assert response.status_code == 200
            data = response.json()
            assert "used" in data["data"]
            assert "max" in data["data"]
            assert "available" in data["data"]
            assert data["data"]["used"] == 1  # Just the owner

    @pytest.mark.asyncio
    async def test_create_invitation(self, auth_headers):
        """Test creating an invitation"""
        async with httpx.AsyncClient() as client:
            # Create org
            create_response = await client.post(
                f"{BASE_URL}/api/v1/organizations",
                headers={"Authorization": auth_headers["Authorization"]},
                json={"name": "Invite Test Org", "email": f"inviteorg_{secrets.token_hex(4)}@example.com"},
            )
            org_id = create_response.json()["data"]["id"]

            # Create invitation
            invite_email = f"invited_{secrets.token_hex(4)}@example.com"
            response = await client.post(
                f"{BASE_URL}/api/v1/organizations/{org_id}/invitations",
                headers={"Authorization": auth_headers["Authorization"]},
                json={"email": invite_email, "role": "member", "message": "Welcome to the team!"},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["email"] == invite_email
            assert data["data"]["role"] == "member"
            assert data["data"]["status"] == "pending"

    @pytest.mark.asyncio
    async def test_list_invitations(self, auth_headers):
        """Test listing pending invitations"""
        async with httpx.AsyncClient() as client:
            # Create org
            create_response = await client.post(
                f"{BASE_URL}/api/v1/organizations",
                headers={"Authorization": auth_headers["Authorization"]},
                json={"name": "List Invites Org", "email": f"listinvorg_{secrets.token_hex(4)}@example.com"},
            )
            org_id = create_response.json()["data"]["id"]

            # Create invitation
            await client.post(
                f"{BASE_URL}/api/v1/organizations/{org_id}/invitations",
                headers={"Authorization": auth_headers["Authorization"]},
                json={"email": f"listinv_{secrets.token_hex(4)}@example.com", "role": "member"},
            )

            # List invitations
            response = await client.get(
                f"{BASE_URL}/api/v1/organizations/{org_id}/invitations", headers={"Authorization": auth_headers["Authorization"]}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert isinstance(data["data"], list)
            assert len(data["data"]) >= 1

    @pytest.mark.asyncio
    async def test_cancel_invitation(self, auth_headers):
        """Test cancelling an invitation"""
        async with httpx.AsyncClient() as client:
            # Create org
            create_response = await client.post(
                f"{BASE_URL}/api/v1/organizations",
                headers={"Authorization": auth_headers["Authorization"]},
                json={"name": "Cancel Invite Org", "email": f"cancelorg_{secrets.token_hex(4)}@example.com"},
            )
            org_id = create_response.json()["data"]["id"]

            # Create invitation
            invite_response = await client.post(
                f"{BASE_URL}/api/v1/organizations/{org_id}/invitations",
                headers={"Authorization": auth_headers["Authorization"]},
                json={"email": f"cancel_{secrets.token_hex(4)}@example.com", "role": "member"},
            )
            invitation_id = invite_response.json()["data"]["id"]

            # Cancel invitation
            response = await client.delete(
                f"{BASE_URL}/api/v1/organizations/{org_id}/invitations/{invitation_id}", headers={"Authorization": auth_headers["Authorization"]}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["data"]["cancelled"] is True

    @pytest.mark.asyncio
    async def test_get_audit_logs(self, auth_headers):
        """Test getting audit logs"""
        async with httpx.AsyncClient() as client:
            # Create org (this creates an audit log entry)
            create_response = await client.post(
                f"{BASE_URL}/api/v1/organizations",
                headers={"Authorization": auth_headers["Authorization"]},
                json={"name": "Audit Log Org", "email": f"auditorg_{secrets.token_hex(4)}@example.com"},
            )
            org_id = create_response.json()["data"]["id"]

            # Get audit logs
            response = await client.get(
                f"{BASE_URL}/api/v1/organizations/{org_id}/audit-logs", headers={"Authorization": auth_headers["Authorization"]}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert isinstance(data["data"], list)
            # Should have at least the creation log
            assert len(data["data"]) >= 1
            assert data["data"][0]["action"] == "organization.created"

    @pytest.mark.asyncio
    async def test_unauthorized_access(self):
        """Test that unauthorized requests are rejected"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/api/v1/organizations", headers={"Authorization": "Bearer invalid_token"})

            assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_cannot_invite_as_owner_role(self, auth_headers):
        """Test that invitations cannot be for owner role"""
        async with httpx.AsyncClient() as client:
            # Create org
            create_response = await client.post(
                f"{BASE_URL}/api/v1/organizations",
                headers={"Authorization": auth_headers["Authorization"]},
                json={"name": "Owner Role Test Org", "email": f"ownerrole_{secrets.token_hex(4)}@example.com"},
            )
            org_id = create_response.json()["data"]["id"]

            # Try to invite as owner
            response = await client.post(
                f"{BASE_URL}/api/v1/organizations/{org_id}/invitations",
                headers={"Authorization": auth_headers["Authorization"]},
                json={"email": f"owner_{secrets.token_hex(4)}@example.com", "role": "owner"},
            )

            assert response.status_code == 400
            assert "Invalid role" in response.json()["detail"]


class TestInvitationPublicEndpoints:
    """Tests for public invitation endpoints"""

    @pytest.mark.asyncio
    async def test_get_invitation_details_invalid_token(self):
        """Test getting invitation details with invalid token"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/api/v1/organizations/invitations/invalid_token_123")

            assert response.status_code == 404


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
