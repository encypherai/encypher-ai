"""
Unit tests for EmbeddingService.

Tests the enterprise embedding service built on encypher-ai package.

NOTE: The EmbeddingService API has been refactored to use the encypher-ai package.
The old methods (_generate_ref_id, _generate_signature, verify_signature) no longer exist.
These tests need to be rewritten to test the current API:
- create_embeddings() - async method that creates embeddings with C2PA manifests
- verify_and_extract_embedding() - async method for verification

TODO: Rewrite tests for current API (v1.0.0 launch blocker)
"""
import pytest
from datetime import datetime
from uuid import uuid4

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from app.services.embedding_service import EmbeddingService, EmbeddingReference
from app.models.content_reference import ContentReference

# Mark entire module as skipped until tests are rewritten for new API
pytestmark = pytest.mark.skip(reason="Tests need rewrite for refactored EmbeddingService API - see TODO in docstring")


@pytest.fixture
def test_private_key():
    """Generate a test Ed25519 private key."""
    return Ed25519PrivateKey.generate()


@pytest.fixture
def embedding_service(test_private_key):
    """Create an EmbeddingService instance for testing."""
    return EmbeddingService(private_key=test_private_key, signer_id="test_signer_001")


class TestRefIdGeneration:
    """Test reference ID generation."""
    
    def test_generate_ref_id_format(self, embedding_service):
        """Test that ref_id has correct format."""
        ref_id = embedding_service._generate_ref_id()
        
        # Should be 64-bit integer
        assert isinstance(ref_id, int)
        assert 0 <= ref_id < 2**64
        
        # Should be representable as 8 hex characters
        ref_hex = format(ref_id, '08x')
        assert len(ref_hex) == 16  # 8 bytes = 16 hex chars
    
    def test_generate_ref_id_uniqueness(self):
        """Test that generated ref_ids are unique."""
        service = EmbeddingService(b'test_secret_key_32_bytes_long!!')
        
        ref_ids = set()
        for _ in range(1000):
            ref_id = service._generate_ref_id()
            assert ref_id not in ref_ids, "Duplicate ref_id generated"
            ref_ids.add(ref_id)
    
    def test_generate_ref_id_monotonic_sequence(self):
        """Test that sequence component increments."""
        service = EmbeddingService(b'test_secret_key_32_bytes_long!!')
        
        # Generate multiple IDs quickly (same timestamp)
        ref_ids = [service._generate_ref_id() for _ in range(10)]
        
        # Extract sequence components (bits 32-47)
        sequences = [(ref_id >> 32) & 0xFFFF for ref_id in ref_ids]
        
        # Should be monotonically increasing
        for i in range(1, len(sequences)):
            assert sequences[i] >= sequences[i-1]


class TestSignatureGeneration:
    """Test HMAC signature generation and verification."""
    
    def test_generate_signature_format(self):
        """Test that signature has correct format."""
        service = EmbeddingService(b'test_secret_key_32_bytes_long!!')
        ref_id = 0x123456789ABCDEF0
        
        signature = service._generate_signature(ref_id)
        
        # Should be 16 hex characters (8 bytes)
        assert isinstance(signature, str)
        assert len(signature) == 16
        assert all(c in '0123456789abcdef' for c in signature)
    
    def test_signature_deterministic(self):
        """Test that same ref_id produces same signature."""
        service = EmbeddingService(b'test_secret_key_32_bytes_long!!')
        ref_id = 0x123456789ABCDEF0
        
        sig1 = service._generate_signature(ref_id)
        sig2 = service._generate_signature(ref_id)
        
        assert sig1 == sig2
    
    def test_signature_different_keys(self):
        """Test that different keys produce different signatures."""
        service1 = EmbeddingService(b'test_secret_key_32_bytes_long!!')
        service2 = EmbeddingService(b'different_key_32_bytes_long!!!')
        ref_id = 0x123456789ABCDEF0
        
        sig1 = service1._generate_signature(ref_id)
        sig2 = service2._generate_signature(ref_id)
        
        assert sig1 != sig2
    
    def test_verify_signature_valid(self):
        """Test verification of valid signature."""
        service = EmbeddingService(b'test_secret_key_32_bytes_long!!')
        ref_id = 0x123456789ABCDEF0
        
        signature = service._generate_signature(ref_id)
        
        assert service.verify_signature(ref_id, signature) is True
    
    def test_verify_signature_invalid(self):
        """Test verification of invalid signature."""
        service = EmbeddingService(b'test_secret_key_32_bytes_long!!')
        ref_id = 0x123456789ABCDEF0
        
        invalid_signature = "0000000000000000"
        
        assert service.verify_signature(ref_id, invalid_signature) is False
    
    def test_verify_signature_wrong_ref_id(self):
        """Test that signature for different ref_id fails."""
        service = EmbeddingService(b'test_secret_key_32_bytes_long!!')
        ref_id1 = 0x123456789ABCDEF0
        ref_id2 = 0xFEDCBA9876543210
        
        signature1 = service._generate_signature(ref_id1)
        
        assert service.verify_signature(ref_id2, signature1) is False


class TestEmbeddingReference:
    """Test EmbeddingReference dataclass."""
    
    def test_to_compact_string(self):
        """Test compact string generation."""
        ref = EmbeddingReference(
            ref_id=0xa3f9c2e1,
            signature="8k3mP9xQ12345678",
            leaf_hash="abc123",
            leaf_index=0,
            text_content="Test sentence",
            document_id="doc_001"
        )
        
        compact = ref.to_compact_string()
        
        assert compact == "ency:v1/a3f9c2e1/8k3mP9xQ"
        assert len(compact) <= 28  # Should be compact
    
    def test_to_url(self):
        """Test verification URL generation."""
        ref = EmbeddingReference(
            ref_id=0xa3f9c2e1,
            signature="8k3mP9xQ12345678",
            leaf_hash="abc123",
            leaf_index=0,
            text_content="Test sentence",
            document_id="doc_001"
        )
        
        url = ref.to_url()
        
        assert url == "https://verify.encypher.ai/a3f9c2e1"
    
    def test_to_dict(self):
        """Test dictionary serialization."""
        ref = EmbeddingReference(
            ref_id=0xa3f9c2e1,
            signature="8k3mP9xQ12345678",
            leaf_hash="abc123",
            leaf_index=0,
            text_content="Test sentence",
            document_id="doc_001"
        )
        
        data = ref.to_dict()
        
        assert data['ref_id'] == 'a3f9c2e1'
        assert data['signature'] == '8k3mP9xQ'
        assert data['embedding'] == 'ency:v1/a3f9c2e1/8k3mP9xQ'
        assert 'verification_url' in data


class TestEmbeddingServiceAsync:
    """Test async methods of EmbeddingService."""
    
    @pytest.fixture
    async def db_session(self):
        """Create test database session."""
        # This would use your test database setup
        # For now, we'll mock it
        from unittest.mock import AsyncMock
        return AsyncMock()
    
    @pytest.fixture
    def service(self):
        """Create embedding service instance."""
        return EmbeddingService(b'test_secret_key_32_bytes_long!!')
    
    @pytest.mark.asyncio
    async def test_create_embeddings_basic(self, service, db_session):
        """Test basic embedding creation."""
        organization_id = "org_001"
        document_id = "doc_001"
        merkle_root_id = uuid4()
        segments = ["Sentence one.", "Sentence two.", "Sentence three."]
        leaf_hashes = ["hash1", "hash2", "hash3"]
        
        embeddings = await service.create_embeddings(
            db=db_session,
            organization_id=organization_id,
            document_id=document_id,
            merkle_root_id=merkle_root_id,
            segments=segments,
            leaf_hashes=leaf_hashes
        )
        
        assert len(embeddings) == 3
        assert all(isinstance(e, EmbeddingReference) for e in embeddings)
        assert embeddings[0].leaf_index == 0
        assert embeddings[1].leaf_index == 1
        assert embeddings[2].leaf_index == 2
    
    @pytest.mark.asyncio
    async def test_create_embeddings_with_license(self, service, db_session):
        """Test embedding creation with license info."""
        organization_id = "org_001"
        document_id = "doc_001"
        merkle_root_id = uuid4()
        segments = ["Test sentence."]
        leaf_hashes = ["hash1"]
        license_info = {
            'type': 'All Rights Reserved',
            'url': 'https://example.com/license'
        }
        
        embeddings = await service.create_embeddings(
            db=db_session,
            organization_id=organization_id,
            document_id=document_id,
            merkle_root_id=merkle_root_id,
            segments=segments,
            leaf_hashes=leaf_hashes,
            license_info=license_info
        )
        
        assert len(embeddings) == 1
    
    @pytest.mark.asyncio
    async def test_create_embeddings_mismatched_lengths(self, service, db_session):
        """Test that mismatched segments/hashes raises error."""
        with pytest.raises(ValueError, match="must have same length"):
            await service.create_embeddings(
                db=db_session,
                organization_id="org_001",
                document_id="doc_001",
                merkle_root_id=uuid4(),
                segments=["Sentence one.", "Sentence two."],
                leaf_hashes=["hash1"]  # Mismatched length
            )


class TestEmbeddingParsing:
    """Test parsing of embedding strings."""
    
    def test_parse_embedding_valid(self):
        """Test parsing valid embedding string."""
        service = EmbeddingService(b'test_secret_key_32_bytes_long!!')
        
        result = service.parse_embedding("ency:v1/a3f9c2e1/8k3mP9xQ")
        
        assert result is not None
        version, ref_id_hex, signature_hex = result
        assert version == "v1"
        assert ref_id_hex == "a3f9c2e1"
        assert signature_hex == "8k3mP9xQ"
    
    def test_parse_embedding_invalid_prefix(self):
        """Test parsing with invalid prefix."""
        service = EmbeddingService(b'test_secret_key_32_bytes_long!!')
        
        result = service.parse_embedding("invalid:v1/a3f9c2e1/8k3mP9xQ")
        
        assert result is None
    
    def test_parse_embedding_invalid_format(self):
        """Test parsing with invalid format."""
        service = EmbeddingService(b'test_secret_key_32_bytes_long!!')
        
        result = service.parse_embedding("ency:v1/invalid")
        
        assert result is None
    
    def test_parse_embedding_short_ref_id(self):
        """Test parsing with short ref_id."""
        service = EmbeddingService(b'test_secret_key_32_bytes_long!!')
        
        result = service.parse_embedding("ency:v1/abc/8k3mP9xQ")
        
        assert result is None


class TestContentReferenceModel:
    """Test ContentReference model methods."""
    
    def test_to_compact_string(self):
        """Test model's to_compact_string method."""
        ref = ContentReference(
            ref_id=0xa3f9c2e1,
            merkle_root_id=uuid4(),
            leaf_hash="abc123",
            leaf_index=0,
            organization_id="org_001",
            document_id="doc_001",
            signature_hash="8k3mP9xQ12345678"
        )
        
        compact = ref.to_compact_string()
        
        assert compact == "ency:v1/a3f9c2e1/8k3mP9xQ"
    
    def test_to_verification_url(self):
        """Test model's to_verification_url method."""
        ref = ContentReference(
            ref_id=0xa3f9c2e1,
            merkle_root_id=uuid4(),
            leaf_hash="abc123",
            leaf_index=0,
            organization_id="org_001",
            document_id="doc_001",
            signature_hash="8k3mP9xQ12345678"
        )
        
        url = ref.to_verification_url()
        
        assert url == "https://verify.encypher.ai/a3f9c2e1"
    
    def test_to_dict_basic(self):
        """Test model's to_dict method."""
        ref = ContentReference(
            ref_id=0xa3f9c2e1,
            merkle_root_id=uuid4(),
            leaf_hash="abc123",
            leaf_index=0,
            organization_id="org_001",
            document_id="doc_001",
            text_content="Full text content",
            text_preview="Full text...",
            signature_hash="8k3mP9xQ12345678",
            created_at=datetime.utcnow()
        )
        
        data = ref.to_dict(include_text=False)
        
        assert data['ref_id'] == 'a3f9c2e1'
        assert data['text_preview'] == 'Full text...'
        assert 'text_content' not in data
    
    def test_to_dict_with_text(self):
        """Test model's to_dict with full text."""
        ref = ContentReference(
            ref_id=0xa3f9c2e1,
            merkle_root_id=uuid4(),
            leaf_hash="abc123",
            leaf_index=0,
            organization_id="org_001",
            document_id="doc_001",
            text_content="Full text content",
            signature_hash="8k3mP9xQ12345678",
            created_at=datetime.utcnow()
        )
        
        data = ref.to_dict(include_text=True)
        
        assert data['text_content'] == 'Full text content'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
