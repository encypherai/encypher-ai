import json
import tempfile
import unittest
from pathlib import Path

from policy_validator_cli.app.policy_parser import PolicySchemaError, load_policy


class TestPolicyParser(unittest.TestCase):
    """Tests for the policy_parser module."""

    def setUp(self):
        """Create a temporary directory for test policy files."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):
        """Clean up temporary directory."""
        self.temp_dir.cleanup()

    def test_load_valid_policy(self):
        """Test loading a valid policy file."""
        # Create a valid policy file
        policy_data = {
            "policy_name": "Test Policy",
            "description": "A test policy",
            "rules": [{"key": "test_key", "required": True, "type": "string", "description": "A test key"}],
        }
        policy_path = self.temp_path / "valid_policy.json"
        with open(policy_path, "w") as f:
            json.dump(policy_data, f)

        # Load the policy
        loaded_policy = load_policy(policy_path)

        # Verify the loaded policy matches the original
        self.assertEqual(loaded_policy["policy_name"], policy_data["policy_name"])
        self.assertEqual(loaded_policy["description"], policy_data["description"])
        self.assertEqual(len(loaded_policy["rules"]), 1)
        self.assertEqual(loaded_policy["rules"][0]["key"], "test_key")
        self.assertEqual(loaded_policy["rules"][0]["required"], True)

    def test_load_nonexistent_policy(self):
        """Test loading a nonexistent policy file."""
        nonexistent_path = self.temp_path / "nonexistent.json"
        with self.assertRaises(FileNotFoundError):
            load_policy(nonexistent_path)

    def test_load_invalid_json(self):
        """Test loading a file with invalid JSON."""
        invalid_json_path = self.temp_path / "invalid.json"
        with open(invalid_json_path, "w") as f:
            f.write("{invalid json")

        with self.assertRaises(PolicySchemaError):
            load_policy(invalid_json_path)

    def test_missing_required_keys(self):
        """Test loading a policy missing required top-level keys."""
        # Missing "rules" key
        missing_rules = {"policy_name": "Test Policy", "description": "A test policy"}
        missing_rules_path = self.temp_path / "missing_rules.json"
        with open(missing_rules_path, "w") as f:
            json.dump(missing_rules, f)

        with self.assertRaises(PolicySchemaError):
            load_policy(missing_rules_path)

        # Missing "policy_name" key
        missing_name = {"description": "A test policy", "rules": []}
        missing_name_path = self.temp_path / "missing_name.json"
        with open(missing_name_path, "w") as f:
            json.dump(missing_name, f)

        with self.assertRaises(PolicySchemaError):
            load_policy(missing_name_path)

    def test_invalid_rule_structure(self):
        """Test loading a policy with invalid rule structure."""
        # Rule missing "key" field
        missing_key = {"policy_name": "Test Policy", "rules": [{"required": True, "type": "string"}]}
        missing_key_path = self.temp_path / "missing_key.json"
        with open(missing_key_path, "w") as f:
            json.dump(missing_key, f)

        with self.assertRaises(PolicySchemaError):
            load_policy(missing_key_path)

        # Rule with invalid "type"
        invalid_type = {"policy_name": "Test Policy", "rules": [{"key": "test_key", "required": True, "type": "invalid_type"}]}
        invalid_type_path = self.temp_path / "invalid_type.json"
        with open(invalid_type_path, "w") as f:
            json.dump(invalid_type, f)

        with self.assertRaises(PolicySchemaError):
            load_policy(invalid_type_path)


if __name__ == "__main__":
    unittest.main()
