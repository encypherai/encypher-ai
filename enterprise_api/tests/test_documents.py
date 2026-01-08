"""Tests for documents endpoints.

Tests the /api/v1/documents endpoints for document management.
Uses async fixtures from conftest.py for proper database and auth handling.
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestListDocuments:
    """Tests for GET /api/v1/documents endpoint."""

    async def test_list_documents_requires_auth(self, client: AsyncClient):
        """Test that listing documents requires authentication."""
        response = await client.get("/api/v1/documents")
        assert response.status_code == 401

    async def test_list_documents_success(self, client: AsyncClient, auth_headers: dict):
        """Test successful document listing."""
        response = await client.get("/api/v1/documents", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "documents" in data["data"]
        assert "total" in data["data"]
        assert "page" in data["data"]

    async def test_list_documents_pagination(self, client: AsyncClient, auth_headers: dict):
        """Test document listing with pagination parameters."""
        response = await client.get(
            "/api/v1/documents?page=1&page_size=10",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["page"] == 1
        assert data["data"]["page_size"] == 10


@pytest.mark.asyncio
class TestGetDocument:
    """Tests for GET /api/v1/documents/{id} endpoint."""

    async def test_get_document_requires_auth(self, client: AsyncClient):
        """Test that getting a document requires authentication."""
        response = await client.get("/api/v1/documents/doc_nonexistent")
        assert response.status_code == 401

    async def test_get_document_not_found(self, client: AsyncClient, auth_headers: dict):
        """Test document not found error."""
        response = await client.get(
            "/api/v1/documents/doc_nonexistent_12345",
            headers=auth_headers
        )
        assert response.status_code == 404


@pytest.mark.asyncio
class TestDeleteDocument:
    """Tests for DELETE /api/v1/documents/{id} endpoint."""

    async def test_delete_document_requires_auth(self, client: AsyncClient):
        """Test that deleting a document requires authentication."""
        response = await client.delete("/api/v1/documents/doc_test")
        assert response.status_code == 401

    async def test_delete_document_not_found(self, client: AsyncClient, auth_headers: dict):
        """Test deleting non-existent document."""
        response = await client.delete(
            "/api/v1/documents/doc_nonexistent_12345",
            headers=auth_headers
        )
        assert response.status_code == 404
