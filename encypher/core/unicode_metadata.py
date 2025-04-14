"""
Unicode Metadata Embedding Utility for EncypherAI

This module provides utilities for embedding metadata (model info, timestamps)
into text using Unicode variation selectors without affecting readability.
"""

import base64
import hashlib
import hmac
import json
import re
import warnings
from datetime import date, datetime, timezone
from typing import Any, Callable, Dict, List, Literal, Optional, Tuple, Union, cast

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.asymmetric.types import PrivateKeyTypes, PublicKeyTypes
from deprecated import deprecated

from .constants import MetadataTarget
from .crypto_utils import BasicPayload, ManifestPayload, OuterPayload, serialize_payload, sign_payload, verify_signature
from .logging_config import logger


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

        # Convert bytes back to bytes object
        if decoded:
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
        metadata_format: Literal["basic", "manifest"] = "basic",
        model_id: Optional[str] = None,
        timestamp: Optional[Union[str, datetime, date, int, float]] = None,
        target: Optional[Union[str, MetadataTarget]] = None,
        custom_metadata: Optional[Dict[str, Any]] = None,
        claim_generator: Optional[str] = None,
        actions: Optional[List[Dict[str, Any]]] = None,
        ai_info: Optional[Dict[str, Any]] = None,
        custom_claims: Optional[Dict[str, Any]] = None,
        distribute_across_targets: bool = False,
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
                             Default is 'basic'. When set to 'manifest', uses a
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
            distribute_across_targets: If True, distribute bits across multiple
                                       targets if needed.

        Returns:
            The text with embedded metadata and digital signature.

        Raises:
            ValueError: If 'timestamp' is not provided, if the target is invalid,
                        if not enough embedding locations are found, or if the
                        metadata + signature is too large.
        """
        logger.debug(
            f"embed_metadata called with text (len={len(text)}), signer_id='{signer_id}', "
            f"format='{metadata_format}', target='{target}', distribute={distribute_across_targets}"
        )
        # --- Start: Input Validation ---
        if not isinstance(text, str):
            logger.error("Input validation failed: 'text' is not a string.")
            raise TypeError("Input 'text' must be a string.")
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

        if metadata_format not in ("basic", "manifest"):
            logger.error("metadata_format must be 'basic' or 'manifest'.")
            raise ValueError("metadata_format must be 'basic' or 'manifest'.")

        if model_id is not None and not isinstance(model_id, str):
            logger.error("If provided, 'model_id' must be a string.")
            raise TypeError("If provided, 'model_id' must be a string.")

        if not isinstance(distribute_across_targets, bool):
            logger.error("'distribute_across_targets' must be a boolean.")
            raise TypeError("'distribute_across_targets' must be a boolean.")

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

        else:
            logger.error(f"Unsupported metadata_format: {metadata_format}")
            raise ValueError(f"Unsupported metadata_format: {metadata_format}")

        # --- End: Payload Construction ---

        # --- Start: Signing ---
        try:
            # Serialize the *complete* payload (basic or manifest) just once
            # Use dict() to ensure we are working with a copy if needed and handle payload_data type
            canonical_payload_bytes = serialize_payload(dict(payload_data))
            signature = sign_payload(private_key, canonical_payload_bytes)
            # Use URL-safe base64 encoding without padding for embedding
            signature_b64 = base64.urlsafe_b64encode(signature).rstrip(b"=").decode("ascii")
            logger.debug(f"Payload signed successfully. Signature (base64): {signature_b64[:10]}...")
        except Exception as e:
            logger.exception("Failed to sign the metadata payload.")
            # Propagate the error, as signing failure is critical
            raise RuntimeError(f"Failed to sign metadata payload: {e}") from e
        # --- End: Signing ---

        # --- Start: Combine Payload and Signature for Embedding ---
        # Combine the payload dictionary, signature, signer_id, and format
        # into the structure expected by the extractor.
        outer_payload_to_embed = {
            "payload": payload_data,  # Embed the dictionary structure
            "signature": signature_b64,
            "signer_id": signer_id,  # Add signer_id to the top level
            "format": metadata_format,  # Add format to the top level
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
    def verify_and_extract_metadata(
        cls,
        text: str,
        public_key_provider: Callable[[str], Optional[PublicKeyTypes]],
        return_payload_on_failure: bool = False,
    ) -> Tuple[Union[BasicPayload, ManifestPayload, None], bool, Optional[str]]:
        """
        Extracts embedded metadata, verifies its signature using a public key,
        and returns the payload, verification status, and signer ID.

        This verification process implements a C2PA-inspired approach for content
        authenticity verification, adapted specifically for plain-text environments.
        Similar to how C2PA verifies digital signatures in media files to establish
        provenance and integrity, this method verifies cryptographic signatures
        embedded directly within text using Unicode variation selectors.

        Args:
            text: Text potentially containing embedded metadata.
            public_key_provider: A callable function that takes a signer_id (str)
                                 and returns the corresponding Ed25519PublicKey
                                 object or None if the key is not found.
                                 This resolver pattern enables flexible key management
                                 similar to C2PA's approach for signature verification.
            return_payload_on_failure: If True, return the payload even when verification fails.
                                      If False (default), return None for the payload when verification fails.

        Returns:
            A tuple containing:
            - The extracted inner payload (Dict[str, Any], basic or manifest) or None
              if extraction/verification fails (unless return_payload_on_failure is True).
            - Verification status (bool): True if the signature is valid, False otherwise.
            - The signer_id (str) found in the metadata, or None if extraction fails.

        Raises:
            TypeError: If public_key_provider returns an invalid key type.
            KeyError: If public_key_provider raises an error (e.g., key not found).
            InvalidSignature: If the signature verification process itself fails.
            Exception: Can propagate errors from base64 decoding or payload serialization.
        """
        logger.debug(f"verify_and_extract_metadata called for text (len={len(text)}).")
        # 1. Extract Outer Payload:
        outer_payload = cls._extract_outer_payload(text)
        if outer_payload is None:
            logger.debug("No outer payload found during extraction.")
            return None, False, None

        # 2. Extract Key Components from Outer Payload:
        signer_id = outer_payload["signer_id"]
        inner_payload = outer_payload["payload"]
        signature_b64 = outer_payload["signature"]

        # Remove modification: The inner_payload should already contain 'format' if it was part of the original signed data.
        # Adding it here causes a mismatch during verification.
        # if "format" in outer_payload and "format" not in inner_payload:
        #     inner_payload["format"] = outer_payload["format"]

        # 3. Look Up Public Key:
        try:
            logger.debug(f"Calling public_key_provider for signer_id: '{signer_id}'")
            public_key = public_key_provider(signer_id)
        except Exception as e:
            # Provider function itself might raise an error
            logger.warning(
                f"public_key_provider raised an exception for signer_id '{signer_id}': {e}",
                exc_info=True,
            )
            return (
                inner_payload if return_payload_on_failure else None,
                False,
                signer_id,
            )

        if public_key is None:
            # Key not found for this signer
            logger.warning(f"Public key not found for signer_id: '{signer_id}'")
            return (
                inner_payload if return_payload_on_failure else None,
                False,
                signer_id,
            )
        if not isinstance(public_key, PublicKeyTypes):
            # Provider returned wrong type
            logger.error(f"public_key_provider returned invalid type ({type(public_key)}) for signer_id '{signer_id}'")
            return (
                inner_payload if return_payload_on_failure else None,
                False,
                signer_id,
            )

        # 4. Serialize Inner Payload (Canonical):
        try:
            canonical_payload_bytes = serialize_payload(dict(inner_payload))
        except Exception as e:
            # Failed to re-serialize the extracted payload
            logger.error(
                f"Failed to re-serialize inner payload for verification: {e}",
                exc_info=True,
            )
            return (
                inner_payload if return_payload_on_failure else None,
                False,
                signer_id,
            )

        # 5. Decode Signature:
        try:
            # Add padding if necessary for urlsafe_b64decode
            signature_bytes = base64.urlsafe_b64decode(signature_b64 + "=" * (-len(signature_b64) % 4))
        except (base64.binascii.Error, TypeError) as e:  # type: ignore [attr-defined]
            # Invalid base64 signature string
            logger.warning(f"Failed to decode base64 signature: {e}", exc_info=False)
            return (
                inner_payload if return_payload_on_failure else None,
                False,
                signer_id,
            )

        # 6. Verify Signature:
        try:
            is_valid = verify_signature(public_key, canonical_payload_bytes, signature_bytes)
        except TypeError as e:
            # E.g., verify_signature raises if key type is wrong (though checked above)
            logger.error(
                f"Signature verification failed due to key type mismatch: {e}",
                exc_info=True,
            )
            return (
                inner_payload if return_payload_on_failure else None,
                False,
                signer_id,
            )
        except InvalidSignature:
            # Signature verification failed
            logger.warning(f"Signature verification failed for signer_id '{signer_id}': Invalid signature.")
            return (
                inner_payload if return_payload_on_failure else None,
                False,
                signer_id,
            )
        except Exception as e:
            # Other unexpected errors during verification
            is_valid = False  # Treat unexpected verification errors as invalid
            logger.error(f"Unexpected error during signature verification: {e}", exc_info=True)

        # 7. Return Result:
        if is_valid:
            logger.info(f"Signature verified successfully for signer_id: '{signer_id}'")
            # Verification successful, return payload, status, and signer_id
            return inner_payload, True, signer_id
        else:
            # Verification failed
            logger.warning(f"Signature verification failed for signer_id: '{signer_id}' (reason determined above).")
            return (
                inner_payload if return_payload_on_failure else None,
                False,
                signer_id,
            )

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
        # 2. Optional: Decompress Bytes (if compression was added to embed):
        #    - Check for marker and decompress if needed. (Skipped for now)

        # 3. Deserialize Outer JSON:
        try:
            outer_data_str = outer_bytes.decode("utf-8")
            outer_data = json.loads(outer_data_str)
            if not isinstance(outer_data, dict):
                logger.warning("Decoded outer data is not a dictionary.")
                return None

            # Minimal validation to check required keys for OuterPayload
            required_keys = ("payload", "signature", "signer_id", "format")
            if not all(k in outer_data for k in required_keys):
                missing_keys = [k for k in required_keys if k not in outer_data]
                logger.warning(f"Extracted outer data missing required keys: {missing_keys}")
                return None

            logger.debug("Successfully extracted and validated outer payload structure.")
            # Attempt to cast to TypedDict for structure validation (best effort)
            # This doesn't deeply validate types within 'payload'
            return cast(OuterPayload, outer_data)

        except (UnicodeDecodeError, json.JSONDecodeError, TypeError) as e:
            logger.warning(f"Failed to decode or parse outer payload JSON: {e}", exc_info=False)  # Less noisy logging
            return None

    @classmethod
    def verify_metadata(
        cls,
        text: str,
        public_key_provider: Callable[[str], Optional[PublicKeyTypes]],
        return_payload_on_failure: bool = False,
    ) -> Tuple[Union[BasicPayload, ManifestPayload, None], bool, Optional[str]]:
        """
        Verify and extract metadata from text embedded using Unicode variation selectors and a public key.

        Args:
            text: Text with embedded metadata
            public_key_provider: A callable function that takes a signer_id (str)
                                 and returns the corresponding Ed25519PublicKey
                                 object or None if the key is not found.
            return_payload_on_failure: If True, return the payload even when verification fails.
                                      If False (default), return None for the payload when verification fails.

        Returns:
            A tuple containing:
            - The extracted inner payload (Dict[str, Any], basic or manifest) or None
              if extraction/verification fails (unless return_payload_on_failure is True).
            - Verification status (bool): True if the signature is valid, False otherwise.
            - The signer_id (str) found in the metadata, or None if extraction fails.

        Raises:
            TypeError: If public_key_provider returns an invalid key type.
            KeyError: If public_key_provider raises an error (e.g., key not found).
            InvalidSignature: If the signature verification process itself fails.
            Exception: Can propagate errors from base64 decoding or payload serialization.
        """
        # --- Input Validation ---
        if not isinstance(text, str):
            raise TypeError("Input 'text' must be a string.")
        if not text:
            # Avoid processing empty strings, return None early
            logger.debug("verify_metadata called with empty text, returning None.")
            return None, False, None
        if not callable(public_key_provider):
            raise TypeError("'public_key_provider' must be a callable function.")
        # --- End Input Validation ---

        # This method now simply calls the main verification method
        logger.debug("Forwarding call to verify_and_extract_metadata.")
        return cls.verify_and_extract_metadata(
            text,
            public_key_provider,
            return_payload_on_failure=return_payload_on_failure,
        )

    @classmethod
    def extract_metadata(cls, text: str) -> Union[BasicPayload, ManifestPayload, None]:
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
            # Ensure payload is a dict before returning
            payload = outer_payload["payload"]
            return payload if isinstance(payload, dict) else None
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
