# validator.py

from typing import Any, Dict, List, Tuple

try:
    from encypher_ai import Encypher, VerificationResult  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - fallback when encypher_ai is unavailable
    from dataclasses import dataclass
    from enum import Enum
    from typing import Any, Dict

    class VerificationStatus(Enum):
        UNKNOWN = "UNKNOWN"

    @dataclass
    class VerificationResult:
        status: VerificationStatus
        is_verified: bool
        metadata: Dict[str, Any]

    class Encypher:
        def verify_from_text(self, text: str) -> VerificationResult:
            return VerificationResult(
                status=VerificationStatus.UNKNOWN,
                is_verified=False,
                metadata={},
            )

class MetadataValidationError(Exception):
    """Custom exception for metadata validation errors against a policy."""
    pass

def validate_metadata(
    metadata: Dict[str, Any],
    policy_rules: List[Dict[str, Any]],
    source_identifier: str = "input"
) -> Tuple[bool, List[str]]:
    """
    Validates extracted metadata against a list of policy rules.

    Args:
        metadata: The metadata extracted from the text (e.g., from Encypher.verify_from_text().metadata).
        policy_rules: A list of rule objects from the loaded policy file.
        source_identifier: A string identifying the source of the metadata (e.g., filename, text input #).

    Returns:
        A tuple: (is_valid: bool, errors: List[str])
    """
    is_valid = True
    errors: List[str] = []

    if not metadata: # Handle cases where metadata might be None or empty
        metadata = {}

    for rule in policy_rules:
        key = rule["key"]
        is_required = rule.get("required", False)
        expected_type = rule.get("type")
        allowed_values = rule.get("allowed_values")

        if key not in metadata:
            if is_required:
                is_valid = False
                errors.append(f"Source '{source_identifier}': Missing required metadata key '{key}'.")
            continue # Skip further checks if key is missing and not required

        value = metadata[key]

        # Type checking
        if expected_type:
            type_valid = False
            if expected_type == "string" and isinstance(value, str):
                type_valid = True
            elif expected_type == "integer" and isinstance(value, int):
                type_valid = True
            elif expected_type == "boolean" and isinstance(value, bool):
                type_valid = True
            elif expected_type == "number" and isinstance(value, (int, float)):
                type_valid = True
            # Add more type checks as needed (e.g., list, object)
            
            if not type_valid:
                is_valid = False
                errors.append(f"Source '{source_identifier}': Metadata key '{key}' has value '{value}' (type: {type(value).__name__}), which does not match expected type '{expected_type}'.")
                continue # If type is wrong, further value checks might be misleading

        # Allowed values checking
        if allowed_values:
            if value not in allowed_values:
                is_valid = False
                errors.append(f"Source '{source_identifier}': Metadata key '{key}' has value '{value}', which is not in the allowed list: {allowed_values}.")

    return is_valid, errors

# Example Usage (can be moved to main.py or tests later)
if __name__ == '__main__':
    sample_policy_rules = [
        {"key": "doc_id", "required": True, "type": "string"},
        {"key": "status", "required": True, "type": "string", "allowed_values": ["draft", "review", "final"]},
        {"key": "internal_only", "required": False, "type": "boolean"}
    ]

    metadata1 = {"doc_id": "XYZ123", "status": "draft", "internal_only": True}
    valid1, errs1 = validate_metadata(metadata1, sample_policy_rules, "doc1")
    print(f"Doc1 Valid: {valid1}, Errors: {errs1}")

    metadata2 = {"doc_id": "ABC456", "status": "published"} # 'published' is not allowed
    valid2, errs2 = validate_metadata(metadata2, sample_policy_rules, "doc2")
    print(f"Doc2 Valid: {valid2}, Errors: {errs2}")

    metadata3 = {"status": "review"} # missing 'doc_id'
    valid3, errs3 = validate_metadata(metadata3, sample_policy_rules, "doc3")
    print(f"Doc3 Valid: {valid3}, Errors: {errs3}")

    metadata4 = {"doc_id": 123, "status": "final"} # doc_id is not string
    valid4, errs4 = validate_metadata(metadata4, sample_policy_rules, "doc4")
    print(f"Doc4 Valid: {valid4}, Errors: {errs4}")
