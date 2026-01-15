"""
C2PA Interoperability Module for Encypher.

This module provides utilities for conceptual interoperability between Encypher's
manifest format and C2PA-like structures. These utilities serve as a bridge for
organizations working with both Encypher (for plain text) and C2PA (for rich media).

Note: This module provides a conceptual mapping, not a fully C2PA-compliant implementation.
The goal is to demonstrate potential interoperability and provide a starting point for
organizations that need to work with both standards.
"""

import base64
import logging
from typing import Any, Optional

import cbor2

from encypher import __version__

# Configure logger
logger = logging.getLogger(__name__)


def _serialize_data_to_cbor_base64(data: dict[str, Any]) -> str:
    """Serializes a dictionary to CBOR and then encodes it as a Base64 string."""
    cbor_data = cbor2.dumps(data)
    base64_encoded_data = base64.b64encode(cbor_data).decode("utf-8")
    return base64_encoded_data


def _deserialize_data_from_cbor_base64(base64_cbor_str: str) -> dict[str, Any]:
    """Decodes a Base64 string and then deserializes it from CBOR to a dictionary."""
    cbor_data = base64.b64decode(base64_cbor_str)
    data = cbor2.loads(cbor_data)
    if not isinstance(data, dict):
        raise ValueError("Deserialized CBOR data is not a dictionary.")
    return data


def _get_c2pa_assertion_data(assertion_dict: dict[str, Any]) -> dict[str, Any]:
    """
    Helper to construct the 'data' field for a C2PA-like assertion
    from an Encypher assertion dictionary. Handles CBOR decoding if specified.
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
                raise ValueError(f"Failed to deserialize CBOR/Base64 data for assertion '{assertion_dict.get('label')}': {e}") from e
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


def encypher_manifest_to_c2pa_like_dict(
    manifest: dict[str, Any],
    content_text: Optional[str] = None,
    embedded_data: Optional[str] = None,
    add_actions_assertion: bool = False,
    add_context: bool = True,
    add_instance_id: bool = True,
) -> dict[str, Any]:
    """
    Converts an Encypher ManifestPayload to a dictionary using field names
    aligned with C2PA v2.2 assertion structures.

    This function provides full C2PA v2.2 compliance for Encypher's plain-text
    manifest format, enabling interoperability with C2PA standards.

    Args:
        manifest: An Encypher manifest payload dictionary (can be a TypedDict ManifestPayload
                 or a regular dict with the same structure)
        content_text: Optional text content to generate content hash for hard binding.
                     If not provided, the hard binding assertion will not include a hash.
        embedded_data: Optional embedded data (Unicode variation selectors) to generate
                     soft binding hash. If not provided, soft binding will not be included.

    Returns:
        A dictionary with field names aligned with C2PA v2.2 concepts, containing the
        same information as the original manifest plus required C2PA fields.

    Example:
        ```python
        from encypher.core.payloads import ManifestPayload
        from encypher.interop.c2pa import encypher_manifest_to_c2pa_like_dict

        # Original Encypher manifest
        manifest = ManifestPayload(
            claim_generator="Encypher/2.4.0",
            assertions=[{"label": "c2pa.created", "when": "2025-04-13T12:00:00Z"}],
            ai_assertion={"model_id": "gpt-4o", "model_version": "1.0"},
            custom_claims={},
            timestamp="2025-04-13T12:00:00Z"
        )

        # Convert to C2PA v2.2 compliant structure with both hard and soft bindings
        c2pa_dict = encypher_manifest_to_c2pa_like_dict(
            manifest,
            "This is the content text",
            "Embedded data as Unicode variation selectors"
        )
        ```
    """
    import hashlib
    import uuid
    from datetime import datetime

    if not isinstance(manifest, dict):
        raise TypeError("Input 'manifest' must be a dictionary or ManifestPayload.")

    # Core fields mapping with C2PA v2.2 compliance
    result = {
        # Use the original claim_generator if available, otherwise use package version
        "claim_generator": manifest.get("claim_generator", f"encypher-ai/{__version__}"),
        "format": "application/x-encypher-ai-manifest",
        "timestamp": manifest.get("timestamp", ""),
    }

    # Add optional C2PA v2.2 context URL if requested
    if add_context:
        result["@context"] = "https://c2pa.org/schemas/v2.3/c2pa.jsonld"

    # Generate a unique instance_id for this manifest (UUID) if requested
    if add_instance_id:
        result["instance_id"] = str(uuid.uuid4())

    # Ensure timestamp is in ISO 8601 format with Z suffix
    if result["timestamp"] and not result["timestamp"].endswith("Z"):
        # If timestamp doesn't end with Z, try to convert it to proper format
        try:
            # Parse the timestamp and convert to ISO format with Z
            dt = datetime.fromisoformat(result["timestamp"].replace("Z", ""))
            result["timestamp"] = dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        except ValueError:
            # If parsing fails, keep the original timestamp
            pass

    # Handle both 'assertions' (standard format) and 'actions' (CBOR manifest format)
    assertions = []

    # Case 1: Standard 'assertions' key (from regular manifest)
    if "assertions" in manifest and isinstance(manifest["assertions"], list):
        assertions = manifest["assertions"]

    # Case 2: 'actions' key (from CBOR manifest)
    elif "actions" in manifest and isinstance(manifest["actions"], list):
        assertions = manifest["actions"]

    # Initialize C2PA assertions list and actions list
    c2pa_assertions = []
    c2pa_actions = []

    # Process assertions/actions
    if assertions:
        for assertion in assertions:
            if isinstance(assertion, dict):
                label = assertion.get("label", "")
                data = _get_c2pa_assertion_data(assertion)

                # Special handling for c2pa.created assertion - ensure timestamp and digitalSourceType are included
                if label == "c2pa.created":
                    # To avoid modifying a TypedDict, create a copy of the data dictionary and re-assign.
                    # This pattern is safer and avoids mypy issues with indexed assignment on complex types.
                    if isinstance(data, dict):  # Type guard for mypy
                        # Create a new dictionary with updated values to avoid in-place modification issues.
                        # This is a more robust pattern than modifying a copy.
                        data = {
                            **data,
                            "timestamp": data.get("timestamp", result["timestamp"]),
                            "digitalSourceType": "http://cv.iptc.org/newscodes/digitalsourcetype/trainedAlgorithmicMedia",
                            "softwareAgent": result["claim_generator"],
                        }

                c2pa_assertion = {"label": label, "data": data}
                c2pa_assertions.append(c2pa_assertion)

                # Track actions for c2pa.actions.v1 assertion
                if assertion.get("when"):
                    action_data = {"action": c2pa_assertion["label"], "when": assertion.get("when", result["timestamp"])}
                    # Ensure action timestamp is in ISO 8601 format with Z suffix
                    if action_data["when"] and not action_data["when"].endswith("Z"):
                        try:
                            dt = datetime.fromisoformat(action_data["when"].replace("Z", ""))
                            action_data["when"] = dt.strftime("%Y-%m-%dT%H:%M:%SZ")
                        except ValueError:
                            pass
                    c2pa_actions.append(action_data)

    # Handle AI assertion as a specialized assertion
    ai_assertion = manifest.get("ai_assertion")
    if ai_assertion and isinstance(ai_assertion, dict):
        ai_c2pa_assertion = {"label": "ai.model.info", "data": ai_assertion}
        c2pa_assertions.append(ai_c2pa_assertion)

    # Add mandatory C2PA v2.2 assertions

    # 1. Add c2pa.actions.v1 assertion (optional based on parameter)
    # Initialize actions_assertion regardless to avoid UnboundLocalError later
    actions_assertion = {"label": "c2pa.actions.v1", "data": {"actions": c2pa_actions}}
    if add_actions_assertion:
        c2pa_assertions.append(actions_assertion)

    # 2. Add c2pa.hash.data.v1 assertion (hard binding)
    if content_text is not None:
        content_hash = hashlib.sha256(content_text.encode("utf-8")).hexdigest()
        hash_assertion = {"label": "c2pa.hash.data.v1", "data": {"hash": content_hash, "alg": "sha256", "exclusions": []}}
        c2pa_assertions.append(hash_assertion)

    # 3. Add c2pa.soft_binding.v1 assertion (soft binding)
    soft_binding_assertion_id = None
    if embedded_data is not None:
        # Generate deterministic hash of the embedded data
        embedded_data_hash = hashlib.sha256(embedded_data.encode("utf-8")).hexdigest()
        soft_binding_assertion = {
            "label": "c2pa.soft_binding.v1",
            "data": {"alg": "encypher.unicode_variation_selector.v1", "hash": embedded_data_hash},
        }
        c2pa_assertions.append(soft_binding_assertion)
        soft_binding_assertion_id = f"#{result['instance_id']}/assertions/{len(c2pa_assertions) - 1}"

        # Add c2pa.watermarked action to the actions list
        watermarked_action = {
            "action": "c2pa.watermarked",
            "when": result["timestamp"],
            "softwareAgent": result["claim_generator"],
            "references": [{"type": "resourceRef", "uri": soft_binding_assertion_id, "description": "Unicode variation selector soft binding"}],
        }
        c2pa_actions.append(watermarked_action)

        # Update the c2pa.actions.v1 assertion with the new watermarked action
        # Create a new data dictionary to avoid indexed assignment on potentially immutable collections
        actions_assertion["data"] = {"actions": c2pa_actions}

        # If we haven't added the actions assertion yet (add_actions_assertion was False),
        # add it now since we have watermarked actions
        if not add_actions_assertion and actions_assertion not in c2pa_assertions:
            c2pa_assertions.append(actions_assertion)

    # Add all assertions to the result
    result["assertions"] = c2pa_assertions

    # Include custom claims
    custom_claims = manifest.get("custom_claims")
    if custom_claims and isinstance(custom_claims, dict):
        result["custom_claims"] = custom_claims

    return result


def c2pa_like_dict_to_encypher_manifest(
    data: dict[str, Any], encode_assertion_data_as_cbor: bool = False, use_nested_data: bool = False
) -> dict[str, Any]:
    """
    Creates an Encypher ManifestPayload from a dictionary structured
    similarly to C2PA assertions. Handles missing fields gracefully.

    This function provides a conceptual bridge from C2PA-like structures
    to Encypher's manifest format, enabling potential interoperability
    between the two approaches.

    Args:
        data: A dictionary with C2PA-like structure containing provenance information.

    Returns:
        An Encypher ManifestPayload dictionary that can be used with Encypher's
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

        # Convert to Encypher manifest
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
                # However, Encypher assertions might just have flat key-value pairs.
                # Let's stick to the original logic of copying key-values unless CBOR is used.
                # If CBOR is used, 'data' will contain the b64 string or be absent if original data was not suitable.

                manifest["assertions"].append(assertion)

    # Include custom claims
    custom_claims = data.get("custom_claims")
    if custom_claims and isinstance(custom_claims, dict):
        manifest["custom_claims"] = custom_claims

    return manifest


def get_c2pa_manifest_schema() -> dict[str, Any]:
    """
    Returns a JSON Schema representation of the C2PA v2.2 structure used by this module.

    This schema provides documentation for the expected structure of C2PA v2.2 compliant dictionaries
    used with the conversion functions in this module.

    Returns:
        A dictionary containing the JSON Schema for C2PA v2.2 structures.
    """
    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "C2PA v2.3 Manifest",
        "description": "A C2PA v2.3 compliant manifest schema for Encypher",
        "type": "object",
        "properties": {
            "@context": {
                "type": "string",
                "description": "The JSON-LD context URL for C2PA v2.3",
                "const": "https://c2pa.org/schemas/v2.3/c2pa.jsonld",
            },
            "instance_id": {"type": "string", "description": "Unique UUID for this manifest instance", "format": "uuid"},
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
                "description": "ISO 8601 UTC timestamp for when the claim was generated (with Z suffix)",
            },
            "assertions": {
                "type": "array",
                "description": "List of assertions about the content",
                "items": {
                    "type": "object",
                    "properties": {
                        "label": {
                            "type": "string",
                            "description": "Type of assertion",
                            "examples": ["c2pa.created", "c2pa.actions.v1", "c2pa.hash.data.v1", "c2pa.soft_binding.v1", "ai.model.info"],
                        },
                        "data": {
                            "type": "object",
                            "description": "Data associated with the assertion",
                        },
                    },
                    "required": ["label", "data"],
                },
            },
            "custom_claims": {
                "type": "object",
                "description": "Additional custom claims",
            },
        },
        "required": ["@context", "instance_id", "claim_generator", "timestamp", "assertions"],
    }
