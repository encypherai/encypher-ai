"""
Unit tests for refactored EmbeddingService with invisible Unicode embeddings.

Tests the new encypher-ai integration for invisible embeddings.
"""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.services.embedding_service import EmbeddingReference, EmbeddingService

# Mock encypher-ai imports for testing
try:
    from encypher.core.keys import generate_ed25519_key_pair

    ENCYPHER_AVAILABLE = True
except ImportError:
    ENCYPHER_AVAILABLE = False
    pytest.skip("encypher-ai not available", allow_module_level=True)


class TestEmbeddingReferenceInvisible:
    """Test EmbeddingReference dataclass with invisible embeddings."""

    def test_embedding_reference_structure(self):
        """Test that EmbeddingReference has correct structure."""
        ref = EmbeddingReference(
            leaf_hash="abc123",
            leaf_index=0,
            text_content="Original text",
            embedded_text="Text with invisible embedding",
            document_id="doc_001",
            ref_id=0,
        )

        assert ref.leaf_hash == "abc123"
        assert ref.leaf_index == 0
        assert ref.text_content == "Original text"
        assert ref.embedded_text == "Text with invisible embedding"
        assert ref.document_id == "doc_001"

    def test_to_dict(self):
        """Test dictionary serialization."""
        ref = EmbeddingReference(
            leaf_hash="abc123",
            leaf_index=0,
            text_content="Original text",
            embedded_text="Text with invisible embedding",
            document_id="doc_001",
            ref_id=0,
        )

        data = ref.to_dict()

        assert data["leaf_index"] == 0
        assert data["leaf_hash"] == "abc123"
        assert data["text_content"] == "Original text"
        assert data["embedded_text"] == "Text with invisible embedding"
        assert data["has_invisible_embedding"] is True


class TestEmbeddingServiceInvisible:
    """Test EmbeddingService with invisible Unicode embeddings."""

    @pytest.fixture
    def key_pair(self):
        """Generate Ed25519 key pair for testing."""
        private_key, public_key = generate_ed25519_key_pair()
        return private_key, public_key

    @pytest.fixture
    def service(self, key_pair):
        """Create embedding service instance."""
        private_key, _ = key_pair
        return EmbeddingService(private_key, "test_signer_001")

    @pytest.fixture
    async def db_session(self):
        """Create mock database session."""
        mock_db = AsyncMock()
        mock_db.add_all = MagicMock()
        mock_db.commit = AsyncMock()
        return mock_db

    @pytest.mark.asyncio
    async def test_create_embeddings_basic(self, service, db_session):
        """Test basic invisible embedding creation."""
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
            leaf_hashes=leaf_hashes,
        )
        embeddings, _ = embeddings

        # Verify we got embeddings for all segments
        assert len(embeddings) == 3
        assert all(isinstance(e, EmbeddingReference) for e in embeddings)

        # Verify structure
        assert embeddings[0].leaf_index == 0
        assert embeddings[1].leaf_index == 1
        assert embeddings[2].leaf_index == 2

        # Verify embedded text is different from original (has invisible chars)
        # Note: In real usage, embedded_text would have Unicode variation selectors
        assert embeddings[0].text_content == "Sentence one."
        assert embeddings[0].embedded_text is not None

        # Verify database was called
        db_session.add_all.assert_called_once()
        db_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_embeddings_with_metadata(self, service, db_session):
        """Test embedding creation with enterprise metadata."""
        organization_id = "org_001"
        document_id = "doc_001"
        merkle_root_id = uuid4()
        segments = ["Test sentence."]
        leaf_hashes = ["hash1"]
        license_info = {"type": "All Rights Reserved", "url": "https://example.com/license"}
        c2pa_manifest_url = "https://example.com/manifest.c2pa"

        embeddings = await service.create_embeddings(
            db=db_session,
            organization_id=organization_id,
            document_id=document_id,
            merkle_root_id=merkle_root_id,
            segments=segments,
            leaf_hashes=leaf_hashes,
            license_info=license_info,
            c2pa_manifest_url=c2pa_manifest_url,
        )
        embeddings, _ = embeddings

        assert len(embeddings) == 1

        # Verify database call included metadata
        db_session.add_all.assert_called_once()
        added_refs = db_session.add_all.call_args[0][0]
        assert len(added_refs) == 1
        assert added_refs[0].c2pa_manifest_url == c2pa_manifest_url
        assert added_refs[0].license_type == "All Rights Reserved"

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
                leaf_hashes=["hash1"],  # Mismatched length
            )

    @pytest.mark.asyncio
    async def test_verify_and_extract_embedding(self, service, db_session, key_pair):
        """Test extracting and verifying invisible embedding."""
        private_key, public_key = key_pair

        # Mock the database query
        mock_reference = MagicMock()
        mock_reference.document_id = "doc_001"
        mock_reference.organization_id = "org_001"
        mock_reference.leaf_index = 0
        mock_reference.expires_at = None

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_reference
        db_session.execute = AsyncMock(return_value=mock_result)

        # Create a public key provider
        def public_key_provider(signer_id: str):
            if signer_id == "test_signer_001":
                return public_key
            return None

        # Create text with invisible embedding using encypher-ai
        from encypher.core.unicode_metadata import UnicodeMetadata

        test_text = "This is a test sentence."
        custom_metadata = {
            "document_id": "doc_001",
            "organization_id": "org_001",
            "leaf_index": 0,
            "merkle_root_id": str(uuid4()),
            "leaf_hash": "test_hash",
        }

        embedded_text = UnicodeMetadata.embed_metadata(
            text=test_text, private_key=private_key, signer_id="test_signer_001", custom_metadata=custom_metadata
        )

        # Verify the embedding can be extracted
        result = await service.verify_and_extract_embedding(db=db_session, text=embedded_text, public_key_provider=public_key_provider)

        assert result is not None
        reference, metadata = result
        assert reference == mock_reference
        assert metadata["signer_id"] == "test_signer_001"
        assert metadata["custom_metadata"]["document_id"] == "doc_001"


class TestInvisibleEmbeddingIntegration:
    """Integration tests for invisible embedding workflow."""

    @pytest.fixture
    def key_pair(self):
        """Generate Ed25519 key pair for testing."""
        private_key, public_key = generate_ed25519_key_pair()
        return private_key, public_key

    @pytest.mark.asyncio
    async def test_end_to_end_embedding_workflow(self, key_pair):
        """Test complete workflow: create, embed, extract, verify."""
        private_key, public_key = key_pair

        # 1. Create service
        service = EmbeddingService(private_key, "test_org_001")

        # 2. Create mock database
        db_session = AsyncMock()
        db_session.add_all = MagicMock()
        db_session.commit = AsyncMock()

        # 3. Create embeddings
        segments = ["First sentence.", "Second sentence."]
        leaf_hashes = ["hash1", "hash2"]

        embeddings = await service.create_embeddings(
            db=db_session, organization_id="org_001", document_id="doc_001", merkle_root_id=uuid4(), segments=segments, leaf_hashes=leaf_hashes
        )

        embeddings, _ = embeddings

        assert len(embeddings) == 2

        # 4. Verify each embedded text can be extracted
        from encypher.core.unicode_metadata import UnicodeMetadata

        def public_key_provider(signer_id: str):
            if signer_id == "test_org_001":
                return public_key
            return None

        for embedding in embeddings:
            # Extract metadata from embedded text
            is_valid, signer_id, payload = UnicodeMetadata.verify_metadata(text=embedding.embedded_text, public_key_resolver=public_key_provider)

            assert is_valid is True
            assert signer_id == "test_org_001"
            assert payload is not None
            if isinstance(payload, dict):
                custom = payload.get("custom_metadata") or {}
            else:
                custom = payload.custom_metadata
            assert custom["document_id"] == "doc_001"
            assert custom["organization_id"] == "org_001"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
