import unittest
from policy_validator_cli.app.validator import validate_metadata

class TestValidator(unittest.TestCase):
    """Tests for the validator module."""

    def setUp(self):
        """Set up test policy rules."""
        self.policy_rules = [
            {
                "key": "doc_id",
                "required": True,
                "type": "string",
                "description": "Document ID"
            },
            {
                "key": "sensitivity",
                "required": True,
                "type": "string",
                "allowed_values": ["public", "internal", "confidential"],
                "description": "Document sensitivity level"
            },
            {
                "key": "version",
                "required": False,
                "type": "integer",
                "description": "Document version"
            },
            {
                "key": "is_draft",
                "required": False,
                "type": "boolean",
                "description": "Whether the document is a draft"
            }
        ]

    def test_valid_metadata(self):
        """Test validation with valid metadata."""
        metadata = {
            "doc_id": "DOC-123",
            "sensitivity": "internal",
            "version": 1,
            "is_draft": True
        }
        is_valid, errors = validate_metadata(metadata, self.policy_rules, "test_source")
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_missing_required_key(self):
        """Test validation with missing required key."""
        # Missing doc_id (required)
        metadata = {
            "sensitivity": "internal",
            "version": 1
        }
        is_valid, errors = validate_metadata(metadata, self.policy_rules, "test_source")
        self.assertFalse(is_valid)
        self.assertEqual(len(errors), 1)
        self.assertIn("Missing required metadata key 'doc_id'", errors[0])

    def test_invalid_type(self):
        """Test validation with invalid data type."""
        # version should be integer, not string
        metadata = {
            "doc_id": "DOC-123",
            "sensitivity": "internal",
            "version": "1.0"  # Should be an integer
        }
        is_valid, errors = validate_metadata(metadata, self.policy_rules, "test_source")
        self.assertFalse(is_valid)
        self.assertEqual(len(errors), 1)
        self.assertIn("does not match expected type 'integer'", errors[0])

    def test_disallowed_value(self):
        """Test validation with value not in allowed list."""
        # "top_secret" is not in allowed values for sensitivity
        metadata = {
            "doc_id": "DOC-123",
            "sensitivity": "top_secret",  # Not in allowed values
            "version": 1
        }
        is_valid, errors = validate_metadata(metadata, self.policy_rules, "test_source")
        self.assertFalse(is_valid)
        self.assertEqual(len(errors), 1)
        self.assertIn("not in the allowed list", errors[0])

    def test_multiple_errors(self):
        """Test validation with multiple errors."""
        metadata = {
            # Missing doc_id
            "sensitivity": "top_secret",  # Not in allowed values
            "version": "2.0",  # Wrong type
            "is_draft": "yes"  # Wrong type
        }
        is_valid, errors = validate_metadata(metadata, self.policy_rules, "test_source")
        self.assertFalse(is_valid)
        self.assertEqual(len(errors), 4)  # 4 errors: missing key, wrong value, 2 wrong types

    def test_empty_metadata(self):
        """Test validation with empty metadata."""
        metadata = {}
        is_valid, errors = validate_metadata(metadata, self.policy_rules, "test_source")
        self.assertFalse(is_valid)
        self.assertEqual(len(errors), 2)  # 2 errors for 2 required keys

    def test_none_metadata(self):
        """Test validation with None metadata."""
        metadata = None
        is_valid, errors = validate_metadata(metadata, self.policy_rules, "test_source")
        self.assertFalse(is_valid)
        self.assertEqual(len(errors), 2)  # 2 errors for 2 required keys

if __name__ == '__main__':
    unittest.main()
