"""
API Key generation and management utilities.

Provides secure API key generation, hashing, and verification for AI company authentication.
"""
import secrets
import bcrypt
from typing import Tuple


API_KEY_PREFIX = "lic_"
API_KEY_LENGTH = 32  # bytes (64 hex characters)


def generate_api_key() -> Tuple[str, str, str]:
    """
    Generate a secure API key for AI company authentication.

    Returns:
        Tuple of (api_key, api_key_hash, api_key_prefix)
        - api_key: The full API key to show to the user (only shown once)
        - api_key_hash: Bcrypt hash to store in database
        - api_key_prefix: First 8 characters for display purposes

    Example:
        >>> api_key, api_key_hash, prefix = generate_api_key()
        >>> print(f"API Key: {api_key}")
        >>> print(f"Prefix: {prefix}")
    """
    # Generate cryptographically secure random bytes
    random_bytes = secrets.token_hex(API_KEY_LENGTH)

    # Create full API key with prefix
    api_key = f"{API_KEY_PREFIX}{random_bytes}"

    # Create display prefix (e.g., "lic_abc1")
    api_key_prefix = api_key[:8]

    # Hash the API key with bcrypt
    api_key_hash = hash_api_key(api_key)

    return api_key, api_key_hash, api_key_prefix


def hash_api_key(api_key: str) -> str:
    """
    Hash an API key using bcrypt.

    Args:
        api_key: The API key to hash

    Returns:
        Bcrypt hash of the API key as a string
    """
    # Convert to bytes and hash with bcrypt
    api_key_bytes = api_key.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(api_key_bytes, salt)

    # Return as string for database storage
    return hashed.decode('utf-8')


def verify_api_key(api_key: str, api_key_hash: str) -> bool:
    """
    Verify an API key against its hash.

    Args:
        api_key: The API key to verify
        api_key_hash: The stored bcrypt hash

    Returns:
        True if the API key matches the hash, False otherwise
    """
    try:
        api_key_bytes = api_key.encode('utf-8')
        hash_bytes = api_key_hash.encode('utf-8')
        return bcrypt.checkpw(api_key_bytes, hash_bytes)
    except Exception:
        return False


def is_valid_api_key_format(api_key: str) -> bool:
    """
    Validate the format of an API key.

    Args:
        api_key: The API key to validate

    Returns:
        True if the API key has the correct format, False otherwise
    """
    if not api_key or not isinstance(api_key, str):
        return False

    # Check prefix
    if not api_key.startswith(API_KEY_PREFIX):
        return False

    # Check length (prefix + 64 hex chars)
    expected_length = len(API_KEY_PREFIX) + (API_KEY_LENGTH * 2)
    if len(api_key) != expected_length:
        return False

    # Check that the rest is valid hex
    key_part = api_key[len(API_KEY_PREFIX):]
    try:
        int(key_part, 16)  # Will raise ValueError if not valid hex
        return True
    except ValueError:
        return False
