"""Base-256 Variation Selector + Reed-Solomon Cryptographic Embedding (ECC mode)

Extends the base VS256 encoding with Reed-Solomon error correction for
partial copy-paste survivability, with full 128-bit HMAC security.

Layout (44 VS chars total):
- Magic prefix:      4 chars  (VS240-VS243, format marker)
- UUID:             16 chars  (16 bytes, database reference)
- HMAC-SHA256/128:  16 chars  (16 bytes, 128-bit cryptographic proof)
- RS parity:         8 chars  (8 bytes, Reed-Solomon GF(256) parity)

Error correction capacity (reedsolo RS(40, 32)):
- 8 parity symbols over GF(256)
- Corrects up to 4 unknown errors (corrupted VS chars)
- Corrects up to 8 known erasures (missing VS chars with known positions)
- In practice: poppler drops ~2.3 VS chars on average from a contiguous
  block (known erasure positions), so 8-erasure capacity is ample.

Security:
- 128-bit UUID uniqueness (unguessable)
- 128-bit HMAC security (truncated from 256-bit SHA-256)
- Matches the security level of the non-ECC base mode (both 128-bit HMAC)
- RS parity does NOT weaken HMAC: parity is computed over UUID+HMAC bytes,
  so an attacker still needs the signing key to produce a valid HMAC.

Compatibility:
- Same VS256 alphabet (VS1-VS256)
- Same magic prefix (VS240-VS243) — detection uses prefix + length
- 44-char total footprint (8 chars more than non-ECC 36-char mode)
- Detection distinguishes ECC (44 chars) from non-ECC (36 chars) by length
"""

import hashlib
import unicodedata
from typing import Optional, Tuple
from uuid import UUID

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import hmac as crypto_hmac
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from reedsolo import RSCodec, ReedSolomonError

# Re-use the VS256 alphabet from vs256_crypto
from app.utils.vs256_crypto import (
    BYTE_TO_VS,
    MAGIC_PREFIX,
    MAGIC_PREFIX_LEN,
    VS_CHAR_SET,
    VS_TO_BYTE,
    decode_bytes_vs256,
    encode_bytes_vs256,
)

# =============================================================================
# RS CODEC — 8 parity symbols over GF(256)
# =============================================================================

_RS_NSYM = 8  # parity symbols
_RS = RSCodec(_RS_NSYM)

# Layout constants
UUID_BYTES = 16
HMAC_BYTES = 16  # HMAC-SHA256/128 (full 128-bit security)
DATA_BYTES = UUID_BYTES + HMAC_BYTES  # 32
PARITY_BYTES = _RS_NSYM  # 8
PAYLOAD_BYTES = DATA_BYTES + PARITY_BYTES  # 40
PAYLOAD_CHARS = PAYLOAD_BYTES  # 1 char per byte (base-256)
SIGNATURE_CHARS = MAGIC_PREFIX_LEN + PAYLOAD_CHARS  # 44 total

# Sentence content commitment bytes appended to HMAC input when enabled.
CONTENT_COMMITMENT_BYTES = 8


# =============================================================================
# KEY DERIVATION (same as vs256_crypto)
# =============================================================================


def derive_signing_key_from_private_key(private_key: Ed25519PrivateKey) -> bytes:
    """Derive a 32-byte HMAC signing key from an Ed25519 private key."""
    raw = private_key.private_bytes_raw()
    return hashlib.sha256(raw + b"vs256_rs_signing_key").digest()


# =============================================================================
# CREATE / VERIFY
# =============================================================================


def create_minimal_signed_uuid(
    sentence_uuid: UUID,
    signing_key: bytes,
    sentence_text: str | None = None,
) -> str:
    """Create a 44-char RS-protected VS256 signature with 128-bit HMAC.

    Layout: MAGIC(4) + UUID(16) + HMAC-128(16) + RS_PARITY(8) = 44 chars.

    Args:
        sentence_uuid: UUID for this sentence (stored in DB).
        signing_key: 32-byte secret key for HMAC.
        sentence_text: Optional sentence text to bind cryptographically.
            If provided, HMAC input includes UUID + SHA256(NFC(text))[:8].
            If omitted, legacy UUID-only signature format is produced.

    Returns:
        44 VS characters (invisible in supported platforms).
    """
    if len(signing_key) < 32:
        raise ValueError("Signing key must be at least 32 bytes")

    uuid_bytes = sentence_uuid.bytes  # 16 bytes

    # HMAC-SHA256 truncated to 16 bytes (128-bit security)
    h = crypto_hmac.HMAC(signing_key, hashes.SHA256(), backend=default_backend())
    h.update(uuid_bytes)
    if sentence_text is not None:
        nfc_bytes = unicodedata.normalize("NFC", sentence_text).encode("utf-8")
        h.update(hashlib.sha256(nfc_bytes).digest()[:CONTENT_COMMITMENT_BYTES])
    hmac_truncated = h.finalize()[:HMAC_BYTES]  # 16 bytes

    # Data = UUID + HMAC-128 (32 bytes)
    data = uuid_bytes + hmac_truncated

    # RS encode: 32 data → 40 encoded (32 data + 8 parity)
    rs_encoded = bytes(_RS.encode(data))  # 40 bytes
    assert len(rs_encoded) == PAYLOAD_BYTES

    # Encode as VS chars
    return MAGIC_PREFIX + encode_bytes_vs256(rs_encoded)


def verify_minimal_signed_uuid(
    signature: str,
    signing_key: bytes,
    sentence_text: str | None = None,
    erase_positions: list[int] | None = None,
) -> Tuple[bool, Optional[UUID]]:
    """Verify an RS-protected VS256 signature and extract the UUID.

    Can recover from up to 8 erasures (known missing positions) or
    4 unknown errors (corrupted chars).

    Args:
        signature: 44-char VS256 ECC signature string.
        signing_key: 32-byte secret key for HMAC verification.
        sentence_text: Optional sentence text used for content-bound signatures.
            When provided, verifier first checks UUID+content commitment, then
            falls back to legacy UUID-only verification for backward compatibility.
        erase_positions: Optional list of 0-indexed positions within the
            40-char payload (after magic prefix) that are known erasures.

    Returns:
        (is_valid, uuid) — uuid is None on failure.
    """
    if len(signature) != SIGNATURE_CHARS:
        return False, None

    # Verify magic prefix
    if signature[:MAGIC_PREFIX_LEN] != MAGIC_PREFIX:
        return False, None

    try:
        # Decode VS chars → bytes
        payload_bytes = decode_bytes_vs256(signature[MAGIC_PREFIX_LEN:])
        if len(payload_bytes) != PAYLOAD_BYTES:
            return False, None

        # RS decode (correct errors / erasures)
        decoded = bytes(_RS.decode(payload_bytes, erase_pos=erase_positions)[0])
        if len(decoded) != DATA_BYTES:
            return False, None

        # Split into UUID and HMAC
        uuid_bytes = decoded[:UUID_BYTES]
        hmac_received = decoded[UUID_BYTES : UUID_BYTES + HMAC_BYTES]

        # Recompute HMAC
        h = crypto_hmac.HMAC(signing_key, hashes.SHA256(), backend=default_backend())
        h.update(uuid_bytes)
        if sentence_text is not None:
            nfc_bytes = unicodedata.normalize("NFC", sentence_text).encode("utf-8")
            h.update(hashlib.sha256(nfc_bytes).digest()[:CONTENT_COMMITMENT_BYTES])
        hmac_expected = h.finalize()[:HMAC_BYTES]

        if hmac_received != hmac_expected:
            if sentence_text is None:
                return False, None
            legacy_h = crypto_hmac.HMAC(signing_key, hashes.SHA256(), backend=default_backend())
            legacy_h.update(uuid_bytes)
            legacy_hmac_expected = legacy_h.finalize()[:HMAC_BYTES]
            if hmac_received != legacy_hmac_expected:
                return False, None

        return True, UUID(bytes=uuid_bytes)

    except (ReedSolomonError, Exception):
        return False, None


def find_all_minimal_signed_uuids(text: str) -> list[tuple[int, int, str]]:
    """Find all 44-char ECC VS256 signatures by magic prefix + length.

    Scans for the 4-char magic prefix followed by exactly 40 valid VS chars.
    This distinguishes ECC (44 chars) from non-ECC (36 chars) signatures.
    """
    signatures = []
    i = 0
    text_len = len(text)

    while i <= text_len - SIGNATURE_CHARS:
        if text[i] == MAGIC_PREFIX[0]:
            if text[i : i + MAGIC_PREFIX_LEN] == MAGIC_PREFIX:
                candidate = text[i : i + SIGNATURE_CHARS]
                if len(candidate) == SIGNATURE_CHARS and all(
                    ch in VS_CHAR_SET for ch in candidate[MAGIC_PREFIX_LEN:]
                ):
                    signatures.append((i, i + SIGNATURE_CHARS, candidate))
                    i += SIGNATURE_CHARS
                    continue
        i += 1

    return signatures


# =============================================================================
# SAFE EMBEDDING (re-exported from vs256_crypto)
# =============================================================================

from app.utils.vs256_crypto import (  # noqa: E402
    embed_signature_safely,
    get_signature_position,
)


def create_safely_embedded_sentence(
    sentence: str,
    sentence_uuid: UUID,
    signing_key: bytes,
) -> str:
    """Create a sentence with RS-protected VS256 signature embedded safely."""
    signature = create_minimal_signed_uuid(sentence_uuid, signing_key)
    return embed_signature_safely(sentence, signature)


# =============================================================================
# ERASURE RECOVERY HELPERS
# =============================================================================


def recover_from_partial_extraction(
    extracted_chars: list[tuple[int, str | None]],
) -> Tuple[bool, Optional[UUID], Optional[bytes]]:
    """Attempt to recover a signature from partially extracted VS chars.

    Args:
        extracted_chars: List of (position, char_or_None) tuples where
            position is 0-43 (within the 44-char signature) and char is
            the extracted VS char or None if missing.

    Returns:
        (success, uuid, raw_payload) — uuid/payload are None on failure.
    """
    if len(extracted_chars) != SIGNATURE_CHARS:
        return False, None, None

    # Separate magic prefix and payload
    prefix_chars = extracted_chars[:MAGIC_PREFIX_LEN]
    payload_entries = extracted_chars[MAGIC_PREFIX_LEN:]

    # Verify magic prefix (must be complete)
    for _pos, ch in prefix_chars:
        if ch is None or ch not in VS_CHAR_SET:
            return False, None, None

    prefix = "".join(ch for _, ch in prefix_chars)
    if prefix != MAGIC_PREFIX:
        return False, None, None

    # Build payload with erasure positions
    payload = bytearray(PAYLOAD_BYTES)
    erase_positions = []
    for i, (_pos, ch) in enumerate(payload_entries):
        if ch is None or ch not in VS_CHAR_SET:
            erase_positions.append(i)
            payload[i] = 0  # placeholder
        else:
            payload[i] = VS_TO_BYTE[ch]

    if len(erase_positions) > _RS_NSYM:
        # Too many erasures — can't recover
        return False, None, None

    try:
        decoded = bytes(_RS.decode(bytes(payload), erase_pos=erase_positions)[0])
        uuid_bytes = decoded[:UUID_BYTES]
        return True, UUID(bytes=uuid_bytes), decoded
    except (ReedSolomonError, Exception):
        return False, None, None
