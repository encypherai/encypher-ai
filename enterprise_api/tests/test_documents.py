"""
Tests for documents endpoints.

Tests the /api/v1/documents endpoints for document management.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone

from fastapi import status
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Test client for FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mock_org_context():
    """Mock organization context."""
    return {
        "organization_id": "org_test123",
        "organization_name": "Test Organization",
        "tier": "professional",
        "features": {},
        "permissions": ["sign", "verify"],
    }


class TestListDocuments:
    """Tests for GET /api/v1/documents endpoint."""

    def test_list_documents_requires_auth(self, client):
        """Test that listing documents requires authentication."""
        response = client.get("/api/v1/documents")
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]

    @patch("app.routers.documents.get_current_organization")
    @patch("app.routers.documents.get_content_db")
    def test_list_documents_success(self, mock_db, mock_auth, client, mock_org_context):
        """Test successful document listing."""
        mock_auth.return_value = mock_org_context

        # Mock count query
        mock_count_result = MagicMock()
        mock_count_result.scalar.return_value = 2

        # Mock documents query
        mock_doc1 = MagicMock()
        mock_doc1.document_id = "doc_001"
        mock_doc1.title = "Test Document 1"
        mock_doc1.document_type = "article"
        mock_doc1.created_at = datetime(2024, 12, 20, 15, 30, 0, tzinfo=timezone.utc)
        mock_doc1.word_count = 500
        mock_doc1.revoked = False

        mock_doc2 = MagicMock()
        mock_doc2.document_id = "doc_002"
        mock_doc2.title = "Test Document 2"
        mock_doc2.document_type = "press_release"
        mock_doc2.created_at = datetime(2024, 12, 21, 10, 0, 0, tzinfo=timezone.utc)
        mock_doc2.word_count = 300
        mock_doc2.revoked = True

        mock_docs_result = MagicMock()
        mock_docs_result.fetchall.return_value = [mock_doc1, mock_doc2]

        mock_session = AsyncMock()
        mock_session.execute.side_effect = [mock_count_result, mock_docs_result]
        mock_db.return_value = mock_session

        response = client.get(
            "/api/v1/documents",
            headers={"Authorization": "Bearer test_key"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["data"]["total"] == 2
        assert len(data["data"]["documents"]) == 2
        assert data["data"]["documents"][0]["document_id"] == "doc_001"
        assert data["data"]["documents"][1]["status"] == "revoked"

    @patch("app.routers.documents.get_current_organization")
    @patch("app.routers.documents.get_content_db")
    def test_list_documents_pagination(self, mock_db, mock_auth, client, mock_org_context):
        """Test document listing with pagination."""
        mock_auth.return_value = mock_org_context

        mock_count_result = MagicMock()
        mock_count_result.scalar.return_value = 150

        mock_docs_result = MagicMock()
        mock_docs_result.fetchall.return_value = []

        mock_session = AsyncMock()
        mock_session.execute.side_effect = [mock_count_result, mock_docs_result]
        mock_db.return_value = mock_session

        response = client.get(
            "/api/v1/documents?page=2&page_size=25",
            headers={"Authorization": "Bearer test_key"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["data"]["page"] == 2
        assert data["data"]["page_size"] == 25
        assert data["data"]["total_pages"] == 6

    @patch("app.routers.documents.get_current_organization")
    @patch("app.routers.documents.get_content_db")
    def test_list_documents_with_search(self, mock_db, mock_auth, client, mock_org_context):
        """Test document listing with search filter."""
        mock_auth.return_value = mock_org_context

        mock_count_result = MagicMock()
        mock_count_result.scalar.return_value = 1

        mock_doc = MagicMock()
        mock_doc.document_id = "doc_001"
        mock_doc.title = "Press Release Q4"
        mock_doc.document_type = "press_release"
        mock_doc.created_at = datetime.now(timezone.utc)
        mock_doc.word_count = 500
        mock_doc.revoked = False

        mock_docs_result = MagicMock()
        mock_docs_result.fetchall.return_value = [mock_doc]

        mock_session = AsyncMock()
        mock_session.execute.side_effect = [mock_count_result, mock_docs_result]
        mock_db.return_value = mock_session

        response = client.get(
            "/api/v1/documents?search=Press",
            headers={"Authorization": "Bearer test_key"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["data"]["total"] == 1


class TestGetDocument:
    """Tests for GET /api/v1/documents/{id} endpoint."""

    def test_get_document_requires_auth(self, client):
        """Test that getting a document requires authentication."""
        response = client.get("/api/v1/documents/doc_001")
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]

    @patch("app.routers.documents.get_current_organization")
    @patch("app.routers.documents.get_content_db")
    def test_get_document_success(self, mock_db, mock_auth, client, mock_org_context):
        """Test successful document retrieval."""
        mock_auth.return_value = mock_org_context

        mock_doc = MagicMock()
        mock_doc.document_id = "doc_001"
        mock_doc.title = "Test Document"
        mock_doc.document_type = "article"
        mock_doc.url = "https://example.com/article"
        mock_doc.created_at = datetime(2024, 12, 20, 15, 30, 0, tzinfo=timezone.utc)
        mock_doc.word_count = 500
        mock_doc.signer_id = "signer_abc"
        mock_doc.revoked = False
        mock_doc.revoked_at = None
        mock_doc.revoked_reason = None

        mock_result = MagicMock()
        mock_result.fetchone.return_value = mock_doc

        mock_session = AsyncMock()
        mock_session.execute.return_value = mock_result
        mock_db.return_value = mock_session

        response = client.get(
            "/api/v1/documents/doc_001",
            headers={"Authorization": "Bearer test_key"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["data"]["document_id"] == "doc_001"
        assert data["data"]["status"] == "active"

    @patch("app.routers.documents.get_current_organization")
    @patch("app.routers.documents.get_content_db")
    def test_get_document_not_found(self, mock_db, mock_auth, client, mock_org_context):
        """Test document not found error."""
        mock_auth.return_value = mock_org_context

        mock_result = MagicMock()
        mock_result.fetchone.return_value = None

        mock_session = AsyncMock()
        mock_session.execute.return_value = mock_result
        mock_db.return_value = mock_session

        response = client.get(
            "/api/v1/documents/nonexistent",
            headers={"Authorization": "Bearer test_key"}
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestGetDocumentHistory:
    """Tests for GET /api/v1/documents/{id}/history endpoint."""

    @patch("app.routers.documents.get_current_organization")
    @patch("app.routers.documents.get_content_db")
    @patch("app.routers.documents.get_db")
    def test_get_document_history_success(self, mock_db, mock_content_db, mock_auth, client, mock_org_context):
        """Test successful document history retrieval."""
        mock_auth.return_value = mock_org_context

        # Mock document query
        mock_doc = MagicMock()
        mock_doc.document_id = "doc_001"
        mock_doc.created_at = datetime(2024, 12, 20, 15, 30, 0, tzinfo=timezone.utc)

        mock_doc_result = MagicMock()
        mock_doc_result.fetchone.return_value = mock_doc

        mock_content_session = AsyncMock()
        mock_content_session.execute.return_value = mock_doc_result
        mock_content_db.return_value = mock_content_session

        # Mock revocation query
        mock_revoke_result = MagicMock()
        mock_revoke_result.fetchall.return_value = []

        mock_session = AsyncMock()
        mock_session.execute.return_value = mock_revoke_result
        mock_db.return_value = mock_session

        response = client.get(
            "/api/v1/documents/doc_001/history",
            headers={"Authorization": "Bearer test_key"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert "history" in data["data"]
        assert len(data["data"]["history"]) >= 1  # At least the signing event


class TestDeleteDocument:
    """Tests for DELETE /api/v1/documents/{id} endpoint."""

    @patch("app.routers.documents.get_current_organization")
    @patch("app.routers.documents.get_content_db")
    @patch("app.routers.documents.get_db")
    @patch("app.routers.documents.status_service")
    def test_delete_document_success(self, mock_status_svc, mock_db, mock_content_db, mock_auth, client, mock_org_context):
        """Test successful document deletion."""
        mock_auth.return_value = mock_org_context

        # Mock document exists check
        mock_doc = MagicMock()
        mock_doc.document_id = "doc_001"

        mock_doc_result = MagicMock()
        mock_doc_result.fetchone.return_value = mock_doc

        mock_content_session = AsyncMock()
        mock_content_session.execute.return_value = mock_doc_result
        mock_content_db.return_value = mock_content_session

        # Mock revocation
        mock_status_svc.revoke_document = AsyncMock()

        mock_session = AsyncMock()
        mock_db.return_value = mock_session

        response = client.delete(
            "/api/v1/documents/doc_001",
            headers={"Authorization": "Bearer test_key"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["data"]["deleted"] is True

    @patch("app.routers.documents.get_current_organization")
    @patch("app.routers.documents.get_content_db")
    def test_delete_document_not_found(self, mock_content_db, mock_auth, client, mock_org_context):
        """Test deleting non-existent document."""
        mock_auth.return_value = mock_org_context

        mock_result = MagicMock()
        mock_result.fetchone.return_value = None

        mock_session = AsyncMock()
        mock_session.execute.return_value = mock_result
        mock_content_db.return_value = mock_session

        response = client.delete(
            "/api/v1/documents/nonexistent",
            headers={"Authorization": "Bearer test_key"}
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
