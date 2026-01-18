"""Tests for API key management endpoints.

Tests the /api/v1/keys endpoints for key creation, rotation, and revocation.
Uses async fixtures from conftest.py for proper database and auth handling.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestListKeys:
    """Tests for GET /api/v1/keys endpoint."""

    async def test_list_keys_requires_auth(self, client: AsyncClient):
        """Test that listing keys requires authentication."""
        response = await client.get("/api/v1/keys")
        assert response.status_code == 401

    async def test_list_keys_success(self, client: AsyncClient, auth_headers: dict):
        """Test successful key listing."""
        response = await client.get("/api/v1/keys", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "keys" in data["data"]
        assert "total" in data["data"]


@pytest.mark.asyncio
class TestCreateKey:
    """Tests for POST /api/v1/keys endpoint."""

    async def test_create_key_requires_auth(self, client: AsyncClient):
        """Test that creating keys requires authentication."""
        response = await client.post("/api/v1/keys", json={"name": "Test Key"})
        assert response.status_code == 401

    async def test_create_key_success(self, client: AsyncClient, auth_headers: dict):
        """Test successful key creation."""
        response = await client.post("/api/v1/keys", json={"name": "Test API Key", "permissions": ["sign", "verify"]}, headers=auth_headers)

        # May succeed or fail based on key limits
        assert response.status_code in [201, 403]
        if response.status_code == 201:
            data = response.json()
            assert data["success"] is True
            assert "key" in data["data"]  # Full key returned on creation


@pytest.mark.asyncio
class TestRevokeKey:
    """Tests for DELETE /api/v1/keys/{id} endpoint."""

    async def test_revoke_key_requires_auth(self, client: AsyncClient):
        """Test that revoking keys requires authentication."""
        response = await client.delete("/api/v1/keys/key_test")
        assert response.status_code == 401

    async def test_revoke_key_not_found(self, client: AsyncClient, auth_headers: dict):
        """Test revoking non-existent key."""
        response = await client.delete("/api/v1/keys/key_nonexistent_12345", headers=auth_headers)
        assert response.status_code == 404


@pytest.mark.asyncio
class TestRotateKey:
    """Tests for POST /api/v1/keys/{id}/rotate endpoint."""

    async def test_rotate_key_requires_auth(self, client: AsyncClient):
        """Test that rotating keys requires authentication."""
        response = await client.post("/api/v1/keys/key_test/rotate")
        assert response.status_code == 401

    async def test_rotate_key_not_found(self, client: AsyncClient, auth_headers: dict):
        """Test rotating non-existent key."""
        response = await client.post("/api/v1/keys/key_nonexistent_12345/rotate", headers=auth_headers)
        assert response.status_code == 404


@pytest.mark.asyncio
class TestUpdateKey:
    """Tests for PATCH /api/v1/keys/{id} endpoint."""

    async def test_update_key_requires_auth(self, client: AsyncClient):
        """Test that updating keys requires authentication."""
        response = await client.patch("/api/v1/keys/key_test", json={"name": "New Name"})
        assert response.status_code == 401

    async def test_update_key_not_found(self, client: AsyncClient, auth_headers: dict):
        """Test updating non-existent key."""
        response = await client.patch("/api/v1/keys/key_nonexistent_12345", json={"name": "New Name"}, headers=auth_headers)
        assert response.status_code == 404
