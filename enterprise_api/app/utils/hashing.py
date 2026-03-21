"""Shared cryptographic hashing utilities."""

import hashlib


def compute_sha256(data: bytes) -> str:
    """Return SHA-256 hash of data with 'sha256:' prefix."""
    return "sha256:" + hashlib.sha256(data).hexdigest()
