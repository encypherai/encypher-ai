"""
Cryptographic signing and verification utilities for EncypherAI.

This module provides functions for signing payloads and verifying signatures
using Ed25519 keys.
"""

from typing import cast

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives.asymmetric.types import PrivateKeyTypes, PublicKeyTypes

from .logging_config import logger


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
        logger.error(f"Signing aborted: Incorrect private key type provided " f"({type(private_key)}). Expected Ed25519PrivateKey.")
        raise TypeError("Signing requires an Ed25519PrivateKey instance.")

    logger.debug(f"Attempting to sign payload ({len(payload_bytes)} bytes) with Ed25519 key.")
    try:
        signature = private_key.sign(payload_bytes)
        logger.info(f"Successfully signed payload (signature length: {len(signature)} bytes).")
        return cast(bytes, signature)
    except Exception as e:
        logger.error(f"Signing operation failed: {e}", exc_info=True)
        raise RuntimeError(f"Signing failed: {e}")


def verify_signature(public_key: PublicKeyTypes, payload_bytes: bytes, signature: bytes) -> bool:
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
        logger.error(f"Verification aborted: Incorrect public key type provided " f"({type(public_key)}). Expected Ed25519PublicKey.")
        raise TypeError("Verification requires an Ed25519PublicKey instance.")

    logger.debug(f"Attempting to verify signature (len={len(signature)}) against payload (len={len(payload_bytes)}) " f"using Ed25519 public key.")
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
