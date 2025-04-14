import json
from typing import Union, Dict, Any, Tuple, Literal, TypedDict, List, Optional, cast
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives.asymmetric.types import (
    PrivateKeyTypes,
    PublicKeyTypes,
)
from cryptography.exceptions import InvalidSignature
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

    Conceptually similar to C2PA assertions, these represent
    operations performed on the content. The naming convention for assertion labels
    follows C2PA patterns (e.g., "c2pa.created", "c2pa.transcribed") to
    maintain conceptual alignment with the broader provenance ecosystem.
    """

    label: str  # e.g., "c2pa.created", "c2pa.transcribed"
    when: str  # ISO 8601 UTC format string
    # Add other optional C2PA assertion fields if needed, e.g.:
    # softwareAgent: Optional[str]
    # digitalSourceType: Optional[str]


class ManifestAiInfo(TypedDict, total=False):
    """
    Optional structure for AI-specific info within the 'manifest' payload.

    This represents a custom assertion type focused on AI-specific attributes,
    similar to how C2PA allows for specialized assertion types. For AI-generated
    content, this provides critical provenance information about the model used.
    """

    model_id: str
    model_version: Optional[str]
    # Add other relevant AI fields


class ManifestPayload(TypedDict):
    """
    Structure for the 'manifest' metadata format payload.

    Inspired by the Coalition for Content Provenance and Authenticity (C2PA) manifests,
    this structure provides a standardized way to embed provenance information
    directly within text content. While C2PA focuses on rich media file formats,
    EncypherAI adapts these concepts specifically for plain-text use cases where
    traditional file embedding methods aren't applicable.

    The manifest includes information about:
    - The software/tool that generated the claim (claim_generator)
    - A list of assertions about the content (conceptually similar to C2PA assertions)
    - AI-specific assertion when relevant (ai_assertion)
    - Custom claims for extensibility
    - Timestamp information
    """

    claim_generator: str
    assertions: List[ManifestAction]
    ai_assertion: Optional[ManifestAiInfo]
    custom_claims: Dict[str, Any]
    timestamp: Optional[
        str
    ]  # ISO 8601 UTC format string (Consider if needed alongside assertions' 'when')


class OuterPayload(TypedDict):
    """
    The complete outer structure embedded into the text.

    This structure wraps either a basic payload or a C2PA-inspired manifest payload,
    adding cryptographic integrity through digital signatures. Similar to C2PA's
    approach of ensuring tamper-evidence through cryptographic signing, this
    structure enables verification of content authenticity and integrity in
    plain-text environments.
    """

    format: Literal["basic", "manifest"]
    signer_id: str
    payload: Union[BasicPayload, ManifestPayload]  # The signed part
    signature: str  # Base64 encoded signature string


# --- End TypedDict Definitions ---


def generate_key_pair() -> Tuple[ed25519.Ed25519PrivateKey, ed25519.Ed25519PublicKey]:
    """
    Generates an Ed25519 key pair.

    Returns:
        Tuple containing the private and public keys.
    """
    try:
        logger.debug("Generating new Ed25519 key pair.")
        private_key = ed25519.Ed25519PrivateKey.generate()
        logger.info("Successfully generated Ed25519 private key.")
        public_key = private_key.public_key()
        logger.debug("Successfully generated corresponding Ed25519 public key.")
        return private_key, public_key
    except Exception as e:
        logger.error(f"Failed to generate Ed25519 key pair: {e}", exc_info=True)
        raise


def sign_payload(private_key: PrivateKeyTypes, payload_bytes: bytes) -> bytes:
    """
    Signs the payload bytes using the private key (Ed25519).

    Args:
        private_key: The Ed25519 private key object.
        payload_bytes: The canonical bytes of the payload to sign.

    Returns:
        The signature bytes.

    Raises:
        TypeError: If the provided key is not an Ed25519 private key.
    """
    if not isinstance(private_key, ed25519.Ed25519PrivateKey):
        logger.error(
            f"Signing aborted: Incorrect private key type provided "
            f"({type(private_key)}). Expected Ed25519PrivateKey."
        )
        raise TypeError("Signing requires an Ed25519PrivateKey instance.")

    logger.debug(
        f"Attempting to sign payload ({len(payload_bytes)} bytes) with Ed25519 key."
    )
    try:
        signature = private_key.sign(payload_bytes)
        logger.info(
            f"Successfully signed payload (signature length: {len(signature)} bytes)."
        )
        return cast(bytes, signature)
    except Exception as e:
        logger.error(f"Signing operation failed: {e}", exc_info=True)
        raise RuntimeError(f"Signing failed: {e}")


def verify_signature(
    public_key: PublicKeyTypes, payload_bytes: bytes, signature: bytes
) -> bool:
    """
    Verifies the signature against the payload using the public key (Ed25519).

    Args:
        public_key: The Ed25519 public key object.
        payload_bytes: The canonical bytes of the payload that was signed.
        signature: The signature bytes to verify.

    Returns:
        True if the signature is valid, False otherwise.

    Raises:
        TypeError: If the provided key is not an Ed25519 public key.
    """
    if not isinstance(public_key, ed25519.Ed25519PublicKey):
        logger.error(
            f"Verification aborted: Incorrect public key type provided "
            f"({type(public_key)}). Expected Ed25519PublicKey."
        )
        raise TypeError("Verification requires an Ed25519PublicKey instance.")

    logger.debug(
        f"Attempting to verify signature (len={len(signature)}) against payload (len={len(payload_bytes)}) "
        f"using Ed25519 public key."
    )
    try:
        public_key.verify(signature, payload_bytes)
        logger.info("Signature verification successful.")
        return True
    except InvalidSignature:
        logger.warning("Signature verification failed: Invalid signature.")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during verification: {e}", exc_info=True)
        raise RuntimeError(f"Verification process failed unexpectedly: {e}") from e


def serialize_payload(payload: Dict[str, Any]) -> bytes:
    """
    Serializes the metadata payload dictionary into canonical JSON bytes.
    Ensures keys are sorted and uses compact separators for consistency.

    Args:
        payload: The dictionary payload.

    Returns:
        UTF-8 encoded bytes of the canonical JSON string.
    """
    payload_type = type(payload).__name__
    logger.debug(f"Attempting to serialize payload of type: {payload_type}")
    try:
        serialized_data = json.dumps(
            payload, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
    except TypeError as e:
        logger.error(
            f"Serialization failed for payload type {payload_type}: {e}", exc_info=True
        )
        raise TypeError(f"Payload is not JSON serializable: {e}")
    except Exception as e:
        logger.error(
            f"Unexpected error during serialization of {payload_type}: {e}",
            exc_info=True,
        )
        raise

    logger.debug(
        f"Successfully serialized {payload_type} payload ({len(serialized_data)} bytes)."
    )
    return serialized_data


def load_private_key(
    key_data: Union[bytes, str], password: Optional[bytes] = None
) -> ed25519.Ed25519PrivateKey:
    """
    Loads an Ed25519 private key from PEM-encoded bytes or string,
    or from raw bytes (32 bytes).

    Args:
        key_data: PEM string/bytes or raw private key bytes.
        password: Optional password for encrypted PEM keys.

    Returns:
        Ed25519 private key object.

    Raises:
        ValueError: If the key format is invalid or unsupported.
        TypeError: If key_data has an invalid type.
    """
    if isinstance(key_data, str):
        key_data = key_data.encode("utf-8")  # Assume PEM if string

    if isinstance(key_data, bytes):
        if (
            b"-----BEGIN PRIVATE KEY-----" in key_data
            or b"-----BEGIN OPENSSH PRIVATE KEY-----" in key_data
            or b"-----BEGIN ED25519 PRIVATE KEY-----" in key_data
        ):
            try:
                loaded_key = serialization.load_pem_private_key(key_data, password=None)
                if isinstance(loaded_key, ed25519.Ed25519PrivateKey):
                    return loaded_key
                else:
                    raise ValueError("PEM data is not an Ed25519 private key")
            except (
                TypeError
            ):  # Will likely raise TypeError if encrypted and password is None
                pass  # Continue to check for encrypted format
            except Exception as e:
                raise ValueError(f"Failed to load unencrypted PEM private key: {e}")

        elif b"-----BEGIN ENCRYPTED PRIVATE KEY-----" in key_data:
            if password is None:
                raise ValueError("Password required for encrypted private key")
            try:
                loaded_key = serialization.load_pem_private_key(
                    key_data,
                    password=password,
                    # backend=default_backend() # Not typically needed unless specific backend required
                )
                if isinstance(loaded_key, ed25519.Ed25519PrivateKey):
                    return loaded_key
                else:
                    raise ValueError(
                        "Encrypted PEM data did not yield an Ed25519 private key"
                    )
            except Exception as e:
                raise ValueError(f"Failed to load encrypted PEM private key: {e}")

        elif len(key_data) == 32:  # Ed25519 private key is 32 bytes
            try:
                return ed25519.Ed25519PrivateKey.from_private_bytes(key_data)
            except Exception as e:
                raise ValueError(f"Failed to load raw private key bytes: {e}")
        else:
            raise ValueError("Invalid private key byte length or format")
    else:
        raise TypeError("key_data must be bytes or a PEM string")


def load_public_key(key_data: Union[bytes, str]) -> ed25519.Ed25519PublicKey:
    """
    Loads an Ed25519 public key from PEM-encoded bytes or string,
    or from raw bytes (32 bytes).

    Args:
        key_data: PEM string/bytes or raw public key bytes.

    Returns:
        Ed25519 public key object.

    Raises:
        ValueError: If the key format is invalid or unsupported.
        TypeError: If key_data has an invalid type.
    """
    if isinstance(key_data, str):
        key_data = key_data.encode("utf-8")  # Assume PEM if string

    if isinstance(key_data, bytes):
        if b"-----BEGIN PUBLIC KEY-----" in key_data:  # Check for PEM format (SPKI)
            try:
                loaded_key = serialization.load_pem_public_key(key_data)
                if isinstance(loaded_key, ed25519.Ed25519PublicKey):
                    return loaded_key
                else:
                    raise ValueError("PEM data is not an Ed25519 public key")
            except Exception as e:
                raise ValueError(f"Failed to load PEM public key: {e}")
        elif len(key_data) == 32:  # Ed25519 public key is 32 bytes
            try:
                return ed25519.Ed25519PublicKey.from_public_bytes(key_data)
            except Exception as e:
                raise ValueError(f"Failed to load raw public key bytes: {e}")
        else:
            raise ValueError("Invalid public key byte length or format")
    else:
        raise TypeError("key_data must be bytes or a PEM string")
