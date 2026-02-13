"""
Cryptographic utilities for key management and encryption.
"""

import os
import logging
from typing import Optional, cast

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from encypher.core.signing import SigningKey
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.utils.aws_signer import AWSSigner

logger = logging.getLogger(__name__)

_DEMO_PRIVATE_KEY: Optional[ed25519.Ed25519PrivateKey] = None

_ENCRYPTED_KEY_PREFIX = b"EPK1"
_ENCRYPTED_KEY_NONCE_LEN = 12


async def load_organization_private_key(organization_id: str, db: AsyncSession) -> SigningKey:
    """
    Load signing key (private key or KMS signer) for organization.

    Args:
        organization_id: The organization's unique identifier
        db: Database session

    Returns:
        SigningKey: Ed25519PrivateKey or Signer implementation

    Raises:
        ValueError: If no valid signing configuration found
    """
    # Handle demo organization - derive private key
    global _DEMO_PRIVATE_KEY
    if organization_id == settings.demo_organization_id:
        return get_demo_private_key()

    # Fetch potentially needed columns: encrypted key and KMS key ID
    try:
        result = await db.execute(
            text("SELECT private_key_encrypted, kms_key_id, kms_region FROM organizations WHERE id = :org_id"), {"org_id": organization_id}
        )
        row = result.fetchone()
    except Exception as e:
        # Fallback or handle error
        raise ValueError(f"Database error loading key for {organization_id}: {e}")

    if not row:
        raise ValueError(f"Organization {organization_id} not found")

    # AWS KMS Logic
    kms_key_id = row.kms_key_id
    if kms_key_id:
        kms_region = row.kms_region or "us-east-1"  # Default to us-east-1 if not specified
        return AWSSigner(key_id=kms_key_id, region_name=kms_region)

    encrypted_key = row.private_key_encrypted

    if not encrypted_key:
        if settings.auto_provision_signing_keys:
            private_key, public_key = generate_ed25519_keypair()
            encrypted_private_key = encrypt_private_key(private_key)
            serialized_public_key = serialize_public_key(public_key)

            update_result = await db.execute(
                text(
                    """
                    UPDATE organizations
                    SET private_key_encrypted = :private_key_encrypted,
                        public_key = :public_key
                    WHERE id = :org_id
                      AND (kms_key_id IS NULL OR kms_key_id = '')
                      AND (private_key_encrypted IS NULL OR OCTET_LENGTH(private_key_encrypted) = 0)
                    RETURNING id
                    """
                ),
                {
                    "org_id": organization_id,
                    "private_key_encrypted": encrypted_private_key,
                    "public_key": serialized_public_key,
                },
            )
            if update_result.fetchone():
                await db.flush()
                return private_key

            refreshed = await db.execute(
                text("SELECT private_key_encrypted, kms_key_id, kms_region FROM organizations WHERE id = :org_id"),
                {"org_id": organization_id},
            )
            row = refreshed.fetchone()
            if row and row.kms_key_id:
                kms_region = row.kms_region or "us-east-1"
                return AWSSigner(key_id=row.kms_key_id, region_name=kms_region)
            encrypted_key = row.private_key_encrypted if row else None

        if not encrypted_key:
            raise ValueError(f"No private key found for organization {organization_id}")

    return decrypt_private_key(bytes(encrypted_key))


async def load_organization_public_key(organization_id: str, db: AsyncSession) -> ed25519.Ed25519PublicKey:
    """
    Load organization's public key from database.

    Args:
        organization_id: The organization's unique identifier
        db: Database session

    Returns:
        Ed25519PublicKey: Public key

    Raises:
        ValueError: If no public key found for organization
    """
    # Handle demo organization - derive public key from private key
    global _DEMO_PRIVATE_KEY
    if organization_id == settings.demo_organization_id:
        private_key = get_demo_private_key()
        return private_key.public_key()

    # Check if this is a user-level org (starts with "user_") - they use demo key
    if organization_id.startswith("user_"):
        logger.info(f"User org {organization_id} uses demo key for verification")
        private_key = get_demo_private_key()
        return private_key.public_key()

    # Look up organization's public key from database.
    # Fall back to deriving from private_key_encrypted when public_key is NULL
    # (auto-provisioned orgs may not have public_key populated yet).
    result = await db.execute(
        text("SELECT public_key, private_key_encrypted FROM organizations WHERE id = :org_id"),
        {"org_id": organization_id},
    )
    row = result.fetchone()

    if not row:
        raise ValueError(f"No public key found for organization {organization_id}")

    if row[0]:
        public_key_bytes = bytes(row[0])
        return ed25519.Ed25519PublicKey.from_public_bytes(public_key_bytes)

    # Fallback: derive public key from encrypted private key
    if row[1]:
        try:
            private_key = decrypt_private_key(bytes(row[1]))
            return private_key.public_key()
        except ValueError:
            logger.warning("Failed to derive public key from private_key_encrypted for org %s", organization_id)

    raise ValueError(f"No public key found for organization {organization_id}")


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
        encoding=serialization.Encoding.Raw, format=serialization.PrivateFormat.Raw, encryption_algorithm=serialization.NoEncryption()
    )

    # Encrypt using AES-GCM
    aesgcm = AESGCM(settings.key_encryption_key_bytes)
    nonce = os.urandom(_ENCRYPTED_KEY_NONCE_LEN)
    encrypted = aesgcm.encrypt(nonce, private_bytes, None)

    return _ENCRYPTED_KEY_PREFIX + nonce + encrypted


def decrypt_private_key(encrypted_key: bytes) -> ed25519.Ed25519PrivateKey:
    """
    Decrypt private key from encrypted storage.

    Args:
        encrypted_key: Encrypted private key bytes

    Returns:
        Ed25519PrivateKey: Decrypted private key

    Raises:
        ValueError: If decryption fails
    """
    try:
        aesgcm = AESGCM(settings.key_encryption_key_bytes)

        if encrypted_key.startswith(_ENCRYPTED_KEY_PREFIX) and len(encrypted_key) > (
            len(_ENCRYPTED_KEY_PREFIX) + _ENCRYPTED_KEY_NONCE_LEN
        ):
            offset = len(_ENCRYPTED_KEY_PREFIX)
            nonce = encrypted_key[offset : offset + _ENCRYPTED_KEY_NONCE_LEN]
            ciphertext = encrypted_key[offset + _ENCRYPTED_KEY_NONCE_LEN :]
            private_key_bytes = aesgcm.decrypt(nonce, ciphertext, None)
        else:
            private_key_bytes = aesgcm.decrypt(settings.encryption_nonce_bytes, encrypted_key, None)

        return ed25519.Ed25519PrivateKey.from_private_bytes(private_key_bytes)
    except Exception as e:
        raise ValueError(f"Failed to decrypt private key: {str(e)}")


def extract_public_key_from_certificate(cert_pem: str) -> ed25519.Ed25519PublicKey:
    """
    Extract public key from X.509 certificate.

    Args:
        cert_pem: PEM-encoded certificate

    Returns:
        Ed25519PublicKey: Public key from certificate
    """
    cert = x509.load_pem_x509_certificate(cert_pem.encode(), default_backend())
    return cast(ed25519.Ed25519PublicKey, cert.public_key())


def serialize_public_key(public_key: ed25519.Ed25519PublicKey) -> bytes:
    """
    Serialize public key to bytes.

    Args:
        public_key: Ed25519 public key

    Returns:
        bytes: Serialized public key
    """
    return public_key.public_bytes(encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw)


def deserialize_public_key(public_key_bytes: bytes) -> ed25519.Ed25519PublicKey:
    """
    Deserialize public key from bytes.

    Args:
        public_key_bytes: Serialized public key

    Returns:
        Ed25519PublicKey: Deserialized public key
    """
    return ed25519.Ed25519PublicKey.from_public_bytes(public_key_bytes)


def get_demo_private_key() -> ed25519.Ed25519PrivateKey:
    """
    Return the demo private key for sandbox signing flows.

    Uses configured hex value if provided, otherwise generates
    an ephemeral key for the process lifetime.
    """
    global _DEMO_PRIVATE_KEY
    if _DEMO_PRIVATE_KEY is not None:
        return _DEMO_PRIVATE_KEY

    if settings.demo_private_key_bytes:
        _DEMO_PRIVATE_KEY = ed25519.Ed25519PrivateKey.from_private_bytes(settings.demo_private_key_bytes)
        return _DEMO_PRIVATE_KEY

    _DEMO_PRIVATE_KEY = ed25519.Ed25519PrivateKey.generate()
    return _DEMO_PRIVATE_KEY
