"""
Cryptographic operations for document signing
"""

import hashlib
import uuid
from typing import Dict, Any
from cryptography.hazmat.primitives import serialization


def generate_document_id() -> str:
    """Generate a unique document ID"""
    return str(uuid.uuid4())


def hash_content(content: str) -> str:
    """Generate SHA-256 hash of content"""
    return hashlib.sha256(content.encode()).hexdigest()


def sign_content(content: str, private_key_pem: str) -> str:
    """
    Sign content with Ed25519 private key

    Args:
        content: Content to sign
        private_key_pem: PEM-encoded private key

    Returns:
        Hex-encoded signature
    """
    # Load private key
    private_key = serialization.load_pem_private_key(private_key_pem.encode(), password=None)

    # Sign content
    signature = private_key.sign(content.encode())

    return signature.hex()


def verify_signature(content: str, signature_hex: str, public_key_pem: str) -> bool:
    """
    Verify Ed25519 signature

    Args:
        content: Original content
        signature_hex: Hex-encoded signature
        public_key_pem: PEM-encoded public key

    Returns:
        True if signature is valid
    """
    try:
        # Load public key
        public_key = serialization.load_pem_public_key(public_key_pem.encode())

        # Verify signature
        signature = bytes.fromhex(signature_hex)
        public_key.verify(signature, content.encode())

        return True
    except Exception:
        return False


def create_manifest(document_id: str, content_hash: str, signature: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a C2PA-style manifest

    Args:
        document_id: Unique document identifier
        content_hash: SHA-256 hash of content
        signature: Ed25519 signature
        metadata: Additional metadata

    Returns:
        Manifest dictionary
    """
    return {
        "manifest_id": document_id,
        "version": "2.0",
        "content_hash": content_hash,
        "signature": signature,
        "algorithm": "Ed25519",
        "hash_algorithm": "SHA-256",
        "metadata": metadata,
    }
