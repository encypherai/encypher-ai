"""Tests for bulk invite endpoint (TEAM_257).

Tests the POST /api/v1/org/members/invite/bulk endpoint.
"""

import uuid

import pytest
from httpx import AsyncClient


class TestBulkInviteEndpoint:
    """Test suite for the bulk invite endpoint."""

    @pytest.mark.asyncio
    async def test_bulk_invite_success(
        self,
        async_client: AsyncClient,
        enterprise_admin_headers: dict,
    ):
        """Test bulk invite with valid emails."""
        emails = [
            {"email": f"bulk-{uuid.uuid4().hex[:8]}@example.com", "role": "member"},
            {"email": f"bulk-{uuid.uuid4().hex[:8]}@example.com", "role": "viewer"},
        ]
        response = await async_client.post(
            "/api/v1/org/members/invite/bulk",
            headers=enterprise_admin_headers,
            json={"invitations": emails},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert data["succeeded"] == 2
        assert data["failed"] == 0
        assert len(data["results"]) == 2
        for result in data["results"]:
            assert result["success"] is True
            assert result["invite_id"] is not None

    @pytest.mark.asyncio
    async def test_bulk_invite_empty_list(
        self,
        async_client: AsyncClient,
        enterprise_admin_headers: dict,
    ):
        """Test bulk invite with empty invitations list."""
        response = await async_client.post(
            "/api/v1/org/members/invite/bulk",
            headers=enterprise_admin_headers,
            json={"invitations": []},
        )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_bulk_invite_rejects_owner_role(
        self,
        async_client: AsyncClient,
        enterprise_admin_headers: dict,
    ):
        """Test that owner role invitations are rejected individually."""
        emails = [
            {"email": f"bulk-{uuid.uuid4().hex[:8]}@example.com", "role": "owner"},
            {"email": f"bulk-{uuid.uuid4().hex[:8]}@example.com", "role": "member"},
        ]
        response = await async_client.post(
            "/api/v1/org/members/invite/bulk",
            headers=enterprise_admin_headers,
            json={"invitations": emails},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert data["succeeded"] == 1
        assert data["failed"] == 1
        # First should fail (owner), second should succeed
        assert data["results"][0]["success"] is False
        assert "owner" in data["results"][0]["error"].lower()
        assert data["results"][1]["success"] is True

    @pytest.mark.asyncio
    async def test_bulk_invite_duplicate_emails(
        self,
        async_client: AsyncClient,
        enterprise_admin_headers: dict,
    ):
        """Test that duplicate emails in the same batch are handled."""
        email = f"bulk-dup-{uuid.uuid4().hex[:8]}@example.com"
        emails = [
            {"email": email, "role": "member"},
            {"email": email, "role": "viewer"},
        ]
        response = await async_client.post(
            "/api/v1/org/members/invite/bulk",
            headers=enterprise_admin_headers,
            json={"invitations": emails},
        )
        assert response.status_code == 200
        data = response.json()
        # First succeeds, second should fail because it becomes pending
        assert data["succeeded"] >= 1

    @pytest.mark.asyncio
    async def test_bulk_invite_unauthorized(
        self,
        async_client: AsyncClient,
    ):
        """Test bulk invite requires authentication."""
        response = await async_client.post(
            "/api/v1/org/members/invite/bulk",
            json={"invitations": [{"email": "a@b.com", "role": "member"}]},
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_bulk_invite_tier_gated(
        self,
        async_client: AsyncClient,
        starter_auth_headers: dict,
    ):
        """Test bulk invite is tier-gated (requires Enterprise)."""
        response = await async_client.post(
            "/api/v1/org/members/invite/bulk",
            headers=starter_auth_headers,
            json={"invitations": [{"email": "a@b.com", "role": "member"}]},
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_bulk_invite_exceeds_limit(
        self,
        async_client: AsyncClient,
        enterprise_admin_headers: dict,
    ):
        """Test that more than 50 invitations are rejected."""
        emails = [{"email": f"bulk-{i}@example.com", "role": "member"} for i in range(51)]
        response = await async_client.post(
            "/api/v1/org/members/invite/bulk",
            headers=enterprise_admin_headers,
            json={"invitations": emails},
        )
        assert response.status_code == 400
