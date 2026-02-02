"""
Integration tests for C2PA compliance.

This module tests the end-to-end functionality of C2PA compliant
embedding, extraction, and verification.
"""

import os
import tempfile
import unittest
import uuid
from datetime import datetime, timezone
from typing import Optional, cast

from cryptography.hazmat.primitives.asymmetric import ed25519

from encypher.core.payloads import C2PAPayload, deserialize_c2pa_payload_from_cbor, serialize_c2pa_payload_to_cbor
from encypher.core.signing import TrustStore
from encypher.core.unicode_metadata import UnicodeMetadata
from encypher.interop.c2pa import encypher_manifest_to_c2pa_like_dict


class TestC2PAIntegration(unittest.TestCase):
    """Test cases for C2PA compliance integration."""

    def setUp(self):
        """Set up test fixtures."""
        # Generate a key pair for testing
        self.private_key = ed25519.Ed25519PrivateKey.generate()
        self.public_key = self.private_key.public_key()
        self.signer_id = "test-signer-id"

        # Sample text content
        self.test_text = "This is a test text for C2PA compliance testing."

        # Sample timestamp for consistent testing
        self.timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        # Sample actions for the manifest
        self.actions = [
            {
                "label": "c2pa.created",
                "when": self.timestamp,
                "digitalSourceType": "http://cv.iptc.org/newscodes/digitalsourcetype/trainedAlgorithmicMedia",
                "softwareAgent": "EncypherAI/2.4.0",
            },
            {
                "label": "c2pa.edited",
                "when": self.timestamp,
                "softwareAgent": "EncypherAI/2.4.0",
                "description": "Text content edited",
            },
        ]

        # Create a temporary directory for trust store
        self.temp_dir = tempfile.TemporaryDirectory()
        self.trust_store_path = os.path.join(self.temp_dir.name, "trust_store")
        os.makedirs(self.trust_store_path, exist_ok=True)
        self.trust_store = TrustStore(self.trust_store_path)

    def tearDown(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()

    def test_c2pa_embedding_and_extraction(self):
        """Test embedding and extracting C2PA compliant metadata."""
        # Embed metadata with C2PA format
        embedded_text = UnicodeMetadata.embed_metadata(
            text=self.test_text,
            private_key=self.private_key,
            signer_id=self.signer_id,
            metadata_format="c2pa",
            timestamp=self.timestamp,
            actions=self.actions,
            claim_generator="EncypherAI/2.4.0",
        )

        # Verify text is modified but content is preserved
        self.assertNotEqual(embedded_text, self.test_text)
        self.assertTrue(self.test_text in embedded_text)

        # Extract metadata without verification
        extracted_payload = UnicodeMetadata.extract_metadata(embedded_text)

        # Check that we got a payload
        self.assertIsNotNone(extracted_payload)

        # Verify it's a C2PA payload
        self.assertIn("@context", extracted_payload)
        self.assertIn("instance_id", extracted_payload)
        self.assertIn("claim_generator", extracted_payload)
        self.assertIn("assertions", extracted_payload)

        # Check required assertions are present
        assertion_labels = {a.get("label") for a in extracted_payload.get("assertions", [])}
        self.assertIn("c2pa.actions.v2", assertion_labels)
        self.assertIn("c2pa.actions.v1", assertion_labels)
        self.assertIn("c2pa.hash.data.v1", assertion_labels)
        self.assertIn("c2pa.soft_binding.v1", assertion_labels)

    def test_c2pa_verification(self):
        """Test verification of C2PA compliant metadata."""
        # Embed metadata with C2PA format
        embedded_text = UnicodeMetadata.embed_metadata(
            text=self.test_text,
            private_key=self.private_key,
            signer_id=self.signer_id,
            metadata_format="c2pa",
            timestamp=self.timestamp,
            actions=self.actions,
            claim_generator="EncypherAI/2.4.0",
        )

        # Define a public key resolver function
        def public_key_resolver(signer_id: str) -> Optional[ed25519.Ed25519PublicKey]:
            if signer_id == self.signer_id:
                return cast(ed25519.Ed25519PublicKey, self.public_key)
            return None

        # Verify the metadata
        is_verified, extracted_signer_id, payload = UnicodeMetadata.verify_metadata(embedded_text, public_key_resolver)

        # Check verification results
        self.assertTrue(is_verified)
        self.assertEqual(extracted_signer_id, self.signer_id)
        self.assertIsNotNone(payload)

        # Verify with wrong public key
        wrong_public_key = ed25519.Ed25519PrivateKey.generate().public_key()

        def wrong_key_resolver(signer_id: str) -> Optional[ed25519.Ed25519PublicKey]:
            return cast(ed25519.Ed25519PublicKey, wrong_public_key)

        is_verified, _, _ = UnicodeMetadata.verify_metadata(embedded_text, wrong_key_resolver)
        self.assertFalse(is_verified)

    def test_c2pa_tamper_detection(self):
        """Test tamper detection for C2PA compliant metadata."""
        # Embed metadata with C2PA format
        embedded_text = UnicodeMetadata.embed_metadata(
            text=self.test_text,
            private_key=self.private_key,
            signer_id=self.signer_id,
            metadata_format="c2pa",
            timestamp=self.timestamp,
            actions=self.actions,
            claim_generator="EncypherAI/2.4.0",
        )

        # Tamper with the text content
        tampered_text = embedded_text.replace("test text", "modified text")

        # Define a public key resolver function
        def public_key_resolver(signer_id: str) -> Optional[ed25519.Ed25519PublicKey]:
            if signer_id == self.signer_id:
                return cast(ed25519.Ed25519PublicKey, self.public_key)
            return None

        # Verify the tampered text
        is_verified, _, _ = UnicodeMetadata.verify_metadata(tampered_text, public_key_resolver)

        # Verification should fail due to content hash mismatch
        self.assertFalse(is_verified)

    def test_c2pa_soft_binding(self):
        """Test soft binding functionality for C2PA."""
        # Create a manifest with embedded data for soft binding
        embedded_data = "Unicode variation selector soft binding test data"

        # Convert to C2PA-like dict with soft binding
        c2pa_dict = encypher_manifest_to_c2pa_like_dict(
            {
                "claim_generator": "EncypherAI/2.4.0",
                "assertions": self.actions,
                "timestamp": self.timestamp,
            },
            content_text=self.test_text,
            embedded_data=embedded_data,
        )

        # Check soft binding assertion is present
        soft_binding_assertion = next((a for a in c2pa_dict["assertions"] if a["label"] == "c2pa.soft_binding.v1"), None)
        self.assertIsNotNone(soft_binding_assertion)
        self.assertEqual(soft_binding_assertion["data"]["alg"], "encypher.unicode_variation_selector.v1")

        # Check watermarked action is present
        actions_assertion = next((a for a in c2pa_dict["assertions"] if a["label"] == "c2pa.actions.v1"), None)
        self.assertIsNotNone(actions_assertion, "c2pa.actions.v1 assertion not found in manifest")

        # Only check for watermarked action if actions assertion exists
        if actions_assertion is not None:
            watermarked_action = next((a for a in actions_assertion["data"]["actions"] if a["action"] == "c2pa.watermarked"), None)
            self.assertIsNotNone(watermarked_action, "c2pa.watermarked action not found in actions assertion")
        self.assertTrue(any(ref.get("type") == "resourceRef" for ref in watermarked_action["references"]))

    def test_cbor_serialization(self):
        """Test CBOR serialization and deserialization for C2PA payloads."""
        # Create a sample C2PA payload
        c2pa_payload: C2PAPayload = {
            "@context": "https://c2pa.org/schemas/v2.2/c2pa.jsonld",
            "instance_id": str(uuid.uuid4()),
            "claim_generator": "EncypherAI/2.4.0",
            "assertions": [
                {
                    "label": "c2pa.actions.v1",
                    "data": {"actions": self.actions},
                    "kind": "Actions",
                }
            ],
        }

        # Serialize to CBOR
        cbor_bytes = serialize_c2pa_payload_to_cbor(c2pa_payload)
        self.assertIsInstance(cbor_bytes, bytes)

        # Deserialize from CBOR
        deserialized_payload = deserialize_c2pa_payload_from_cbor(cbor_bytes)

        # Check deserialized payload matches original
        self.assertEqual(deserialized_payload["@context"], c2pa_payload["@context"])
        self.assertEqual(deserialized_payload["instance_id"], c2pa_payload["instance_id"])
        self.assertEqual(deserialized_payload["claim_generator"], c2pa_payload["claim_generator"])
        self.assertEqual(len(deserialized_payload["assertions"]), len(c2pa_payload["assertions"]))


if __name__ == "__main__":
    unittest.main()
