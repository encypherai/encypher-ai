"""
Cryptographic utilities for key management and encryption.
"""
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import serialization
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from app.config import settings
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional


async def load_organization_private_key(
    organization_id: str,
    db: AsyncSession
) -> ed25519.Ed25519PrivateKey:
    """
    Load and decrypt organization's private key from database.

    Args:
        organization_id: The organization's unique identifier
        db: Database session

    Returns:
        Ed25519PrivateKey: Decrypted private key

    Raises:
        ValueError: If no private key found for organization
    """
    result = await db.execute(
        text("SELECT private_key_encrypted FROM organizations WHERE organization_id = :org_id"),
        {"org_id": organization_id}
    )
    row = result.fetchone()

    if not row or not row[0]:
        raise ValueError(f"No private key found for organization {organization_id}")

    encrypted_key = row[0]

    # Decrypt using AES-GCM
    aesgcm = AESGCM(settings.key_encryption_key_bytes)
    private_key_bytes = aesgcm.decrypt(
        settings.encryption_nonce_bytes,
        bytes(encrypted_key),
        None
    )

    # Load Ed25519 private key
    return ed25519.Ed25519PrivateKey.from_private_bytes(private_key_bytes)


def generate_ed25519_keypair() -> tuple[ed25519.Ed25519PrivateKey, ed25519.Ed25519PublicKey]:
    """
    Generate new Ed25519 keypair.

    Returns:
        tuple: (private_key, public_key)
    """
    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    return private_key, public_key


def encrypt_private_key(private_key: ed25519.Ed25519PrivateKey) -> bytes:
    """
    Encrypt private key for secure storage.

    Args:
        private_key: Ed25519 private key to encrypt

    Returns:
        bytes: Encrypted private key
    """
    # Serialize private key to bytes
    private_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption()
    )

    # Encrypt using AES-GCM
    aesgcm = AESGCM(settings.key_encryption_key_bytes)
    encrypted = aesgcm.encrypt(
        settings.encryption_nonce_bytes,
        private_bytes,
        None
    )

    return encrypted


def extract_public_key_from_certificate(cert_pem: str) -> ed25519.Ed25519PublicKey:
    """
    Extract public key from X.509 certificate.

    Args:
        cert_pem: PEM-encoded certificate

    Returns:
        Ed25519PublicKey: Public key from certificate
    """
    cert = x509.load_pem_x509_certificate(cert_pem.encode(), default_backend())
    return cert.public_key()


def serialize_public_key(public_key: ed25519.Ed25519PublicKey) -> bytes:
    """
    Serialize public key to bytes.

    Args:
        public_key: Ed25519 public key

    Returns:
        bytes: Serialized public key
    """
    return public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )


def deserialize_public_key(public_key_bytes: bytes) -> ed25519.Ed25519PublicKey:
    """
    Deserialize public key from bytes.

    Args:
        public_key_bytes: Serialized public key

    Returns:
        Ed25519PublicKey: Deserialized public key
    """
    return ed25519.Ed25519PublicKey.from_public_bytes(public_key_bytes)
