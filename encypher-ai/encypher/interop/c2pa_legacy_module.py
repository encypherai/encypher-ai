"""
C2PA Interoperability Module for EncypherAI.

This module provides utilities for conceptual interoperability between EncypherAI's
manifest format and C2PA-like structures. These utilities serve as a bridge for
organizations working with both EncypherAI (for plain text) and C2PA (for rich media).

Note: This module provides a conceptual mapping, not a fully C2PA-compliant implementation.
The goal is to demonstrate potential interoperability and provide a starting point for
organizations that need to work with both standards.
"""

from typing import Any


def encypher_manifest_to_c2pa_like_dict(manifest: dict[str, Any]) -> dict[str, Any]:
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

    # Map assertions to C2PA assertions
    assertions = manifest.get("assertions", [])
    if assertions and isinstance(assertions, list):
        c2pa_assertions = []
        for assertion in assertions:
            if isinstance(assertion, dict):
                # Create an assertion object from each assertion
                c2pa_assertion = {
                    "label": assertion.get("label", ""),  # Use label as C2PA label
                    "data": {
                        "timestamp": assertion.get("when", ""),
                        # Include any other assertion fields
                        **{k: v for k, v in assertion.items() if k not in ["label", "when"]},
                    },
                }
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


def c2pa_like_dict_to_encypher_manifest(data: dict[str, Any]) -> dict[str, Any]:
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
                for k, v in assertion_data.items():
                    if k != "timestamp":
                        assertion[k] = v

                manifest["assertions"].append(assertion)

    # Include custom claims
    custom_claims = data.get("custom_claims")
    if custom_claims and isinstance(custom_claims, dict):
        manifest["custom_claims"] = custom_claims

    return manifest


def get_c2pa_manifest_schema() -> dict[str, Any]:
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
