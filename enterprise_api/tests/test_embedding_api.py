"""
Integration tests for embedding API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from app.main import app

client = TestClient(app)


class TestEncodeWithEmbeddingsEndpoint:
    """Test /enterprise/embeddings/encode-with-embeddings endpoint."""
    
    @patch('app.api.v1.endpoints.embeddings.MerkleService')
    @patch('app.api.v1.endpoints.embeddings.embedding_service')
    def test_encode_with_embeddings_basic(self, mock_embedding_service, mock_merkle_service):
        """Test basic encoding with embeddings."""
        # Mock Merkle service
        mock_root = AsyncMock()
        mock_root.root_id = "test-root-id"
        mock_root.root_hash = "abc123"
        mock_root.total_leaves = 3
        mock_root.tree_depth = 2
        
        mock_merkle_service.encode_document = AsyncMock(return_value={
            'sentence': mock_root
        })
        
        # Mock embedding service
        from app.services.embedding_service import EmbeddingReference
        mock_embeddings = [
            EmbeddingReference(
                ref_id=0xa3f9c2e1,
                signature="8k3mP9xQ12345678",
                leaf_hash="hash1",
                leaf_index=0,
                text_content="Sentence one.",
                document_id="doc_001"
            ),
            EmbeddingReference(
                ref_id=0xb4a8d3f2,
                signature="9m4nQ0yR12345678",
                leaf_hash="hash2",
                leaf_index=1,
                text_content="Sentence two.",
                document_id="doc_001"
            )
        ]
        
        mock_embedding_service.create_embeddings = AsyncMock(return_value=mock_embeddings)
        
        # Make request
        response = client.post(
            "/api/v1/enterprise/embeddings/encode-with-embeddings",
            json={
                "document_id": "doc_001",
                "text": "Sentence one. Sentence two.",
                "segmentation_level": "sentence"
            }
        )
        
        # Assertions
        assert response.status_code == 201
        data = response.json()
        assert data['success'] is True
        assert data['document_id'] == "doc_001"
        assert 'merkle_tree' in data
        assert 'embeddings' in data
        assert len(data['embeddings']) == 2


class TestPublicVerifyEndpoint:
    """Test /public/verify/{ref_id} endpoint."""
    
    @patch('app.api.v1.public.verify.embedding_service')
    def test_verify_valid_embedding(self, mock_embedding_service):
        """Test verification of valid embedding."""
        # Mock content reference
        from app.models.content_reference import ContentReference
        from uuid import uuid4
        
        mock_reference = ContentReference(
            ref_id=0xa3f9c2e1,
            merkle_root_id=uuid4(),
            leaf_hash="abc123",
            leaf_index=0,
            organization_id="org_001",
            document_id="doc_001",
            text_content="Test sentence.",
            text_preview="Test sentence.",
            signature_hash="8k3mP9xQ12345678",
            license_type="All Rights Reserved"
        )
        
        mock_embedding_service.verify_embedding = AsyncMock(return_value=mock_reference)
        
        # Make request
        response = client.get("/api/v1/public/verify/a3f9c2e1?signature=8k3mP9xQ")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data['valid'] is True
        assert data['ref_id'] == "a3f9c2e1"
        assert 'content' in data
        assert 'document' in data
    
    @patch('app.api.v1.public.verify.embedding_service')
    def test_verify_invalid_embedding(self, mock_embedding_service):
        """Test verification of invalid embedding."""
        mock_embedding_service.verify_embedding = AsyncMock(return_value=None)
        
        # Make request
        response = client.get("/api/v1/public/verify/invalid1?signature=00000000")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data['valid'] is False
        assert 'error' in data
    
    def test_verify_invalid_ref_id_format(self):
        """Test verification with invalid ref_id format."""
        response = client.get("/api/v1/public/verify/abc?signature=8k3mP9xQ")
        
        assert response.status_code == 400
        data = response.json()
        assert 'detail' in data


class TestBatchVerifyEndpoint:
    """Test /public/verify/batch endpoint."""
    
    @patch('app.api.v1.public.verify.embedding_service')
    def test_batch_verify_mixed_results(self, mock_embedding_service):
        """Test batch verification with mixed valid/invalid results."""
        from app.models.content_reference import ContentReference
        from uuid import uuid4
        
        # Mock: first reference valid, second invalid
        def mock_verify(db, ref_id_hex, signature_hex):
            if ref_id_hex == "a3f9c2e1":
                return ContentReference(
                    ref_id=0xa3f9c2e1,
                    merkle_root_id=uuid4(),
                    leaf_hash="abc123",
                    leaf_index=0,
                    organization_id="org_001",
                    document_id="doc_001",
                    text_preview="Test sentence.",
                    signature_hash="8k3mP9xQ12345678"
                )
            return None
        
        mock_embedding_service.verify_embedding = AsyncMock(side_effect=mock_verify)
        
        # Make request
        response = client.post(
            "/api/v1/public/verify/batch",
            json={
                "references": [
                    {"ref_id": "a3f9c2e1", "signature": "8k3mP9xQ"},
                    {"ref_id": "invalid1", "signature": "00000000"}
                ]
            }
        )
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data['total'] == 2
        assert data['valid_count'] == 1
        assert data['invalid_count'] == 1
        assert len(data['results']) == 2


class TestHTMLEmbedder:
    """Test HTML embedding utility."""
    
    def test_embed_data_attribute(self):
        """Test embedding with data-attribute method."""
        from app.utils.embeddings.html_embedder import HTMLEmbedder
        from app.services.embedding_service import EmbeddingReference
        
        html = "<p>Sentence one.</p><p>Sentence two.</p>"
        embeddings = [
            EmbeddingReference(
                ref_id=0xa3f9c2e1,
                signature="8k3mP9xQ12345678",
                leaf_hash="hash1",
                leaf_index=0,
                text_content="Sentence one.",
                document_id="doc_001"
            ),
            EmbeddingReference(
                ref_id=0xb4a8d3f2,
                signature="9m4nQ0yR12345678",
                leaf_hash="hash2",
                leaf_index=1,
                text_content="Sentence two.",
                document_id="doc_001"
            )
        ]
        
        result = HTMLEmbedder.embed_in_paragraphs(html, embeddings, method="data-attribute")
        
        assert 'data-encypher="ency:v1/a3f9c2e1/8k3mP9xQ"' in result
        assert 'data-encypher="ency:v1/b4a8d3f2/9m4nQ0yR"' in result
    
    def test_extract_references(self):
        """Test extracting references from HTML."""
        from app.utils.embeddings.html_embedder import HTMLEmbedder
        
        html = '<p data-encypher="ency:v1/a3f9c2e1/8k3mP9xQ">Test</p>'
        
        references = HTMLEmbedder.extract_references(html)
        
        assert len(references) == 1
        assert references[0] == "ency:v1/a3f9c2e1/8k3mP9xQ"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
