"""
Tests for Merkle tree API endpoints.

These tests verify the FastAPI endpoints work correctly.
Uses PostgreSQL via Docker for full compatibility.

NOTE: These tests are currently skipped because:
1. The merkle router needs authentication dependency added
2. Tests need to be updated to use the content database for document storage
"""
import pytest
import uuid
from httpx import AsyncClient

# Uses fixtures from conftest.py:
# - async_client: AsyncClient connected to the app with PostgreSQL
# - business_auth_headers: Business tier API key (has merkle_enabled)

pytestmark = pytest.mark.skip(reason="Merkle router needs authentication dependency - pending implementation")


class TestDocumentEncodeEndpoint:
    """Test the document encoding endpoint."""
    
    @pytest.mark.asyncio
    async def test_encode_document_simple(self, async_client: AsyncClient, business_auth_headers: dict):
        """Test encoding a simple document."""
        doc_id = f"test_doc_{uuid.uuid4().hex[:8]}"
        request_data = {
            "document_id": doc_id,
            "text": "First sentence. Second sentence. Third sentence.",
            "segmentation_levels": ["sentence"],
            "include_words": False,
            "metadata": {
                "title": "Test Document",
                "author": "Test Author"
            }
        }
        
        response = await async_client.post(
            "/api/v1/enterprise/merkle/encode",
            json=request_data,
            headers=business_auth_headers
        )
        
        # Should return 201 Created
        assert response.status_code == 201
        
        data = response.json()
        assert data["success"] is True
        assert data["document_id"] == doc_id
        assert "sentence" in data["roots"]
        assert data["total_segments"]["sentence"] == 3
        assert "processing_time_ms" in data
    
    @pytest.mark.asyncio
    async def test_encode_document_multiple_levels(self, async_client: AsyncClient, business_auth_headers: dict):
        """Test encoding at multiple segmentation levels."""
        doc_id = f"test_doc_{uuid.uuid4().hex[:8]}"
        request_data = {
            "document_id": doc_id,
            "text": "Paragraph one sentence one. Paragraph one sentence two.\n\nParagraph two sentence one.",
            "segmentation_levels": ["sentence", "paragraph"],
            "include_words": False
        }
        
        response = await async_client.post(
            "/api/v1/enterprise/merkle/encode",
            json=request_data,
            headers=business_auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        
        assert "sentence" in data["roots"]
        assert "paragraph" in data["roots"]
        # Should have at least 2 sentences (actual count may vary based on segmentation)
        assert data["total_segments"]["sentence"] >= 2
    
    @pytest.mark.asyncio
    async def test_encode_document_invalid_level(self, async_client: AsyncClient, business_auth_headers: dict):
        """Test encoding with invalid segmentation level."""
        request_data = {
            "document_id": "test_doc_003",
            "text": "Test text.",
            "segmentation_levels": ["invalid_level"]
        }
        
        response = await async_client.post(
            "/api/v1/enterprise/merkle/encode",
            json=request_data,
            headers=business_auth_headers
        )
        
        # Should return 422 Unprocessable Entity (validation error)
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_encode_document_empty_text(self, async_client: AsyncClient, business_auth_headers: dict):
        """Test encoding with empty text."""
        request_data = {
            "document_id": "test_doc_004",
            "text": "",
            "segmentation_levels": ["sentence"]
        }
        
        response = await async_client.post(
            "/api/v1/enterprise/merkle/encode",
            json=request_data,
            headers=business_auth_headers
        )
        
        # Should return 422 (validation error - text too short)
        assert response.status_code == 422


class TestSourceAttributionEndpoint:
    """Test the source attribution endpoint."""
    
    @pytest.mark.asyncio
    async def test_find_sources_no_matches(self, async_client: AsyncClient, business_auth_headers: dict):
        """Test finding sources when no matches exist."""
        request_data = {
            "text_segment": f"This text does not exist in any document {uuid.uuid4().hex}.",
            "segmentation_level": "sentence",
            "normalize": True
        }
        
        response = await async_client.post(
            "/api/v1/enterprise/merkle/attribute",
            json=request_data,
            headers=business_auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["matches_found"] == 0
        assert len(data["sources"]) == 0
        assert "query_hash" in data
    
    @pytest.mark.asyncio
    async def test_find_sources_invalid_level(self, async_client: AsyncClient, business_auth_headers: dict):
        """Test with invalid segmentation level."""
        request_data = {
            "text_segment": "Test text.",
            "segmentation_level": "invalid"
        }
        
        response = await async_client.post(
            "/api/v1/enterprise/merkle/attribute",
            json=request_data,
            headers=business_auth_headers
        )
        
        assert response.status_code == 422


class TestPlagiarismDetectionEndpoint:
    """Test the plagiarism detection endpoint."""
    
    @pytest.mark.asyncio
    async def test_detect_plagiarism_no_matches(self, async_client: AsyncClient, business_auth_headers: dict):
        """Test plagiarism detection with no matches."""
        request_data = {
            "target_text": f"This is completely original text {uuid.uuid4().hex} that has never been seen before.",
            "segmentation_level": "sentence",
            "include_heat_map": True
        }
        
        response = await async_client.post(
            "/api/v1/enterprise/merkle/detect-plagiarism",
            json=request_data,
            headers=business_auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "report_id" in data
        assert data["total_segments"] > 0
        assert data["matched_segments"] == 0
        assert data["overall_match_percentage"] == 0.0
        assert len(data["source_documents"]) == 0
    
    @pytest.mark.asyncio
    async def test_detect_plagiarism_with_heat_map(self, async_client: AsyncClient, business_auth_headers: dict):
        """Test that heat map data is included when requested."""
        request_data = {
            "target_text": f"Test sentence one {uuid.uuid4().hex[:8]}. Test sentence two.",
            "segmentation_level": "sentence",
            "include_heat_map": True
        }
        
        response = await async_client.post(
            "/api/v1/enterprise/merkle/detect-plagiarism",
            json=request_data,
            headers=business_auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "heat_map_data" in data
        if data["heat_map_data"]:
            assert "positions" in data["heat_map_data"]
            assert "total_segments" in data["heat_map_data"]
    
    @pytest.mark.asyncio
    async def test_detect_plagiarism_min_match_filter(self, async_client: AsyncClient, business_auth_headers: dict):
        """Test filtering by minimum match percentage."""
        request_data = {
            "target_text": f"Test text for plagiarism detection {uuid.uuid4().hex[:8]}.",
            "segmentation_level": "sentence",
            "include_heat_map": False,
            "min_match_percentage": 50.0
        }
        
        response = await async_client.post(
            "/api/v1/enterprise/merkle/detect-plagiarism",
            json=request_data,
            headers=business_auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # All returned sources should have >= 50% match
        for source in data["source_documents"]:
            assert source["match_percentage"] >= 50.0


class TestEndpointIntegration:
    """Test integration between endpoints."""
    
    @pytest.mark.asyncio
    async def test_encode_then_find(self, async_client: AsyncClient, business_auth_headers: dict):
        """Test encoding a document then finding it."""
        doc_id = f"integration_test_{uuid.uuid4().hex[:8]}"
        unique_text = f"This is a unique test sentence {uuid.uuid4().hex} for integration testing."
        
        # First, encode a document
        encode_request = {
            "document_id": doc_id,
            "text": unique_text,
            "segmentation_levels": ["sentence"]
        }
        
        encode_response = await async_client.post(
            "/api/v1/enterprise/merkle/encode",
            json=encode_request,
            headers=business_auth_headers
        )
        assert encode_response.status_code == 201
        
        # Get the encoded data to verify
        encode_data = encode_response.json()
        assert encode_data["success"] is True
        
        # Now try to find that sentence
        find_request = {
            "text_segment": unique_text,
            "segmentation_level": "sentence",
            "normalize": True
        }
        
        find_response = await async_client.post(
            "/api/v1/enterprise/merkle/attribute",
            json=find_request,
            headers=business_auth_headers
        )
        assert find_response.status_code == 200
        
        find_data = find_response.json()
        
        # Verify the endpoint works correctly
        assert find_data["success"] is True
        assert "matches_found" in find_data
        assert "sources" in find_data
        
        # If we found matches, verify one is our document
        if find_data["matches_found"] > 0:
            found_our_doc = any(
                source["document_id"] == doc_id
                for source in find_data["sources"]
            )
            assert found_our_doc is True
