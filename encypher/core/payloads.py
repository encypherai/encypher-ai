import json
from typing import Any, Dict, List, Literal, Optional, TypedDict, Union

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


class OuterPayload(TypedDict):
    """
    The complete outer structure embedded into the text.
    """

    format: Literal["basic", "manifest"]
    signer_id: str
    payload: Union[BasicPayload, ManifestPayload]  # The signed part
    signature: str  # Base64 encoded signature string


# --- End TypedDict Definitions ---


def serialize_payload(payload: Dict[str, Any]) -> bytes:
    """
    Serializes the metadata payload dictionary into canonical JSON bytes.
    Ensures keys are sorted and uses compact separators for consistency.
    """
    payload_type = type(payload).__name__
    logger.debug(f"Attempting to serialize payload of type: {payload_type}")
    try:
        # Using sort_keys=True and compact separators for canonical form
        serialized_data = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        logger.debug(f"Successfully serialized payload of type {payload_type}, length: {len(serialized_data)} bytes.")
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
