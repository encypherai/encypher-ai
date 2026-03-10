"""Base-256 Variation Selector + Reed-Solomon Cryptographic Embedding (ECC mode)

Extends the base VS256 encoding with Reed-Solomon error correction for
partial copy-paste survivability, with full 128-bit HMAC security.

Layout (44 VS chars total):
- Magic prefix:      4 chars  (VS240-VS243, format marker)
- log_id:           16 chars  (16 bytes, transparency log reference)
- HMAC-SHA256/128:  16 chars  (16 bytes, 128-bit cryptographic proof)
- RS parity:         8 chars  (8 bytes, Reed-Solomon GF(256) parity)

Error correction capacity (reedsolo RS(40, 32)):
- 8 parity symbols over GF(256)
- Corrects up to 4 unknown errors (corrupted VS chars)
- Corrects up to 8 known erasures (missing VS chars with known positions)
- In practice: poppler drops ~2.3 VS chars on average from a contiguous
  block (known erasure positions), so 8-erasure capacity is ample.

Security:
- 128-bit log_id uniqueness (hyperscale-safe: ~2e-12 collision P over 10yr at 20B/day)
- 128-bit HMAC security (truncated from 256-bit SHA-256)
- Matches the security level of the non-ECC base mode (both 128-bit HMAC)
- RS parity does NOT weaken HMAC: parity is computed over log_id+HMAC bytes,
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

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import hmac as crypto_hmac
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from reedsolo import ReedSolomonError, RSCodec

# Re-use the VS256 alphabet and log_id from vs256_crypto
from app.utils.vs256_crypto import (
    LOG_ID_BYTES,
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
HMAC_BYTES = 16  # HMAC-SHA256/128 (full 128-bit security)
DATA_BYTES = LOG_ID_BYTES + HMAC_BYTES  # 32
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


def create_signed_marker(
    log_id: bytes,
    signing_key: bytes,
    sentence_text: str | None = None,
) -> str:
    """Create a 44-char RS-protected VS256 signed marker with 128-bit HMAC.

    Layout: MAGIC(4) + log_id(16) + HMAC-128(16) + RS_PARITY(8) = 44 chars.

    Args:
        log_id: 16-byte identifier from generate_log_id().
        signing_key: 32-byte secret key for HMAC.
        sentence_text: Optional sentence text to bind cryptographically.
            If provided, HMAC input includes log_id + SHA256(NFC(text))[:8].
            If omitted, log_id-only signature format is produced.

    Returns:
        44 VS characters (invisible in supported platforms).
    """
    if len(log_id) != LOG_ID_BYTES:
        raise ValueError(f"log_id must be {LOG_ID_BYTES} bytes, got {len(log_id)}")
    if len(signing_key) < 32:
        raise ValueError("Signing key must be at least 32 bytes")

    # HMAC-SHA256 truncated to 16 bytes (128-bit security)
    h = crypto_hmac.HMAC(signing_key, hashes.SHA256(), backend=default_backend())
    h.update(log_id)
    if sentence_text is not None:
        nfc_bytes = unicodedata.normalize("NFC", sentence_text).encode("utf-8")
        h.update(hashlib.sha256(nfc_bytes).digest()[:CONTENT_COMMITMENT_BYTES])
    hmac_truncated = h.finalize()[:HMAC_BYTES]  # 16 bytes

    # Data = log_id + HMAC-128 (32 bytes)
    data = log_id + hmac_truncated

    # RS encode: 32 data -> 40 encoded (32 data + 8 parity)
    rs_encoded = bytes(_RS.encode(data))  # 40 bytes
    assert len(rs_encoded) == PAYLOAD_BYTES

    return MAGIC_PREFIX + encode_bytes_vs256(rs_encoded)


def verify_signed_marker(
    signature: str,
    signing_key: bytes,
    sentence_text: str | None = None,
    erase_positions: list[int] | None = None,
) -> Tuple[bool, Optional[bytes]]:
    """Verify an RS-protected VS256 signed marker and extract the log_id.

    Tries content-bound verification first; falls back to content-free for
    backward compatibility. Can recover from up to 8 erasures or 4 errors.

    Args:
        signature: 44-char VS256 ECC signature string.
        signing_key: 32-byte secret key for HMAC verification.
        sentence_text: Optional sentence text used for content-bound signatures.
        erase_positions: Optional list of 0-indexed positions within the
            40-char payload (after magic prefix) that are known erasures.

    Returns:
        (True, log_id_bytes) on success, (False, None) on any failure.
    """
    if len(signature) != SIGNATURE_CHARS:
        return False, None

    if signature[:MAGIC_PREFIX_LEN] != MAGIC_PREFIX:
        return False, None

    try:
        payload_bytes = decode_bytes_vs256(signature[MAGIC_PREFIX_LEN:])
        if len(payload_bytes) != PAYLOAD_BYTES:
            return False, None

        decoded = bytes(_RS.decode(payload_bytes, erase_pos=erase_positions)[0])
        if len(decoded) != DATA_BYTES:
            return False, None

        log_id = decoded[:LOG_ID_BYTES]
        hmac_received = decoded[LOG_ID_BYTES : LOG_ID_BYTES + HMAC_BYTES]

        def _hmac(include_text: bool) -> bytes:
            h = crypto_hmac.HMAC(signing_key, hashes.SHA256(), backend=default_backend())
            h.update(log_id)
            if include_text and sentence_text is not None:
                nfc_bytes = unicodedata.normalize("NFC", sentence_text).encode("utf-8")
                h.update(hashlib.sha256(nfc_bytes).digest()[:CONTENT_COMMITMENT_BYTES])
            return h.finalize()[:HMAC_BYTES]

        if hmac_received == _hmac(include_text=True):
            return True, log_id
        if sentence_text is not None and hmac_received == _hmac(include_text=False):
            return True, log_id
        return False, None

    except (ReedSolomonError, Exception):
        return False, None


def find_all_markers(text: str) -> list[tuple[int, int, str]]:
    """Find all 44-char ECC VS256 signed markers by magic prefix + length.

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
                if len(candidate) == SIGNATURE_CHARS and all(ch in VS_CHAR_SET for ch in candidate[MAGIC_PREFIX_LEN:]):
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
)


def create_embedded_sentence(
    sentence: str,
    log_id: bytes,
    signing_key: bytes,
) -> str:
    """Create a sentence with RS-protected VS256 signed marker embedded safely."""
    signature = create_signed_marker(log_id, signing_key, sentence_text=sentence)
    return embed_signature_safely(sentence, signature)


# =============================================================================
# ERASURE RECOVERY HELPERS
# =============================================================================


def recover_from_partial_extraction(
    extracted_chars: list[tuple[int, str | None]],
) -> Tuple[bool, Optional[bytes], Optional[bytes]]:
    """Attempt to recover a signature from partially extracted VS chars.

    Args:
        extracted_chars: List of (position, char_or_None) tuples where
            position is 0-43 (within the 44-char signature) and char is
            the extracted VS char or None if missing.

    Returns:
        (success, log_id_bytes, raw_payload) — log_id/payload are None on failure.
    """
    if len(extracted_chars) != SIGNATURE_CHARS:
        return False, None, None

    prefix_chars = extracted_chars[:MAGIC_PREFIX_LEN]
    payload_entries = extracted_chars[MAGIC_PREFIX_LEN:]

    for _pos, ch in prefix_chars:
        if ch is None or ch not in VS_CHAR_SET:
            return False, None, None

    prefix = "".join(ch for _, ch in prefix_chars)
    if prefix != MAGIC_PREFIX:
        return False, None, None

    payload = bytearray(PAYLOAD_BYTES)
    erase_positions = []
    for i, (_pos, ch) in enumerate(payload_entries):
        if ch is None or ch not in VS_CHAR_SET:
            erase_positions.append(i)
            payload[i] = 0
        else:
            payload[i] = VS_TO_BYTE[ch]

    if len(erase_positions) > _RS_NSYM:
        return False, None, None

    try:
        decoded = bytes(_RS.decode(bytes(payload), erase_pos=erase_positions)[0])
        log_id = decoded[:LOG_ID_BYTES]
        return True, log_id, decoded
    except (ReedSolomonError, Exception):
        return False, None, None
