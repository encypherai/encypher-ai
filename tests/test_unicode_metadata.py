"""
Tests for the UnicodeMetadata class.
"""

import time
from datetime import datetime, timezone

import pytest

from encypher.core.keys import generate_ed25519_key_pair as generate_key_pair
from encypher.core.unicode_metadata import MetadataTarget, UnicodeMetadata


class TestUnicodeMetadata:
    """Test cases for UnicodeMetadata class."""

    def test_encode_decode(self):
        """Test encoding and decoding text using variation selectors."""
        original_text = "Test text"
        emoji = "🔍"

        encoded = UnicodeMetadata.encode(emoji, original_text)
        decoded = UnicodeMetadata.decode(encoded)

        assert decoded == original_text
        assert encoded.startswith(emoji)
        assert len(encoded) > len(emoji)

    @pytest.mark.skip(reason="Test based on old embed_metadata signature (HMAC), incompatible with new signature-based method.")
    def test_embed_extract_metadata(self):
        """Test embedding and extracting metadata."""
        text = "This is a test text with some spaces and punctuation."
        model_id = "test-model"
        # Use a specific datetime and convert to timestamp
        test_dt = datetime.fromisoformat("2025-03-19T10:35:00+00:00")
        timestamp = int(test_dt.timestamp())

        # Test with different targets
        for target in [t for t in MetadataTarget if t != MetadataTarget.NONE]:
            encoded_text = UnicodeMetadata.embed_metadata(text=text, model_id=model_id, timestamp=timestamp, target=target)

            # Ensure the text is modified (metadata added)
            assert encoded_text != text

            # Extract metadata
            metadata = UnicodeMetadata.extract_metadata(encoded_text)

            # Verify extracted metadata
            assert metadata.get("model_id") == model_id
            # Verify the timestamp is a datetime object with the correct value
            assert isinstance(metadata.get("timestamp"), datetime)
            assert metadata.get("timestamp").replace(microsecond=0) == test_dt.replace(microsecond=0)

    @pytest.mark.skip(reason="Test based on old embed_metadata signature (HMAC), incompatible with new signature-based method.")
    def test_custom_metadata(self):
        """Test embedding and extracting custom metadata."""
        text = "This is a test text."
        custom_metadata = {
            "user_id": "test-user",
            "session_id": "test-session",
            "custom_field": "custom value",
        }

        encoded_text = UnicodeMetadata.embed_metadata(text=text, custom_metadata=custom_metadata)

        # Extract metadata
        metadata = UnicodeMetadata.extract_metadata(encoded_text)

        # Verify custom metadata
        for key, value in custom_metadata.items():
            assert metadata.get(key) == value

    @pytest.mark.skip(reason="Test based on old embed_metadata signature (HMAC), incompatible with new signature-based method.")
    def test_no_metadata_target(self):
        """Test with NONE metadata target."""
        text = "This is a test text."
        model_id = "test-model"

        encoded_text = UnicodeMetadata.embed_metadata(text=text, model_id=model_id, target=MetadataTarget.NONE)

        # With NONE target, the text should remain unchanged
        assert encoded_text == text

        # Extract metadata should return empty values
        metadata = UnicodeMetadata.extract_metadata(encoded_text)
        assert metadata.get("model_id") == ""
        assert metadata.get("timestamp") is None

    @pytest.mark.skip(reason="Test based on old embed_metadata signature (HMAC), incompatible with new signature-based method.")
    def test_empty_text(self):
        """Test with empty text."""
        text = ""
        metadata = {"model_id": "test-model", "timestamp": int(time.time())}

        # Encode metadata
        encoded_text = UnicodeMetadata.embed_metadata(text, metadata)

        # Ensure the text is modified (metadata added)
        assert encoded_text != text
        assert len(encoded_text) > 0

        # Decode metadata
        extracted_metadata = UnicodeMetadata.extract_metadata(encoded_text)

        # Verify extracted metadata
        assert extracted_metadata is not None, "Metadata should be extracted even from empty text"
        assert extracted_metadata.get("model_id") == metadata["model_id"]
        assert int(extracted_metadata.get("timestamp")) == metadata["timestamp"]

    @pytest.mark.skip(reason="Test based on old embed_metadata signature (HMAC), incompatible with new signature-based method.")
    def test_datetime_timestamp(self):
        """Test with datetime object as timestamp."""
        text = "This is a test text."
        model_id = "test-model"
        timestamp = datetime.now(timezone.utc)

        encoded_text = UnicodeMetadata.embed_metadata(text=text, model_id=model_id, timestamp=timestamp)

        # Extract metadata
        metadata = UnicodeMetadata.extract_metadata(encoded_text)

        # Verify timestamp (as datetime object in metadata)
        assert isinstance(metadata.get("timestamp"), datetime)
        # Compare the timestamps ignoring microseconds
        extracted_ts = metadata.get("timestamp").replace(microsecond=0)
        original_ts = timestamp.replace(microsecond=0)
        assert extracted_ts == original_ts

    def test_variation_selector_conversion(self):
        """Test conversion between bytes and variation selectors."""
        # Test valid byte values
        for byte in [0, 15, 16, 255]:
            vs = UnicodeMetadata.to_variation_selector(byte)
            assert vs is not None

            # Convert back
            byte_back = UnicodeMetadata.from_variation_selector(ord(vs))
            assert byte_back == byte

        # Test invalid byte value
        assert UnicodeMetadata.to_variation_selector(256) is None

        # Test invalid code point
        assert UnicodeMetadata.from_variation_selector(0x0000) is None

    @pytest.mark.skip(reason="Test based on old embed_metadata signature (HMAC), incompatible with new signature-based method.")
    def test_hmac_verification(self):
        """Test HMAC verification."""
        # Use a fixed timestamp to avoid any timing issues

        # Create metadata dictionary directly to ensure consistent format

        # Create encoder with the secret key
        # encoder = MetadataEncoder(hmac_secret_key=hmac_secret_key)

        # Encode the metadata
        # encoded_text = encoder.encode_metadata(text, metadata)

        # Verify with correct key
        # is_valid, extracted_metadata, _ = encoder.verify_text(encoded_text)

        # Check verification result
        # assert is_valid, "HMAC verification should succeed with correct key"
        # assert extracted_metadata is not None
        # assert extracted_metadata.get("model_id") == model_id
        # assert int(extracted_metadata.get("timestamp")) == timestamp

        # Verify with incorrect key
        # wrong_encoder = MetadataEncoder(hmac_secret_key="wrong-secret")
        # is_valid_wrong, _, _ = wrong_encoder.verify_text(encoded_text)

        # Check verification result with wrong key
        # assert not is_valid_wrong, "HMAC verification should fail with incorrect key"

    def test_unicode_metadata_non_string_input(self, key_pair_1):
        """Test that non-string input raises TypeError for embed_metadata."""
        private_key, _ = key_pair_1
        with pytest.raises(TypeError, match="Input text must be a string"):
            # Now the type check happens before any len() call
            UnicodeMetadata.embed_metadata(12345, private_key, "test-signer")  # type: ignore
        with pytest.raises(TypeError, match="Input text must be a string"):
            UnicodeMetadata.embed_metadata(None, private_key, "test-signer")  # type: ignore
        with pytest.raises(TypeError, match="Input text must be a string"):
            UnicodeMetadata.embed_metadata(["list"], private_key, "test-signer")  # type: ignore


@pytest.fixture
def key_pair_1():
    """Generate a key pair for testing."""
    return generate_key_pair()
