"""
Security utilities for key generation and validation
"""
import secrets
import hashlib
from .config import settings


def generate_api_key() -> str:
    """
    Generate a secure API key
    Format: ency_<random_string>
    """
    # Generate cryptographically secure random bytes
    random_bytes = secrets.token_urlsafe(settings.KEY_LENGTH)
    
    # Create key with prefix
    api_key = f"{settings.KEY_PREFIX}{random_bytes}"
    
    return api_key


def hash_api_key(api_key: str) -> str:
    """
    Hash an API key for storage
    Uses SHA-256 for fast lookups
    """
    return hashlib.sha256(api_key.encode()).hexdigest()


def verify_api_key_format(api_key: str) -> bool:
    """
    Verify that an API key has the correct format
    """
    if not api_key:
        return False
    
    # Check prefix
    if not api_key.startswith(settings.KEY_PREFIX):
        return False
    
    # Check minimum length
    if len(api_key) < len(settings.KEY_PREFIX) + 20:
        return False
    
    return True


def generate_key_fingerprint(api_key: str) -> str:
    """
    Generate a fingerprint for an API key
    Used for display purposes (first 8 chars of hash)
    """
    key_hash = hash_api_key(api_key)
    return key_hash[:8]
