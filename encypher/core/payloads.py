import json
from typing import Any, Dict, List, Literal, Optional, TypedDict, Union, cast

import cbor2

# Assuming logging_config.py is in the same directory (core)
from .logging_config import logger

# --- TypedDict Definitions for Metadata Payloads ---


class BasicPayload(TypedDict):
    """Structure for the 'basic' metadata format payload."""

    model_id: Optional[str]
    timestamp: Optional[str]  # Recommended: ISO 8601 UTC format string
    custom_metadata: Dict[str, Any]


class ManifestAction(TypedDict):
    """
    Structure for an assertion within the 'manifest' payload.
    Conceptually similar to C2PA assertions...
    """

    label: str  # e.g., "c2pa.created", "c2pa.transcribed"
    when: str  # ISO 8601 UTC format string


class ManifestAiInfo(TypedDict, total=False):
    """
    Optional structure for AI-specific info within the 'manifest' payload.
    """

    model_id: str
    model_version: Optional[str]


class ManifestPayload(TypedDict):
    """
    Structure for the 'manifest' metadata format payload.
    Inspired by C2PA manifests...
    """

    claim_generator: str
    assertions: List[ManifestAction]
    ai_assertion: Optional[ManifestAiInfo]
    custom_claims: Dict[str, Any]
    timestamp: Optional[str]  # ISO 8601 UTC format string


# --- New C2PA v2.2 compliant TypedDicts ---


class C2PAAssertion(TypedDict):
    """Structure for a C2PA assertion."""

    label: str
    data: Dict[str, Any]
    kind: Optional[str]


C2PAPayload = TypedDict(
    "C2PAPayload",
    {
        "@context": str,
        "instance_id": str,
        "claim_generator": str,
        "assertions": List[C2PAAssertion],
    },
)


# Specific assertion data TypedDicts for clarity
class C2PAActionsAssertionData(TypedDict):
    actions: List[Dict[str, Any]]


class C2PAHashDataAssertionData(TypedDict):
    hash: str
    alg: str
    exclusions: List[Any]


class C2PASoftBindingAssertionData(TypedDict):
    alg: str
    hash: str


# --- Union of all possible inner payload types for clarity ---
# This is for payloads that are dictionaries, not serialized strings.
InnerPayloadTypes = Union[BasicPayload, ManifestPayload, C2PAPayload]


class OuterPayload(TypedDict):
    """
    The complete outer structure embedded into the text.
    This structure is designed to be backward-compatible and extensible.
    """

    # The format literal is extended to include new formats.
    format: Literal["basic", "manifest", "cbor_manifest", "c2pa_v2_2"]
    signer_id: str
    # The payload can be a dictionary for JSON-based formats, or a
    # base64-encoded string for binary formats like CBOR.
    payload: Union[BasicPayload, ManifestPayload, str]
    signature: str  # Base64 encoded signature string


# --- End TypedDict Definitions ---


# --- Serialization Functions ---


def serialize_payload(payload: Dict[str, Any]) -> bytes:
    """
    Serializes the metadata payload dictionary into canonical JSON bytes.
    This is used for 'basic' and 'manifest' formats.
    Ensures keys are sorted and uses compact separators for consistency.
    """
    payload_type = type(payload).__name__
    logger.debug(f"Attempting to serialize JSON payload of type: {payload_type}")
    try:
        # Using sort_keys=True and compact separators for canonical form
        serialized_data = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        logger.debug(f"Successfully serialized JSON payload of type {payload_type}, length: {len(serialized_data)} bytes.")
        return serialized_data
    except TypeError as e:
        logger.error(f"Serialization failed for payload type {payload_type} due to non-serializable content: {e}", exc_info=True)
        raise TypeError(f"Payload of type {payload_type} is not JSON serializable: {e}")
    except Exception as e:
        logger.error(
            f"Unexpected error during serialization of {payload_type}: {e}",
            exc_info=True,
        )
        raise RuntimeError(f"Unexpected error serializing payload of type {payload_type}: {e}")


# New serialization functions for C2PA
def serialize_c2pa_payload_to_cbor(payload: C2PAPayload) -> bytes:
    """Serializes a C2PAPayload TypedDict into a CBOR byte string."""
    logger.debug("Attempting to serialize C2PA payload to CBOR.")
    try:
        cbor_bytes = cbor2.dumps(payload)
        logger.debug(f"Successfully serialized C2PA payload to CBOR, length: {len(cbor_bytes)} bytes.")
        return bytes(cbor_bytes)
    except Exception as e:
        logger.error(f"Unexpected error during C2PA CBOR serialization: {e}", exc_info=True)
        raise RuntimeError(f"Unexpected error serializing C2PA payload to CBOR: {e}")


def deserialize_c2pa_payload_from_cbor(cbor_bytes: bytes) -> C2PAPayload:
    """Deserializes a CBOR byte string into a C2PAPayload TypedDict."""
    logger.debug(f"Attempting to deserialize {len(cbor_bytes)} bytes from CBOR to C2PA payload.")
    try:
        payload = cbor2.loads(cbor_bytes)
        # Basic validation to ensure it looks like our payload
        if not isinstance(payload, dict) or "assertions" not in payload:
            logger.warning("Deserialized CBOR data does not appear to be a valid C2PA payload.")
            # Fall through and let the type checker/caller handle it, but log a warning.
        logger.debug("Successfully deserialized CBOR to C2PA payload.")
        return cast(C2PAPayload, payload)  # Ensure type safety with explicit cast
    except cbor2.CBORDecodeError as e:
        logger.error(f"CBOR decoding failed: {e}", exc_info=True)
        raise ValueError(f"Failed to decode CBOR bytes: {e}")
    except Exception as e:
        logger.error(f"Unexpected error during C2PA CBOR deserialization: {e}", exc_info=True)
        raise RuntimeError(f"Unexpected error deserializing C2PA payload from CBOR: {e}")
