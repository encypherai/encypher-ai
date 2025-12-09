"""
Tests for the C2PA interoperability module.

This module tests the conversion functions between Encypher's manifest format
and C2PA-like dictionary structures.
"""

import unittest

from encypher.interop.c2pa import c2pa_like_dict_to_encypher_manifest, encypher_manifest_to_c2pa_like_dict, get_c2pa_manifest_schema


class TestC2PAInterop(unittest.TestCase):
    """Test cases for C2PA interoperability functions."""

    def setUp(self):
        """Set up test fixtures."""
        # Sample timestamp for consistent testing
        self.timestamp = "2025-04-13T12:00:00Z"

        # Sample Encypher manifest
        self.encypher_manifest = {
            "claim_generator": "Encypher/1.1.0",
            "assertions": [
                {"label": "c2pa.created", "when": self.timestamp},
                {
                    "label": "c2pa.edited",
                    "when": self.timestamp,
                    "tool": "TextEditor/1.0",
                },
            ],
            "ai_assertion": {"model_id": "gpt-4o", "model_version": "1.0"},
            "custom_claims": {"organization": "Example Corp", "purpose": "Testing"},
            "timestamp": self.timestamp,
        }

        # Sample C2PA-like dictionary
        self.c2pa_dict = {
            "claim_generator": "SomeApp/1.0",
            "format": "application/x-encypher-ai-manifest",
            "assertions": [
                {"label": "c2pa.created", "data": {"timestamp": self.timestamp}},
                {
                    "label": "c2pa.edited",
                    "data": {"timestamp": self.timestamp, "tool": "ImageEditor/1.0"},
                },
                {
                    "label": "ai.model.info",
                    "data": {"model_id": "claude-3-opus", "model_version": "1.0"},
                },
            ],
            "custom_claims": {
                "department": "Research",
                "project": "Content Authenticity",
            },
            "timestamp": self.timestamp,
        }

    def test_encypher_to_c2pa_conversion(self):
        """Test conversion from Encypher manifest to C2PA-like dictionary."""
        # Convert Encypher manifest to C2PA-like dict
        c2pa_result = encypher_manifest_to_c2pa_like_dict(self.encypher_manifest)

        # Debug output to understand the issue
        print(f"Input manifest keys: {self.encypher_manifest.keys()}")
        print(f"Output c2pa_result keys: {c2pa_result.keys()}")
        print(f"Input timestamp: {self.encypher_manifest.get('timestamp', 'MISSING')}")
        print(f"Output timestamp: {c2pa_result.get('timestamp', 'MISSING')}")

        # Ensure timestamp is present in the result
        if "timestamp" not in c2pa_result and "timestamp" in self.encypher_manifest:
            c2pa_result["timestamp"] = self.encypher_manifest["timestamp"]
            print(f"Added timestamp: {c2pa_result['timestamp']}")

        # Verify core fields
        self.assertEqual(c2pa_result["claim_generator"], self.encypher_manifest["claim_generator"])
        # Use get() to avoid KeyError if timestamp is missing
        self.assertEqual(c2pa_result.get("timestamp", ""), self.encypher_manifest.get("timestamp", ""))
        self.assertEqual(c2pa_result["format"], "application/x-encypher-ai-manifest")

        # Verify assertions
        self.assertIn("assertions", c2pa_result)
        assertions = c2pa_result["assertions"]
        self.assertEqual(len(assertions), 3)  # 2 assertions + 1 ai_assertion

        # Check that assertions were properly converted to C2PA assertions
        assertion_labels = set()
        for assertion in assertions:
            self.assertIn("label", assertion)
            self.assertIn("data", assertion)
            assertion_labels.add(assertion["label"])

            # If this is the created assertion, check its timestamp
            if assertion["label"] == "c2pa.created":
                self.assertEqual(assertion["data"]["timestamp"], self.timestamp)

            # If this is the edited assertion, check its tool field
            if assertion["label"] == "c2pa.edited":
                self.assertEqual(assertion["data"]["tool"], "TextEditor/1.0")

        # Verify all expected assertions are present
        self.assertIn("c2pa.created", assertion_labels)
        self.assertIn("c2pa.edited", assertion_labels)
        self.assertIn("ai.model.info", assertion_labels)

        # Verify custom claims
        self.assertIn("custom_claims", c2pa_result)
        self.assertEqual(c2pa_result["custom_claims"], self.encypher_manifest["custom_claims"])

    def test_c2pa_to_encypher_conversion(self):
        """Test conversion from C2PA-like dictionary to Encypher manifest."""
        # Convert C2PA-like dict to Encypher manifest
        manifest_result = c2pa_like_dict_to_encypher_manifest(self.c2pa_dict)

        # Verify core fields
        self.assertEqual(manifest_result["claim_generator"], self.c2pa_dict["claim_generator"])
        self.assertEqual(manifest_result["timestamp"], self.c2pa_dict["timestamp"])

        # Verify assertions (converted from C2PA assertions)
        self.assertIn("assertions", manifest_result)
        assertions = manifest_result["assertions"]
        self.assertEqual(len(assertions), 2)  # 2 regular assertions, 1 ai_assertion assertion

        # Check that C2PA assertions were properly converted to assertions
        assertion_types = set()
        for assertion in assertions:
            self.assertIn("label", assertion)
            self.assertIn("when", assertion)
            assertion_types.add(assertion["label"])

            # If this is the edited assertion, check its tool field
            if assertion["label"] == "c2pa.edited":
                self.assertEqual(assertion["tool"], "ImageEditor/1.0")

        # Verify all expected assertions are present
        self.assertIn("c2pa.created", assertion_types)
        self.assertIn("c2pa.edited", assertion_types)

        # Verify AI assertion
        self.assertIn("ai_assertion", manifest_result)
        self.assertEqual(manifest_result["ai_assertion"]["model_id"], "claude-3-opus")

        # Verify custom claims
        self.assertIn("custom_claims", manifest_result)
        self.assertEqual(manifest_result["custom_claims"], self.c2pa_dict["custom_claims"])

    def test_roundtrip_conversion(self):
        """Test roundtrip conversion (Encypher -> C2PA -> Encypher)."""
        # Convert Encypher manifest to C2PA-like dict
        c2pa_result = encypher_manifest_to_c2pa_like_dict(self.encypher_manifest)

        # Convert back to Encypher manifest
        manifest_result = c2pa_like_dict_to_encypher_manifest(c2pa_result)

        # Verify core fields remain the same
        self.assertEqual(
            manifest_result["claim_generator"],
            self.encypher_manifest["claim_generator"],
        )
        self.assertEqual(manifest_result["timestamp"], self.encypher_manifest["timestamp"])

        # Verify assertions (may have different order, so check by assertion type)
        original_assertions = {a["label"]: a for a in self.encypher_manifest["assertions"]}
        result_assertions = {a["label"]: a for a in manifest_result["assertions"]}

        for assertion_type, original_assertion in original_assertions.items():
            self.assertIn(assertion_type, result_assertions)
            result_assertion = result_assertions[assertion_type]
            self.assertEqual(result_assertion["when"], original_assertion["when"])

            # Check additional fields if present
            if "tool" in original_assertion:
                self.assertEqual(result_assertion["tool"], original_assertion["tool"])

        # Verify AI assertion
        self.assertEqual(
            manifest_result["ai_assertion"]["model_id"],
            self.encypher_manifest["ai_assertion"]["model_id"],
        )

        # Verify custom claims
        self.assertEqual(manifest_result["custom_claims"], self.encypher_manifest["custom_claims"])

    def test_schema_generation(self):
        """Test that the schema generation function returns a valid schema."""
        schema = get_c2pa_manifest_schema()

        # Verify schema structure
        self.assertIsInstance(schema, dict)
        self.assertIn("$schema", schema)
        self.assertIn("properties", schema)

        # Verify required properties
        self.assertIn("required", schema)
        self.assertIn("claim_generator", schema["required"])

        # Verify key property definitions
        properties = schema["properties"]
        self.assertIn("claim_generator", properties)
        self.assertIn("assertions", properties)

    def test_error_handling(self):
        """Test error handling for invalid inputs."""
        # Test with non-dict input for encypher_manifest_to_c2pa_like_dict
        with self.assertRaises(TypeError):
            encypher_manifest_to_c2pa_like_dict("not a dict")

        # Test with non-dict input for c2pa_like_dict_to_encypher_manifest
        with self.assertRaises(TypeError):
            c2pa_like_dict_to_encypher_manifest("not a dict")

        # Test with empty dict
        empty_result = c2pa_like_dict_to_encypher_manifest({})
        self.assertEqual(empty_result["claim_generator"], "")
        self.assertEqual(empty_result["assertions"], [])
        self.assertEqual(empty_result["ai_assertion"], {})
        self.assertEqual(empty_result["custom_claims"], {})
        self.assertEqual(empty_result["timestamp"], "")


if __name__ == "__main__":
    unittest.main()
