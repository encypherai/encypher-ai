"""Base-256 Variation Selector Cryptographic Embedding (vs256_embedding mode)

Uses ALL 256 Unicode Variation Selectors as a base-256 alphabet for maximum
density invisible signatures.

Key features:
- Base-256 encoding using VS1-VS256 (1 char per byte, 8 bits per character)
- HMAC-SHA256 for minimal signed UUIDs (sentence-level)
- Magic prefix detection (4 VS chars) to distinguish from other VS uses
- Compact encoding: 36 chars per minimal signature (4 prefix + 32 payload)
- Works in Google Docs, PDF, browsers (NOT Microsoft Word)

Alphabet:
- VS1-VS16 (BMP):            U+FE00 - U+FE0F  (16 chars, byte values 0-15)
- VS17-VS256 (Supplementary): U+E0100 - U+E01EF (240 chars, byte values 16-255)
- Total: 256 characters = 1 byte per character

Compatibility:
- Google Docs: Renders invisibly ✅
- PDF (from GDocs): Preserves invisibility ✅
- Web browsers: Renders invisibly ✅
- Microsoft Word: Shows □ box glyphs ❌ — use zw_embedding instead

Density comparison:
- zw_embedding (base-4):      128 chars per signature, Word-compatible
- vs256_embedding (base-256):  36 chars per signature, NOT Word-compatible
- Improvement: 3.6x fewer characters
"""

import hashlib
import os
import unicodedata
from typing import Optional, Tuple

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import hmac as crypto_hmac
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


# =============================================================================
# BASE-256 VARIATION SELECTOR ALPHABET
# =============================================================================
#
# VS1-VS16 (BMP):             U+FE00 - U+FE0F  (16 chars, byte values 0-15)
# VS17-VS256 (Supplementary): U+E0100 - U+E01EF (240 chars, byte values 16-255)
#
# Total: 256 characters = 1 byte per character (8 bits per character)
# This is 4x denser than base-4 ZW encoding (4 chars per byte)
# =============================================================================

VS_BMP_START = 0xFE00    # VS1
VS_BMP_END = 0xFE0F      # VS16
VS_SUPP_START = 0xE0100  # VS17
VS_SUPP_END = 0xE01EF    # VS256

# Build lookup tables at module load time
BYTE_TO_VS: list[str] = []
VS_TO_BYTE: dict[str, int] = {}

# VS1-VS16 → byte values 0-15
for _i in range(16):
    _ch = chr(VS_BMP_START + _i)
    BYTE_TO_VS.append(_ch)
    VS_TO_BYTE[_ch] = _i

# VS17-VS256 → byte values 16-255
for _i in range(240):
    _ch = chr(VS_SUPP_START + _i)
    BYTE_TO_VS.append(_ch)
    VS_TO_BYTE[_ch] = _i + 16

VS_CHAR_SET: frozenset = frozenset(VS_TO_BYTE.keys())

# Verify completeness
assert len(BYTE_TO_VS) == 256, f"Expected 256 VS chars, got {len(BYTE_TO_VS)}"
assert len(VS_TO_BYTE) == 256, f"Expected 256 VS mappings, got {len(VS_TO_BYTE)}"


# =============================================================================
# MAGIC PREFIX - Distinguishes VS256 signatures from other VS usage
# =============================================================================
#
# Uses supplementary-plane VS chars (VS240-VS243) that never appear in
# natural emoji variation sequences. VS1-VS16 are common in emoji text
# (e.g. U+FE0F text presentation selector), but VS240+ are not.
#
# Byte values: 239, 240, 241, 242
# Code points: U+E018F, U+E0190, U+E0191, U+E0192
# =============================================================================

MAGIC_PREFIX = BYTE_TO_VS[239] + BYTE_TO_VS[240] + BYTE_TO_VS[241] + BYTE_TO_VS[242]
MAGIC_PREFIX_LEN = 4

# Signature layout constants
LOG_ID_BYTES = 16            # 128-bit random log reference (hyperscale-safe)
PAYLOAD_BYTES = 32           # 16 log_id + 16 HMAC
PAYLOAD_CHARS = 32           # 1 char per byte in base-256
SIGNATURE_CHARS = MAGIC_PREFIX_LEN + PAYLOAD_CHARS  # 36 total

# Sentence content commitment bytes appended to HMAC input when enabled.
CONTENT_COMMITMENT_BYTES = 8


# =============================================================================
# BASE-256 ENCODING/DECODING
# =============================================================================


def encode_byte_vs256(byte_value: int) -> str:
    """
    Encode a single byte (0-255) as one Variation Selector character.

    Base-256: each byte maps to exactly 1 VS character.
    - Bytes 0-15  → VS1-VS16  (U+FE00 - U+FE0F, BMP)
    - Bytes 16-255 → VS17-VS256 (U+E0100 - U+E01EF, Supplementary)

    Args:
        byte_value: Integer 0-255

    Returns:
        Single VS character
    """
    if not 0 <= byte_value <= 255:
        raise ValueError(f"Byte value must be 0-255, got {byte_value}")
    return BYTE_TO_VS[byte_value]


def decode_byte_vs256(char: str) -> int:
    """
    Decode a single Variation Selector character to a byte value.

    Args:
        char: Single VS character

    Returns:
        Byte value (0-255)
    """
    if len(char) != 1:
        raise ValueError(f"Expected 1 character, got {len(char)}")
    result = VS_TO_BYTE.get(char)
    if result is None:
        raise ValueError(f"Invalid VS character: U+{ord(char):04X}")
    return result


def encode_bytes_vs256(data: bytes) -> str:
    """
    Encode arbitrary binary data as Variation Selector characters.

    Each byte becomes exactly 1 VS character (base-256).

    Args:
        data: Binary data to encode

    Returns:
        String of VS characters (len == len(data))
    """
    return "".join(BYTE_TO_VS[b] for b in data)


def decode_bytes_vs256(encoded: str) -> bytes:
    """
    Decode Variation Selector encoded data back to bytes.

    Args:
        encoded: String of VS characters

    Returns:
        Decoded binary data
    """
    result = []
    for ch in encoded:
        val = VS_TO_BYTE.get(ch)
        if val is None:
            raise ValueError(f"Invalid VS character: U+{ord(ch):04X}")
        result.append(val)
    return bytes(result)


# =============================================================================
# SIGNED MARKER - Sentence-level provenance (base-256)
# =============================================================================
#
# Format (36 VS chars total):
# - Magic prefix: 4 chars (VS240-VS243, signature marker)
# - log_id: 16 chars (16 bytes, transparency log reference)
# - HMAC-SHA256: 16 chars (16 bytes truncated, cryptographic proof)
#
# Compare to zw_embedding: 128 chars for same 32-byte payload
# Improvement: 3.6x fewer characters (36 vs 128)
#
# Detection: Magic prefix + 32 contiguous VS chars
# =============================================================================


def generate_log_id() -> bytes:
    """
    Generate a random 16-byte log ID.

    128-bit random identifier referencing a transparency log entry.
    Birthday collision probability is ~2e-12 over 10 years at 20B msg/day
    across the global AI ecosystem -- safe at any deployment scale.
    """
    return os.urandom(LOG_ID_BYTES)


def create_signed_marker(
    log_id: bytes,
    signing_key: bytes,
    sentence_text: str | None = None,
) -> str:
    """
    Create a compact cryptographically signed marker using base-256 VS encoding.

    Format (36 VS chars total):
    - Magic prefix: 4 chars (VS240-VS243, format marker)
    - log_id: 16 chars (transparency log reference)
    - HMAC-SHA256: 16 chars (cryptographic proof, 128-bit truncated)

    Security:
    - 128-bit log_id uniqueness (hyperscale-safe)
    - 128-bit HMAC security (truncated from 256-bit)
    - Signing key should be org-specific secret (derived from private key)

    Args:
        log_id: 16-byte identifier returned by generate_log_id().
        signing_key: 32-byte secret key for HMAC (org-specific).
        sentence_text: Optional sentence text to bind cryptographically.
            If provided, HMAC input includes log_id + SHA256(NFC(text))[:8].
            If omitted, log_id-only signature format is produced.

    Returns:
        36 VS characters (invisible in Google Docs, PDF, browsers)
    """
    if len(log_id) != LOG_ID_BYTES:
        raise ValueError(f"log_id must be {LOG_ID_BYTES} bytes, got {len(log_id)}")
    if len(signing_key) < 32:
        raise ValueError("Signing key must be at least 32 bytes")

    # Create HMAC-SHA256 over log_id, truncate to 16 bytes (128-bit security)
    h = crypto_hmac.HMAC(signing_key, hashes.SHA256(), backend=default_backend())
    h.update(log_id)
    if sentence_text is not None:
        nfc_bytes = unicodedata.normalize("NFC", sentence_text).encode("utf-8")
        h.update(hashlib.sha256(nfc_bytes).digest()[:CONTENT_COMMITMENT_BYTES])
    hmac_truncated = h.finalize()[:16]  # 128-bit security

    # Encode: magic + log_id + HMAC
    payload = log_id + hmac_truncated  # 32 bytes
    encoded_payload = encode_bytes_vs256(payload)  # 32 VS chars

    return MAGIC_PREFIX + encoded_payload  # 36 VS chars


def verify_signed_marker(
    signature: str,
    signing_key: bytes,
    sentence_text: str | None = None,
) -> Tuple[bool, Optional[bytes]]:
    """
    Verify a VS256 signed marker (36 chars) and extract the log_id.

    Tries content-bound verification first; falls back to content-free
    verification for backward compatibility with markers created without
    sentence_text.

    Args:
        signature: 36-character VS256 signature string.
        signing_key: 32-byte secret key for HMAC verification.
        sentence_text: Optional sentence text used for content-bound signatures.

    Returns:
        (True, log_id_bytes) on success, (False, None) on any failure.
    """
    if len(signature) != SIGNATURE_CHARS:
        return False, None

    # Verify magic prefix
    if signature[:MAGIC_PREFIX_LEN] != MAGIC_PREFIX:
        return False, None

    try:
        # Decode the 32-char payload
        payload = decode_bytes_vs256(signature[MAGIC_PREFIX_LEN:])

        if len(payload) != PAYLOAD_BYTES:
            return False, None

        # Split into log_id and HMAC
        log_id = payload[:LOG_ID_BYTES]
        hmac_received = payload[LOG_ID_BYTES:]

        def _hmac(include_text: bool) -> bytes:
            h = crypto_hmac.HMAC(signing_key, hashes.SHA256(), backend=default_backend())
            h.update(log_id)
            if include_text and sentence_text is not None:
                nfc_bytes = unicodedata.normalize("NFC", sentence_text).encode("utf-8")
                h.update(hashlib.sha256(nfc_bytes).digest()[:CONTENT_COMMITMENT_BYTES])
            return h.finalize()[:16]

        if hmac_received == _hmac(include_text=True):
            return True, log_id
        if sentence_text is not None and hmac_received == _hmac(include_text=False):
            return True, log_id
        return False, None

    except Exception:
        return False, None


def find_all_markers(text: str) -> list[tuple[int, int, str]]:
    """
    Find all VS256 signed markers by detecting magic prefix + 32 VS payload.

    Detection strategy:
    1. Scan for the 4-char magic prefix (VS240, VS241, VS242, VS243)
    2. Verify the next 32 chars are all valid VS characters
    3. Return (start, end, signature_string) tuples

    Args:
        text: Text potentially containing VS256 signatures

    Returns:
        List of (start_pos, end_pos, signature_string) tuples
    """
    signatures = []
    i = 0
    text_len = len(text)

    while i <= text_len - SIGNATURE_CHARS:
        # Quick check: does first char match magic prefix start?
        if text[i] == MAGIC_PREFIX[0]:
            # Full magic prefix check
            if text[i : i + MAGIC_PREFIX_LEN] == MAGIC_PREFIX:
                # Verify remaining 32 chars are all VS
                candidate = text[i : i + SIGNATURE_CHARS]
                if len(candidate) == SIGNATURE_CHARS and all(
                    ch in VS_CHAR_SET for ch in candidate[MAGIC_PREFIX_LEN:]
                ):
                    signatures.append((i, i + SIGNATURE_CHARS, candidate))
                    i += SIGNATURE_CHARS
                    continue
        i += 1

    return signatures


def extract_marker(text: str) -> Optional[str]:
    """
    Extract first VS256 signed marker from text.

    Args:
        text: Text containing VS256 signatures

    Returns:
        The signature string (36 chars) or None
    """
    sigs = find_all_markers(text)
    return sigs[0][2] if sigs else None


def remove_markers(text: str) -> str:
    """
    Remove all VS256 signed markers from text.

    Args:
        text: Text with VS256 signatures

    Returns:
        Clean text with all signatures removed
    """
    sigs = find_all_markers(text)
    result = text
    for start, end, _sig in reversed(sigs):
        result = result[:start] + result[end:]
    return result


# =============================================================================
# KEY DERIVATION
# =============================================================================


def derive_signing_key_from_private_key(private_key: Ed25519PrivateKey) -> bytes:
    """
    Derive a 32-byte HMAC signing key from an Ed25519 private key.

    Uses the same derivation as zw_crypto.py to ensure key compatibility.
    The same org key works for both zw_embedding and vs256_embedding modes.

    Args:
        private_key: Ed25519 private key

    Returns:
        32-byte signing key for HMAC operations
    """
    private_bytes = private_key.private_bytes_raw()
    return hashlib.sha256(b"encypher-hmac-key:" + private_bytes).digest()


# =============================================================================
# SAFE EMBEDDING POSITION - Insert before terminal punctuation
# =============================================================================

# Terminal punctuation characters
TERMINAL_PUNCTUATION = ".!?"

# Extended punctuation (includes quotes that often follow terminal punctuation)
TRAILING_PUNCTUATION = ".!?\"')]}»\u201d"


def embed_signature_safely(text: str, signature: str) -> str:
    """
    Embed VS256 signature before terminal punctuation to reduce accidental deletion.

    In editors, users typically delete from the end. By placing the invisible
    signature BEFORE the final punctuation, accidental deletion is less likely.

    Examples:
        "Hello world." → "Hello world[SIG]."
        "What time is it?" → "What time is it[SIG]?"
        "Wow!" → "Wow[SIG]!"
        "No punctuation" → "No punctuation[SIG]"

    Args:
        text: Original text (sentence)
        signature: VS256 signature to embed

    Returns:
        Text with signature embedded before terminal punctuation
    """
    if not text:
        return signature

    # Find how many trailing punctuation characters there are
    trailing_count = 0
    for char in reversed(text):
        if char in TRAILING_PUNCTUATION:
            trailing_count += 1
        else:
            break

    if trailing_count > 0:
        # Insert signature before trailing punctuation
        insert_pos = len(text) - trailing_count
        return text[:insert_pos] + signature + text[insert_pos:]
    else:
        # No terminal punctuation, append at end
        return text + signature


def get_signature_position(text: str) -> int:
    """
    Get the recommended position for embedding a VS256 signature.

    Args:
        text: Text to analyze

    Returns:
        Index where signature should be inserted
    """
    if not text:
        return 0

    trailing_count = 0
    for char in reversed(text):
        if char in TRAILING_PUNCTUATION:
            trailing_count += 1
        else:
            break

    return len(text) - trailing_count


def create_embedded_sentence(
    sentence: str,
    log_id: bytes,
    signing_key: bytes,
) -> str:
    """
    Create a sentence with VS256 signed marker embedded safely.

    Combines create_signed_marker() with safe positioning.

    Args:
        sentence: Original sentence text
        log_id: 16-byte log identifier from generate_log_id()
        signing_key: HMAC signing key

    Returns:
        Sentence with 36-char VS256 signature embedded before terminal punctuation
    """
    signature = create_signed_marker(log_id, signing_key, sentence_text=sentence)
    return embed_signature_safely(sentence, signature)
