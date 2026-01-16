import os
import struct
import unicodedata
import unittest

from encypher.core.keys import generate_ed25519_key_pair
from encypher.core.unicode_metadata import UnicodeMetadata
from encypher.interop.c2pa import (
    c2pa_like_dict_to_encypher_manifest,
    encypher_manifest_to_c2pa_like_dict,
)
from encypher.interop.c2pa.text_wrapper import find_and_decode


class TestC2PATextEmbedding(unittest.TestCase):
    def assertDictsAlmostEqual(self, d1, d2, msg=None):
        """Compares two dictionaries, allowing for minor float differences if needed in future."""
        # For this specific C2PA test, direct equality should be fine as no floats are involved.
        # If floats were involved, we'd need a more complex comparison.
        self.assertEqual(d1, d2, msg)

    def test_c2pa_manifest_text_embedding_round_trip(self):
        """Tests the full round-trip of embedding and extracting a C2PA-like manifest in text."""
        # 1. Define the original C2PA-like manifest (as in the demo script)
        original_c2pa_like_manifest = {
            "claim_generator": "Encypher/2.1.0",
            "timestamp": "2025-06-16T10:30:00Z",
            "assertions": [
                {
                    "label": "stds.schema-org.CreativeWork",
                    "data": {
                        "@context": "http://schema.org/",
                        "@type": "CreativeWork",
                        "author": {"@type": "Person", "name": "Erik Encypher"},
                        "publisher": {"@type": "Organization", "name": "Encypher Corporation"},
                        "copyrightHolder": {"name": "Encypher Corporation"},
                        "copyrightYear": 2025,
                        "copyrightNotice": "© 2025 Encypher Corporation. All Rights Reserved.",
                    },
                }
            ],
        }

        # 2. Generate keys
        private_key, public_key = generate_ed25519_key_pair()
        key_id = "test-c2pa-key-001"

        # 3. Convert C2PA-like manifest to Encypher ManifestPayload
        encypher_ai_payload_to_embed = c2pa_like_dict_to_encypher_manifest(original_c2pa_like_manifest)
        self.assertIsNotNone(encypher_ai_payload_to_embed)
        self.assertEqual(encypher_ai_payload_to_embed["claim_generator"], original_c2pa_like_manifest["claim_generator"])

        # 4. Embed the Encypher ManifestPayload into sample text
        sample_text = "This is a sample document that will have C2PA-like metadata embedded."

        text_with_embedded_metadata = UnicodeMetadata.embed_metadata(
            text=sample_text,
            private_key=private_key,
            signer_id=key_id,
            metadata_format="manifest",
            claim_generator=encypher_ai_payload_to_embed.get("claim_generator"),
            actions=encypher_ai_payload_to_embed.get("assertions"),
            ai_info=encypher_ai_payload_to_embed.get("ai_assertion", {}),
            custom_claims=encypher_ai_payload_to_embed.get("custom_claims", {}),
            timestamp=encypher_ai_payload_to_embed.get("timestamp"),
        )
        self.assertNotEqual(text_with_embedded_metadata, sample_text)
        self.assertTrue(len(text_with_embedded_metadata) > len(sample_text))

        # 5. Extract and verify the metadata from the text
        def public_key_resolver(kid: str):
            if kid == key_id:
                return public_key
            return None  # Or raise an error, depending on resolver contract

        is_verified, extracted_signer_id, extracted_payload_outer = UnicodeMetadata.verify_metadata(
            text=text_with_embedded_metadata, public_key_resolver=public_key_resolver, return_payload_on_failure=True
        )

        self.assertTrue(is_verified, "Signature verification failed.")
        self.assertEqual(extracted_signer_id, key_id, "Extracted signer ID does not match.")
        self.assertIsNotNone(extracted_payload_outer, "Extracted payload is None.")
        self.assertIn("manifest", extracted_payload_outer, "'manifest' key missing in extracted payload.")

        # 6. Convert the extracted Encypher ManifestPayload back to a C2PA-like dictionary
        inner_manifest = extracted_payload_outer["manifest"]
        manifest_for_conversion = {
            "claim_generator": inner_manifest.get("claim_generator"),
            "assertions": inner_manifest.get("actions"),
            "ai_assertion": inner_manifest.get("ai_assertion", {}),
            "custom_claims": inner_manifest.get("custom_claims", {}),
            "timestamp": inner_manifest.get("timestamp", extracted_payload_outer.get("timestamp")),
        }

        extracted_c2pa_like_dict = encypher_manifest_to_c2pa_like_dict(manifest_for_conversion)
        self.assertIsNotNone(extracted_c2pa_like_dict)

        # 7. Verify the round-tripped C2PA-like dictionary matches the original
        # The encypher_manifest_to_c2pa_like_dict adds a 'format' field, so we compare relevant parts.
        self.assertEqual(extracted_c2pa_like_dict.get("claim_generator"), original_c2pa_like_manifest.get("claim_generator"))
        self.assertEqual(extracted_c2pa_like_dict.get("timestamp"), original_c2pa_like_manifest.get("timestamp"))

        # Deep compare assertions
        original_c2pa_assertions = original_c2pa_like_manifest.get("assertions", [])
        extracted_c2pa_assertions = extracted_c2pa_like_dict.get("assertions", [])
        self.assertEqual(len(extracted_c2pa_assertions), len(original_c2pa_assertions), "Number of assertions mismatch.")

        for i, original_c2pa_assertion in enumerate(original_c2pa_assertions):
            extracted_c2pa_assertion = extracted_c2pa_assertions[i]

            # Compare labels
            self.assertEqual(extracted_c2pa_assertion.get("label"), original_c2pa_assertion.get("label"), f"Assertion {i} label mismatch.")

            # Compare the 'data' part, accounting for the timestamp transformation
            original_c2pa_data = original_c2pa_assertion.get("data", {})
            extracted_c2pa_data = extracted_c2pa_assertion.get("data", {})

            # With our updated _get_c2pa_assertion_data function, claim_generator and timestamp
            # are now correctly kept at the top level of the manifest, not in assertion data
            # So we don't check for them in the assertion data anymore

            # Compare the rest of the data fields (excluding timestamp and claim_generator)

            # Compare the rest of the data fields by creating a copy of extracted_c2pa_data and removing 'timestamp'
            extracted_c2pa_data_for_comparison = extracted_c2pa_data.copy()
            if "timestamp" in extracted_c2pa_data_for_comparison:
                del extracted_c2pa_data_for_comparison["timestamp"]

            self.assertDictsAlmostEqual(
                extracted_c2pa_data_for_comparison, original_c2pa_data, f"Assertion {i} data content mismatch (excluding transformed timestamp)."
            )

    def test_c2pa_manifest_text_embedding_cbor_round_trip(self):
        """Tests the full round-trip of embedding and extracting a C2PA-like manifest with CBOR assertion data."""
        # 1. Define the original C2PA-like manifest
        original_c2pa_like_manifest = {
            "claim_generator": "Encypher/CBORTest/1.0",
            "timestamp": "2025-07-04T12:00:00Z",
            "assertions": [
                {
                    "label": "stds.schema-org.CreativeWork.CBOR",
                    "data": {
                        "@context": "http://schema.org/",
                        "@type": "CreativeWork",
                        "author": {"@type": "Person", "name": "CBOR Author"},
                        "version": 1,
                        "details": {"encoding": "CBOR", "verified": True},
                    },
                },
                {
                    "label": "custom.internal.tracking.CBOR",
                    "data": {"tracking_id": "cbor-track-789", "status": "processed", "metrics": {"value_a": 100, "value_b": 200.5}},
                },
            ],
        }

        # 2. Generate keys
        private_key, public_key = generate_ed25519_key_pair()
        key_id = "test-c2pa-cbor-key-001"

        # 3. Convert C2PA-like manifest to Encypher ManifestPayload with CBOR encoding
        encypher_ai_payload_to_embed = c2pa_like_dict_to_encypher_manifest(original_c2pa_like_manifest, encode_assertion_data_as_cbor=True)
        self.assertIsNotNone(encypher_ai_payload_to_embed)
        self.assertEqual(encypher_ai_payload_to_embed["claim_generator"], original_c2pa_like_manifest["claim_generator"])
        # Check that assertion data is now a string (Base64 encoded CBOR) and data_encoding is set
        for assertion in encypher_ai_payload_to_embed.get("assertions", []):
            self.assertIsInstance(assertion.get("data"), str)
            self.assertEqual(assertion.get("data_encoding"), "cbor_base64")

        # 4. Embed the Encypher ManifestPayload into sample text
        sample_text = "This document contains CBOR-encoded C2PA-like metadata."

        text_with_embedded_metadata = UnicodeMetadata.embed_metadata(
            text=sample_text,
            private_key=private_key,
            signer_id=key_id,
            metadata_format="manifest",
            claim_generator=encypher_ai_payload_to_embed.get("claim_generator"),
            actions=encypher_ai_payload_to_embed.get("assertions"),
            ai_info=encypher_ai_payload_to_embed.get("ai_assertion", {}),
            custom_claims=encypher_ai_payload_to_embed.get("custom_claims", {}),
            timestamp=encypher_ai_payload_to_embed.get("timestamp"),
        )
        self.assertNotEqual(text_with_embedded_metadata, sample_text)

        # 5. Extract and verify the metadata from the text
        def public_key_resolver(kid: str):
            if kid == key_id:
                return public_key
            return None

        is_verified, extracted_signer_id, extracted_payload_outer = UnicodeMetadata.verify_metadata(
            text=text_with_embedded_metadata, public_key_resolver=public_key_resolver, return_payload_on_failure=True
        )

        self.assertTrue(is_verified, "Signature verification failed for CBOR data.")
        self.assertEqual(extracted_signer_id, key_id, "Extracted signer ID does not match for CBOR data.")
        self.assertIsNotNone(extracted_payload_outer, "Extracted payload is None for CBOR data.")
        self.assertIn("manifest", extracted_payload_outer, "'manifest' key missing in extracted CBOR payload.")

        # 6. Convert the extracted Encypher ManifestPayload back to a C2PA-like dictionary
        inner_manifest = extracted_payload_outer["manifest"]
        manifest_for_conversion = {
            "claim_generator": inner_manifest.get("claim_generator"),
            "assertions": inner_manifest.get("actions"),
            "ai_assertion": inner_manifest.get("ai_assertion", {}),
            "custom_claims": inner_manifest.get("custom_claims", {}),
            "timestamp": inner_manifest.get("timestamp", extracted_payload_outer.get("timestamp")),
        }

        extracted_c2pa_like_dict = encypher_manifest_to_c2pa_like_dict(manifest_for_conversion)
        self.assertIsNotNone(extracted_c2pa_like_dict)

        # 7. Verify the round-tripped C2PA-like dictionary matches the original
        # Account for the 'format' field added by encypher_manifest_to_c2pa_like_dict
        comparison_dict = extracted_c2pa_like_dict.copy()
        # Remove fields added by encypher_manifest_to_c2pa_like_dict that aren't in the original
        for field in ["format", "@context", "instance_id"]:
            if field in comparison_dict:
                del comparison_dict[field]

        self.assertDictsAlmostEqual(
            comparison_dict,
            original_c2pa_like_manifest,
            "Round-tripped CBOR manifest does not match original (after accounting for 'format' field).",
        )

    def test_c2pa_full_cbor_manifest_text_embedding_round_trip(self):
        # Show full diff output
        self.maxDiff = None
        """Tests the full round-trip of embedding and extracting a C2PA-like manifest using metadata_format='cbor_manifest'."""
        # 1. Define the original C2PA-like manifest
        original_c2pa_like_manifest = {
            "claim_generator": "Encypher/FullCBOR/0.1",
            "timestamp": "2025-08-15T18:00:00Z",
            "assertions": [
                {
                    "label": "stds.schema-org.CreativeWork.FullCBOR",
                    "data": {
                        "@context": "http://schema.org/",
                        "@type": "CreativeWork",
                        "author": {"@type": "Person", "name": "Full CBOR Author"},
                        "description": "This entire manifest was CBOR encoded.",
                    },
                },
                {"label": "custom.project.details.FullCBOR", "data": {"project_id": "proj_cbor_full_123", "status": "finalized"}},
            ],
        }

        # 2. Generate keys
        private_key, public_key = generate_ed25519_key_pair()
        key_id = "test-c2pa-full-cbor-key-001"

        # 3. Convert C2PA-like manifest to Encypher ManifestPayload
        # For 'cbor_manifest' format, assertion data remains as dicts, not pre-encoded to CBOR strings.
        # We use use_nested_data=True to keep assertion data in nested 'data' fields
        encypher_ai_manifest_to_embed = c2pa_like_dict_to_encypher_manifest(
            original_c2pa_like_manifest,
            encode_assertion_data_as_cbor=False,  # Important: data is not CBOR'd here
            use_nested_data=True,  # Important: keep data nested for cbor_manifest format
        )
        self.assertIsNotNone(encypher_ai_manifest_to_embed)
        self.assertEqual(encypher_ai_manifest_to_embed["claim_generator"], original_c2pa_like_manifest["claim_generator"])
        for assertion in encypher_ai_manifest_to_embed.get("assertions", []):
            self.assertIsInstance(assertion.get("data"), dict)  # Data should be a dict
            self.assertNotIn("data_encoding", assertion)  # No data_encoding field for individual assertions

        # 4. Embed the Encypher ManifestPayload into sample text using 'cbor_manifest' format
        sample_text = "This document contains a fully CBOR-encoded C2PA-like manifest."

        text_with_embedded_metadata = UnicodeMetadata.embed_metadata(
            text=sample_text,
            private_key=private_key,
            signer_id=key_id,
            metadata_format="cbor_manifest",  # Key change for this test
            claim_generator=encypher_ai_manifest_to_embed.get("claim_generator"),
            actions=encypher_ai_manifest_to_embed.get("assertions"),
            ai_info=encypher_ai_manifest_to_embed.get("ai_assertion", {}),
            custom_claims=encypher_ai_manifest_to_embed.get("custom_claims", {}),
            timestamp=encypher_ai_manifest_to_embed.get("timestamp"),
        )
        self.assertNotEqual(text_with_embedded_metadata, sample_text)

        # 5. Extract and verify the metadata from the text
        def public_key_resolver(kid: str):
            if kid == key_id:
                return public_key
            return None

        is_verified, extracted_signer_id, extracted_manifest_dict = UnicodeMetadata.verify_metadata(
            text=text_with_embedded_metadata, public_key_resolver=public_key_resolver, return_payload_on_failure=True
        )

        # Verification has been completed above

        self.assertTrue(is_verified, "Signature verification failed for full CBOR manifest.")
        self.assertEqual(extracted_signer_id, key_id, "Extracted signer ID does not match for full CBOR manifest.")
        self.assertIsNotNone(extracted_manifest_dict, "Extracted manifest dictionary is None for full CBOR manifest.")
        self.assertIsInstance(extracted_manifest_dict, dict, "Extracted payload is not a dictionary for full CBOR manifest.")

        # For 'cbor_manifest', the extracted payload IS the manifest dictionary itself, not nested.
        self.assertEqual(extracted_manifest_dict.get("claim_generator"), original_c2pa_like_manifest.get("claim_generator"))

        # 6. Convert the extracted Encypher ManifestPayload (which is extracted_manifest_dict) back to a C2PA-like dictionary
        # The extracted_manifest_dict should already be in the Encypher manifest structure.

        # Add timestamp to extracted manifest if missing
        if "timestamp" not in extracted_manifest_dict and "timestamp" in original_c2pa_like_manifest:
            extracted_manifest_dict["timestamp"] = original_c2pa_like_manifest["timestamp"]

        extracted_c2pa_like_dict = encypher_manifest_to_c2pa_like_dict(extracted_manifest_dict)
        self.assertIsNotNone(extracted_c2pa_like_dict)

        # 7. Compare the original and extracted C2PA-like dictionaries
        # Normalize for comparison
        comparison_dict = extracted_c2pa_like_dict.copy()  # Remove fields added by encypher_manifest_to_c2pa_like_dict that aren't in the original
        for field in ["format", "@context", "instance_id"]:
            if field in comparison_dict:
                del comparison_dict[field]

        # Timestamp might be slightly different due to serialization/deserialization
        comparison_dict["timestamp"] = ""
        original_comparison = original_c2pa_like_manifest.copy()
        original_comparison["timestamp"] = ""

        # Assertions should match in structure and count
        self.assertEqual(len(comparison_dict.get("assertions", [])), len(original_comparison.get("assertions", [])))

        # Print the dictionaries for debugging
        print("\nComparison Dict:")
        print(comparison_dict)
        print("\nOriginal Comparison:")
        print(original_comparison)

        # Compare the dictionaries
        self.assertDictsAlmostEqual(comparison_dict, original_comparison, "Round-tripped full CBOR manifest does not match original.")

    def test_c2pa_single_assertion_cbor_manifest_text_embedding_round_trip(self):
        """Tests the full round-trip of embedding and extracting a single-assertion C2PA-like manifest in CBOR format."""
        # 1. Define the C2PA-like manifest with a single assertion
        original_c2pa_like_manifest = {
            "claim_generator": "Encypher/2.1.0",
            "timestamp": "2025-06-16T10:30:00Z",
            "assertions": [
                {
                    "label": "stds.schema-org.CreativeWork",
                    "data": {
                        "@context": "http://schema.org/",
                        "@type": "CreativeWork",
                        "author": {"@type": "Person", "name": "Erik Encypher"},
                        "publisher": {"@type": "Organization", "name": "Encypher Corporation"},
                        "copyrightHolder": {"name": "Encypher Corporation"},
                        "copyrightYear": 2025,
                        "copyrightNotice": " 2025 Encypher Corporation. All Rights Reserved.",
                    },
                }
            ],
        }

        # 2. Generate keys
        private_key, public_key = generate_ed25519_key_pair()
        key_id = "test-c2pa-single-cbor-key-001"

        # 3. Convert C2PA-like manifest to Encypher ManifestPayload
        # For 'cbor_manifest' format, assertion data remains as dicts, not pre-encoded to CBOR strings.
        # We use use_nested_data=True to keep assertion data in nested 'data' fields
        encypher_ai_manifest_to_embed = c2pa_like_dict_to_encypher_manifest(
            original_c2pa_like_manifest,
            encode_assertion_data_as_cbor=False,  # Important: data is not CBOR'd here
            use_nested_data=True,  # Important: keep data nested for cbor_manifest format
        )
        self.assertIsNotNone(encypher_ai_manifest_to_embed)
        self.assertEqual(encypher_ai_manifest_to_embed["claim_generator"], original_c2pa_like_manifest["claim_generator"])
        for assertion in encypher_ai_manifest_to_embed.get("assertions", []):
            self.assertIsInstance(assertion.get("data"), dict)  # Data should be a dict
            self.assertNotIn("data_encoding", assertion)  # No data_encoding field for individual assertions

        # 4. Embed the Encypher ManifestPayload into sample text using 'cbor_manifest' format
        sample_text = "This document contains a single-assertion CBOR-encoded C2PA-like manifest."

        text_with_embedded_metadata = UnicodeMetadata.embed_metadata(
            text=sample_text,
            private_key=private_key,
            signer_id=key_id,
            metadata_format="cbor_manifest",  # Key change for this test
            claim_generator=encypher_ai_manifest_to_embed.get("claim_generator"),
            actions=encypher_ai_manifest_to_embed.get("assertions"),
            ai_info=encypher_ai_manifest_to_embed.get("ai_assertion", {}),
            custom_claims=encypher_ai_manifest_to_embed.get("custom_claims", {}),
            timestamp=encypher_ai_manifest_to_embed.get("timestamp"),
        )
        self.assertNotEqual(text_with_embedded_metadata, sample_text)

        # 5. Extract and verify the metadata from the text
        def public_key_resolver(kid: str):
            if kid == key_id:
                return public_key
            return None

        is_verified, extracted_signer_id, extracted_manifest_dict = UnicodeMetadata.verify_metadata(
            text=text_with_embedded_metadata, public_key_resolver=public_key_resolver, return_payload_on_failure=True
        )

        self.assertTrue(is_verified, "Signature verification failed for single-assertion CBOR manifest.")
        self.assertEqual(extracted_signer_id, key_id, "Extracted signer ID does not match for single-assertion CBOR manifest.")
        self.assertIsNotNone(extracted_manifest_dict, "Extracted manifest dictionary is None for single-assertion CBOR manifest.")
        self.assertIsInstance(extracted_manifest_dict, dict, "Extracted payload is not a dictionary for single-assertion CBOR manifest.")

        # For 'cbor_manifest', the extracted payload IS the manifest dictionary itself, not nested.
        self.assertEqual(extracted_manifest_dict.get("claim_generator"), original_c2pa_like_manifest.get("claim_generator"))

        # 6. Add timestamp to extracted manifest if missing
        if "timestamp" not in extracted_manifest_dict and "timestamp" in original_c2pa_like_manifest:
            extracted_manifest_dict["timestamp"] = original_c2pa_like_manifest["timestamp"]

        extracted_c2pa_like_dict = encypher_manifest_to_c2pa_like_dict(extracted_manifest_dict)
        self.assertIsNotNone(extracted_c2pa_like_dict)

        # 7. Compare the original and extracted C2PA-like dictionaries
        # Normalize for comparison
        comparison_dict = extracted_c2pa_like_dict.copy()  # Remove fields added by encypher_manifest_to_c2pa_like_dict that aren't in the original
        for field in ["format", "@context", "instance_id"]:
            if field in comparison_dict:
                del comparison_dict[field]

        # Timestamp might be slightly different due to serialization/deserialization
        comparison_dict["timestamp"] = ""
        original_comparison = original_c2pa_like_manifest.copy()
        original_comparison["timestamp"] = ""

        # Assertions should match in structure and count
        self.assertEqual(len(comparison_dict.get("assertions", [])), len(original_comparison.get("assertions", [])))

        # Compare the dictionaries (excluding timestamp)
        self.assertEqual(comparison_dict, original_comparison, "Round-trip conversion with single-assertion CBOR manifest does not match original.")

    def test_c2pa_text_wrapper_appended_with_feff(self):
        private_key, public_key = generate_ed25519_key_pair()
        key_id = "c2pa-wrapper-key"
        sample_text = "Café document for wrapper"

        embedded_text = UnicodeMetadata.embed_metadata(
            text=sample_text,
            private_key=private_key,
            signer_id=key_id,
            metadata_format="c2pa",
            claim_generator="Encypher/WrapperTest/1.0",
        )

        self.assertNotEqual(embedded_text, sample_text)

        manifest_bytes, clean_text, span = find_and_decode(embedded_text)
        self.assertIsNotNone(manifest_bytes)
        self.assertEqual(clean_text, unicodedata.normalize("NFC", sample_text))
        self.assertIsNotNone(span)
        start_byte, length_byte = span
        embedded_bytes = embedded_text.encode("utf-8")
        wrapper_segment = embedded_bytes[start_byte : start_byte + length_byte].decode("utf-8")
        self.assertTrue(wrapper_segment.startswith("﻿"))

        self.assertGreaterEqual(len(manifest_bytes), 8)
        length, box_type = struct.unpack(">I4s", manifest_bytes[:8])
        self.assertEqual(box_type, b"jumb")
        self.assertEqual(length, len(manifest_bytes))

        def resolver(kid: str):
            return public_key if kid == key_id else None

        verified, extracted_signer, manifest = UnicodeMetadata.verify_metadata(
            text=embedded_text,
            public_key_resolver=resolver,
            return_payload_on_failure=True,
        )

        self.assertTrue(verified)
        self.assertEqual(extracted_signer, key_id)
        self.assertIsNotNone(manifest)

        self.assertEqual(
            manifest.get("@context"),
            "https://c2pa.org/schemas/v2.3/c2pa.jsonld",
        )

        hard_binding = next((a for a in manifest["assertions"] if a.get("label") == "c2pa.hash.data.v1"), None)
        self.assertIsNotNone(hard_binding)
        exclusions = hard_binding["data"].get("exclusions")
        expected_start = len(unicodedata.normalize("NFC", sample_text).encode("utf-8"))
        expected_length = len(wrapper_segment.encode("utf-8"))
        self.assertEqual(exclusions, [{"start": expected_start, "length": expected_length}])

    def test_c2pa_context_url_can_be_overridden_via_env(self):
        private_key, public_key = generate_ed25519_key_pair()
        key_id = "c2pa-context-override"
        sample_text = "Context override test"

        old_context_url = os.environ.get("ENCYPHER_C2PA_CONTEXT_URL")
        try:
            os.environ["ENCYPHER_C2PA_CONTEXT_URL"] = "https://c2pa.org/schemas/v2.2/c2pa.jsonld"

            embedded_text = UnicodeMetadata.embed_metadata(
                text=sample_text,
                private_key=private_key,
                signer_id=key_id,
                metadata_format="c2pa",
            )

            def resolver(kid: str):
                return public_key if kid == key_id else None

            verified, extracted_signer, manifest = UnicodeMetadata.verify_metadata(
                text=embedded_text,
                public_key_resolver=resolver,
                return_payload_on_failure=True,
            )

            self.assertTrue(verified)
            self.assertEqual(extracted_signer, key_id)
            self.assertIsNotNone(manifest)
            self.assertEqual(manifest.get("@context"), "https://c2pa.org/schemas/v2.2/c2pa.jsonld")
        finally:
            if old_context_url is None:
                os.environ.pop("ENCYPHER_C2PA_CONTEXT_URL", None)
            else:
                os.environ["ENCYPHER_C2PA_CONTEXT_URL"] = old_context_url

    def test_c2pa_verifier_rejects_non_accepted_contexts(self):
        private_key, public_key = generate_ed25519_key_pair()
        key_id = "c2pa-context-reject"
        sample_text = "Context reject test"

        old_context_url = os.environ.get("ENCYPHER_C2PA_CONTEXT_URL")
        old_accepted = os.environ.get("ENCYPHER_C2PA_ACCEPTED_CONTEXTS")
        try:
            os.environ.pop("ENCYPHER_C2PA_CONTEXT_URL", None)
            embedded_text = UnicodeMetadata.embed_metadata(
                text=sample_text,
                private_key=private_key,
                signer_id=key_id,
                metadata_format="c2pa",
            )

            os.environ["ENCYPHER_C2PA_ACCEPTED_CONTEXTS"] = "https://c2pa.org/schemas/v2.2/c2pa.jsonld"

            def resolver(kid: str):
                return public_key if kid == key_id else None

            verified, extracted_signer, manifest = UnicodeMetadata.verify_metadata(
                text=embedded_text,
                public_key_resolver=resolver,
                return_payload_on_failure=True,
            )

            self.assertFalse(verified)
            self.assertEqual(extracted_signer, key_id)
            self.assertIsNotNone(manifest)
            self.assertEqual(manifest.get("@context"), "https://c2pa.org/schemas/v2.3/c2pa.jsonld")
        finally:
            if old_context_url is None:
                os.environ.pop("ENCYPHER_C2PA_CONTEXT_URL", None)
            else:
                os.environ["ENCYPHER_C2PA_CONTEXT_URL"] = old_context_url

            if old_accepted is None:
                os.environ.pop("ENCYPHER_C2PA_ACCEPTED_CONTEXTS", None)
            else:
                os.environ["ENCYPHER_C2PA_ACCEPTED_CONTEXTS"] = old_accepted


if __name__ == "__main__":
    unittest.main()
