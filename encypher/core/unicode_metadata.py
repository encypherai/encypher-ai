"""
Unicode Metadata Embedding Utility for Encypher

This module provides utilities for embedding metadata (model info, timestamps)
into text using Unicode variation selectors without affecting readability.
"""

import base64
import binascii
import copy
import hashlib
import json
import re
import unicodedata
import uuid
from datetime import date, datetime, timezone
from typing import Any, Callable, Literal, Optional, Union, cast

import cbor2
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

from encypher import __version__
from encypher.interop.c2pa.text_hashing import compute_normalized_hash, normalize_text
from encypher.interop.c2pa.text_wrapper import encode_wrapper, find_and_decode

from .constants import MetadataTarget
from .logging_config import logger
from .payloads import (
    BasicPayload,
    C2PAAssertion,
    C2PAPayload,
    ManifestPayload,
    OuterPayload,
    deserialize_c2pa_payload_from_cbor,
    deserialize_jumbf_payload,
    serialize_c2pa_payload_to_cbor,
    serialize_jumbf_payload,
    serialize_payload,
)
from .signing import SigningKey, extract_payload_from_cose_sign1, sign_c2pa_cose, sign_payload, verify_c2pa_cose, verify_signature


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
    REGEX_PATTERNS: dict[MetadataTarget, re.Pattern] = {
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
        decoded: list[int] = []

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
        # Strategy: Prefer a contiguous trailing block (FILE_END embedding),
        # then fall back to interleaved scanning only if none found.
        # This avoids accidentally capturing short VS runs inside the text
        # (e.g., emoji presentation selectors) that are not metadata.

        # 1) Check for variation selectors appended at the very end of the text.
        #    Skip ignorable trailing markers such as whitespace/newlines, BOM, and zero-width marks
        #    that tests may inject after the metadata block.
        def _is_ignorable_trailing(ch: str) -> bool:
            # Common ignorable characters that may appear after the selector block at EOF
            # - Whitespace and newlines (including CRLF components)
            # - BOM (\ufeff) if FILE_END_ZWNBSP was used
            # - Zero-width characters sometimes used as markers
            ignorable_codepoints = {
                "\ufeff",  # BOM
                "\u200b",  # ZWSP
                "\u200c",  # ZWNJ
                "\u200d",  # ZWJ
                "\u2060",  # Word Joiner
                "\u202f",  # Narrow no-break space
            }
            return ch.isspace() or ch in ignorable_codepoints

        # Find the final contiguous run of variation selectors at the end,
        # skipping ignorable trailing markers first. Require a minimum length
        # to avoid picking up stray single VS-16 inserted as noise.
        end_idx = len(text) - 1
        while end_idx >= 0 and _is_ignorable_trailing(text[end_idx]):
            end_idx -= 1

        # Walk backward to detect the run of variation selectors
        run_start = end_idx
        while run_start >= 0 and cls.from_variation_selector(ord(text[run_start])) is not None:
            run_start -= 1
        run_start += 1  # move to first VS of the run

        run_len = (end_idx - run_start + 1) if end_idx >= run_start else 0
        MIN_TRAILING_RUN = 16  # conservative lower bound; actual payloads are much larger

        if run_len >= MIN_TRAILING_RUN:
            decoded_trailing: list[int] = [cls.from_variation_selector(ord(ch)) or 0 for ch in text[run_start : end_idx + 1]]
            logger.debug(
                f"Extracted {len(decoded_trailing)} bytes from variation selectors at end of text (run_start={run_start}, end_idx={end_idx})."
            )
            return bytes(decoded_trailing)

        # 2) If no trailing block is found, attempt interleaved extraction as a fallback.
        #    This is less reliable but may succeed for ALL_CHARACTERS target.
        decoded_interleaved: list[int] = []
        for char in text:
            code_point = ord(char)
            byte = cls.from_variation_selector(code_point)

            # If we've found a non-variation selector after we've started
            # collecting bytes, we're done
            if byte is None and len(decoded_interleaved) > 0:
                break
            # If it's not a variation selector and we haven't started collecting
            # bytes yet, it's probably the base character (emoji), so skip it
            elif byte is None:
                continue

            decoded_interleaved.append(byte)

        if decoded_interleaved:
            return bytes(decoded_interleaved)

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
                raise ValueError(f"Invalid timestamp value: {ts}") from None
        elif isinstance(ts, str):
            try:
                # Attempt to parse ISO 8601 format
                dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            except ValueError:
                # If parsing fails, raise error - we need a consistent format
                raise ValueError(f"Invalid timestamp string format: {ts}. Use ISO 8601.") from None
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
    def _omit_keys_recursive(data: Union[dict[str, Any], list[Any]], keys: list[str]) -> None:
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
    ) -> list[int]:
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
                raise ValueError(f"Invalid target: {target}. Must be one of {valid_targets}.") from None
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
        private_key: SigningKey,
        signer_id: str,
        metadata_format: Literal["basic", "manifest", "cbor_manifest", "c2pa"] = "manifest",
        model_id: Optional[str] = None,
        timestamp: Optional[Union[str, datetime, date, int, float]] = None,
        target: Optional[Union[str, MetadataTarget]] = None,
        custom_metadata: Optional[dict[str, Any]] = None,
        claim_generator: Optional[str] = None,
        actions: Optional[list[dict[str, Any]]] = None,
        ingredients: Optional[list[dict[str, Any]]] = None,
        ai_info: Optional[dict[str, Any]] = None,
        custom_claims: Optional[dict[str, Any]] = None,
        custom_assertions: Optional[list[dict[str, Any]]] = None,
        omit_keys: Optional[list[str]] = None,
        distribute_across_targets: bool = False,
        add_hard_binding: bool = True,
    ) -> str:
        if metadata_format == "c2pa":
            # Convert timestamp once for C2PA-specific embedding (optional)
            try:
                iso_timestamp = cls._format_timestamp(timestamp)
            except (ValueError, TypeError) as e:
                logger.error(f"Timestamp error: {e}", exc_info=True)
                raise ValueError(f"Timestamp error: {e}") from e

            return cls._embed_c2pa(
                text=text,
                private_key=private_key,
                signer_id=signer_id,
                claim_generator=claim_generator,
                actions=actions,
                ingredients=ingredients,
                iso_timestamp=iso_timestamp,
                target=target,
                distribute_across_targets=distribute_across_targets,
                add_hard_binding=add_hard_binding,
                custom_assertions=custom_assertions,
            )
        # --- Start: Input Validation ---
        if not isinstance(text, str):
            logger.error("Input validation failed: 'text' is not a string.")
            raise TypeError("Input text must be a string")

        # Validate private key: accept either Ed25519PrivateKey OR a custom Signer (has .sign method)
        is_signer = hasattr(private_key, "sign") and callable(private_key.sign)
        if not isinstance(private_key, Ed25519PrivateKey) and not is_signer:
            # Note: PrivateKeyTypes is broader, but we specifically need Ed25519 here for signing.
            logger.error("Input validation failed: 'private_key' is not an Ed25519PrivateKey instance or Signer.")
            raise TypeError("Input 'private_key' must be an Ed25519PrivateKey instance or Signer implementation.")

        if not signer_id or not isinstance(signer_id, str):
            # Enhanced to check type as well
            logger.error("Input validation failed: 'signer_id' is not a non-empty string.")
            raise ValueError("A non-empty string 'signer_id' must be provided.")

        # Timestamp is optional across all formats; when provided it will be normalized.

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
                raise ValueError(f"Invalid target: {target}. Must be one of {valid_targets}.") from None
        else:
            logger.error("'target' must be a string or MetadataTarget enum member.")
            raise TypeError("'target' must be a string or MetadataTarget enum member.")

        if metadata_format not in ("basic", "manifest", "cbor_manifest", "c2pa", "jumbf"):
            logger.error("metadata_format must be 'basic', 'manifest', 'cbor_manifest', 'jumbf', or 'c2pa'.")
            raise ValueError("metadata_format must be 'basic', 'manifest', 'cbor_manifest', 'jumbf', or 'c2pa'.")

        if model_id is not None and not isinstance(model_id, str):
            logger.error("If provided, 'model_id' must be a string.")
            raise TypeError("If provided, 'model_id' must be a string.")

        if not isinstance(distribute_across_targets, bool):
            logger.error("'distribute_across_targets' must be a boolean.")
            raise TypeError("'distribute_across_targets' must be a boolean.")

        if omit_keys is not None:
            if not isinstance(omit_keys, list) or not all(isinstance(k, str) for k in omit_keys):
                raise TypeError("'omit_keys' must be a list of strings if provided.")
            # Only signer_id and format remain mandatory; timestamp may be omitted.
            mandatory = {"signer_id", "format"}
            if any(k in mandatory for k in omit_keys):
                raise ValueError("Cannot omit required metadata fields: signer_id or format")

        # Convert timestamp
        try:
            iso_timestamp = cls._format_timestamp(timestamp)
        except (ValueError, TypeError) as e:
            logger.error(f"Timestamp error: {e}", exc_info=True)
            raise ValueError(f"Timestamp error: {e}") from e

        payload_data: dict[str, Any]  # Use Dict[str, Any] for flexible construction

        if metadata_format == "basic":
            logger.debug("Using 'basic' metadata format.")
            payload_data = {
                "signer_id": signer_id,
                "format": metadata_format,  # Explicitly include format
            }
            if iso_timestamp is not None:
                payload_data["timestamp"] = iso_timestamp
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
                "format": metadata_format,  # Keep format for clarity
            }
            if iso_timestamp is not None:
                payload_data["timestamp"] = iso_timestamp

            # 2. Construct the inner manifest dictionary
            inner_manifest: dict[str, Any] = {}
            if claim_generator:
                inner_manifest["claim_generator"] = claim_generator
            if actions:
                inner_manifest["actions"] = actions
            if ai_info:
                inner_manifest["ai_info"] = ai_info
            if custom_claims:
                inner_manifest["custom_claims"] = custom_claims
            if custom_metadata:
                inner_manifest["custom_metadata"] = custom_metadata
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
                "format": "manifest",  # Internally, it's a manifest structure before CBOR encoding
            }
            if iso_timestamp is not None:
                payload_data["timestamp"] = iso_timestamp
            cbor_manifest_dict: dict[str, Any] = {}
            if claim_generator:
                cbor_manifest_dict["claim_generator"] = claim_generator
            if actions:
                cbor_manifest_dict["actions"] = actions
            if ai_info:
                cbor_manifest_dict["ai_info"] = ai_info
            if custom_claims:
                cbor_manifest_dict["custom_claims"] = custom_claims
            if custom_metadata:
                cbor_manifest_dict["custom_metadata"] = custom_metadata
            if model_id:
                if "ai_info" not in cbor_manifest_dict:
                    cbor_manifest_dict["ai_info"] = {}
                cbor_manifest_dict["ai_info"]["model_id"] = model_id
            payload_data["manifest"] = cbor_manifest_dict
            # The actual CBOR processing will happen during signing/packaging
        elif metadata_format == "jumbf":
            logger.debug("Using 'jumbf' metadata format.")
            iso_timestamp = cls._format_timestamp(timestamp)
            payload_data = {
                "signer_id": signer_id,
                "format": "manifest",
            }
            if iso_timestamp is not None:
                payload_data["timestamp"] = iso_timestamp
            jumbf_manifest_dict: dict[str, Any] = {}
            if claim_generator:
                jumbf_manifest_dict["claim_generator"] = claim_generator
            if actions:
                jumbf_manifest_dict["actions"] = actions
            if ai_info:
                jumbf_manifest_dict["ai_info"] = ai_info
            if custom_claims:
                jumbf_manifest_dict["custom_claims"] = custom_claims
            if model_id:
                if "ai_info" not in jumbf_manifest_dict:
                    jumbf_manifest_dict["ai_info"] = {}
                jumbf_manifest_dict["ai_info"]["model_id"] = model_id
            payload_data["manifest"] = jumbf_manifest_dict
            # JUMBF binary processing will happen during signing/packaging
        else:
            logger.error(f"Unsupported metadata_format: {metadata_format}")
            raise ValueError(f"Unsupported metadata_format: {metadata_format}")

        # --- End: Payload Construction ---

        if omit_keys:
            cls._omit_keys_recursive(payload_data, omit_keys)

        # --- Start: Signing & Packaging Logic based on format ---

        # --- Start: Signing & Packaging Logic based on format ---
        signature_b64: str
        payload_for_outer_dict: Union[dict[str, Any], str]
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
        elif metadata_format == "jumbf":
            try:
                jumbf_bytes = serialize_jumbf_payload(payload_data)
                signature = sign_payload(private_key, jumbf_bytes)
                signature_b64 = base64.urlsafe_b64encode(signature).rstrip(b"=").decode("ascii")
                payload_for_outer_dict = base64.b64encode(jumbf_bytes).decode("utf-8")
                actual_payload_type_for_outer = "jumbf"
                logger.debug(f"JUMBF payload signed successfully. Signature (base64): {signature_b64[:10]}...")
            except Exception as e:
                logger.exception("Failed to process or sign JUMBF payload.")
                raise RuntimeError(f"Failed to process or sign JUMBF payload: {e}") from e
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
            raise RuntimeError(f"Failed to serialize outer payload: {e}") from e

        logger.debug(f"Serialized outer payload size: {len(outer_bytes)} bytes")

        # 7. Convert Outer Bytes to Variation Selectors:
        try:
            selector_chars = cls._bytes_to_variation_selectors(outer_bytes)
        except ValueError as e:
            # Handle potential errors from the helper
            logger.error(f"Failed to convert metadata bytes to selectors: {e}", exc_info=True)
            raise RuntimeError(f"Failed to convert metadata bytes to selectors: {e}") from e

        if not selector_chars:
            # Nothing to embed, return original text
            return text

        # 9. Handle special end-of-file targets first
        embedding_target = target if target is not None else MetadataTarget.WHITESPACE
        if embedding_target == MetadataTarget.FILE_END or embedding_target == MetadataTarget.FILE_END_ZWNBSP:
            prefix = "\ufeff" if embedding_target == MetadataTarget.FILE_END_ZWNBSP else ""
            embedded_text = text + prefix + "".join(selector_chars)
            logger.info("Successfully embedded metadata at file end for signer '%s'.", signer_id)
            return embedded_text

        # Otherwise use position-based targets
        try:
            # find_targets now returns list of indices
            target_indices = cls.find_targets(text, embedding_target)
        except ValueError as e:
            # Propagate errors from find_targets (e.g., invalid target string)
            logger.error(f"Failed to find embedding targets: {e}", exc_info=True)
            raise ValueError(f"Failed to find embedding targets: {e}") from e

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
            # Distribute selectors across multiple targets
            if len(target_indices) < len(selector_chars):
                err_msg = (
                    f"Not enough targets ({len(target_indices)}) found in text "
                    f"to embed metadata of length {len(selector_chars)} "
                    f"using target '{target_display}'. Required: {len(selector_chars)}."
                )
                logger.error(err_msg)
                raise ValueError(err_msg)

            result_parts: list[str] = []
            last_text_idx = 0
            selector_idx = 0

            for target_idx in sorted(target_indices):
                # Append text before the target character
                result_parts.append(text[last_text_idx:target_idx])
                # Append the target character itself
                result_parts.append(text[target_idx])
                if selector_idx < len(selector_chars):
                    # Append one selector after the target character
                    result_parts.append(selector_chars[selector_idx])
                    selector_idx += 1
                last_text_idx = target_idx + 1
                if selector_idx >= len(selector_chars):
                    break

            # Append any remaining text after the final target processed
            result_parts.append(text[last_text_idx:])
            embedded_text = "".join(result_parts)
            logger.info("Successfully embedded metadata (distributed) for signer '%s'.", signer_id)
            return embedded_text
        else:
            # Embed the entire selector block after the first available target character
            target_idx = target_indices[0]
            embedded_text = text[: target_idx + 1] + "".join(selector_chars) + text[target_idx + 1 :]
            logger.info("Successfully embedded metadata (single-point) for signer '%s'.", signer_id)
            return embedded_text

    @staticmethod
    def _compute_text_hash(text: str, algorithm: str = "sha256") -> str:
        """Compute hex digest of *text* using *algorithm* after NFC normalization."""
        import hashlib
        import unicodedata

        normalized = unicodedata.normalize("NFC", text)
        try:
            h = hashlib.new(algorithm.replace("-", ""))
        except ValueError:
            raise ValueError(f"Unsupported hash algorithm '{algorithm}' for C2PA") from None
        h.update(normalized.encode("utf-8"))
        return h.hexdigest()

    @classmethod
    def _embed_c2pa(
        cls,
        text: str,
        private_key: SigningKey,
        signer_id: str,
        claim_generator: Optional[str],
        actions: Optional[list[dict[str, Any]]],
        ingredients: Optional[list[dict[str, Any]]],
        iso_timestamp: Optional[str],
        target: Optional[Union[str, MetadataTarget]],
        distribute_across_targets: bool,
        add_hard_binding: bool,
        custom_assertions: Optional[list[dict[str, Any]]] = None,
    ) -> str:
        """
        Constructs and embeds a C2PA-compliant manifest.

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
            ingredients: A list of ingredient dictionaries for provenance chain.
            iso_timestamp: The ISO 8601 formatted timestamp for the actions.
            target: The embedding target strategy.
            distribute_across_targets: If True, distribute bits across multiple targets.
            add_hard_binding: If True, include the hard binding assertion in the manifest.
            custom_assertions: Optional list of custom C2PA assertions to include.

        Returns:
            The text with the embedded C2PA manifest.
        """
        if not isinstance(private_key, ed25519.Ed25519PrivateKey):
            raise TypeError("For C2PA embedding, 'private_key' must be an Ed25519PrivateKey instance.")

        private_key = cast(Ed25519PrivateKey, private_key)

        base_hash_result = compute_normalized_hash(text)
        normalized_text = base_hash_result.normalized_text
        content_hash = base_hash_result.hexdigest

        current_exclusions: list[dict[str, int]] = []

        base_actions: list[dict[str, Any]] = copy.deepcopy(actions) if actions else []
        claim_gen = claim_generator or f"encypher-ai/{__version__}"
        instance_id = str(uuid.uuid4())

        # Only add c2pa.created if no creation or edit action exists
        has_creation_or_edit_action = any(a.get("label") in ["c2pa.created", "c2pa.edited"] for a in base_actions)

        if not has_creation_or_edit_action:
            # Build created action with consistent field ordering: label, when, softwareAgent, then other fields
            created_action: dict[str, Any] = {
                "label": "c2pa.created",
            }
            if iso_timestamp is not None:
                created_action["when"] = iso_timestamp
            created_action["softwareAgent"] = claim_gen
            created_action["digitalSourceType"] = "http://cv.iptc.org/newscodes/digitalsourcetype/trainedAlgorithmicMedia"
            base_actions.insert(0, created_action)

        # Build watermarked action with consistent field ordering
        wm_action: dict[str, Any] = {
            "label": "c2pa.watermarked",
        }
        if iso_timestamp is not None:
            wm_action["when"] = iso_timestamp
        wm_action["softwareAgent"] = claim_gen
        wm_action["description"] = "Text embedded with Unicode variation selectors."

        wrapper_text = ""
        cose_sign1_bytes: Optional[bytes] = None

        MAX_ITERATIONS = 6
        for _ in range(MAX_ITERATIONS):
            c2pa_manifest: C2PAPayload = {
                "@context": "https://c2pa.org/schemas/v2.2/c2pa.jsonld",
                "instance_id": instance_id,
                "claim_generator": claim_gen,
                "assertions": [],
            }

            # Add ingredients for provenance chain (if provided)
            if ingredients:
                c2pa_manifest["ingredients"] = ingredients

            actions_data: dict[str, Any] = {"actions": copy.deepcopy(base_actions)}
            c2pa_manifest["assertions"].append({"label": "c2pa.actions.v1", "data": actions_data, "kind": "Actions"})

            # Add custom assertions if provided
            if custom_assertions:
                for custom_assertion in custom_assertions:
                    label = custom_assertion.get("label")
                    data = custom_assertion.get("data", {})
                    if label:
                        # Determine kind based on label
                        kind = "CustomAssertion"
                        if "location" in label:
                            kind = "Location"
                        elif "training-mining" in label:
                            kind = "TrainingMining"
                        elif "claim_review" in label:
                            kind = "ClaimReview"
                        elif "thumbnail" in label:
                            kind = "Thumbnail"

                        c2pa_manifest["assertions"].append({"label": label, "data": data, "kind": kind})

            if add_hard_binding:
                hard_binding_data = {
                    "hash": content_hash,
                    "alg": "sha256",
                    "exclusions": copy.deepcopy(current_exclusions),
                }
                c2pa_manifest["assertions"].append({"label": "c2pa.hash.data.v1", "data": hard_binding_data, "kind": "ContentHash"})

            manifest_for_hashing = copy.deepcopy(c2pa_manifest)
            placeholder_soft_binding: C2PAAssertion = {
                "label": "c2pa.soft_binding.v1",
                "data": {"alg": "encypher.unicode_variation_selector.v1", "hash": ""},
                "kind": "SoftBinding",
            }
            manifest_for_hashing["assertions"].append(placeholder_soft_binding)

            actions_data_copy = next(
                (a["data"] for a in manifest_for_hashing["assertions"] if a.get("label") == "c2pa.actions.v1"),
                None,
            )
            if actions_data_copy and isinstance(actions_data_copy.get("actions"), list):
                actions_data_copy["actions"].append(copy.deepcopy(wm_action))

            cbor_for_hashing = serialize_c2pa_payload_to_cbor(manifest_for_hashing)
            actual_soft_binding_hash = hashlib.sha256(cbor_for_hashing).hexdigest()

            final_soft_binding_assertion: C2PAAssertion = {
                "label": "c2pa.soft_binding.v1",
                "data": {"alg": "encypher.unicode_variation_selector.v1", "hash": actual_soft_binding_hash},
                "kind": "SoftBinding",
            }
            c2pa_manifest["assertions"].append(final_soft_binding_assertion)
            actions_data["actions"].append(copy.deepcopy(wm_action))

            final_cbor_payload_bytes = serialize_c2pa_payload_to_cbor(c2pa_manifest)
            cose_sign1_bytes = sign_c2pa_cose(private_key, final_cbor_payload_bytes)

            jumbf_payload = {
                "format": "c2pa",
                "signer_id": signer_id,
                "cose_sign1": base64.b64encode(cose_sign1_bytes).decode("utf-8"),
            }
            jumbf_bytes = serialize_jumbf_payload(jumbf_payload)
            wrapper_text = encode_wrapper(jumbf_bytes)

            final_text = normalized_text + wrapper_text

            exclusion_tuples: list[tuple[int, int]] = []
            new_exclusions: list[dict[str, int]] = []

            if add_hard_binding:
                wrapper_length_bytes = len(wrapper_text.encode("utf-8"))
                normalized_final_text = normalize_text(final_text)
                wrapper_index = normalized_final_text.rfind(wrapper_text)
                if wrapper_index < 0:
                    raise RuntimeError("Failed to locate C2PA wrapper inside normalized text")
                exclusion_start = len(normalized_final_text[:wrapper_index].encode("utf-8"))
                exclusion_tuples = [(exclusion_start, wrapper_length_bytes)]
                new_exclusions = [{"start": exclusion_start, "length": wrapper_length_bytes}]

            hash_result = compute_normalized_hash(final_text, exclusion_tuples)
            actual_hash = hash_result.hexdigest

            if add_hard_binding:
                if actual_hash != content_hash:
                    content_hash = actual_hash
                    current_exclusions = new_exclusions
                    continue
                if new_exclusions != current_exclusions:
                    current_exclusions = new_exclusions
                    continue
            break
        else:
            raise RuntimeError("Failed to stabilise C2PA wrapper exclusion offsets")

        if not wrapper_text:
            raise RuntimeError("Failed to produce C2PA wrapper text")

        logger.info("Successfully embedded C2PA manifest for signer '%s'.", signer_id)
        return normalized_text + wrapper_text

    @classmethod
    def verify_metadata(
        cls,
        text: str,
        public_key_resolver: Callable[[str], Optional[Ed25519PublicKey]],
        return_payload_on_failure: bool = False,
        require_hard_binding: bool = True,
    ) -> tuple[bool, Optional[str], Union[BasicPayload, ManifestPayload, C2PAPayload, None]]:
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
        if payload_format == "c2pa":
            try:
                manifest_bytes, clean_text, span = find_and_decode(text)
            except ValueError as err:
                logger.warning(f"Failed to decode C2PA wrapper during verification: {err}")
                return False, signer_id, None

            if manifest_bytes is None or span is None:
                logger.warning("C2PA format indicated but no text wrapper found.")
                return False, signer_id, None

            wrapper_segment = text[span[0] : span[1]]
            normalized_full_text = unicodedata.normalize("NFC", text)
            normalized_index = normalized_full_text.rfind(wrapper_segment)
            if normalized_index < 0:
                logger.warning("Unable to locate wrapper segment in normalized text during verification.")
                return False, signer_id, None

            exclusion_start = len(normalized_full_text[:normalized_index].encode("utf-8"))
            exclusion_length = len(wrapper_segment.encode("utf-8"))

            return cls._verify_c2pa(
                original_text=text,
                outer_payload=outer_payload,
                public_key_resolver=public_key_resolver,
                return_payload_on_failure=return_payload_on_failure,
                require_hard_binding=require_hard_binding,
                wrapper_exclusion=(exclusion_start, exclusion_length),
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
        actual_inner_payload: Union[dict[str, Any], None] = None

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
        elif payload_format == "jumbf":
            if not isinstance(inner_payload, str):
                logger.error(f"JUMBF payload expected string, got {type(inner_payload)}.")
                return False, signer_id, None
            try:
                payload_to_verify_bytes = base64.b64decode(inner_payload.encode("utf-8"))
                actual_inner_payload = deserialize_jumbf_payload(payload_to_verify_bytes)
            except (binascii.Error, ValueError) as e:
                logger.error(f"Failed to decode JUMBF payload: {e}")
                return False, signer_id, None
        elif payload_format in ("basic", "manifest"):
            if not isinstance(inner_payload, dict):
                logger.error(f"JSON payload ('{payload_format}') expected dict, got {type(inner_payload)}.")
                return False, signer_id, None
            try:
                payload_to_verify_bytes = serialize_payload(dict(inner_payload))
                # Create a new dict from the TypedDict's items to satisfy mypy's strict checking.
                # This is more explicit and robust than casting.
                actual_inner_payload = dict(inner_payload.items())
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
    def _verify_c2pa(
        cls,
        original_text: str,
        outer_payload: OuterPayload,
        public_key_resolver: Callable[[str], Optional[Ed25519PublicKey]],
        return_payload_on_failure: bool,
        require_hard_binding: bool,  # New parameter
        wrapper_exclusion: Optional[tuple[int, int]],
    ) -> tuple[bool, Optional[str], Union[C2PAPayload, None]]:
        """
        Verifies a C2PA-compliant manifest.

        This internal method performs a series of checks to validate the authenticity
        and integrity of an embedded C2PA manifest, including signature verification,
        soft binding, and hard binding checks.

        Args:
            original_text: The full text asset (including the wrapper) provided for verification.
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
                    payload = extract_payload_from_cose_sign1(cose_sign1_bytes)
                    if payload is None:
                        return False, signer_id, None
                    unverified_manifest = deserialize_c2pa_payload_from_cbor(payload)
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
                    payload = extract_payload_from_cose_sign1(cose_sign1_bytes)
                    if payload is None:
                        return False, signer_id, None
                    unverified_manifest = deserialize_c2pa_payload_from_cbor(payload)
                    return False, signer_id, unverified_manifest
                except Exception:
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

            exclusions_data = hard_binding_assertion["data"].get("exclusions")
            expected_exclusion: Optional[tuple[int, int]] = None
            if isinstance(exclusions_data, list) and exclusions_data:
                first = exclusions_data[0]
                if isinstance(first, dict):
                    start_val = first.get("start")
                    length_val = first.get("length")
                elif isinstance(first, (list, tuple)) and len(first) >= 2:
                    start_val, length_val = first[0], first[1]
                else:
                    start_val = length_val = None
                if start_val is not None and length_val is not None:
                    try:
                        expected_exclusion = (int(start_val), int(length_val))
                    except (TypeError, ValueError):
                        expected_exclusion = None

            # Use the exclusion range from the manifest (expected_exclusion) as the authoritative source.
            # The manifest's exclusion was calculated at signing time relative to the signed text.
            # For sentence-level embeddings, wrapper_exclusion (calculated from current text position)
            # may differ from expected_exclusion, but the manifest's value is what matters for verification.
            if expected_exclusion is not None:
                exclusion_ranges = [expected_exclusion]
                if wrapper_exclusion is not None and expected_exclusion != wrapper_exclusion:
                    logger.debug(
                        "C2PA verification: Using manifest exclusion %s (wrapper position was %s).",
                        expected_exclusion,
                        wrapper_exclusion,
                    )
            elif wrapper_exclusion is not None:
                # Fallback to wrapper exclusion if manifest doesn't specify one
                exclusion_ranges = [wrapper_exclusion]
            else:
                exclusion_ranges = []

            hard_hash_result = compute_normalized_hash(original_text, exclusion_ranges)
            actual_hard_hash = hard_hash_result.hexdigest

            if expected_hard_hash != actual_hard_hash:
                logger.warning(
                    f"C2PA verification: Hard binding (content) hash mismatch. "
                    f"Expected '{expected_hard_hash}', got '{actual_hard_hash}'. Text may have been tampered with."
                )
                return False, signer_id, c2pa_manifest

        # All checks passed
        logger.info(f"C2PA manifest for signer '{signer_id}' verified successfully (Signature, Soft Binding, Hard Binding).")
        return True, signer_id, c2pa_manifest

    @classmethod
    def _bytes_to_variation_selectors(cls, data: bytes) -> list[str]:
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
        # 0. Prefer C2PA text wrappers (FEFF-prefixed contiguous blocks)
        try:
            manifest_bytes, _clean_text, _span = find_and_decode(text)
        except ValueError as err:
            logger.warning(f"Failed to decode C2PA text wrapper: {err}")
            return None

        if manifest_bytes is not None:
            logger.debug("Detected C2PA text wrapper – attempting JUMBF decode.")
            try:
                manifest_store = deserialize_jumbf_payload(manifest_bytes)
            except Exception as exc:
                logger.warning(f"Failed to deserialize JUMBF payload from text wrapper: {exc}")
                return None

            if not isinstance(manifest_store, dict):
                logger.warning("Decoded JUMBF manifest store is not a dictionary.")
                return None

            signer_id = manifest_store.get("signer_id")
            cose_sign1 = manifest_store.get("cose_sign1")
            if not signer_id or not isinstance(cose_sign1, str):
                logger.warning("C2PA manifest store missing signer_id or cose_sign1.")
                return None

            outer_payload: OuterPayload = {
                "format": "c2pa",
                "signer_id": signer_id,
                "payload": base64.b64encode(manifest_bytes).decode("utf-8"),
                "signature": "c2pa_manifest_store",
            }
            outer_payload["cose_sign1"] = cose_sign1
            return outer_payload

        # 1. Extract Bytes for legacy/other formats:
        logger.debug("Attempting to extract bytes from text.")
        outer_bytes = cls.extract_bytes(text)
        if not outer_bytes:
            logger.debug("No variation selector bytes found in text.")
            return None

        logger.debug(
            "Extracted %d bytes from variation selectors. head_hex=%s tail_hex=%s",
            len(outer_bytes),
            outer_bytes[:32].hex(),
            outer_bytes[-32:].hex() if len(outer_bytes) >= 32 else outer_bytes.hex(),
        )

        # 2. Deserialize Outer JSON with diagnostics
        try:
            outer_data_str = outer_bytes.decode("utf-8")
            # Some environments may prepend BOM. Strip it to avoid JSON parse errors at col 1.
            if outer_data_str.startswith("\ufeff"):
                outer_data_str = outer_data_str.lstrip("\ufeff")
            preview = outer_data_str[:120].encode("unicode_escape").decode("ascii")
            logger.debug("Outer JSON decode preview (first 120 chars, escaped): %s", preview)

            outer_data = json.loads(outer_data_str)
            if not isinstance(outer_data, dict):
                logger.warning("Decoded outer data is not a dictionary.")
                return None

            payload_format = outer_data.get("format")
            if payload_format == "c2pa":
                required_keys: tuple[str, ...] = ("cose_sign1", "signer_id", "format")
                if not all(k in outer_data for k in required_keys):
                    missing_keys = [k for k in required_keys if k not in outer_data]
                    logger.warning("Extracted C2PA data missing required keys: %s", missing_keys)
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
                    logger.warning("Error processing COSE_Sign1 data: %s", e)
                    return None
            else:
                required_keys = ("payload", "signature", "signer_id", "format")
                if not all(k in outer_data for k in required_keys):
                    missing_keys = [k for k in required_keys if k not in outer_data]
                    logger.warning("Extracted outer data missing required keys: %s", missing_keys)
                    return None

            logger.debug("Successfully extracted and validated outer payload structure.")
            return cast(OuterPayload, outer_data)

        except (UnicodeDecodeError, json.JSONDecodeError, TypeError) as e:
            # Fallback: trim to outermost JSON braces and retry
            try:
                s = outer_bytes.decode("utf-8")
            except UnicodeDecodeError:
                logger.warning("Failed to decode or parse outer payload JSON: %s", e, exc_info=False)
                return None
            start = s.find("{")
            end = s.rfind("}")
            if start != -1 and end != -1 and start < end:
                candidate = s[start : end + 1]
                if candidate.startswith("\ufeff"):
                    candidate = candidate.lstrip("\ufeff")
                cand_preview = candidate[:120].encode("unicode_escape").decode("ascii")
                logger.debug("Attempting JSON parse of trimmed candidate (escaped preview): %s", cand_preview)
                try:
                    outer_data = json.loads(candidate)
                    if isinstance(outer_data, dict):
                        payload_format = outer_data.get("format")
                        required_keys = (
                            ("cose_sign1", "signer_id", "format") if payload_format == "c2pa" else ("payload", "signature", "signer_id", "format")
                        )
                        if all(k in outer_data for k in required_keys):
                            logger.debug("Fallback trimmed JSON parse succeeded.")
                            return cast(OuterPayload, outer_data)
                        logger.warning("Trimmed JSON missing required keys: %s", [k for k in required_keys if k not in outer_data])
                    else:
                        logger.warning("Trimmed JSON candidate is not a dict.")
                except json.JSONDecodeError as e2:
                    logger.warning("Fallback trimmed JSON parse failed: %s", e2, exc_info=False)
            logger.warning("Failed to decode or parse outer payload JSON: %s", e, exc_info=False)
            return None

    @classmethod
    def extract_metadata(cls, text: str) -> Optional[Union[BasicPayload, ManifestPayload, C2PAPayload]]:
        """Extract embedded metadata without verifying signature.

        Returns the inner payload for legacy formats, or the decoded C2PA manifest
        for 'c2pa' format. Returns None if extraction fails.
        """
        if not isinstance(text, str):
            raise TypeError("Input 'text' must be a string.")
        logger.debug("extract_metadata called for text (len=%d).", len(text))

        outer_payload = cls._extract_outer_payload(text)
        if not outer_payload or "payload" not in outer_payload:
            return None

        inner_payload = outer_payload["payload"]
        payload_format = outer_payload.get("format")

        if payload_format == "c2pa":
            cose_sign1_b64 = outer_payload.get("cose_sign1")
            try:
                if isinstance(cose_sign1_b64, str):
                    cose_sign1_bytes = base64.b64decode(cose_sign1_b64)
                    cbor_bytes = extract_payload_from_cose_sign1(cose_sign1_bytes)
                    if cbor_bytes is not None:
                        return deserialize_c2pa_payload_from_cbor(cbor_bytes)
            except (binascii.Error, ValueError, cbor2.CBORDecodeError) as exc:
                logger.warning(f"Failed to decode COSE payload during C2PA extraction: {exc}")
                return None

            if isinstance(inner_payload, str):
                try:
                    manifest_store_bytes = base64.b64decode(inner_payload)
                    manifest_store = deserialize_jumbf_payload(manifest_store_bytes)
                    cose_embedded = manifest_store.get("cose_sign1") if isinstance(manifest_store, dict) else None
                    if isinstance(cose_embedded, str):
                        cose_sign1_bytes = base64.b64decode(cose_embedded)
                        cbor_bytes = extract_payload_from_cose_sign1(cose_sign1_bytes)
                        if cbor_bytes is not None:
                            return deserialize_c2pa_payload_from_cbor(cbor_bytes)
                except (binascii.Error, ValueError, cbor2.CBORDecodeError) as exc:
                    logger.warning(f"Failed to decode C2PA manifest store during extraction: {exc}")
                    return None
            return None

        if payload_format == "cbor_manifest":
            if isinstance(inner_payload, str):
                try:
                    cbor_bytes = base64.b64decode(inner_payload)
                    # The decoded bytes represent the CBOR-encoded manifest dict
                    decoded_payload = cbor2.loads(cbor_bytes)
                    # For cbor_manifest, merge the manifest contents with the top-level payload
                    if isinstance(decoded_payload, dict) and "manifest" in decoded_payload:
                        result = dict(decoded_payload)
                        manifest_data = result.pop("manifest", {})
                        if isinstance(manifest_data, dict):
                            result.update(manifest_data)
                        return cast(Union[BasicPayload, ManifestPayload, C2PAPayload], result)
                    return cast(Union[BasicPayload, ManifestPayload, C2PAPayload], decoded_payload)
                except (binascii.Error, ValueError, cbor2.CBORDecodeError) as e:
                    logger.warning(f"Failed to decode CBOR manifest payload during non-verifying extraction: {e}")
                    return None
            return None

        # For "basic" and "manifest" formats, the inner_payload is already a dict
        if isinstance(inner_payload, dict):
            # For manifest format, merge the manifest contents with the top-level payload
            if payload_format == "manifest" and "manifest" in inner_payload:
                result = dict(inner_payload)
                manifest_data = result.pop("manifest", {})
                if isinstance(manifest_data, dict):
                    result.update(manifest_data)
                return cast(Union[BasicPayload, ManifestPayload, C2PAPayload], result)
            return cast(Union[BasicPayload, ManifestPayload, C2PAPayload], inner_payload)
        return None
