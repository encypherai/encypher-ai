"""
Unicode Metadata Embedding Utility for EncypherAI

This module provides utilities for embedding metadata (model info, timestamps)
into text using Unicode variation selectors without affecting readability.
"""

import base64
import binascii
import copy
import hashlib
import hmac
import json
import re
import uuid
import warnings
from datetime import date, datetime, timezone
from typing import Any, Callable, Dict, List, Literal, Optional, Tuple, Union, cast

import cbor2
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives.asymmetric.types import PrivateKeyTypes
from deprecated import deprecated
from pycose.messages import CoseMessage

from encypher import __version__

from .constants import MetadataTarget
from .logging_config import logger
from .payloads import (
    BasicPayload,
    C2PAAssertion,
    C2PAPayload,
    ManifestPayload,
    OuterPayload,
    deserialize_c2pa_payload_from_cbor,
    serialize_c2pa_payload_to_cbor,
    serialize_payload,
)
from .signing import extract_payload_from_cose_sign1, sign_c2pa_cose, sign_payload, verify_c2pa_cose, verify_signature


class UnicodeMetadata:
    """
    Utility class for embedding and extracting metadata using Unicode
    variation selectors.
    """

    # Variation selectors block (VS1-VS16: U+FE00 to U+FE0F)
    VARIATION_SELECTOR_START: int = 0xFE00
    VARIATION_SELECTOR_END: int = 0xFE0F

    # Variation selectors supplement (VS17-VS256: U+E0100 to U+E01EF)
    VARIATION_SELECTOR_SUPPLEMENT_START: int = 0xE0100
    VARIATION_SELECTOR_SUPPLEMENT_END: int = 0xE01EF

    # Regular expressions for different target types
    REGEX_PATTERNS: Dict[MetadataTarget, re.Pattern] = {
        MetadataTarget.WHITESPACE: re.compile(r"(\s)"),
        MetadataTarget.PUNCTUATION: re.compile(r"([.,!?;:])"),
        MetadataTarget.FIRST_LETTER: re.compile(r"(\b\w)"),
        MetadataTarget.LAST_LETTER: re.compile(r"(\w\b)"),
        MetadataTarget.ALL_CHARACTERS: re.compile(r"(.)"),
    }

    @classmethod
    def to_variation_selector(cls, byte: int) -> Optional[str]:
        """
        Convert a byte to a variation selector character

        Args:
            byte: Byte value (0-255)

        Returns:
            Unicode variation selector character or None if byte is out of range
        """
        if 0 <= byte < 16:
            return chr(cls.VARIATION_SELECTOR_START + byte)
        elif 16 <= byte < 256:
            return chr(cls.VARIATION_SELECTOR_SUPPLEMENT_START + byte - 16)
        else:
            return None

    @classmethod
    def from_variation_selector(cls, code_point: int) -> Optional[int]:
        """
        Convert a variation selector code point to a byte

        Args:
            code_point: Unicode code point

        Returns:
            Byte value (0-255) or None if not a variation selector
        """
        if cls.VARIATION_SELECTOR_START <= code_point <= cls.VARIATION_SELECTOR_END:
            return code_point - cls.VARIATION_SELECTOR_START
        elif cls.VARIATION_SELECTOR_SUPPLEMENT_START <= code_point <= cls.VARIATION_SELECTOR_SUPPLEMENT_END:
            return (code_point - cls.VARIATION_SELECTOR_SUPPLEMENT_START) + 16
        else:
            return None

    @classmethod
    def encode(cls, emoji: str, text: str) -> str:
        """
        Encode text into an emoji using Unicode variation selectors

        Args:
            emoji: Base character to encode the text into
            text: Text to encode

        Returns:
            Encoded string with the text hidden in variation selectors
        """
        # Convert the string to UTF-8 bytes
        bytes_data = text.encode("utf-8")

        # Start with the emoji
        encoded = emoji

        # Add variation selectors for each byte
        for byte in bytes_data:
            vs = cls.to_variation_selector(byte)
            if vs:
                encoded += vs

        return encoded

    @classmethod
    def decode(cls, text: str) -> str:
        """
        Decode text from Unicode variation selectors

        Args:
            text: Text with embedded variation selectors

        Returns:
            Decoded text
        """
        # Extract bytes from variation selectors
        decoded: List[int] = []

        for char in text:
            code_point = ord(char)
            byte = cls.from_variation_selector(code_point)

            # If we've found a non-variation selector after we've started
            # collecting bytes, we're done
            if byte is None and len(decoded) > 0:
                break
            # If it's not a variation selector and we haven't started collecting
            # bytes yet, it's probably the base character (emoji), so skip it
            elif byte is None:
                continue

            decoded.append(byte)

        # Convert bytes back to text
        if decoded:
            return bytes(decoded).decode("utf-8")
        else:
            return ""

    @classmethod
    def extract_bytes(cls, text: str) -> bytes:
        """
        Extract bytes from Unicode variation selectors

        Args:
            text: Text with embedded variation selectors

        Returns:
            Bytes extracted from variation selectors
        """
        # Extract bytes from variation selectors
        decoded: List[int] = []

        # First try the standard approach: find variation selectors interleaved in text
        for char in text:
            code_point = ord(char)
            byte = cls.from_variation_selector(code_point)

            # If we've found a non-variation selector after we've started
            # collecting bytes, we're done
            if byte is None and len(decoded) > 0:
                break
            # If it's not a variation selector and we haven't started collecting
            # bytes yet, it's probably the base character (emoji), so skip it
            elif byte is None:
                continue

            decoded.append(byte)

        # If we found bytes using the standard approach, return them
        if decoded:
            return bytes(decoded)

        # Fallback approach: Check for variation selectors appended at the end of the text
        # This handles the fallback embedding strategy where selectors are appended to the end
        decoded = []

        # Start from the end of the text and collect all consecutive variation selectors
        for i in range(len(text) - 1, -1, -1):
            char = text[i]
            code_point = ord(char)
            byte = cls.from_variation_selector(code_point)

            # If not a variation selector, stop collecting
            if byte is None:
                break

            decoded.insert(0, byte)  # Insert at beginning to maintain order

        # Convert bytes back to bytes object
        if decoded:
            logger.debug(f"Extracted {len(decoded)} bytes from variation selectors at end of text.")
            return bytes(decoded)
        else:
            return b""

    @classmethod
    def _format_timestamp(cls, ts: Optional[Union[str, datetime, date, int, float]]) -> Optional[str]:
        """Helper to format various timestamp inputs into ISO 8601 UTC string.

        Args:
            ts: The timestamp input. Can be None, an ISO 8601 string,
                a datetime object, a date object, or an int/float epoch
                timestamp.

        Returns:
            The timestamp formatted as an ISO 8601 string in UTC (e.g., "YYYY-MM-DDTHH:MM:SSZ"),
            or None if the input was None.

        Raises:
            ValueError: If the input is an invalid timestamp value or format.
            TypeError: If the input type is not supported.
        """
        if ts is None:
            return None

        dt: Optional[datetime] = None
        if isinstance(ts, datetime):
            dt = ts
        elif isinstance(ts, date):
            # Assume start of day if only date is given
            dt = datetime.combine(ts, datetime.min.time())
        elif isinstance(ts, (int, float)):
            try:
                # Assume UTC if timezone not specified for epoch
                dt = datetime.fromtimestamp(ts, tz=timezone.utc)
            except (OSError, ValueError):
                # Handle potential errors like invalid timestamp value
                raise ValueError(f"Invalid timestamp value: {ts}")
        elif isinstance(ts, str):
            try:
                # Attempt to parse ISO 8601 format
                dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            except ValueError:
                # If parsing fails, raise error - we need a consistent format
                raise ValueError(f"Invalid timestamp string format: {ts}. Use ISO 8601.")
        else:
            raise TypeError(f"Unsupported timestamp type: {type(ts)}")

        # Ensure timezone is UTC
        if dt.tzinfo is None:
            # Assume UTC if naive, or raise error if local timezone is ambiguous?
            # Let's assume UTC for simplicity here, but could be configurable.
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            dt = dt.astimezone(timezone.utc)

        # Format as ISO 8601 with 'Z' for UTC
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")  # Simplified ISO format

    @classmethod
    def _strip_variation_selectors(cls, text: str) -> str:
        """Removes all Unicode variation selectors from a string."""
        # This regex matches characters in the VS1-VS16 and VS17-VS256 ranges.
        pattern = re.compile(r"[\uFE00-\uFE0F\U000E0100-\U000E01EF]")
        return pattern.sub("", text)

    @staticmethod
    def _omit_keys_recursive(data: Union[Dict[str, Any], List[Any]], keys: List[str]) -> None:
        """Recursively remove specified keys from nested dictionaries."""
        if isinstance(data, dict):
            for k in list(data.keys()):
                if k in keys:
                    data.pop(k, None)
                else:
                    v = data[k]
                    if isinstance(v, (dict, list)):
                        UnicodeMetadata._omit_keys_recursive(v, keys)
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, (dict, list)):
                    UnicodeMetadata._omit_keys_recursive(item, keys)

    @classmethod
    def find_targets(
        cls,
        text: str,
        target: Optional[Union[str, MetadataTarget]] = None,
    ) -> List[int]:
        """
        Find indices of characters in text where metadata can be embedded.

        Args:
            text: The text to find targets in.
            target: Where to embed metadata ('whitespace', 'punctuation', etc.,
                    or MetadataTarget enum).

        Returns:
            List of indices where metadata can be embedded.

        Raises:
            ValueError: If target is an invalid string.
        """
        if target is None:
            target_enum = MetadataTarget.WHITESPACE  # Keep track of the enum value
        elif isinstance(target, MetadataTarget):
            target_enum = target
        elif isinstance(target, str):
            try:
                target_enum = MetadataTarget(target.lower())  # Convert string to enum
            except ValueError:
                valid_targets = [t.name for t in MetadataTarget]
                raise ValueError(f"Invalid target: {target}. Must be one of {valid_targets}.")
        else:
            raise TypeError("'target' must be a string or MetadataTarget enum member.")

        pattern = cls.REGEX_PATTERNS[target_enum]
        matches = pattern.finditer(text)

        indices = []
        for match in matches:
            indices.append(match.start())

        return indices

    @classmethod
    def embed_metadata(
        cls,
        text: str,
        private_key: PrivateKeyTypes,
        signer_id: str,
        metadata_format: Literal["basic", "manifest", "cbor_manifest", "c2pa_v2_2"] = "manifest",
        model_id: Optional[str] = None,
        timestamp: Optional[Union[str, datetime, date, int, float]] = None,
        target: Optional[Union[str, MetadataTarget]] = None,
        custom_metadata: Optional[Dict[str, Any]] = None,
        claim_generator: Optional[str] = None,
        actions: Optional[List[Dict[str, Any]]] = None,
        ai_info: Optional[Dict[str, Any]] = None,
        custom_claims: Optional[Dict[str, Any]] = None,
        omit_keys: Optional[List[str]] = None,
        distribute_across_targets: bool = False,
        add_hard_binding: bool = True,  # New parameter
    ) -> str:
        """
        Embed metadata into text using Unicode variation selectors, signing with a private key.

        When using 'manifest' format, this method implements a C2PA-inspired approach for
        content provenance and authenticity, adapted specifically for plain-text environments
        where traditional file-based embedding methods aren't applicable. The manifest structure
        parallels C2PA's concepts of assertions, claim generators, and cryptographic integrity.

        Args:
            text: The text to embed metadata into.
            private_key: The Ed25519 private key object for signing.
            signer_id: A string identifying the signer/key pair (used for
                       verification lookup).
            metadata_format: The format for the metadata payload ('basic' or 'manifest').
                             Default is 'manifest'. When set to 'manifest', uses a
                             C2PA-inspired structured format.
            model_id: Model identifier (used in 'basic' and optionally in
                      'manifest' ai_info).
            timestamp: Timestamp (datetime, ISO string, int/float epoch). Stored as
                       ISO 8601 UTC string.
                       **This field is mandatory.**
            target: Where to embed metadata ('whitespace', 'punctuation', etc.,
                    or MetadataTarget enum).
            custom_metadata: Dictionary for custom fields (used in 'basic' payload).
            claim_generator: Claim generator string (used in 'manifest' format).
                             Similar to C2PA's concept of identifying the
                             software/tool that generated the claim.
            actions: List of action dictionaries (used in 'manifest' format).
                     Conceptually similar to C2PA assertions about operations
                     performed on the content.
            ai_info: Dictionary with AI-specific info (used in 'manifest' format).
                     Represents a custom assertion type focused on AI-specific
                     attributes.
            custom_claims: Dictionary for custom C2PA-like claims (used in
                           'manifest' format).
            omit_keys: List of metadata keys to omit from the payload prior to
                        signing. Required fields like 'signer_id' and
                        'timestamp' cannot be omitted.
            distribute_across_targets: If True, distribute bits across multiple
                                       targets if needed.
            add_hard_binding: If True, include the hard binding assertion in the
                              manifest. Default is True.

        Returns:
            The text with embedded metadata and digital signature.

        Raises:
            ValueError: If 'timestamp' is not provided, if the target is invalid,
                        if not enough embedding locations are found, or if the
                        metadata + signature is too large.
        """
        logger.debug(
            f"embed_metadata called with text (type={type(text).__name__}), signer_id='{signer_id}', "
            f"format='{metadata_format}', target='{target}', distribute={distribute_across_targets}"
        )

        if metadata_format == "c2pa_v2_2":
            # Convert timestamp once for C2PA-specific embedding
            try:
                iso_timestamp = cls._format_timestamp(timestamp)
                if iso_timestamp is None:
                    raise ValueError("A 'timestamp' must be provided for C2PA embedding.")
            except (ValueError, TypeError) as e:
                logger.error(f"Timestamp error: {e}", exc_info=True)
                raise ValueError(f"Timestamp error: {e}")

            return cls._embed_c2pa_v2_2(
                text=text,
                private_key=private_key,
                signer_id=signer_id,
                claim_generator=claim_generator,
                actions=actions,
                iso_timestamp=iso_timestamp,
                target=target,
                distribute_across_targets=distribute_across_targets,
                add_hard_binding=add_hard_binding,
            )
        # --- Start: Input Validation ---
        if not isinstance(text, str):
            logger.error("Input validation failed: 'text' is not a string.")
            raise TypeError("Input text must be a string")
        if not isinstance(private_key, Ed25519PrivateKey):
            # Note: PrivateKeyTypes is broader, but we specifically need Ed25519 here for signing.
            logger.error("Input validation failed: 'private_key' is not an Ed25519PrivateKey instance.")
            raise TypeError("Input 'private_key' must be an Ed25519PrivateKey instance.")
        if not signer_id or not isinstance(signer_id, str):
            # Enhanced to check type as well
            logger.error("Input validation failed: 'signer_id' is not a non-empty string.")
            raise ValueError("A non-empty string 'signer_id' must be provided.")

        if timestamp is None:
            logger.error("Input validation failed: 'timestamp' is not provided.")
            raise ValueError("A 'timestamp' must be provided for metadata embedding.")

        # Validate target
        if target is None:
            pass  # Keep track of the enum value
        elif isinstance(target, MetadataTarget):
            pass
        elif isinstance(target, str):
            try:
                MetadataTarget(target.lower())  # Convert string to enum
            except ValueError:
                valid_targets = [t.name for t in MetadataTarget]
                logger.error(f"Invalid target: {target}. Must be one of {valid_targets}.")
                raise ValueError(f"Invalid target: {target}. Must be one of {valid_targets}.")
        else:
            logger.error("'target' must be a string or MetadataTarget enum member.")
            raise TypeError("'target' must be a string or MetadataTarget enum member.")

        if metadata_format not in ("basic", "manifest", "cbor_manifest", "c2pa_v2_2"):
            logger.error("metadata_format must be 'basic', 'manifest', 'cbor_manifest', or 'c2pa_v2_2'.")
            raise ValueError("metadata_format must be 'basic', 'manifest', 'cbor_manifest', or 'c2pa_v2_2'.")

        if model_id is not None and not isinstance(model_id, str):
            logger.error("If provided, 'model_id' must be a string.")
            raise TypeError("If provided, 'model_id' must be a string.")

        if not isinstance(distribute_across_targets, bool):
            logger.error("'distribute_across_targets' must be a boolean.")
            raise TypeError("'distribute_across_targets' must be a boolean.")

        if omit_keys is not None:
            if not isinstance(omit_keys, list) or not all(isinstance(k, str) for k in omit_keys):
                raise TypeError("'omit_keys' must be a list of strings if provided.")
            mandatory = {"signer_id", "timestamp", "format"}
            if any(k in mandatory for k in omit_keys):
                raise ValueError("Cannot omit required metadata fields: signer_id, timestamp, or format")

        # Convert timestamp
        try:
            iso_timestamp = cls._format_timestamp(timestamp)
        except (ValueError, TypeError) as e:
            logger.error(f"Timestamp error: {e}", exc_info=True)
            raise ValueError(f"Timestamp error: {e}")

        payload_data: Dict[str, Any]  # Use Dict[str, Any] for flexible construction

        if metadata_format == "basic":
            logger.debug("Using 'basic' metadata format.")
            payload_data = {
                "signer_id": signer_id,
                "timestamp": iso_timestamp,
                "format": metadata_format,  # Explicitly include format
            }
            if model_id:
                payload_data["model_id"] = model_id
            if custom_metadata:
                # Merge custom metadata, ensuring no overlaps with standard keys
                standard_keys = {"signer_id", "timestamp", "format", "model_id"}
                if any(key in standard_keys for key in custom_metadata):
                    logger.warning("Custom metadata keys overlap with standard keys.")
                    # Prioritize standard keys; filter out overlaps from custom
                    filtered_custom = {k: v for k, v in custom_metadata.items() if k not in standard_keys}
                    payload_data["custom_metadata"] = filtered_custom
                else:
                    payload_data["custom_metadata"] = custom_metadata
        elif metadata_format == "manifest":
            logger.debug("Using 'manifest' metadata format.")
            # Ensure timestamp is in the correct format
            iso_timestamp = cls._format_timestamp(timestamp)

            # 1. Construct the main payload structure
            payload_data = {
                "signer_id": signer_id,
                "timestamp": iso_timestamp,
                "format": metadata_format,  # Keep format for clarity
            }

            # 2. Construct the inner manifest dictionary
            inner_manifest: Dict[str, Any] = {}
            if claim_generator:
                inner_manifest["claim_generator"] = claim_generator
            if actions:
                inner_manifest["actions"] = actions
            if ai_info:
                inner_manifest["ai_info"] = ai_info
            if custom_claims:
                inner_manifest["custom_claims"] = custom_claims
            if model_id:  # Optionally include model_id within manifest
                # Decide where it fits best, e.g., under ai_info or top-level
                if "ai_info" not in inner_manifest:
                    inner_manifest["ai_info"] = {}
                inner_manifest["ai_info"]["model_id"] = model_id

            # 3. **Crucial Change:** Add the inner manifest dictionary directly
            #    Do NOT serialize the inner manifest separately here.
            payload_data["manifest"] = inner_manifest  # Add the dict, not serialized bytes
        elif metadata_format == "cbor_manifest":
            logger.debug("Using 'cbor_manifest' metadata format.")
            # Construct payload_data dictionary similar to 'manifest'
            iso_timestamp = cls._format_timestamp(timestamp)
            payload_data = {
                "signer_id": signer_id,
                "timestamp": iso_timestamp,
                "format": "manifest",  # Internally, it's a manifest structure before CBOR encoding
            }
            cbor_manifest_dict: Dict[str, Any] = {}
            if claim_generator:
                cbor_manifest_dict["claim_generator"] = claim_generator
            if actions:
                cbor_manifest_dict["actions"] = actions
            if ai_info:
                cbor_manifest_dict["ai_info"] = ai_info
            if custom_claims:
                cbor_manifest_dict["custom_claims"] = custom_claims
            if model_id:
                if "ai_info" not in cbor_manifest_dict:
                    cbor_manifest_dict["ai_info"] = {}
                cbor_manifest_dict["ai_info"]["model_id"] = model_id
            payload_data["manifest"] = cbor_manifest_dict
            # The actual CBOR processing will happen during signing/packaging
        else:
            logger.error(f"Unsupported metadata_format: {metadata_format}")
            raise ValueError(f"Unsupported metadata_format: {metadata_format}")

        # --- End: Payload Construction ---

        if omit_keys:
            cls._omit_keys_recursive(payload_data, omit_keys)

        # --- Start: Signing & Packaging Logic based on format ---

        # --- Start: Signing & Packaging Logic based on format ---
        signature_b64: str
        payload_for_outer_dict: Union[Dict[str, Any], str]
        actual_payload_type_for_outer: str

        if metadata_format == "cbor_manifest":
            try:
                # payload_data is the manifest dictionary constructed earlier
                # 1. Serialize the manifest dictionary to CBOR bytes
                cbor_manifest_bytes = cbor2.dumps(payload_data)
                logger.debug(f"CBOR serialized manifest size: {len(cbor_manifest_bytes)} bytes")

                # 2. Sign these raw CBOR bytes
                # ASSUMPTION: sign_payload will be adapted to handle raw bytes if Union[PrivateKeyTypes, bytes] is passed,
                # or a new function like sign_raw_payload(private_key, cbor_manifest_bytes) will be used.
                signature = sign_payload(private_key, cbor_manifest_bytes)
                signature_b64 = base64.urlsafe_b64encode(signature).rstrip(b"=").decode("ascii")
                logger.debug(f"CBOR Manifest signed successfully. Signature (base64): {signature_b64[:10]}...")

                # 3. Base64 encode the CBOR bytes for the 'payload' field in the outer dict
                payload_for_outer_dict = base64.b64encode(cbor_manifest_bytes).decode("utf-8")
                actual_payload_type_for_outer = "cbor_manifest"  # This is the new type for the outer package
            except Exception as e:
                logger.exception("Failed to process or sign CBOR manifest payload.")
                raise RuntimeError(f"Failed to process or sign CBOR manifest payload: {e}") from e
        else:  # For "basic" or "manifest" (JSON-based)
            try:
                # Serialize the *complete* payload (basic or manifest dict) to canonical JSON bytes
                canonical_payload_bytes = serialize_payload(dict(payload_data))
                signature = sign_payload(private_key, canonical_payload_bytes)
                signature_b64 = base64.urlsafe_b64encode(signature).rstrip(b"=").decode("ascii")
                logger.debug(f"Payload signed successfully. Signature (base64): {signature_b64[:10]}...")

                payload_for_outer_dict = payload_data  # The dictionary itself for JSON-based formats
                actual_payload_type_for_outer = metadata_format  # "basic" or "manifest"
            except Exception as e:
                logger.exception("Failed to sign the metadata payload.")
                raise RuntimeError(f"Failed to sign metadata payload: {e}") from e

        # --- End: Conditional Signing Logic ---

        # --- Start: Combine Payload and Signature for Embedding (Outer Structure) ---
        # This outer_payload_to_embed is what gets JSON serialized, then b64 encoded for steganography.
        outer_payload_to_embed = {
            "payload": payload_for_outer_dict,  # Either dict (for JSON) or b64_str (for CBOR_manifest)
            "signature": signature_b64,
            "signer_id": signer_id,
            "format": actual_payload_type_for_outer,  # "basic", "manifest", or "cbor_manifest"
        }

        # 6. Serialize the Outer Object:
        try:
            outer_bytes = serialize_payload(dict(outer_payload_to_embed))
        except Exception as e:
            logger.error(f"Failed to serialize outer payload: {e}", exc_info=True)
            raise RuntimeError(f"Failed to serialize outer payload: {e}")

        logger.debug(f"Serialized outer payload size: {len(outer_bytes)} bytes")

        # 7. Convert Outer Bytes to Variation Selectors:
        try:
            selector_chars = cls._bytes_to_variation_selectors(outer_bytes)
        except ValueError as e:
            # Handle potential errors from the helper
            logger.error(f"Failed to convert metadata bytes to selectors: {e}", exc_info=True)
            raise RuntimeError(f"Failed to convert metadata bytes to selectors: {e}")

        if not selector_chars:
            # Nothing to embed, return original text
            return text

        # 9. Find Embedding Targets:
        # Use the existing find_targets, but ensure target is passed correctly
        embedding_target = target if target is not None else MetadataTarget.WHITESPACE
        try:
            # find_targets now returns list of indices
            target_indices = cls.find_targets(text, embedding_target)
        except ValueError as e:
            # Propagate errors from find_targets (e.g., invalid target string)
            logger.error(f"Failed to find embedding targets: {e}", exc_info=True)
            raise ValueError(f"Failed to find embedding targets: {e}")

        target_display = embedding_target.value if hasattr(embedding_target, "value") else embedding_target
        logger.debug(f"Found {len(target_indices)} potential embedding targets using '{target_display}'.")

        # 10. Check if at least one target was found & Embed Selectors into Text:
        if not target_indices:
            err_msg = (
                f"No suitable targets found in text using target '{target_display}'. "
                f"Need at least one target to embed metadata of length {len(selector_chars)}."
            )
            logger.error(err_msg)
            raise ValueError(err_msg)

        if distribute_across_targets:
            # Original approach: distribute across multiple targets
            if len(target_indices) < len(selector_chars):
                err_msg = (
                    f"Not enough targets ({len(target_indices)}) found in text "
                    f"to embed metadata of length {len(selector_chars)} "
                    f"using target '{target_display}'. Required: {len(selector_chars)}."
                )
                logger.error(err_msg)
                raise ValueError(err_msg)

            # Build the result string with interleaved selectors
            result_parts = []
            last_text_idx = 0
            selector_idx = 0

            # Sort targets by index to process text sequentially
            target_indices.sort()

            for target_idx in target_indices:
                if selector_idx < len(selector_chars):
                    # Add text segment before the target insertion point
                    result_parts.append(text[last_text_idx:target_idx])
                    # Add the target character followed by the variation selector
                    result_parts.append(text[target_idx])
                    result_parts.append(selector_chars[selector_idx])
                    # Update indices
                    last_text_idx = target_idx + 1  # Skip the original character at target_idx
                    selector_idx += 1
                else:
                    # Once all data is embedded, stop processing targets
                    break

            # Add any remaining text after the last embedding point
            result_parts.append(text[last_text_idx:])
            result = "".join(result_parts)
            logger.info(f"Successfully embedded metadata (distributed) for signer '{signer_id}'.")
            return result
        else:
            # New default approach: embed all metadata after the first target
            target_idx = target_indices[0]

            # Build the result string with all selectors after the first target character
            # Keep the target character and add all selectors immediately after it
            result = text[: target_idx + 1] + "".join(selector_chars) + text[target_idx + 1 :]
            logger.info(f"Successfully embedded metadata (single-point) for signer '{signer_id}'.")
            return result

    @classmethod
    def _embed_c2pa_v2_2(
        cls,
        text: str,
        private_key: PrivateKeyTypes,
        signer_id: str,
        claim_generator: Optional[str],
        actions: Optional[List[Dict[str, Any]]],
        iso_timestamp: str,
        target: Optional[Union[str, MetadataTarget]],
        distribute_across_targets: bool,
        add_hard_binding: bool,  # New parameter
    ) -> str:
        """
        Constructs and embeds a C2PA v2.2 compliant manifest.

        This internal method orchestrates the creation of a C2PA manifest, including
        mandatory assertions, content hashing (hard binding), and a soft binding
        hash. The resulting manifest is serialized to CBOR, signed, and then
        embedded into the text using Unicode variation selectors.

        Args:
            text: The original, clean text content to be watermarked.
            private_key: The Ed25519 private key for signing the manifest.
            signer_id: An identifier for the key pair.
            claim_generator: A string identifying the software agent creating the claim.
            actions: A list of action dictionaries to include in the manifest.
            iso_timestamp: The ISO 8601 formatted timestamp for the actions.
            target: The embedding target strategy.
            distribute_across_targets: If True, distribute bits across multiple targets.
            add_hard_binding: If True, include the hard binding assertion in the manifest.

        Returns:
            The text with the embedded C2PA manifest.
        """
        if not isinstance(private_key, ed25519.Ed25519PrivateKey):
            raise TypeError("For C2PA v2.2 embedding, 'private_key' must be an Ed25519PrivateKey instance.")

        # --- 1. Construct the C2PA Manifest ---
        c2pa_manifest: C2PAPayload = {
            "@context": "https://c2pa.org/schemas/v2.2/c2pa.jsonld",
            "instance_id": str(uuid.uuid4()),
            "claim_generator": claim_generator or f"encypher-ai/{__version__}",
            "assertions": [],
        }

        # --- 2. Build Mandatory Assertions ---
        # a) c2pa.actions.v1 assertion
        actions_data: Dict[str, Any] = {"actions": actions if actions is not None else []}
        if not any(a.get("label") == "c2pa.created" for a in actions_data["actions"]):
            actions_data["actions"].insert(
                0,
                {
                    "label": "c2pa.created",
                    "when": iso_timestamp,
                    "digitalSourceType": "http://cv.iptc.org/newscodes/digitalsourcetype/trainedAlgorithmicMedia",
                    "softwareAgent": c2pa_manifest["claim_generator"],
                },
            )
        c2pa_manifest["assertions"].append({"label": "c2pa.actions.v1", "data": actions_data, "kind": "Actions"})

        # b) c2pa.hash.data.v1 (Hard Binding)
        if add_hard_binding:
            clean_text_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
            c2pa_manifest["assertions"].append(
                {"label": "c2pa.hash.data.v1", "data": {"hash": clean_text_hash, "alg": "sha256", "exclusions": []}, "kind": "ContentHash"}
            )

        # --- 3. Prepare for Soft Binding (Deterministic Hashing) ---
        # a) Create a temporary manifest copy that includes a placeholder soft binding.
        manifest_for_hashing = copy.deepcopy(c2pa_manifest)

        # b) Add the placeholder soft binding and watermarked action to the copy.
        placeholder_soft_binding: "C2PAAssertion" = {
            "label": "c2pa.soft_binding.v1",
            "data": {"alg": "encypher.unicode_variation_selector.v1", "hash": ""},
            "kind": "SoftBinding",
        }
        manifest_for_hashing["assertions"].append(placeholder_soft_binding)

        actions_data_copy = next((a["data"] for a in manifest_for_hashing["assertions"] if a["label"] == "c2pa.actions.v1"), None)
        if actions_data_copy and isinstance(actions_data_copy.get("actions"), list):
            actions_data_copy["actions"].append(
                {
                    "label": "c2pa.watermarked",
                    "when": iso_timestamp,
                    "softwareAgent": c2pa_manifest["claim_generator"],
                    "description": "Text embedded with Unicode variation selectors.",
                }
            )

        # c) Serialize the modified manifest and calculate the definitive hash.
        cbor_for_hashing = serialize_c2pa_payload_to_cbor(manifest_for_hashing)
        actual_soft_binding_hash = hashlib.sha256(cbor_for_hashing).hexdigest()

        # d) Create the final soft binding assertion with the real hash.
        final_soft_binding_assertion: "C2PAAssertion" = {
            "label": "c2pa.soft_binding.v1",
            "data": {"alg": "encypher.unicode_variation_selector.v1", "hash": actual_soft_binding_hash},
            "kind": "SoftBinding",
        }
        c2pa_manifest["assertions"].append(final_soft_binding_assertion)

        # e) Add the 'watermarked' action to the original manifest.
        actions_data["actions"].append(
            {
                "label": "c2pa.watermarked",
                "when": iso_timestamp,
                "softwareAgent": c2pa_manifest["claim_generator"],
                "description": "Text embedded with Unicode variation selectors.",
            }
        )

        # --- 4. Finalize, Serialize, and Sign ---
        # Re-serialize the final manifest, which now includes the correct soft binding hash.
        final_cbor_payload_bytes = serialize_c2pa_payload_to_cbor(c2pa_manifest)

        # Sign the final CBOR payload using COSE_Sign1.
        cose_sign1_bytes = sign_c2pa_cose(private_key, final_cbor_payload_bytes)

        # --- 5. Package and Embed ---
        # The outer structure contains the signed COSE object.
        outer_payload_to_embed = {
            "cose_sign1": base64.b64encode(cose_sign1_bytes).decode("utf-8"),
            "signer_id": signer_id,
            "format": "c2pa_v2_2",
        }
        outer_bytes = serialize_payload(dict(outer_payload_to_embed))
        selector_chars = cls._bytes_to_variation_selectors(outer_bytes)

        # --- 6. Find Targets and Embed ---
        embedding_target = target if target is not None else MetadataTarget.WHITESPACE
        target_indices = cls.find_targets(text, embedding_target)
        target_display = embedding_target.value if hasattr(embedding_target, "value") else embedding_target

        if not target_indices:
            raise ValueError(f"No suitable targets found in text using target '{target_display}'.")

        # Ensure we have the original text in the output
        logger.debug(f"Embedding {len(selector_chars)} variation selectors into text")

        if distribute_across_targets:
            if len(target_indices) < len(selector_chars):
                raise ValueError(f"Not enough targets ({len(target_indices)}) found to distribute {len(selector_chars)} selectors.")
            result_parts = []
            last_text_idx = 0
            for i, target_idx in enumerate(target_indices):
                if i < len(selector_chars):
                    result_parts.append(text[last_text_idx : target_idx + 1])  # Include the target character
                    result_parts.append(selector_chars[i])  # Add the selector after the target
                    last_text_idx = target_idx + 1
                else:
                    break
            result_parts.append(text[last_text_idx:])  # Add remaining text
            return "".join(result_parts)
        else:
            # Insert all selectors after the first target character
            # Ensure the original text is preserved by keeping it intact and only adding selectors
            target_idx = target_indices[0]
            result = text[: target_idx + 1] + "".join(selector_chars) + text[target_idx + 1 :]

            # Verify the original text is preserved in the result
            if text not in result:
                logger.warning("Original text not preserved in embedding result. Adjusting embedding strategy.")
                # Alternative approach: append selectors at the end of text
                result = text + "".join(selector_chars)

            return result

    @classmethod
    def verify_metadata(
        cls,
        text: str,
        public_key_resolver: Callable[[str], Optional[Ed25519PublicKey]],
        return_payload_on_failure: bool = False,
        require_hard_binding: bool = True,
    ) -> Tuple[bool, Optional[str], Union[BasicPayload, ManifestPayload, C2PAPayload, None]]:
        """
        Verify and extract metadata from text embedded using Unicode variation selectors and a public key.

        Args:
            text: Text with embedded metadata
            public_key_resolver: A callable function that takes a signer_id (str)
                                 and returns the corresponding Ed25519PublicKey
                                 object or None if the key is not found.
            return_payload_on_failure: If True, return the payload even when verification fails.
            require_hard_binding: If True, require the hard binding assertion in C2PA manifests.

        Returns:
            A tuple containing:
            - Verification status (bool): True if the signature is valid, False otherwise.
            - The signer_id (str) found in the metadata, or None if extraction fails.
            - The extracted inner payload or None if extraction/verification fails.
        """
        logger.debug(f"verify_metadata called for text (len={len(text)}).")

        # --- Input Validation ---
        if not isinstance(text, str):
            raise TypeError("Input 'text' must be a string.")
        if not text:
            logger.debug("verify_metadata called with empty text, returning None.")
            return False, None, None

        # 1. Extract Outer Payload:
        outer_payload = cls._extract_outer_payload(text)
        if outer_payload is None:
            logger.debug("No outer payload found during extraction.")
            return False, None, None

        # 2. Extract Key Components from Outer Payload:
        payload_format = outer_payload.get("format")
        signer_id = outer_payload.get("signer_id")

        if not signer_id:
            logger.warning("No signer_id found in outer payload.")
            return False, None, None

        # --- Format-Specific Verification Dispatch ---
        if payload_format == "c2pa_v2_2":
            clean_text = cls._strip_variation_selectors(text)
            return cls._verify_c2pa_v2_2(
                text=clean_text,
                outer_payload=outer_payload,
                public_key_resolver=public_key_resolver,
                return_payload_on_failure=return_payload_on_failure,
                require_hard_binding=require_hard_binding,
            )

        # --- Legacy Format Verification ('basic', 'manifest', 'cbor_manifest') ---
        inner_payload = outer_payload.get("payload")
        signature_b64 = outer_payload.get("signature")

        # Prepare a payload for return in case of early failure.
        # It can only be a dict, not a string, to match the function signature.
        payload_for_early_failure: Optional[Union[BasicPayload, ManifestPayload]] = None
        if return_payload_on_failure and isinstance(inner_payload, dict):
            payload_for_early_failure = cast(Union[BasicPayload, ManifestPayload], inner_payload)

        if inner_payload is None or signature_b64 is None:
            logger.warning("Legacy payload is missing 'payload' or 'signature'.")
            return False, signer_id, None

        # 3. Look Up Public Key:
        try:
            public_key = public_key_resolver(signer_id)
        except Exception as e:
            logger.warning(f"public_key_resolver raised an exception for signer_id '{signer_id}': {e}", exc_info=True)
            return False, signer_id, cast(Union[BasicPayload, ManifestPayload, C2PAPayload, None], payload_for_early_failure)

        if public_key is None:
            logger.warning(f"Public key not found for signer_id: '{signer_id}'")
            return False, signer_id, cast(Union[BasicPayload, ManifestPayload, C2PAPayload, None], payload_for_early_failure)

        if not isinstance(public_key, Ed25519PublicKey):
            logger.error(f"public_key_resolver returned invalid type ({type(public_key)}) for signer_id '{signer_id}'")
            return False, signer_id, cast(Union[BasicPayload, ManifestPayload, C2PAPayload, None], payload_for_early_failure)

        # 4. Prepare Payload Bytes for Verification
        payload_to_verify_bytes: bytes
        actual_inner_payload: Union[Dict[str, Any], None] = None

        if payload_format == "cbor_manifest":
            if not isinstance(inner_payload, str):
                logger.error(f"CBOR manifest payload expected string, got {type(inner_payload)}.")
                return False, signer_id, None
            try:
                payload_to_verify_bytes = base64.b64decode(inner_payload.encode("utf-8"))
                # Load the CBOR data
                cbor_data = cbor2.loads(payload_to_verify_bytes)

                # For cbor_manifest format, we need to extract the actual manifest data
                # The structure should match what we created during embed_metadata
                if isinstance(cbor_data, dict) and "manifest" in cbor_data:
                    actual_inner_payload = cbor_data["manifest"]
                else:
                    # If the structure doesn't match what we expect, use the whole payload
                    actual_inner_payload = cbor_data
            except (binascii.Error, cbor2.CBORDecodeError) as e:
                logger.error(f"Failed to decode CBOR manifest payload: {e}")
                return False, signer_id, None
        elif payload_format in ("basic", "manifest"):
            if not isinstance(inner_payload, dict):
                logger.error(f"JSON payload ('{payload_format}') expected dict, got {type(inner_payload)}.")
                return False, signer_id, None
            try:
                payload_to_verify_bytes = serialize_payload(dict(inner_payload))
                # Create a new dict from the TypedDict's items to satisfy mypy's strict checking.
                # This is more explicit and robust than casting.
                actual_inner_payload = {k: v for k, v in inner_payload.items()}
            except Exception as e:
                logger.error(f"Failed to serialize '{payload_format}' payload for verification: {e}")
                return False, signer_id, inner_payload if return_payload_on_failure else None
        else:
            logger.error(f"Unknown payload format '{payload_format}' found during verification.")
            # Only return the payload if it's a dict, to match the function signature.
            payload_to_return = inner_payload if isinstance(inner_payload, dict) else None
            return (
                False,
                signer_id,
                cast(Union[BasicPayload, ManifestPayload, C2PAPayload, None], payload_to_return) if return_payload_on_failure else None,
            )

        # 5. Decode and Verify Signature
        try:
            signature_bytes = base64.urlsafe_b64decode(signature_b64 + "=" * (-len(signature_b64) % 4))
            is_valid = verify_signature(public_key, payload_to_verify_bytes, signature_bytes)
        except (binascii.Error, InvalidSignature, TypeError) as e:
            logger.warning(f"Signature verification failed for signer_id '{signer_id}': {e}")
            is_valid = False

        # 6. Return Result
        if is_valid:
            logger.info(f"Signature verified successfully for signer_id: '{signer_id}', format: '{payload_format}'.")
            return True, signer_id, cast(Union[BasicPayload, ManifestPayload, C2PAPayload, None], actual_inner_payload)
        else:
            logger.warning(f"Signature verification failed for signer_id: '{signer_id}', format: '{payload_format}'.")
            return (
                False,
                signer_id,
                cast(Union[BasicPayload, ManifestPayload, C2PAPayload, None], actual_inner_payload) if return_payload_on_failure else None,
            )

    @classmethod
    def _verify_c2pa_v2_2(
        cls,
        text: str,
        outer_payload: OuterPayload,
        public_key_resolver: Callable[[str], Optional[Ed25519PublicKey]],
        return_payload_on_failure: bool,
        require_hard_binding: bool,  # New parameter
    ) -> Tuple[bool, Optional[str], Union[C2PAPayload, None]]:
        """
        Verifies a C2PA v2.2 compliant manifest.

        This internal method performs a series of checks to validate the authenticity
        and integrity of an embedded C2PA manifest, including signature verification,
        soft binding, and hard binding checks.

        Args:
            text: The clean text content, stripped of metadata.
            outer_payload: The deserialized outer payload containing the manifest.
            public_key_resolver: A function to retrieve the public key for a given signer ID.
            return_payload_on_failure: Flag to control returning the payload on failure.
            require_hard_binding: If True, require the hard binding assertion in the manifest.

        Returns:
            A tuple with verification status, signer ID, and the C2PA payload.
        """
        signer_id = outer_payload["signer_id"]
        cose_sign1_b64 = outer_payload.get("cose_sign1")

        if not cose_sign1_b64 or not isinstance(cose_sign1_b64, str):
            logger.error("C2PA payload missing 'cose_sign1' field or it has incorrect type.")
            return False, signer_id, None

        try:
            cose_sign1_bytes = base64.b64decode(cose_sign1_b64)
        except (binascii.Error, ValueError, TypeError) as e:
            logger.error(f"Failed to decode cose_sign1 payload: {e}", exc_info=True)
            return False, signer_id, None

        # --- 1. Signature Verification using COSE ---
        public_key = public_key_resolver(signer_id)
        if not public_key:
            logger.warning(f"C2PA verification: Public key not found for signer_id: {signer_id}")
            if return_payload_on_failure:
                try:
                    decoded_msg = CoseMessage.decode(cose_sign1_bytes)
                    if decoded_msg.payload is None:
                        return False, signer_id, None
                    unverified_manifest = deserialize_c2pa_payload_from_cbor(bytes(decoded_msg.payload))
                    return False, signer_id, unverified_manifest
                except Exception:
                    return False, signer_id, None
            return False, signer_id, None

        try:
            cbor_payload_bytes = verify_c2pa_cose(public_key, cose_sign1_bytes)
            c2pa_manifest = deserialize_c2pa_payload_from_cbor(cbor_payload_bytes)
        except (InvalidSignature, ValueError) as e:
            logger.warning(f"C2PA COSE verification failed for signer_id: {signer_id}. Reason: {e}")
            if return_payload_on_failure:
                try:
                    decoded_msg = CoseMessage.decode(cose_sign1_bytes)
                    if decoded_msg.payload is None:
                        return False, signer_id, None
                    unverified_manifest = deserialize_c2pa_payload_from_cbor(bytes(decoded_msg.payload))
                    return False, signer_id, unverified_manifest
                except Exception as decode_err:
                    logger.error(f"Could not decode unverified COSE payload for inspection: {decode_err}")
                    return False, signer_id, None
            return False, signer_id, None
        except Exception as e:
            logger.error(f"An unexpected error occurred during COSE verification: {e}", exc_info=True)
            return False, signer_id, None

        # --- 2. Manifest Content Validation ---
        # a) Check @context URL
        expected_context = "https://c2pa.org/schemas/v2.2/c2pa.jsonld"
        if c2pa_manifest.get("@context") != expected_context:
            logger.warning(f"C2PA verification: Manifest @context mismatch. Expected '{expected_context}', got '{c2pa_manifest.get('@context')}'.")
            return False, signer_id, c2pa_manifest

        # b) Check for mandatory assertions
        assertions = c2pa_manifest.get("assertions", [])
        assertion_labels = {a.get("label") for a in assertions if isinstance(a, dict)}
        required_assertions = {"c2pa.actions.v1", "c2pa.soft_binding.v1"}
        if require_hard_binding:
            required_assertions.add("c2pa.hash.data.v1")
        if not required_assertions.issubset(assertion_labels):
            missing = required_assertions - assertion_labels
            logger.warning(f"C2PA verification: Manifest missing required assertions: {missing}")
            return False, signer_id, c2pa_manifest

        # --- 3. Soft Binding Verification (Deterministic Hashing) ---
        soft_binding_assertion = next((a for a in assertions if isinstance(a, dict) and a.get("label") == "c2pa.soft_binding.v1"), None)
        if soft_binding_assertion is None:
            logger.warning("C2PA verification: Soft binding assertion not found.")
            return False, signer_id if signer_id is not None else None, c2pa_manifest

        # a) Extract the expected hash from the received manifest.
        expected_soft_hash = soft_binding_assertion["data"].get("hash")

        # b) Create a deep copy of the manifest to modify for hash calculation.
        manifest_for_hashing = copy.deepcopy(c2pa_manifest)

        # c) Find the soft binding assertion in the copy and replace its hash with a placeholder.
        assertion_to_modify = next(
            (a for a in manifest_for_hashing.get("assertions", []) if isinstance(a, dict) and a.get("label") == "c2pa.soft_binding.v1"), None
        )
        if assertion_to_modify:
            assertion_to_modify["data"]["hash"] = ""

        # d) Serialize the modified manifest and calculate the hash.
        cbor_for_hashing = serialize_c2pa_payload_to_cbor(manifest_for_hashing)
        actual_soft_hash = hashlib.sha256(cbor_for_hashing).hexdigest()

        # e) Compare the calculated hash with the expected hash.
        if expected_soft_hash != actual_soft_hash:
            logger.warning(f"C2PA verification: Soft binding hash mismatch. Expected '{expected_soft_hash}', got '{actual_soft_hash}'.")
            return False, signer_id, c2pa_manifest

        # --- 4. Hard Binding Verification ---
        if require_hard_binding:
            hard_binding_assertion = next((a for a in assertions if isinstance(a, dict) and a.get("label") == "c2pa.hash.data.v1"), None)
            if hard_binding_assertion is None:
                logger.warning("C2PA verification: Hard binding assertion not found.")
                return False, signer_id if signer_id is not None else None, c2pa_manifest
            expected_hard_hash = hard_binding_assertion["data"].get("hash")
            actual_hard_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()

            if expected_hard_hash != actual_hard_hash:
                logger.warning(
                    (
                        f"C2PA verification: Hard binding (content) hash mismatch. "
                        f"Expected '{expected_hard_hash}', got '{actual_hard_hash}'. Text may have been tampered with."
                    )
                )
                return False, signer_id, c2pa_manifest

        # All checks passed
        logger.info(f"C2PA manifest for signer '{signer_id}' verified successfully (Signature, Soft Binding, Hard Binding).")
        return True, signer_id, c2pa_manifest

    @classmethod
    def _bytes_to_variation_selectors(cls, data: bytes) -> List[str]:
        """Convert bytes into a list of Unicode variation selector characters."""
        selectors = [cls.to_variation_selector(byte) for byte in data]
        valid_selectors = [s for s in selectors if s is not None]
        if len(valid_selectors) != len(data):
            # This should theoretically not happen if input is bytes (0-255)
            logger.error("Invalid byte value encountered during selector conversion.")
            raise ValueError("Invalid byte value encountered during selector conversion.")
        return valid_selectors

    @classmethod
    def _extract_outer_payload(cls, text: str) -> Optional[OuterPayload]:
        """Extracts the raw OuterPayload dict from embedded bytes.

        Finds the metadata markers, extracts the embedded bytes, decodes the
        outer JSON structure, and returns the OuterPayload TypedDict if valid.

        Args:
            text: The text containing potentially embedded metadata.

        Returns:
            The extracted OuterPayload dictionary if found and successfully parsed,
            otherwise None.

        Raises:
            (Indirectly via called methods) UnicodeDecodeError, json.JSONDecodeError, TypeError
        """
        # 1. Extract Bytes:
        logger.debug("Attempting to extract bytes from text.")
        outer_bytes = cls.extract_bytes(text)
        if not outer_bytes:
            logger.debug("No variation selector bytes found in text.")
            return None

        logger.debug(f"Extracted {len(outer_bytes)} bytes from variation selectors.")

        # 3. Deserialize Outer JSON:
        try:
            outer_data_str = outer_bytes.decode("utf-8")
            outer_data = json.loads(outer_data_str)
            if not isinstance(outer_data, dict):
                logger.warning("Decoded outer data is not a dictionary.")
                return None

            # Check the format to determine which keys are required
            payload_format = outer_data.get("format")
            required_keys: Tuple[str, ...]

            if payload_format == "c2pa_v2_2":
                required_keys = ("cose_sign1", "signer_id", "format")
                if not all(k in outer_data for k in required_keys):
                    missing_keys = [k for k in required_keys if k not in outer_data]
                    logger.warning(f"Extracted C2PA v2.2 data missing required keys: {missing_keys}")
                    return None

                try:
                    cose_sign1_bytes = base64.b64decode(outer_data["cose_sign1"])
                    cbor_payload = extract_payload_from_cose_sign1(cose_sign1_bytes)
                    if cbor_payload:
                        outer_data["payload"] = base64.b64encode(cbor_payload).decode("utf-8")
                        outer_data["signature"] = "cose_sign1_embedded"
                    else:
                        logger.warning("Failed to extract payload from COSE_Sign1 structure")
                        return None
                except Exception as e:
                    logger.warning(f"Error processing COSE_Sign1 data: {e}")
                    return None
            else:
                required_keys = ("payload", "signature", "signer_id", "format")
                if not all(k in outer_data for k in required_keys):
                    missing_keys = [k for k in required_keys if k not in outer_data]
                    logger.warning(f"Extracted outer data missing required keys: {missing_keys}")
                    return None

            logger.debug("Successfully extracted and validated outer payload structure.")
            return cast(OuterPayload, outer_data)

        except (UnicodeDecodeError, json.JSONDecodeError, TypeError) as e:
            logger.warning(f"Failed to decode or parse outer payload JSON: {e}", exc_info=False)
            return None

    @classmethod
    def extract_metadata(cls, text: str) -> Union[BasicPayload, ManifestPayload, C2PAPayload, None]:
        """
        Extracts embedded metadata from text without verifying its signature.

        Finds the metadata markers, extracts the embedded bytes, decodes the
        outer JSON structure, and returns the inner 'payload' dictionary.

        Similar to how C2PA allows for inspection of manifest contents separate
        from verification, this method enables access to the embedded provenance
        information without cryptographic validation. This is useful for debugging,
        analysis, or when working with content where verification isn't the primary goal.
        When using the 'manifest' format, the extracted payload will contain C2PA-inspired
        structured provenance information.

        Args:
            text: The text containing potentially embedded metadata.

        Returns:
            The extracted inner metadata dictionary if found and successfully parsed,
            otherwise None.
        """
        # --- Input Validation ---
        if not isinstance(text, str):
            raise TypeError("Input 'text' must be a string.")
        # --- End Input Validation ---
        logger.debug(f"extract_metadata called for text (len={len(text)}).")

        outer_payload = cls._extract_outer_payload(text)

        if outer_payload and "payload" in outer_payload:
            inner_payload = outer_payload["payload"]
            payload_format = outer_payload.get("format")

            # For C2PA, the payload is a b64 string. We need to decode it.
            if payload_format == "c2pa_v2_2":
                if isinstance(inner_payload, str):
                    try:
                        cbor_bytes = base64.b64decode(inner_payload)
                        return deserialize_c2pa_payload_from_cbor(cbor_bytes)
                    except (binascii.Error, ValueError, cbor2.CBORDecodeError):
                        logger.warning("Failed to decode C2PA payload during non-verifying extraction.")
                        return None
                return None  # Invalid format for C2PA payload

            return inner_payload if isinstance(inner_payload, dict) else None
        return None

    # --- Deprecated Methods ---

    @classmethod
    @deprecated(
        version="1.1.0",
        reason="HMAC verification is deprecated. Use Ed25519 digital signatures via the primary verify_metadata method.",
    )
    def _verify_metadata_hmac_deprecated(cls, text: str, hmac_secret_key: str) -> Tuple[Dict[str, Any], bool]:  # Renamed method
        """
        Verify and extract metadata from text embedded using Unicode variation selectors and an HMAC secret key.

        Args:
            text: Text with embedded metadata
            hmac_secret_key: HMAC secret key for verification

        Returns:
            A tuple containing:
            - The extracted inner payload (Dict[str, Any], basic or manifest) or empty dict if extraction fails.
            - Verification status (bool): True if the signature is valid, False otherwise.
        """
        # --- Start: Input Validation ---
        if not isinstance(text, str):
            raise TypeError("Input 'text' must be a string.")
        if not isinstance(hmac_secret_key, str):
            raise TypeError("Input 'hmac_secret_key' must be a string.")
        # --- End Input Validation ---

        warnings.warn(
            "verify_metadata with HMAC is deprecated. Use Ed25519 signatures.",
            DeprecationWarning,
            stacklevel=2,
        )
        logger.warning("Deprecated HMAC verify_metadata called.")

        # 1. Extract Bytes:
        outer_bytes = cls.extract_bytes(text)
        if not outer_bytes:
            return {}, False

        # 2. Optional: Decompress Bytes (if compression was added to embed):
        #    - Check for marker and decompress if needed. (Skipped for now)

        # 3. Deserialize Outer JSON:
        try:
            outer_data = json.loads(outer_bytes.decode("utf-8"))

            # Minimal validation
            if not isinstance(outer_data, dict) or "payload" not in outer_data or "signature" not in outer_data:
                logger.warning("Deprecated HMAC: Extracted outer data missing required keys.")
                return {}, False

            inner_payload = outer_data.get("payload", {})
            signature = outer_data.get("signature", "")

            # Ensure payload is dict for serialization
            if not isinstance(inner_payload, dict):
                logger.warning("Deprecated HMAC: Extracted inner payload is not a dictionary.")
                return {}, False

            # 3. Re-serialize Payload for Verification:
            try:
                canonical_payload_bytes = json.dumps(inner_payload, separators=(",", ":")).encode("utf-8")
            except Exception as e:
                # Failed to re-serialize the extracted payload
                logger.error(
                    f"Failed to re-serialize inner payload for verification: {e}",
                    exc_info=True,
                )
                return {}, False

            # Generate expected HMAC signature
            hmac_obj = hmac.new(
                hmac_secret_key.encode("utf-8"),
                canonical_payload_bytes,
                hashlib.sha256,
            )
            expected_signature = hmac_obj.hexdigest()

            # 5. Compare Signatures:
            is_valid = hmac.compare_digest(expected_signature, signature)

            if is_valid:
                logger.info("Deprecated HMAC: Verification successful.")
                return inner_payload, True
            else:
                logger.warning("Deprecated HMAC: Verification failed.")
                return inner_payload, False  # Return payload even on failure

        except (UnicodeDecodeError, json.JSONDecodeError) as e:
            logger.error(f"Deprecated HMAC: Error decoding/parsing metadata: {e}", exc_info=True)
            return {}, False  # Return empty dict and False on error
        except Exception as e:
            logger.error(
                f"Deprecated HMAC: Unexpected error during verification: {e}",
                exc_info=True,
            )
            return {}, False
