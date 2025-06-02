# policy_parser.py

import json
from pathlib import Path
from typing import Dict, Any, List

class PolicySchemaError(Exception):
    """Custom exception for policy schema validation errors."""
    pass

def load_policy(policy_path: Path) -> Dict[str, Any]:
    """Loads and validates the basic structure of a policy JSON file."""
    if not policy_path.exists() or not policy_path.is_file():
        raise FileNotFoundError(f"Policy file not found: {policy_path}")

    try:
        with open(policy_path, 'r', encoding='utf-8') as f:
            policy_data = json.load(f)
    except json.JSONDecodeError as e:
        raise PolicySchemaError(f"Invalid JSON in policy file {policy_path}: {e}")
    except Exception as e:
        raise PolicySchemaError(f"Error reading policy file {policy_path}: {e}")

    # Basic structural validation
    if not isinstance(policy_data, dict):
        raise PolicySchemaError(f"Policy file {policy_path} must contain a JSON object at the root.")

    required_top_level_keys = ["policy_name", "rules"]
    for key in required_top_level_keys:
        if key not in policy_data:
            raise PolicySchemaError(f"Missing required top-level key '{key}' in policy file {policy_path}.")

    if not isinstance(policy_data.get("rules"), list):
        raise PolicySchemaError(f"'rules' key in policy file {policy_path} must be a list.")

    # Further validation of individual rules can be added here or in a separate function
    # For example, check if each rule has a 'key' and 'required' field.
    for idx, rule in enumerate(policy_data["rules"]):
        if not isinstance(rule, dict):
            raise PolicySchemaError(f"Rule at index {idx} in policy file {policy_path} is not a valid object.")
        if "key" not in rule or not isinstance(rule["key"], str):
            raise PolicySchemaError(f"Rule at index {idx} in policy file {policy_path} missing 'key' or key is not a string.")
        if "required" not in rule or not isinstance(rule["required"], bool):
            raise PolicySchemaError(f"Rule '{rule.get('key')}' (index {idx}) in policy file {policy_path} missing 'required' field or it's not a boolean.")
        if "type" in rule and rule["type"] not in ["string", "integer", "boolean", "number"]:
             raise PolicySchemaError(f"Rule '{rule.get('key')}' (index {idx}) has an invalid 'type': {rule['type']}. Supported types: string, integer, boolean, number.")
        if "allowed_values" in rule and not isinstance(rule["allowed_values"], list):
            raise PolicySchemaError(f"Rule '{rule.get('key')}' (index {idx}) has 'allowed_values' but it's not a list.")

    return policy_data
