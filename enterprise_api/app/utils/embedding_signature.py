"""Helpers for minimal embedding signature generation."""

from __future__ import annotations

import hashlib
import hmac
import secrets
from typing import Optional

from app.config import settings

_EPHEMERAL_SECRET: Optional[bytes] = None


def _get_secret_bytes() -> bytes:
    global _EPHEMERAL_SECRET

    configured = settings.embedding_signature_secret_bytes
    if configured:
        return configured

    if settings.is_production:
        raise RuntimeError("Embedding signature secret is required in production")

    if _EPHEMERAL_SECRET is None:
        _EPHEMERAL_SECRET = secrets.token_bytes(32)

    return _EPHEMERAL_SECRET


def compute_signature_hash(ref_id: int) -> str:
    """Compute the HMAC signature hash for a reference id."""
    secret = _get_secret_bytes()
    ref_hex = format(ref_id, "08x")
    return hmac.new(secret, ref_hex.encode("utf-8"), hashlib.sha256).hexdigest()
