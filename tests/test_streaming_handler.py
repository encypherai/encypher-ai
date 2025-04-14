"""
Tests for the StreamingHandler class.
"""

from datetime import datetime, timezone

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from encypher.core.unicode_metadata import MetadataTarget, UnicodeMetadata
from encypher.streaming.handlers import StreamingHandler


class TestStreamingHandler:
    """Test cases for StreamingHandler class."""

    @pytest.fixture
    def test_key_pair(self):
        """Generate a test key pair for signing metadata."""
        private_key = Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        return private_key, public_key

    @pytest.fixture
    def test_public_key_provider(self, test_key_pair):
        """Create a public key provider function for testing."""
        _, public_key = test_key_pair

        def resolver(signer_id):
            if signer_id == "test_signer":
                return public_key
            else:
                return None

        return resolver

    def test_process_text_chunk(self, test_key_pair, test_public_key_provider):
        """Test processing a text chunk."""
        private_key, _ = test_key_pair
        metadata = {
            "model_id": "test-model",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "custom_metadata": {"test_key": "test_value"},
        }

        handler = StreamingHandler(
            metadata=metadata,
            target=MetadataTarget.WHITESPACE,
            private_key=private_key,
            signer_id="test_signer",
            metadata_format="basic",
        )

        # Process a chunk
        chunk = "This is a test chunk with spaces."
        processed_chunk = handler.process_chunk(chunk)

        # Ensure the chunk is modified (metadata added)
        assert processed_chunk != chunk

        # Extract and verify metadata from processed chunk
        extracted_payload, is_valid, extracted_signer_id = UnicodeMetadata.verify_and_extract_metadata(processed_chunk, test_public_key_provider)

        # Verify signature and extracted data
        assert is_valid is True
        assert extracted_signer_id == "test_signer"
        assert extracted_payload is not None
        assert extracted_payload.get("model_id") == metadata["model_id"]
        assert extracted_payload.get("format") == "basic"

    def test_encode_first_chunk_only(self, test_key_pair, test_public_key_provider):
        """Test encoding only the first chunk."""
        private_key, _ = test_key_pair
        metadata = {
            "model_id": "test-model",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "custom_metadata": {"test_key": "test_value"},
        }

        handler = StreamingHandler(
            metadata=metadata,
            target=MetadataTarget.WHITESPACE,
            encode_first_chunk_only=True,
            private_key=private_key,
            signer_id="test_signer",
            metadata_format="basic",
        )

        # Process first chunk
        chunk1 = "This is the first chunk with enough spaces for embedding."
        processed_chunk1 = handler.process_chunk(chunk1)

        # Ensure the first chunk is modified (metadata added)
        assert processed_chunk1 != chunk1
        assert handler.has_encoded is True

        # Process second chunk
        chunk2 = "This is the second chunk."
        processed_chunk2 = handler.process_chunk(chunk2)

        # Second chunk should not be modified
        assert processed_chunk2 == chunk2

        # Verify metadata in the first processed chunk
        extracted_payload, is_valid, extracted_signer_id = UnicodeMetadata.verify_and_extract_metadata(processed_chunk1, test_public_key_provider)
        assert is_valid is True
        assert extracted_signer_id == "test_signer"
        assert extracted_payload.get("model_id") == metadata["model_id"]

    def test_encode_all_chunks(self, test_key_pair, test_public_key_provider):
        """Test encoding all chunks with accumulation."""
        private_key, _ = test_key_pair
        metadata = {
            "model_id": "test-model",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "custom_metadata": {"test_key": "test_value"},
        }

        # Note: encode_first_chunk_only=False is not fully supported in the current implementation
        # but we can test the warning/fallback behavior
        handler = StreamingHandler(
            metadata=metadata,
            target=MetadataTarget.WHITESPACE,
            encode_first_chunk_only=False,  # This should trigger a warning and fallback
            private_key=private_key,
            signer_id="test_signer",
            metadata_format="basic",
        )

        # Process multiple chunks
        chunks = [
            "This is the first chunk.",
            "This is the second chunk.",
            "This is the third chunk with spaces.",
        ]

        processed_chunks = []
        for chunk in chunks:
            processed_chunk = handler.process_chunk(chunk)
            processed_chunks.append(processed_chunk)

        # Since encode_first_chunk_only=False is not fully supported,
        # we expect the chunks to be returned unmodified
        assert processed_chunks[0] == chunks[0]
        assert processed_chunks[1] == chunks[1]
        assert processed_chunks[2] == chunks[2]

    def test_process_dict_chunk_openai(self, test_key_pair, test_public_key_provider):
        """Test processing an OpenAI-style dictionary chunk."""
        private_key, _ = test_key_pair
        metadata = {
            "model_id": "test-model",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "custom_metadata": {"test_key": "test_value"},
        }

        handler = StreamingHandler(
            metadata=metadata,
            target=MetadataTarget.WHITESPACE,
            private_key=private_key,
            signer_id="test_signer",
            metadata_format="basic",
        )

        # Create an OpenAI-style chunk with enough spaces for embedding
        original_content = "This is a test chunk with plenty of spaces for embedding metadata."
        chunk = {
            "id": "chatcmpl-123",
            "object": "chat.completion.chunk",
            "created": 1677858242,
            "model": "gpt-3.5-turbo-0613",
            "choices": [
                {
                    "index": 0,
                    "delta": {"content": original_content},
                    "finish_reason": None,
                }
            ],
        }

        # Process the chunk
        processed_chunk = handler.process_chunk(chunk)

        # Extract the processed content
        processed_content = processed_chunk["choices"][0]["delta"]["content"]

        # Ensure the content was modified (metadata added)
        assert processed_content != original_content
        assert len(processed_content) > len(original_content)

        # Verify other parts of the chunk remain unchanged
        assert processed_chunk["id"] == chunk["id"]
        assert processed_chunk["created"] == chunk["created"]
        assert processed_chunk["model"] == chunk["model"]

        # Verify metadata in the processed content
        extracted_payload, is_valid, extracted_signer_id = UnicodeMetadata.verify_and_extract_metadata(processed_content, test_public_key_provider)
        assert is_valid is True
        assert extracted_signer_id == "test_signer"
        assert extracted_payload.get("model_id") == metadata["model_id"]

    def test_process_dict_chunk_anthropic(self, test_key_pair, test_public_key_provider):
        """Test processing an Anthropic-style dictionary chunk."""
        # Note: The current implementation doesn't have special handling for Anthropic format
        # This test is kept for future implementation
        private_key, _ = test_key_pair
        metadata = {
            "model_id": "test-model",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "custom_metadata": {"test_key": "test_value"},
        }

        handler = StreamingHandler(
            metadata=metadata,
            target=MetadataTarget.WHITESPACE,
            private_key=private_key,
            signer_id="test_signer",
            metadata_format="basic",
        )

        # Create an Anthropic-style chunk
        original_content = "This is a test chunk with plenty of spaces for embedding metadata."
        chunk = {
            "completion": original_content,
            "stop_reason": None,
            "model": "claude-2",
        }

        # Process the chunk - this will likely return the original chunk since
        # Anthropic format isn't specifically handled yet
        processed_chunk = handler.process_chunk(chunk)

        # Since we don't have specific Anthropic handling yet, we expect the chunk to be unchanged
        assert processed_chunk == chunk

    def test_reset(self, test_key_pair, test_public_key_provider):
        """Test resetting the handler."""
        private_key, _ = test_key_pair
        metadata = {
            "model_id": "test-model",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "custom_metadata": {"test_key": "test_value"},
        }

        handler = StreamingHandler(
            metadata=metadata,
            target=MetadataTarget.WHITESPACE,
            private_key=private_key,
            signer_id="test_signer",
            metadata_format="basic",
        )

        # Process a chunk with enough spaces
        chunk = "This is a test chunk with plenty of spaces for embedding metadata."
        handler.process_chunk(chunk)

        # Handler should have encoded metadata
        assert handler.has_encoded is True

        # Reset the handler
        handler.reset()

        # Handler should be reset
        assert handler.has_encoded is False
        assert handler.accumulated_text == ""
        assert handler.is_accumulating is False

        # Process another chunk
        chunk2 = "This is another test chunk with spaces for embedding."
        processed_chunk2 = handler.process_chunk(chunk2)

        # Handler should encode metadata again
        assert handler.has_encoded is True
        assert processed_chunk2 != chunk2

    def test_accumulation_for_small_chunks(self, test_key_pair, test_public_key_provider):
        """Test accumulation of small chunks until enough targets are found."""
        private_key, _ = test_key_pair
        metadata = {
            "model_id": "test-model",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "custom_metadata": {"test_key": "test_value"},
        }

        handler = StreamingHandler(
            metadata=metadata,
            target=MetadataTarget.WHITESPACE,
            private_key=private_key,
            signer_id="test_signer",
            metadata_format="basic",
        )

        # Process small chunks without enough targets
        chunk1 = "Small"
        chunk2 = "chunks"
        chunk3 = "without"
        chunk4 = "enough spaces for embedding."

        # Process the first three chunks - they should be accumulated but not modified
        processed_chunk1 = handler.process_chunk(chunk1)
        assert processed_chunk1 == chunk1
        assert handler.is_accumulating is True
        assert handler.has_encoded is False

        processed_chunk2 = handler.process_chunk(chunk2)
        assert processed_chunk2 == chunk2
        assert handler.is_accumulating is True
        assert handler.has_encoded is False

        processed_chunk3 = handler.process_chunk(chunk3)
        assert processed_chunk3 == chunk3
        assert handler.is_accumulating is True
        assert handler.has_encoded is False

        # Process the fourth chunk which has spaces - this should trigger embedding
        processed_chunk4 = handler.process_chunk(chunk4)
        assert processed_chunk4 != chunk1 + chunk2 + chunk3 + chunk4
        assert handler.is_accumulating is False
        assert handler.has_encoded is True

        # Verify metadata in the processed content
        extracted_payload, is_valid, extracted_signer_id = UnicodeMetadata.verify_and_extract_metadata(processed_chunk4, test_public_key_provider)
        assert is_valid is True
        assert extracted_signer_id == "test_signer"
        assert extracted_payload.get("model_id") == metadata["model_id"]

    def test_finalize_already_encoded(self, test_key_pair, test_public_key_provider):
        """Test finalizing the stream when metadata has already been encoded."""
        private_key, _ = test_key_pair
        metadata = {
            "model_id": "test-model",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "custom_metadata": {"test_key": "test_value"},
        }

        handler = StreamingHandler(
            metadata=metadata,
            target=MetadataTarget.WHITESPACE,
            private_key=private_key,
            signer_id="test_signer",
            metadata_format="basic",
        )

        # Process a chunk with enough targets to trigger embedding
        chunk = "This chunk has enough spaces for embedding metadata."
        processed_chunk = handler.process_chunk(chunk)

        # Verify that metadata was embedded
        assert processed_chunk != chunk
        assert handler.has_encoded is True

        # Finalize should return None since metadata was already embedded
        final_text = handler.finalize()
        assert final_text is None

    def test_finalize_with_no_targets(self, test_key_pair, test_public_key_provider):
        """Test finalizing the stream with accumulated text that has no targets."""
        private_key, _ = test_key_pair
        metadata = {
            "model_id": "test-model",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "custom_metadata": {"test_key": "test_value"},
        }

        handler = StreamingHandler(
            metadata=metadata,
            target=MetadataTarget.WHITESPACE,  # Looking for whitespace
            private_key=private_key,
            signer_id="test_signer",
            metadata_format="basic",
        )

        # Process chunks with no whitespace
        chunk1 = "Small"
        chunk2 = "chunks"
        chunk3 = "without-any-whitespace"

        # Process chunks - they should be accumulated but not modified
        handler.process_chunk(chunk1)
        handler.process_chunk(chunk2)
        handler.process_chunk(chunk3)

        # Verify that no metadata was embedded yet
        assert handler.has_encoded is False
        assert handler.is_accumulating is True

        # Finalize should return the accumulated text unmodified
        # since there are no targets for embedding
        final_text = handler.finalize()

        # Should return the original text since embedding will fail
        assert final_text is not None
        assert final_text == chunk1 + chunk2 + chunk3
