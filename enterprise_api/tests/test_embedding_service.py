"""
Unit tests for EmbeddingService.

Tests the enterprise embedding service built on encypher-ai package.
The service provides:
- create_embeddings() - Creates embeddings with C2PA manifests
- verify_and_extract_embedding() - Verifies and extracts embedding data
- get_reference_by_id() - Retrieves content reference by ID
- get_references_by_document() - Gets all references for a document
"""
import pytest
import pytest_asyncio
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock, patch

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from app.services.embedding_service import EmbeddingService, EmbeddingReference


@pytest.fixture
def test_private_key():
    """Generate a test Ed25519 private key."""
    return Ed25519PrivateKey.generate()


@pytest.fixture
def embedding_service(test_private_key):
    """Create an EmbeddingService instance for testing."""
    return EmbeddingService(private_key=test_private_key, signer_id="test_signer_001")


class TestEmbeddingServiceInit:
    """Test EmbeddingService initialization."""
    
    def test_init_with_valid_key(self, test_private_key):
        """Test initialization with valid Ed25519 key."""
        service = EmbeddingService(
            private_key=test_private_key,
            signer_id="test_signer"
        )
        assert service.private_key == test_private_key
        assert service.signer_id == "test_signer"
    
    def test_init_stores_signer_id(self, test_private_key):
        """Test that signer_id is stored correctly."""
        signer_id = "org_demo_signer_001"
        service = EmbeddingService(
            private_key=test_private_key,
            signer_id=signer_id
        )
        assert service.signer_id == signer_id


class TestEmbeddingReference:
    """Test EmbeddingReference dataclass."""
    
    def test_create_embedding_reference(self):
        """Test creating an EmbeddingReference."""
        ref = EmbeddingReference(
            leaf_hash="abc123def456",
            leaf_index=0,
            text_content="Test sentence content.",
            embedded_text="Test sentence content.\ufeffXXX",
            document_id="doc_001"
        )
        
        assert ref.leaf_hash == "abc123def456"
        assert ref.leaf_index == 0
        assert ref.text_content == "Test sentence content."
        assert ref.document_id == "doc_001"
        assert ref.ref_id is None  # Optional, set after DB insert
    
    def test_embedding_reference_to_dict(self):
        """Test EmbeddingReference.to_dict() serialization."""
        ref = EmbeddingReference(
            leaf_hash="abc123def456",
            leaf_index=2,
            text_content="Test sentence.",
            embedded_text="Test sentence.\ufeffXXX",
            document_id="doc_test_001",
            ref_id=12345
        )
        
        data = ref.to_dict()
        
        assert data['leaf_index'] == 2
        assert data['leaf_hash'] == "abc123def456"
        assert data['text_content'] == "Test sentence."
        assert data['embedded_text'] == "Test sentence.\ufeffXXX"
        assert data['document_id'] == "doc_test_001"
        assert data['has_invisible_embedding'] is True
    
    def test_embedding_reference_optional_ref_id(self):
        """Test that ref_id is optional."""
        ref = EmbeddingReference(
            leaf_hash="hash",
            leaf_index=0,
            text_content="text",
            embedded_text="text",
            document_id="doc"
        )
        assert ref.ref_id is None
        
        ref_with_id = EmbeddingReference(
            leaf_hash="hash",
            leaf_index=0,
            text_content="text",
            embedded_text="text",
            document_id="doc",
            ref_id=999
        )
        assert ref_with_id.ref_id == 999


class TestCreateEmbeddings:
    """Test EmbeddingService.create_embeddings() method."""
    
    @pytest_asyncio.fixture
    async def mock_db(self):
        """Create a mock database session."""
        mock = AsyncMock()
        mock.execute = AsyncMock(return_value=MagicMock(rowcount=0))
        mock.commit = AsyncMock()
        mock.flush = AsyncMock()
        mock.add_all = MagicMock()
        return mock
    
    @pytest.mark.asyncio
    async def test_create_embeddings_validates_length_mismatch(self, embedding_service, mock_db):
        """Test that mismatched segments/hashes raises ValueError."""
        with pytest.raises(ValueError, match="must have same length"):
            await embedding_service.create_embeddings(
                db=mock_db,
                organization_id="org_001",
                document_id="doc_001",
                merkle_root_id=uuid4(),
                segments=["Sentence one.", "Sentence two."],
                leaf_hashes=["hash1"]  # Mismatched length
            )
    
    @pytest.mark.asyncio
    async def test_create_embeddings_returns_correct_count(self, embedding_service, mock_db):
        """Test that create_embeddings returns correct number of references."""
        segments = ["First sentence.", "Second sentence.", "Third sentence."]
        leaf_hashes = ["hash1", "hash2", "hash3"]
        
        embeddings, full_doc = await embedding_service.create_embeddings(
            db=mock_db,
            organization_id="org_demo",
            document_id="doc_test",
            merkle_root_id=uuid4(),
            segments=segments,
            leaf_hashes=leaf_hashes
        )
        
        assert len(embeddings) == 3
    
    @pytest.mark.asyncio
    async def test_create_embeddings_returns_embedding_references(self, embedding_service, mock_db):
        """Test that create_embeddings returns EmbeddingReference objects."""
        segments = ["Test sentence."]
        leaf_hashes = ["testhash123"]
        
        embeddings, full_doc = await embedding_service.create_embeddings(
            db=mock_db,
            organization_id="org_demo",
            document_id="doc_test",
            merkle_root_id=uuid4(),
            segments=segments,
            leaf_hashes=leaf_hashes
        )
        
        assert len(embeddings) == 1
        assert isinstance(embeddings[0], EmbeddingReference)
        assert embeddings[0].leaf_index == 0
        assert embeddings[0].leaf_hash == "testhash123"
        assert embeddings[0].text_content == "Test sentence."
        assert embeddings[0].document_id == "doc_test"
    
    @pytest.mark.asyncio
    async def test_create_embeddings_preserves_leaf_indices(self, embedding_service, mock_db):
        """Test that leaf indices are preserved correctly."""
        segments = ["A", "B", "C", "D", "E"]
        leaf_hashes = ["h1", "h2", "h3", "h4", "h5"]
        
        embeddings, _ = await embedding_service.create_embeddings(
            db=mock_db,
            organization_id="org_demo",
            document_id="doc_test",
            merkle_root_id=uuid4(),
            segments=segments,
            leaf_hashes=leaf_hashes
        )
        
        for i, emb in enumerate(embeddings):
            assert emb.leaf_index == i
            assert emb.leaf_hash == f"h{i+1}"
    
    @pytest.mark.asyncio
    async def test_create_embeddings_returns_full_document(self, embedding_service, mock_db):
        """Test that create_embeddings returns the full embedded document."""
        segments = ["First.", "Second."]
        leaf_hashes = ["h1", "h2"]
        
        embeddings, full_doc = await embedding_service.create_embeddings(
            db=mock_db,
            organization_id="org_demo",
            document_id="doc_test",
            merkle_root_id=uuid4(),
            segments=segments,
            leaf_hashes=leaf_hashes
        )
        
        # Full document should contain both segments
        assert "First" in full_doc
        assert "Second" in full_doc
        # Should have invisible embedding (ZWNBSP prefix)
        assert "\ufeff" in full_doc
    
    @pytest.mark.asyncio
    async def test_create_embeddings_with_license_info(self, embedding_service, mock_db):
        """Test embedding creation with license information."""
        segments = ["Licensed content."]
        leaf_hashes = ["hash1"]
        license_info = {
            'type': 'CC-BY-4.0',
            'url': 'https://creativecommons.org/licenses/by/4.0/'
        }
        
        embeddings, _ = await embedding_service.create_embeddings(
            db=mock_db,
            organization_id="org_demo",
            document_id="doc_test",
            merkle_root_id=uuid4(),
            segments=segments,
            leaf_hashes=leaf_hashes,
            license_info=license_info
        )
        
        assert len(embeddings) == 1
    
    @pytest.mark.asyncio
    async def test_create_embeddings_calls_db_operations(self, embedding_service, mock_db):
        """Test that database operations are called."""
        segments = ["Test."]
        leaf_hashes = ["h1"]
        
        await embedding_service.create_embeddings(
            db=mock_db,
            organization_id="org_demo",
            document_id="doc_test",
            merkle_root_id=uuid4(),
            segments=segments,
            leaf_hashes=leaf_hashes
        )
        
        # Should delete old references
        assert mock_db.execute.called
        # Should add new references
        assert mock_db.add_all.called
        # Should flush (not commit - deferred for performance)
        assert mock_db.flush.called


class TestGetReferenceById:
    """Test EmbeddingService.get_reference_by_id() method."""
    
    @pytest_asyncio.fixture
    async def mock_db(self):
        """Create a mock database session."""
        return AsyncMock()
    
    @pytest.mark.asyncio
    async def test_get_reference_by_id_returns_none_when_not_found(self, embedding_service, mock_db):
        """Test that get_reference_by_id returns None when not found."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result
        
        result = await embedding_service.get_reference_by_id(mock_db, 12345)
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_reference_by_id_returns_reference(self, embedding_service, mock_db):
        """Test that get_reference_by_id returns the reference when found."""
        mock_reference = MagicMock()
        mock_reference.ref_id = 12345
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_reference
        mock_db.execute.return_value = mock_result
        
        result = await embedding_service.get_reference_by_id(mock_db, 12345)
        
        assert result == mock_reference


class TestGetReferencesByDocument:
    """Test EmbeddingService.get_references_by_document() method."""
    
    @pytest_asyncio.fixture
    async def mock_db(self):
        """Create a mock database session."""
        return AsyncMock()
    
    @pytest.mark.asyncio
    async def test_get_references_by_document_returns_list(self, embedding_service, mock_db):
        """Test that get_references_by_document returns a list."""
        mock_refs = [MagicMock(), MagicMock()]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_refs
        mock_db.execute.return_value = mock_result
        
        result = await embedding_service.get_references_by_document(
            mock_db, "doc_001"
        )
        
        assert isinstance(result, list)
        assert len(result) == 2
    
    @pytest.mark.asyncio
    async def test_get_references_by_document_with_org_filter(self, embedding_service, mock_db):
        """Test filtering by organization_id."""
        mock_refs = [MagicMock()]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_refs
        mock_db.execute.return_value = mock_result
        
        result = await embedding_service.get_references_by_document(
            mock_db, "doc_001", organization_id="org_demo"
        )
        
        assert len(result) == 1
        # Verify execute was called (query was built)
        assert mock_db.execute.called


class TestVerifyAndExtractEmbedding:
    """Test EmbeddingService.verify_and_extract_embedding() method."""
    
    @pytest_asyncio.fixture
    async def mock_db(self):
        """Create a mock database session."""
        return AsyncMock()
    
    @pytest.mark.asyncio
    async def test_verify_returns_none_for_invalid_embedding(self, embedding_service, mock_db):
        """Test that invalid embeddings return None."""
        # Mock UnicodeMetadata.verify_metadata to return invalid
        with patch('app.services.embedding_service.UnicodeMetadata') as mock_um:
            mock_um.verify_metadata.return_value = (False, None, None)
            
            result = await embedding_service.verify_and_extract_embedding(
                db=mock_db,
                text="Plain text without embedding",
                public_key_provider=lambda x: None
            )
            
            assert result is None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
