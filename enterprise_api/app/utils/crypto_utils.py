"""
Cryptographic utilities for key management and encryption.
"""

import logging
import os
from typing import Optional, cast

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec, ed25519, rsa
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from encypher.core.signing import SigningKey
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.utils.aws_signer import AWSSigner

logger = logging.getLogger(__name__)

_DEMO_PRIVATE_KEY: Optional[ed25519.Ed25519PrivateKey] = None


def extract_private_key_bytes(private_key: SigningKey) -> bytes:
    """Extract raw private key bytes for HMAC key derivation.

    Supports Ed25519, EC, and RSA key types. For Ed25519 keys, returns the
    32-byte seed. For EC/RSA keys, returns DER-encoded PKCS8 bytes (since
    Raw encoding is only supported for Ed25519/X25519).
    """
    if isinstance(private_key, ed25519.Ed25519PrivateKey):
        return private_key.private_bytes_raw()
    return private_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )


_ENCRYPTED_KEY_PREFIX = b"EPK1"
_ENCRYPTED_KEY_NONCE_LEN = 12
_ENCRYPTED_SECRET_PREFIX = b"EPS1"
_ENCRYPTED_SECRET_NONCE_LEN = 12


def load_managed_signing_private_key() -> SigningKey:
    """Load managed signer private key from settings.

    Supports Ed25519, EC, and RSA PEM PKCS8/PKCS1 encoded private keys.
    """
    pem = settings.managed_signer_private_key_pem
    if not pem:
        raise ValueError("managed_signer_private_key_pem is not configured")

    try:
        key = serialization.load_pem_private_key(pem.encode("utf-8"), password=None, backend=default_backend())
    except Exception as exc:  # pragma: no cover - defensive
        raise ValueError(f"Failed to load managed signer private key: {exc}") from exc

    if not isinstance(key, (ed25519.Ed25519PrivateKey, ec.EllipticCurvePrivateKey, rsa.RSAPrivateKey)):
        raise ValueError("Managed signer private key must be Ed25519, EC, or RSA")

    return key


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
            text("SELECT private_key_encrypted, kms_key_id, kms_region FROM organizations WHERE id = :org_id"),
            {"org_id": organization_id},
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
    Encrypt Ed25519 private key for secure storage (legacy format).

    Args:
        private_key: Ed25519 private key to encrypt

    Returns:
        bytes: Encrypted private key
    """
    # Serialize private key to bytes
    private_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption(),
    )

    # Encrypt using AES-GCM
    aesgcm = AESGCM(settings.key_encryption_key_bytes)
    nonce = os.urandom(_ENCRYPTED_KEY_NONCE_LEN)
    encrypted = aesgcm.encrypt(nonce, private_bytes, None)

    return _ENCRYPTED_KEY_PREFIX + nonce + encrypted


_ENCRYPTED_PEM_KEY_PREFIX = b"EPK2"


def encrypt_private_key_pem(private_key: SigningKey) -> bytes:
    """
    Encrypt any private key (Ed25519, EC, RSA) for secure storage using PKCS8 PEM.

    Args:
        private_key: Private key to encrypt (Ed25519, EC, or RSA)

    Returns:
        bytes: Encrypted private key with EPK2 prefix
    """
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    aesgcm = AESGCM(settings.key_encryption_key_bytes)
    nonce = os.urandom(_ENCRYPTED_KEY_NONCE_LEN)
    encrypted = aesgcm.encrypt(nonce, private_pem, None)

    return _ENCRYPTED_PEM_KEY_PREFIX + nonce + encrypted


def encrypt_sensitive_value(value: str) -> bytes:
    """Encrypt a short UTF-8 secret for secure storage."""
    plaintext = value.encode("utf-8")
    aesgcm = AESGCM(settings.key_encryption_key_bytes)
    nonce = os.urandom(_ENCRYPTED_SECRET_NONCE_LEN)
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)
    return _ENCRYPTED_SECRET_PREFIX + nonce + ciphertext


def decrypt_private_key(encrypted_key: bytes) -> SigningKey:
    """
    Decrypt private key from encrypted storage.

    Handles both legacy Ed25519 raw format (EPK1 prefix) and
    PKCS8 PEM format (EPK2 prefix) for EC/RSA/Ed25519 keys.

    Args:
        encrypted_key: Encrypted private key bytes

    Returns:
        SigningKey: Decrypted private key (Ed25519, EC, or RSA)

    Raises:
        ValueError: If decryption fails
    """
    try:
        aesgcm = AESGCM(settings.key_encryption_key_bytes)

        # EPK2 format: PKCS8 PEM (supports all key types)
        if encrypted_key.startswith(_ENCRYPTED_PEM_KEY_PREFIX):
            offset = len(_ENCRYPTED_PEM_KEY_PREFIX)
            nonce = encrypted_key[offset : offset + _ENCRYPTED_KEY_NONCE_LEN]
            ciphertext = encrypted_key[offset + _ENCRYPTED_KEY_NONCE_LEN :]
            private_pem = aesgcm.decrypt(nonce, ciphertext, None)
            key = serialization.load_pem_private_key(private_pem, password=None, backend=default_backend())
            if not isinstance(key, (ed25519.Ed25519PrivateKey, ec.EllipticCurvePrivateKey, rsa.RSAPrivateKey)):
                raise ValueError(f"Unsupported key type: {type(key)}")
            return key

        # Legacy EPK1 format: Ed25519 raw bytes
        if encrypted_key.startswith(_ENCRYPTED_KEY_PREFIX) and len(encrypted_key) > (len(_ENCRYPTED_KEY_PREFIX) + _ENCRYPTED_KEY_NONCE_LEN):
            offset = len(_ENCRYPTED_KEY_PREFIX)
            nonce = encrypted_key[offset : offset + _ENCRYPTED_KEY_NONCE_LEN]
            ciphertext = encrypted_key[offset + _ENCRYPTED_KEY_NONCE_LEN :]
            private_key_bytes = aesgcm.decrypt(nonce, ciphertext, None)
        else:
            private_key_bytes = aesgcm.decrypt(settings.encryption_nonce_bytes, encrypted_key, None)

        return ed25519.Ed25519PrivateKey.from_private_bytes(private_key_bytes)
    except Exception as e:
        raise ValueError(f"Failed to decrypt private key: {str(e)}")


def decrypt_sensitive_value(encrypted_value: bytes) -> str:
    """Decrypt a short UTF-8 secret from encrypted storage."""
    try:
        if not encrypted_value.startswith(_ENCRYPTED_SECRET_PREFIX):
            raise ValueError("Encrypted secret has invalid prefix")

        offset = len(_ENCRYPTED_SECRET_PREFIX)
        nonce = encrypted_value[offset : offset + _ENCRYPTED_SECRET_NONCE_LEN]
        ciphertext = encrypted_value[offset + _ENCRYPTED_SECRET_NONCE_LEN :]
        aesgcm = AESGCM(settings.key_encryption_key_bytes)
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
        return plaintext.decode("utf-8")
    except Exception as e:
        raise ValueError(f"Failed to decrypt sensitive value: {str(e)}")


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
