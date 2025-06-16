"""
C2PA Interoperability Module for EncypherAI.

This module provides utilities for conceptual interoperability between EncypherAI's
manifest format and C2PA-like structures. These utilities serve as a bridge for
organizations working with both EncypherAI (for plain text) and C2PA (for rich media).

Note: This module provides a conceptual mapping, not a fully C2PA-compliant implementation.
The goal is to demonstrate potential interoperability and provide a starting point for
organizations that need to work with both standards.
"""

import base64
import logging
from typing import Any, Dict

import cbor2

# Configure logger
logger = logging.getLogger(__name__)


def _serialize_data_to_cbor_base64(data: Dict[str, Any]) -> str:
    """Serializes a dictionary to CBOR and then encodes it as a Base64 string."""
    cbor_data = cbor2.dumps(data)
    base64_encoded_data = base64.b64encode(cbor_data).decode("utf-8")
    return base64_encoded_data


def _deserialize_data_from_cbor_base64(base64_cbor_str: str) -> Dict[str, Any]:
    """Decodes a Base64 string and then deserializes it from CBOR to a dictionary."""
    cbor_data = base64.b64decode(base64_cbor_str)
    data = cbor2.loads(cbor_data)
    if not isinstance(data, dict):
        raise ValueError("Deserialized CBOR data is not a dictionary.")
    return data


def _get_c2pa_assertion_data(assertion_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Helper to construct the 'data' field for a C2PA-like assertion
    from an EncypherAI assertion dictionary. Handles CBOR decoding if specified.
    Also handles both nested and flattened assertion data structures.
    """
    # Case 1: CBOR encoded data
    if assertion_dict.get("data_encoding") == "cbor_base64":
        cbor_b64_str = assertion_dict.get("data")
        if isinstance(cbor_b64_str, str):
            try:
                deserialized_data = _deserialize_data_from_cbor_base64(cbor_b64_str)
                return deserialized_data
            except Exception as e:
                raise ValueError(f"Failed to deserialize CBOR/Base64 data for assertion '{assertion_dict.get('label')}': {e}")
        else:
            raise ValueError(f"Assertion '{assertion_dict.get('label')}' has 'data_encoding' as CBOR but 'data' is not a string.")

    # Case 2: Direct nested data field present
    if "data" in assertion_dict and isinstance(assertion_dict["data"], dict):
        # If there's a direct 'data' field that's a dict, use it directly
        # Don't add timestamp to data - it should be at top level only
        return assertion_dict["data"].copy()

    # Case 3: Default/legacy case - construct data from flattened fields
    # Exclude timestamp/when from data - it should be at top level only
    return {k: v for k, v in assertion_dict.items() if k not in ["label", "when", "timestamp", "data", "data_encoding"]}


def encypher_manifest_to_c2pa_like_dict(manifest: Dict[str, Any]) -> Dict[str, Any]:
    """
    Converts an EncypherAI ManifestPayload to a dictionary using field names
    conceptually aligned with C2PA assertion structures.

    This function provides a conceptual bridge between EncypherAI's plain-text
    manifest format and C2PA's rich media manifest structure, enabling potential
    interoperability between the two approaches.

    Args:
        manifest: An EncypherAI manifest payload dictionary (can be a TypedDict ManifestPayload
                 or a regular dict with the same structure)

    Returns:
        A dictionary with field names aligned with C2PA concepts, containing the
        same information as the original manifest.

    Example:
        ```python
        from encypher.core.payloads import ManifestPayload
        from encypher.interop.c2pa import encypher_manifest_to_c2pa_like_dict

        # Original EncypherAI manifest
        manifest = ManifestPayload(
            claim_generator="EncypherAI/1.1.0",
            assertions=[{"label": "c2pa.created", "when": "2025-04-13T12:00:00Z"}],
            ai_assertion={"model_id": "gpt-4o", "model_version": "1.0"},
            custom_claims={},
            timestamp="2025-04-13T12:00:00Z"
        )

        # Convert to C2PA-like structure
        c2pa_dict = encypher_manifest_to_c2pa_like_dict(manifest)
        ```
    """
    if not isinstance(manifest, dict):
        raise TypeError("Input 'manifest' must be a dictionary or ManifestPayload.")

    # Core fields mapping
    result = {
        "claim_generator": manifest.get("claim_generator", ""),
        "format": "application/x-encypher-ai-manifest",  # Custom format identifier
        "timestamp": manifest.get("timestamp", ""),
    }

    # Handle both 'assertions' (standard format) and 'actions' (CBOR manifest format)
    assertions = []

    # Case 1: Standard 'assertions' key (from regular manifest)
    if "assertions" in manifest and isinstance(manifest["assertions"], list):
        assertions = manifest["assertions"]

    # Case 2: 'actions' key (from CBOR manifest)
    elif "actions" in manifest and isinstance(manifest["actions"], list):
        assertions = manifest["actions"]

    # Process assertions/actions
    if assertions:
        c2pa_assertions = []
        for assertion in assertions:
            if isinstance(assertion, dict):
                # Create an assertion object from each assertion
                c2pa_assertion = {
                    "label": assertion.get("label", ""),  # Use label as C2PA label
                    "data": _get_c2pa_assertion_data(assertion),
                }

                # Special handling for c2pa.created assertion - ensure timestamp is included in data
                if c2pa_assertion["label"] == "c2pa.created":
                    if "data" not in c2pa_assertion or not isinstance(c2pa_assertion["data"], dict):
                        c2pa_assertion["data"] = {}
                    # Add timestamp to the data field if not already present
                    if "timestamp" not in c2pa_assertion["data"]:
                        c2pa_assertion["data"]["timestamp"] = manifest.get("timestamp", "")

                c2pa_assertions.append(c2pa_assertion)
        result["assertions"] = c2pa_assertions

    # Handle AI assertion as a specialized assertion
    ai_assertion = manifest.get("ai_assertion")
    if ai_assertion and isinstance(ai_assertion, dict):
        ai_c2pa_assertion = {"label": "ai.model.info", "data": ai_assertion}
        if "assertions" in result:
            result["assertions"].append(ai_c2pa_assertion)
        else:
            result["assertions"] = [ai_c2pa_assertion]

    # Include custom claims
    custom_claims = manifest.get("custom_claims")
    if custom_claims and isinstance(custom_claims, dict):
        result["custom_claims"] = custom_claims

    return result


def c2pa_like_dict_to_encypher_manifest(
    data: Dict[str, Any], encode_assertion_data_as_cbor: bool = False, use_nested_data: bool = False
) -> Dict[str, Any]:
    """
    Creates an EncypherAI ManifestPayload from a dictionary structured
    similarly to C2PA assertions. Handles missing fields gracefully.

    This function provides a conceptual bridge from C2PA-like structures
    to EncypherAI's manifest format, enabling potential interoperability
    between the two approaches.

    Args:
        data: A dictionary with C2PA-like structure containing provenance information.

    Returns:
        An EncypherAI ManifestPayload dictionary that can be used with EncypherAI's
        embedding functions.

    Example:
        ```python
        from encypher.interop.c2pa import c2pa_like_dict_to_encypher_manifest

        # C2PA-like structure
        c2pa_data = {
            "claim_generator": "SomeApp/1.0",
            "assertions": [
                {
                    "label": "c2pa.created",
                    "data": {"timestamp": "2025-04-13T12:00:00Z"}
                },
                {
                    "label": "ai.model.info",
                    "data": {"model_id": "gpt-4o", "model_version": "1.0"}
                }
            ],
            "timestamp": "2025-04-13T12:00:00Z"
        }

        # Convert to EncypherAI manifest
        manifest = c2pa_like_dict_to_encypher_manifest(c2pa_data)
        ```
    """
    if not isinstance(data, dict):
        raise TypeError("Input 'data' must be a dictionary.")

    # Initialize the manifest with required fields
    manifest = {
        "claim_generator": data.get("claim_generator", ""),
        "assertions": [],
        "ai_assertion": {},
        "custom_claims": {},
        "timestamp": data.get("timestamp", ""),
    }

    # Process assertions
    c2pa_assertions = data.get("assertions", [])
    if c2pa_assertions and isinstance(c2pa_assertions, list):
        for c2pa_assertion in c2pa_assertions:
            if not isinstance(c2pa_assertion, dict):
                continue

            label = c2pa_assertion.get("label", "")
            assertion_data = c2pa_assertion.get("data", {})

            # Check if this is an AI model info assertion
            if label == "ai.model.info" and isinstance(assertion_data, dict):
                manifest["ai_assertion"] = assertion_data
            # Otherwise, treat as a regular assertion
            elif label:
                assertion = {
                    "label": label,
                    "when": assertion_data.get("timestamp", manifest["timestamp"]),
                }
                # Include any other data fields
                # If CBOR encoding is requested, the 'data' field itself will be handled.
                if encode_assertion_data_as_cbor and isinstance(assertion_data, dict) and assertion_data:
                    try:
                        assertion["data"] = _serialize_data_to_cbor_base64(assertion_data)
                        assertion["data_encoding"] = "cbor_base64"
                    except Exception as e:
                        # Optionally log an error or handle it if CBOR encoding fails
                        # For now, falling back to JSON-like data if CBOR fails
                        # Or, re-raise if strict CBOR encoding is required when flag is true
                        logger.warning(f"CBOR serialization failed for assertion data: {e}. Storing as JSON.")
                        # Copy over original data fields if CBOR fails and we fall back
                        for k, v in assertion_data.items():
                            if k != "timestamp":  # 'when' is already set from timestamp
                                assertion[k] = v
                        if "data" in assertion:
                            del assertion["data"]  # remove partially set cbor data
                        if "data_encoding" in assertion:
                            del assertion["data_encoding"]

                else:
                    # If not encoding as CBOR (i.e., encode_assertion_data_as_cbor is False):
                    # We need to decide how to structure the assertion data based on use_nested_data parameter.
                    if isinstance(assertion_data, dict):
                        if use_nested_data:
                            # For 'cbor_manifest' format, keep data nested under 'data' key
                            assertion["data"] = assertion_data
                        else:
                            # For traditional 'manifest' format, flatten data fields into assertion
                            for k, v in assertion_data.items():
                                if k != "timestamp":  # 'when' is already set from timestamp
                                    assertion[k] = v
                    # If assertion_data is not a dict, no data is added to the assertion

                # Ensure 'data' key exists if not CBOR encoded and original assertion_data was empty but not None
                # This part is tricky because the original logic copied individual keys.
                # If not encoding as CBOR and assertion_data was an empty dict,
                # the loop above wouldn't add a 'data' field.
                # C2PA assertions typically have a 'data' object, even if empty.
                # However, EncypherAI assertions might just have flat key-value pairs.
                # Let's stick to the original logic of copying key-values unless CBOR is used.
                # If CBOR is used, 'data' will contain the b64 string or be absent if original data was not suitable.

                manifest["assertions"].append(assertion)

    # Include custom claims
    custom_claims = data.get("custom_claims")
    if custom_claims and isinstance(custom_claims, dict):
        manifest["custom_claims"] = custom_claims

    return manifest


def get_c2pa_manifest_schema() -> Dict[str, Any]:
    """
    Returns a JSON Schema representation of the C2PA-like structure used by this module.

    This schema provides documentation for the expected structure of C2PA-like dictionaries
    used with the conversion functions in this module.

    Returns:
        A dictionary containing the JSON Schema for C2PA-like structures.
    """
    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "C2PA-like Manifest",
        "description": "A simplified schema for C2PA-like manifests used with EncypherAI",
        "type": "object",
        "properties": {
            "claim_generator": {
                "type": "string",
                "description": "Identifier for the software/tool that generated this claim",
            },
            "format": {
                "type": "string",
                "description": "Format identifier for the manifest",
            },
            "timestamp": {
                "type": "string",
                "format": "date-time",
                "description": "ISO 8601 UTC timestamp for when the claim was generated",
            },
            "assertions": {
                "type": "array",
                "description": "List of assertions about the content",
                "items": {
                    "type": "object",
                    "properties": {
                        "label": {
                            "type": "string",
                            "description": "Type of assertion (e.g., 'c2pa.created')",
                        },
                        "data": {
                            "type": "object",
                            "description": "Data associated with the assertion",
                        },
                    },
                    "required": ["label"],
                },
            },
            "custom_claims": {
                "type": "object",
                "description": "Additional custom claims",
            },
        },
        "required": ["claim_generator"],
    }
