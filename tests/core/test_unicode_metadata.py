# ruff: noqa: E501
import json
import zlib
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Dict, Optional, Tuple, cast

import pytest
from cryptography.hazmat.primitives.asymmetric.types import PrivateKeyTypes, PublicKeyTypes

from encypher.core.keys import generate_ed25519_key_pair as generate_key_pair  # Needed for manual verification check
from encypher.core.unicode_metadata import MetadataTarget, UnicodeMetadata

# --- Test Fixtures ---


@pytest.fixture(scope="module")
def key_pair_1() -> Tuple[PrivateKeyTypes, PublicKeyTypes]:
    """Generate first key pair for tests."""
    return generate_key_pair()


@pytest.fixture(scope="module")
def key_pair_2() -> Tuple[PrivateKeyTypes, PublicKeyTypes]:
    """Generate a second, different key pair for tests."""
    return generate_key_pair()


@pytest.fixture
def sample_text() -> str:
    """Provides a much longer sample text with abundant targets for embedding metadata."""
    # This text needs to be significantly long and varied to ensure enough targets
    # of both whitespace and punctuation types for ~500 bytes of payload.
    # Let's add multiple paragraphs and different styles.
    paragraph1 = (
        "This is the first paragraph of a substantially longer sample text document, meticulously crafted for testing metadata embedding procedures. "
        "Our primary objective is to guarantee a sufficient quantity of 'target' characters—such as spaces, commas, periods, newlines (though maybe not embeddable), question marks, exclamation points, and semicolons—within this block. "
        "These targets are essential for successfully embedding the necessary metadata payload. This payload encompasses not merely the original data but also a robust cryptographic signature and associated signer identification. Punctuation, indeed, helps significantly! "
        "Consider these numbers: 123, 45.67, -890. Is variability not the spice of life? Yes! Yes, it is! "
    )
    paragraph2 = (
        "Moving to the second paragraph, we explore the intricacies of the embedding process itself. It involves meticulously scanning the text to identify suitable locations (the aforementioned targets). "
        "Once identified, the compressed and serialized metadata payload is encoded using specific Unicode variation selectors or similar techniques. Then, it's subtly inserted into the text at these target locations. "
        "The key is to make these insertions minimally disruptive to the original text's appearance and flow. Think about that; it's quite clever, right? What about a list? Item 1; Item 2; Item 3. "
    )
    paragraph3 = (
        "Finally, the third paragraph focuses on the verification stage. This critical step involves extracting the embedded bytes from their hidden locations within the text. "
        "The extracted bytes are then decoded, decompressed, and deserialized to reconstruct the original payload structure. The most crucial part follows: checking the cryptographic signature. "
        "This involves using the public key associated with the claimed signer ID (retrieved from a trusted provider) to validate the signature against the reconstructed payload data. If they match, the metadata is authentic! "
        "We sincerely hope this greatly extended version provides more than ample space for all test cases. Let's add one more: 987-654-3210. Success? We hope so..."
    )
    return f"{paragraph1}\n\n{paragraph2}\n\n{paragraph3}"


@pytest.fixture
def basic_metadata() -> Dict[str, Any]:
    """Sample basic metadata."""
    return {
        "model_id": "test_basic_model_v1",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "custom_metadata": {"source": "test", "run_id": 123},
    }


@pytest.fixture
def manifest_metadata() -> Dict[str, Any]:
    """Sample manifest metadata."""
    now = datetime.now(timezone.utc)
    return {
        "claim_generator": "pytest-encypher/1.0",
        "timestamp": now.isoformat(),
        "actions": [
            {
                "action": "c2pa.created",
                "when": (now - timedelta(seconds=10)).isoformat(),
            },
            {
                "action": "c2pa.edited",
                "when": now.isoformat(),
                "softwareAgent": "pytest",
            },
        ],
        "ai_info": {"model_id": "test_manifest_model_v2", "version": "2.1-beta"},
        "custom_claims": {"project": "refactor", "verified": False},
    }


# --- Public Key Provider Fixture ---


@pytest.fixture
def public_key_provider(key_pair_1, key_pair_2) -> Callable[[str], Optional[PublicKeyTypes]]:
    """Provides a function to resolve signer IDs to public keys."""
    priv1, pub1 = key_pair_1
    priv2, pub2 = key_pair_2

    key_map = {
        "signer_1": pub1,
        "signer_2": pub2,
    }

    def resolver(signer_id: str) -> Optional[PublicKeyTypes]:
        return key_map.get(signer_id)

    return resolver


# --- Helper Function ---


def decode_and_deserialize(text: str) -> Optional[Dict[str, Any]]:
    """Helper to extract bytes, decompress, and deserialize for inspection."""
    raw_bytes = UnicodeMetadata.extract_bytes(text)
    if not raw_bytes:
        return None
    try:
        # Assume compression header if first byte is 'z'
        if raw_bytes.startswith(b"z"):
            decompressed_bytes = zlib.decompress(raw_bytes[1:])
        else:
            decompressed_bytes = raw_bytes
        # Cast the result of json.loads to Dict[str, Any] to satisfy mypy
        deserialized_data = json.loads(decompressed_bytes.decode("utf-8"))
        return cast(Dict[str, Any], deserialized_data)
    except (zlib.error, json.JSONDecodeError, UnicodeDecodeError):
        return None


class TestUnicodeMetadata:
    """Tests for the UnicodeMetadata class using signatures."""

    # --- Test Cases ---

    @pytest.mark.parametrize(
        "metadata_format, metadata_fixture",
        [
            ("basic", "basic_metadata"),
            ("manifest", "manifest_metadata"),
            ("jumbf", "manifest_metadata"),
        ],
    )
    def test_embed_verify_extract_success(
        self,
        key_pair_1,
        sample_text,
        metadata_format,
        metadata_fixture,
        public_key_provider,
        request,  # Required to use fixture names indirectly
    ):
        """Test successful embedding, verification, and extraction."""
        private_key, public_key = key_pair_1
        signer_id = "signer_1"
        metadata = request.getfixturevalue(metadata_fixture)

        # Store original payload for comparison (handle TypedDict conversion if needed)
        if "timestamp" not in metadata:
            metadata["timestamp"] = datetime.now(timezone.utc).isoformat()

        original_payload = metadata.copy()

        embedded_text = UnicodeMetadata.embed_metadata(
            text=sample_text,
            private_key=private_key,
            signer_id=signer_id,
            metadata_format=metadata_format,
            target=MetadataTarget.PUNCTUATION,  # Use punctuation
            **metadata,
        )

        assert embedded_text != sample_text

        # Add debug information
        # Verify text was embedded successfully
        assert len(embedded_text) > len(sample_text)

        # Extract bytes for debugging
        extracted_bytes = UnicodeMetadata.extract_bytes(embedded_text)
        # Verify bytes were extracted

        # Try to decode the extracted bytes
        try:
            outer_data_str = extracted_bytes.decode("utf-8")
            outer_data = json.loads(outer_data_str)
            # Verify outer data structure
            assert "format" in outer_data
        except Exception as e:
            pytest.fail(f"Error decoding extracted bytes: {e}")

        is_valid, extracted_signer_id, extracted_payload = UnicodeMetadata.verify_metadata(embedded_text, public_key_provider)

        # Add more debug information
        # Verify extraction results
        assert is_valid
        assert extracted_signer_id == signer_id
        assert extracted_payload is not None

        assert is_valid is True
        assert extracted_signer_id == signer_id
        # Compare extracted payload with the original input metadata
        # Note: Timestamp formatting might differ slightly if not ISO string initially
        # We compare the core content
        assert extracted_payload is not None
        if metadata_format == "jumbf":
            # JUMBF inner payload uses manifest structure
            assert extracted_payload.get("format") == "manifest"
        else:
            assert extracted_payload.get("format") == metadata_format

        # Compare relevant fields based on format
        if metadata_format == "basic":
            assert extracted_payload.get("model_id") == original_payload.get("model_id")
            assert "timestamp" in extracted_payload
            assert extracted_payload.get("custom_metadata") == original_payload.get("custom_metadata")
        elif metadata_format in ("manifest", "jumbf"):
            # Access nested manifest fields
            manifest_payload = extracted_payload.get("manifest", {})
            assert manifest_payload.get("claim_generator") == original_payload.get("claim_generator")
            # Compare actions - might need careful comparison due to structure/order
            assert manifest_payload.get("actions") == original_payload.get("actions")
            assert manifest_payload.get("ai_info") == original_payload.get("ai_info")
            assert manifest_payload.get("custom_claims") == original_payload.get("custom_claims")

    def test_embed_metadata_allows_missing_timestamp(self, key_pair_1, sample_text, public_key_provider):
        """Embedding should succeed without a timestamp (timestamp is optional)."""
        private_key, _ = key_pair_1
        signer_id = "signer_1"

        embedded_text = UnicodeMetadata.embed_metadata(
            text=sample_text,
            private_key=private_key,
            signer_id=signer_id,
            metadata_format="basic",
            model_id="test_model",
            timestamp=None,  # Explicitly omitted
            custom_metadata={"data": "value"},
            target=MetadataTarget.PUNCTUATION,
        )

        is_valid, extracted_signer_id, payload = UnicodeMetadata.verify_metadata(embedded_text, public_key_provider)
        assert is_valid is True
        assert extracted_signer_id == signer_id
        assert payload is not None
        # For basic format with no timestamp provided, 'timestamp' should be absent
        assert payload.get("format") == "basic"
        assert "timestamp" not in payload

    def test_verify_wrong_key(
        self,
        key_pair_1,
        key_pair_2,
        sample_text,
        basic_metadata,
        public_key_provider,
    ):
        """Test verification failure when the wrong public key is used (via provider)."""
        private_key_signer1, _ = key_pair_1
        _, public_key_signer2 = key_pair_2
        signer_id = "signer_1"

        # Define a provider that returns the wrong key
        def wrong_key_provider(s_id: str) -> Optional[PublicKeyTypes]:
            if s_id == "signer_1":
                return cast(PublicKeyTypes, public_key_signer2)  # Return signer 2's key for signer 1's ID
            return None

        # Embed with key 1
        embedded_text = UnicodeMetadata.embed_metadata(
            text=sample_text,
            private_key=private_key_signer1,
            signer_id=signer_id,
            metadata_format="basic",
            target=MetadataTarget.PUNCTUATION,  # Use punctuation
            **basic_metadata,
        )

        # Verify with wrong key provider
        is_valid, extracted_signer_id, extracted_payload = UnicodeMetadata.verify_metadata(
            embedded_text,
            wrong_key_provider,
            return_payload_on_failure=True,  # Return payload even when verification fails
        )

        assert is_valid is False
        assert extracted_signer_id == signer_id
        assert extracted_payload is not None  # Payload is extracted, but verification fails

    def test_verify_tampered_data(
        self,
        key_pair_1,
        key_pair_2,
        sample_text,
        basic_metadata,
        public_key_provider,
    ):
        """Test verification failure when the embedded data is altered."""
        private_key_1, _ = key_pair_1
        private_key_2, _ = key_pair_2
        signer_id = "signer_1"

        # First, embed metadata with key_pair_1
        embedded_text = UnicodeMetadata.embed_metadata(
            text=sample_text,
            private_key=private_key_1,
            signer_id=signer_id,
            metadata_format="basic",
            target=MetadataTarget.PUNCTUATION,  # Use punctuation
            **basic_metadata,
        )

        # Create tampered text by re-embedding the same metadata with a different key
        # This simulates tampering with the data while keeping the same signer_id
        tampered_text = UnicodeMetadata.embed_metadata(
            text=sample_text,
            private_key=private_key_2,  # Use a different key
            signer_id=signer_id,  # But claim to be the same signer
            metadata_format="basic",
            target=MetadataTarget.PUNCTUATION,
            **basic_metadata,
        )

        assert tampered_text != embedded_text

        # Verify the tampered text with the original signer's public key
        is_valid, extracted_signer_id, extracted_payload = UnicodeMetadata.verify_metadata(
            tampered_text,
            public_key_provider,
            return_payload_on_failure=True,  # Return payload even when verification fails
        )

        # Verification should fail due to tampered data (wrong key used)
        assert is_valid is False
        # Payload should still be extracted since we're using return_payload_on_failure=True
        assert extracted_payload is not None

    def test_verify_failure_wrong_key(
        self,
        key_pair_1,
        key_pair_2,
        sample_text,
        public_key_provider,
    ):
        """Test verification failure with the wrong public key."""
        private_key_1, _ = key_pair_1
        signer_id = "signer_2"  # ID associated with key_pair_2 in the provider

        encoded_text = UnicodeMetadata.embed_metadata(
            text=sample_text,
            private_key=private_key_1,
            signer_id=signer_id,  # Sign with key 1, but claim to be signer 2
            metadata_format="basic",
            model_id="wrong_key_test",
            timestamp=datetime.now(timezone.utc).isoformat(),
            target=MetadataTarget.PUNCTUATION,  # Use punctuation
        )

        # Verification should fail because signature doesn't match public key for signer_id
        is_valid, extracted_signer_id, extracted_payload = UnicodeMetadata.verify_metadata(encoded_text, public_key_provider)

        assert not is_valid
        assert extracted_payload is None

    def test_verify_failure_invalid_signature_format(
        self,
        key_pair_1,
        sample_text,
        public_key_provider,
    ):
        """Test verification failure with a malformed signature string."""
        private_key, _ = key_pair_1
        signer_id = "signer_1"
        encoded_text = UnicodeMetadata.embed_metadata(
            text=sample_text,
            private_key=private_key,
            signer_id=signer_id,
            metadata_format="basic",
            model_id="bad_sig_test",
            timestamp=datetime.now(timezone.utc).isoformat(),
            target=MetadataTarget.PUNCTUATION,  # Use punctuation
        )

        # With the new embedding approach, we'll just modify a few variation selectors
        # Find the first variation selector and change it
        for i, char in enumerate(encoded_text):
            code_point = ord(char)
            if UnicodeMetadata.VARIATION_SELECTOR_START <= code_point <= UnicodeMetadata.VARIATION_SELECTOR_END:
                # Replace this variation selector with a different one
                corrupted_text = encoded_text[:i] + chr(code_point + 1) + encoded_text[i + 1 :]
                break
            elif UnicodeMetadata.VARIATION_SELECTOR_SUPPLEMENT_START <= code_point <= UnicodeMetadata.VARIATION_SELECTOR_SUPPLEMENT_END:
                # Replace this variation selector with a different one
                corrupted_text = encoded_text[:i] + chr(code_point + 1) + encoded_text[i + 1 :]
                break
        else:
            # If no variation selectors found, just append an invalid one
            corrupted_text = encoded_text + chr(UnicodeMetadata.VARIATION_SELECTOR_START)

        # Verify the corrupted text
        is_valid, extracted_signer_id, extracted_payload = UnicodeMetadata.verify_metadata(corrupted_text, public_key_provider)

        assert not is_valid
        assert extracted_payload is None

    def test_verify_failure_unknown_signer_id(
        self,
        key_pair_1,
        sample_text,
        public_key_provider,
    ):
        """Test verification failure when signer_id is unknown to the provider."""
        private_key, _ = key_pair_1
        signer_id = "signer_unknown"  # This ID is not in the provider map

        encoded_text = UnicodeMetadata.embed_metadata(
            text=sample_text,
            private_key=private_key,
            signer_id=signer_id,
            metadata_format="basic",
            model_id="unknown_signer_test",
            timestamp=datetime.now(timezone.utc).isoformat(),
            target=MetadataTarget.PUNCTUATION,  # Use punctuation
        )

        # Verification should fail as provider returns None
        is_valid, extracted_signer_id, extracted_payload = UnicodeMetadata.verify_metadata(encoded_text, public_key_provider)

        assert not is_valid
        assert extracted_payload is None

    def test_verify_failure_key_mismatch(self, key_pair_1, sample_text):
        """Test verification failure when provider returns wrong key type."""
        private_key, public_key = key_pair_1  # Correctly unpack public_key
        signer_id = "signer_1"
        encoded_text = UnicodeMetadata.embed_metadata(
            text=sample_text,
            private_key=private_key,
            signer_id=signer_id,
            metadata_format="basic",
            model_id="key_mismatch_test",
            timestamp=datetime.now(timezone.utc).isoformat(),
            target=MetadataTarget.PUNCTUATION,  # Use punctuation
        )

        # Provider returns a private key instead of public
        def wrong_key_provider(s_id: str) -> Optional[PublicKeyTypes]:
            if s_id == "signer_1":
                return cast(PublicKeyTypes, private_key)  # Return private key for signer 1
            return None  # Original for others

        is_valid, extracted_signer_id, extracted_payload = UnicodeMetadata.verify_metadata(encoded_text, wrong_key_provider)

        assert not is_valid
        assert extracted_payload is None

    def test_verify_failure_provider_error(self, key_pair_1, sample_text):
        """Test verification failure when provider raises an exception."""
        private_key, _ = key_pair_1
        signer_id = "signer_1"
        encoded_text = UnicodeMetadata.embed_metadata(
            text=sample_text,
            private_key=private_key,
            signer_id=signer_id,
            metadata_format="basic",
            model_id="provider_error_test",
            timestamp=datetime.now(timezone.utc).isoformat(),
            target=MetadataTarget.PUNCTUATION,  # Use punctuation
        )

        # Provider raises an error
        def error_provider(s_id: str) -> Optional[PublicKeyTypes]:
            raise Exception("Mock provider error")

        is_valid, extracted_signer_id, extracted_payload = UnicodeMetadata.verify_metadata(encoded_text, error_provider)

        assert not is_valid
        assert extracted_payload is None

    def test_unicode_metadata_extract_metadata(self, sample_text, basic_metadata, key_pair_1):
        """Test extracting metadata without verification."""
        private_key, public_key = key_pair_1
        signer_id_to_use = "test-key-1"
        # Ensure timestamp is in basic_metadata fixture before using it
        if "timestamp" not in basic_metadata:
            basic_metadata["timestamp"] = datetime.now(timezone.utc).isoformat()
        metadata_to_embed = basic_metadata  # Use the basic_metadata fixture directly

        # Embed metadata - Corrected call
        encoded_text = UnicodeMetadata.embed_metadata(
            text=sample_text,
            private_key=private_key,
            signer_id=signer_id_to_use,  # Pass the signer_id
            metadata_format="basic",  # Specify format
            target=MetadataTarget.WHITESPACE,
            **metadata_to_embed,  # Unpack the metadata dictionary
        )

        # Extract metadata
        extracted_metadata = UnicodeMetadata.extract_metadata(encoded_text)
        assert extracted_metadata is not None, "Metadata should be extracted"
        # Check some key metadata fields (excluding signature/key_id if not needed)
        # Compare against metadata_to_embed
        assert extracted_metadata.get("model_id") == metadata_to_embed.get("model_id")
        assert extracted_metadata.get("timestamp") is not None  # Just check presence
        assert extracted_metadata.get("custom_metadata") == metadata_to_embed.get("custom_metadata")

    def test_unicode_metadata_extract_metadata_no_metadata(self, sample_text):
        """Test extracting metadata when none is present."""
        extracted_metadata = UnicodeMetadata.extract_metadata(sample_text)
        assert extracted_metadata is None, "Should return None when no metadata is embedded"

    def test_unicode_metadata_extract_metadata_corrupted(self, sample_text, basic_metadata, key_pair_1):
        """Test extracting metadata when the embedded data is corrupted."""
        private_key, public_key = key_pair_1
        signer_id_to_use = "test-key-1"

        # Ensure timestamp is included in the metadata
        metadata_to_embed = {**basic_metadata}
        if "timestamp" not in metadata_to_embed:
            metadata_to_embed["timestamp"] = datetime.now(timezone.utc).isoformat()

        # Embed metadata
        encoded_text = UnicodeMetadata.embed_metadata(
            text=sample_text,
            private_key=private_key,
            signer_id=signer_id_to_use,
            metadata_format="basic",
            target=MetadataTarget.WHITESPACE,
            **metadata_to_embed,
        )

        # Create corrupted text by replacing some characters
        # This will corrupt any embedded variation selectors
        corrupted_text = ""
        for i, char in enumerate(encoded_text):
            # Replace every 10th character to corrupt the data
            if i % 10 == 0 and i > 0:
                corrupted_text += "X"
            else:
                corrupted_text += char

        # Try to extract metadata from the corrupted text
        extracted_metadata = UnicodeMetadata.extract_metadata(corrupted_text)
        assert extracted_metadata is None, "Should return None for corrupted data"

    def test_unicode_metadata_verify_with_manifest(self, manifest_metadata, key_pair_1, sample_text, public_key_provider):
        """Test verification with manifest metadata."""
        private_key, public_key = key_pair_1
        signer_id = "signer_1"

        encoded_text = UnicodeMetadata.embed_metadata(
            text=sample_text,
            private_key=private_key,
            signer_id=signer_id,
            metadata_format="manifest",
            **manifest_metadata,
        )

        # Verify the encoded text
        is_valid, extracted_signer_id, extracted_payload = UnicodeMetadata.verify_metadata(encoded_text, public_key_provider)

        assert is_valid
        assert extracted_signer_id == signer_id
        assert extracted_payload is not None
        assert extracted_payload.get("format") == "manifest"
        # Access nested manifest fields
        manifest_payload = extracted_payload.get("manifest", {})
        assert manifest_payload.get("claim_generator") == manifest_metadata.get("claim_generator")
        assert manifest_payload.get("actions") == manifest_metadata.get("actions")
        assert manifest_payload.get("ai_info") == manifest_metadata.get("ai_info")
        assert manifest_payload.get("custom_claims") == manifest_metadata.get("custom_claims")

    def test_embed_metadata_omit_keys(self, key_pair_1, sample_text, public_key_provider):
        private_key, _ = key_pair_1
        signer_id = "signer_1"
        metadata = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "custom_metadata": {
                "user_id": "abc",
                "session_id": "123",
                "keep": True,
            },
        }

        embedded_text = UnicodeMetadata.embed_metadata(
            text=sample_text,
            private_key=private_key,
            signer_id=signer_id,
            metadata_format="basic",
            target=MetadataTarget.PUNCTUATION,
            omit_keys=["user_id", "session_id"],
            **metadata,
        )

        is_valid, extracted_signer_id, payload = UnicodeMetadata.verify_metadata(embedded_text, public_key_provider)

        assert is_valid
        assert extracted_signer_id == signer_id
        assert payload is not None
        custom_meta = payload.get("custom_metadata", {})
        assert "user_id" not in custom_meta
        assert "session_id" not in custom_meta

    @pytest.mark.skip(reason=("Test based on old embed_metadata signature (HMAC), incompatible " "with new signature-based method."))
    def test_embed_extract_metadata(self):
        pass

    @pytest.mark.skip(reason=("Test based on old embed_metadata signature (HMAC), incompatible " "with new signature-based method."))
    def test_custom_metadata(self):
        pass

    @pytest.mark.skip(reason=("Test based on old embed_metadata signature (HMAC), incompatible " "with new signature-based method."))
    def test_no_metadata_target(self):
        pass

    @pytest.mark.skip(reason=("Test based on old embed_metadata signature (HMAC), incompatible " "with new signature-based method."))
    def test_datetime_timestamp(self):
        pass

    @pytest.fixture
    def sample_text(self) -> str:
        """Provides a much longer sample text with abundant targets for embedding metadata."""
        # This text needs to be significantly long and varied to ensure enough targets
        # of both whitespace and punctuation types for ~500 bytes of payload.
        # Let's add multiple paragraphs and different styles.
        paragraph1 = (
            "This is the first paragraph of a substantially longer sample text document, meticulously crafted for testing metadata embedding procedures. "
            "Our primary objective is to guarantee a sufficient quantity of 'target' characters—such as spaces, commas, periods, newlines (though maybe not embeddable), question marks, exclamation points, and semicolons—within this block. "
            "These targets are essential for successfully embedding the necessary metadata payload. This payload encompasses not merely the original data but also a robust cryptographic signature and associated signer identification. Punctuation, indeed, helps significantly! "
            "Consider these numbers: 123, 45.67, -890. Is variability not the spice of life? Yes! Yes, it is! "
        )
        paragraph2 = (
            "Moving to the second paragraph, we explore the intricacies of the embedding process itself. It involves meticulously scanning the text to identify suitable locations (the aforementioned targets). "
            "Once identified, the compressed and serialized metadata payload is encoded using specific Unicode variation selectors or similar techniques. Then, it's subtly inserted into the text at these target locations. "
            "The key is to make these insertions minimally disruptive to the original text's appearance and flow. Think about that; it's quite clever, right? What about a list? Item 1; Item 2; Item 3. "
        )
        paragraph3 = (
            "Finally, the third paragraph focuses on the verification stage. This critical step involves extracting the embedded bytes from their hidden locations within the text. "
            "The extracted bytes are then decoded, decompressed, and deserialized to reconstruct the original payload structure. The most crucial part follows: checking the cryptographic signature. "
            "This involves using the public key associated with the claimed signer ID (retrieved from a trusted provider) to validate the signature against the reconstructed payload data. If they match, the metadata is authentic! "
            "We sincerely hope this greatly extended version provides more than ample space for all test cases. Let's add one more: 987-654-3210. Success? We hope so..."  # noqa: E501
        )
        return f"{paragraph1}\n\n{paragraph2}\n\n{paragraph3}"  # noqa: E501
