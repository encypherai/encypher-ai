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
from typing import Optional, cast

from encypher.core.signing import SigningKey
from app.utils.aws_signer import AWSSigner

_DEMO_PRIVATE_KEY: Optional[ed25519.Ed25519PrivateKey] = None


async def load_organization_private_key(
    organization_id: str,
    db: AsyncSession
) -> SigningKey:
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
            text("SELECT private_key_encrypted, kms_key_id, kms_region FROM organizations WHERE id = :org_id"),
            {"org_id": organization_id}
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
        # If no local key, maybe check for KMS config from settings or another source?
        # For scaffolding, we raise error if local key missing AND no KMS logic active.
        raise ValueError(f"No private key found for organization {organization_id}")

    # Decrypt using AES-GCM
    aesgcm = AESGCM(settings.key_encryption_key_bytes)
    private_key_bytes = aesgcm.decrypt(
        settings.encryption_nonce_bytes,
        bytes(encrypted_key),
        None
    )

    # Load Ed25519 private key
    return ed25519.Ed25519PrivateKey.from_private_bytes(private_key_bytes)


async def load_organization_public_key(
    organization_id: str,
    db: AsyncSession
) -> ed25519.Ed25519PublicKey:
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
        # Load the private key first (which handles demo org)
        # Use the synchronous helper if we are in a sync context or just call the helper
        # Actually, get_demo_private_key is synchronous.
        private_key = get_demo_private_key()
        return private_key.public_key()
    
    result = await db.execute(
        text("SELECT public_key FROM organizations WHERE id = :org_id"),
        {"org_id": organization_id}
    )
    row = result.fetchone()

    if not row or not row[0]:
        raise ValueError(f"No public key found for organization {organization_id}")

    public_key_bytes = bytes(row[0])

    # Load Ed25519 public key from raw bytes
    return ed25519.Ed25519PublicKey.from_public_bytes(public_key_bytes)


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
        # Decrypt using AES-GCM
        aesgcm = AESGCM(settings.key_encryption_key_bytes)
        private_key_bytes = aesgcm.decrypt(
            settings.encryption_nonce_bytes,
            encrypted_key,
            None
        )

        # Load Ed25519 private key
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
        _DEMO_PRIVATE_KEY = ed25519.Ed25519PrivateKey.from_private_bytes(
            cast(bytes, settings.demo_private_key_bytes)
        )
        return _DEMO_PRIVATE_KEY

    _DEMO_PRIVATE_KEY = ed25519.Ed25519PrivateKey.generate()
    return _DEMO_PRIVATE_KEY
