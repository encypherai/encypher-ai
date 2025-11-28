"""
Security utilities for authentication and authorization
"""
import hashlib
import base64
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import bcrypt
import jwt  # PyJWT
from .config import settings


def _prehash_password(password: str) -> bytes:
    """
    Pre-hash password with SHA-256 to avoid bcrypt's 72-byte limit.
    Returns base64-encoded hash (44 chars) which is always < 72 bytes.
    """
    sha256_hash = hashlib.sha256(password.encode('utf-8')).digest()
    return base64.b64encode(sha256_hash)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    prehashed = _prehash_password(plain_password)
    try:
        return bcrypt.checkpw(prehashed, hashed_password.encode('utf-8'))
    except Exception:
        # Fall back to trying without pre-hash for legacy passwords
        try:
            return bcrypt.checkpw(
                plain_password.encode('utf-8'), 
                hashed_password.encode('utf-8')
            )
        except Exception:
            return False


def get_password_hash(password: str) -> str:
    """Hash a password (pre-hashes with SHA-256 to avoid 72-byte limit)"""
    prehashed = _prehash_password(password)
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(prehashed, salt)
    return hashed.decode('utf-8')


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create a JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and verify a JWT token"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None


def verify_token(token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:  # noqa: S107
    """Verify a token and check its type"""
    payload = decode_token(token)
    if payload and payload.get("type") == token_type:
        return payload
    return None
