"""Print-Survivable Micro ECC Embedding.

Encodes a full VS256-RS-compatible provenance payload (32 bytes = log_id + HMAC)
into inter-word spacing using 4 Unicode space variants, protected by
Reed-Solomon RS(48,32) error correction.

4-symbol alphabet (ordered by ascending physical width):
  0 = U+200A  HAIR SPACE       (~0.1 em)
  1 = U+2006  SIX-PER-EM SPACE (~0.167 em)
  2 = U+2009  THIN SPACE        (~0.2 em)
  3 = U+0020  REGULAR SPACE     (~0.25 em)

Layout (192 inter-word positions):
  [log_id: 16 B] [HMAC-128: 16 B] [RS parity: 16 B] = 48 bytes
  48 bytes x 4 symbols/byte = 192 base-4 symbols = 192 inter-word positions

Each position carries 2 bits (one base-4 symbol).  Positions are interleaved
across the full document for burst-error resilience.

Error correction capacity:
  RS(48,32) over GF(256) with 16 parity symbols:
  - Corrects up to 8 unknown byte errors (vs 4 for RS(40,32))
  - Corrects up to 16 known-position erasures (vs 8)
  - Minimum gap between symbols is 0.033 em (thin - six-per-em), so the
    extra parity provides comfortable margin for print/scan noise.

Survives: high-quality print/scan (300-600 DPI), PDF copy-paste, ZWC stripping
Lost when: aggressive whitespace normalisation, low-quality OCR, plain-text email

Target use cases: government documents, invoices, bank statements, legal filings.
"""

import hashlib
import logging
import unicodedata
from typing import Optional, Tuple

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import hmac as crypto_hmac
from reedsolo import RSCodec, ReedSolomonError

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# 4-symbol alphabet (ordered by ascending physical width)
# ---------------------------------------------------------------------------

HAIR_SPACE = "\u200a"  # symbol 0 (~0.1 em)
SIX_PER_EM_SPACE = "\u2006"  # symbol 1 (~0.167 em)
THIN_SPACE = "\u2009"  # symbol 2 (~0.2 em)
REGULAR_SPACE = "\u0020"  # symbol 3 (~0.25 em)

SYMBOL_CHARS: list[str] = [HAIR_SPACE, SIX_PER_EM_SPACE, THIN_SPACE, REGULAR_SPACE]
CHAR_TO_SYMBOL: dict[str, int] = {c: i for i, c in enumerate(SYMBOL_CHARS)}
SPACE_CHAR_SET: frozenset[str] = frozenset(SYMBOL_CHARS)

# Physical widths in em units (nominal, font-dependent)
SYMBOL_WIDTHS_EM: list[float] = [0.10, 0.167, 0.20, 0.25]

# ---------------------------------------------------------------------------
# Payload layout
# ---------------------------------------------------------------------------

LOG_ID_BYTES = 16  # 128-bit random log reference
HMAC_BYTES = 16  # HMAC-SHA256/128
DATA_BYTES = LOG_ID_BYTES + HMAC_BYTES  # 32
CONTENT_COMMITMENT_BYTES = 8  # bytes of SHA256(NFC(sentence)) in HMAC input

# Reed-Solomon: RS(48, 32) over GF(256) - doubled parity vs vs256_rs_crypto
# for print-channel robustness (tightest symbol gap is only 0.033 em).
_RS_NSYM = 16
_RS = RSCodec(_RS_NSYM)
PARITY_BYTES = _RS_NSYM  # 16
PAYLOAD_BYTES = DATA_BYTES + PARITY_BYTES  # 48

# 48 bytes x 4 symbols/byte (2 bits per symbol) = 192 positions
SYMBOLS_PER_BYTE = 4
MIN_POSITIONS = PAYLOAD_BYTES * SYMBOLS_PER_BYTE  # 192


# ---------------------------------------------------------------------------
# Interleaved position selection
# ---------------------------------------------------------------------------


def _select_positions(total_spaces: int, needed: int) -> list[int]:
    """Select *needed* positions from *total_spaces* with maximum spacing.

    Uses evenly-spaced interleaving: idx[i] = floor(i * total / needed).
    This distributes encoded symbols across the full document, so a
    localised OCR failure (burst error) affects non-adjacent RS symbols.
    """
    if total_spaces < needed:
        return []
    return [i * total_spaces // needed for i in range(needed)]


# ---------------------------------------------------------------------------
# Base-4 encoding (2 bits per position, MSB-first)
# ---------------------------------------------------------------------------


def _bytes_to_symbols(data: bytes) -> list[int]:
    """Convert bytes to a list of base-4 symbols (2 bits each, MSB-first).

    Each byte produces 4 symbols: bits 7-6, 5-4, 3-2, 1-0.
    """
    symbols: list[int] = []
    for byte_val in data:
        symbols.append((byte_val >> 6) & 0x03)
        symbols.append((byte_val >> 4) & 0x03)
        symbols.append((byte_val >> 2) & 0x03)
        symbols.append(byte_val & 0x03)
    return symbols


def _symbols_to_bytes(symbols: list[int]) -> bytes:
    """Convert base-4 symbols back to bytes (4 symbols per byte, MSB-first)."""
    if len(symbols) % SYMBOLS_PER_BYTE != 0:
        raise ValueError(f"Symbol count {len(symbols)} is not a multiple of {SYMBOLS_PER_BYTE}")
    result = bytearray()
    for i in range(0, len(symbols), SYMBOLS_PER_BYTE):
        byte_val = (symbols[i] << 6) | (symbols[i + 1] << 4) | (symbols[i + 2] << 2) | symbols[i + 3]
        result.append(byte_val)
    return bytes(result)


# ---------------------------------------------------------------------------
# HMAC construction (matches vs256_rs_crypto format)
# ---------------------------------------------------------------------------


def build_payload(
    log_id: bytes,
    signing_key: bytes,
    sentence_text: str | None = None,
) -> bytes:
    """Build the 40-byte RS-encoded payload: log_id(16) + HMAC(16) + RS(8).

    The HMAC construction matches vs256_rs_crypto.create_signed_marker exactly,
    so both the digital and print channels produce identical log_id + HMAC pairs
    and can be cross-verified against the same transparency log entry.

    Args:
        log_id: 16-byte identifier from the transparency log.
        signing_key: 32-byte HMAC key derived from the org Ed25519 private key.
        sentence_text: Optional sentence for content-bound HMAC.

    Returns:
        40 bytes: 32 data + 8 RS parity.
    """
    if len(log_id) != LOG_ID_BYTES:
        raise ValueError(f"log_id must be {LOG_ID_BYTES} bytes, got {len(log_id)}")
    if len(signing_key) < 32:
        raise ValueError("signing_key must be at least 32 bytes")

    h = crypto_hmac.HMAC(signing_key, hashes.SHA256(), backend=default_backend())
    h.update(log_id)
    if sentence_text is not None:
        nfc_bytes = unicodedata.normalize("NFC", sentence_text).encode("utf-8")
        h.update(hashlib.sha256(nfc_bytes).digest()[:CONTENT_COMMITMENT_BYTES])
    hmac_truncated = h.finalize()[:HMAC_BYTES]

    data = log_id + hmac_truncated  # 32 bytes
    rs_encoded = bytes(_RS.encode(data))  # 40 bytes
    return rs_encoded


def build_document_payload(org_id: str, document_id: str) -> bytes:
    """Build a 40-byte RS-encoded document-level payload for print embedding.

    This is the document-level variant (no per-sentence signing key).
    Uses HMAC(org_id, document_id) as a deterministic 16-byte log_id,
    then RS-encodes the 32-byte data block.

    For full provenance chain, prefer build_payload() with a real log_id
    from the transparency log.
    """
    # Deterministic log_id from org + doc (same as print_stego.build_payload)
    key = org_id.encode("utf-8")
    msg = document_id.encode("utf-8")
    hmac_full = hashlib.new("sha256", key + msg).digest()
    log_id = hmac_full[:LOG_ID_BYTES]
    hmac_val = hmac_full[LOG_ID_BYTES : LOG_ID_BYTES + HMAC_BYTES]

    data = log_id + hmac_val  # 32 bytes
    rs_encoded = bytes(_RS.encode(data))  # 40 bytes
    return rs_encoded


# ---------------------------------------------------------------------------
# Encoder
# ---------------------------------------------------------------------------


def encode_print_micro_ecc(text: str, payload: bytes) -> str:
    """Encode a 40-byte RS-protected payload into inter-word spacing.

    Replaces selected inter-word space characters with one of 4 Unicode
    space variants, each carrying 2 bits. Positions are interleaved across
    the full document for burst-error resilience.

    Args:
        text: Input text with regular spaces between words.
        payload: 40-byte RS-encoded payload from build_payload().

    Returns:
        Text with encoded inter-word spacing, or the original text unmodified
        if the document has fewer than 160 inter-word spaces (graceful no-op).
    """
    if len(payload) != PAYLOAD_BYTES:
        raise ValueError(f"Payload must be {PAYLOAD_BYTES} bytes, got {len(payload)}")

    chars = list(text)
    space_positions = [i for i, c in enumerate(chars) if c == REGULAR_SPACE]

    if len(space_positions) < MIN_POSITIONS:
        logger.warning(
            "print_micro_ecc: %d spaces available, %d required - returning text unmodified",
            len(space_positions),
            MIN_POSITIONS,
        )
        return text

    # Interleaved position selection
    selected = _select_positions(len(space_positions), MIN_POSITIONS)
    encode_indices = [space_positions[s] for s in selected]

    # Convert payload to base-4 symbols
    symbols = _bytes_to_symbols(payload)

    # Replace spaces with symbol characters
    for pos_idx, char_idx in enumerate(encode_indices):
        chars[char_idx] = SYMBOL_CHARS[symbols[pos_idx]]

    return "".join(chars)


# ---------------------------------------------------------------------------
# Decoder
# ---------------------------------------------------------------------------


def decode_print_micro_ecc(text: str) -> Optional[bytes]:
    """Decode a print micro ECC payload from inter-word spacing.

    Reads the 4-symbol space characters at interleaved positions,
    converts to bytes, and applies RS error correction.

    Args:
        text: Text that may contain an encoded print micro ECC payload.

    Returns:
        32-byte data payload (log_id + HMAC) on success, or None if:
        - The text has fewer than 160 space-like characters
        - No non-regular spaces are detected (no encoding present)
        - RS error correction fails (too many errors)
    """
    # Collect all space positions and their symbols
    space_entries: list[tuple[int, str]] = []
    for i, c in enumerate(text):
        if c in SPACE_CHAR_SET:
            space_entries.append((i, c))

    if len(space_entries) < MIN_POSITIONS:
        return None

    # Select the same interleaved positions the encoder used
    selected = _select_positions(len(space_entries), MIN_POSITIONS)

    # Check for presence of non-regular spaces in selected positions
    has_encoding = False
    symbols: list[int] = []
    for s in selected:
        _pos, ch = space_entries[s]
        sym = CHAR_TO_SYMBOL.get(ch)
        if sym is None:
            symbols.append(3)  # treat unknown as regular space
        else:
            symbols.append(sym)
            if sym != 3:  # not regular space
                has_encoding = True

    if not has_encoding:
        return None  # no encoding detected

    # Convert symbols to bytes
    try:
        raw_bytes = _symbols_to_bytes(symbols)
    except ValueError:
        return None

    if len(raw_bytes) != PAYLOAD_BYTES:
        return None

    # RS decode: correct errors and extract 32-byte data
    try:
        decoded = bytes(_RS.decode(raw_bytes)[0])
        if len(decoded) != DATA_BYTES:
            return None
        return decoded
    except ReedSolomonError:
        return None


def decode_with_erasures(
    text: str,
    erasure_indices: list[int] | None = None,
) -> Optional[bytes]:
    """Decode with known-position erasures for enhanced RS recovery.

    When the caller knows which space positions are uncertain (e.g., OCR
    confidence scores), passing them as erasures doubles RS correction
    capacity for those positions (up to 8 erasures vs 4 unknown errors).

    Args:
        text: Text that may contain an encoded print micro ECC payload.
        erasure_indices: 0-indexed positions within the 160-symbol sequence
            that are known to be unreliable.

    Returns:
        32-byte data payload on success, or None on failure.
    """
    space_entries: list[tuple[int, str]] = []
    for i, c in enumerate(text):
        if c in SPACE_CHAR_SET:
            space_entries.append((i, c))

    if len(space_entries) < MIN_POSITIONS:
        return None

    selected = _select_positions(len(space_entries), MIN_POSITIONS)

    symbols: list[int] = []
    for s in selected:
        _pos, ch = space_entries[s]
        sym = CHAR_TO_SYMBOL.get(ch, 3)
        symbols.append(sym)

    try:
        raw_bytes = _symbols_to_bytes(symbols)
    except ValueError:
        return None

    if len(raw_bytes) != PAYLOAD_BYTES:
        return None

    # Map symbol-level erasure indices to byte-level erasure positions
    byte_erasures: list[int] | None = None
    if erasure_indices:
        byte_set: set[int] = set()
        for sym_idx in erasure_indices:
            byte_set.add(sym_idx // SYMBOLS_PER_BYTE)
        byte_erasures = sorted(byte_set)
        if len(byte_erasures) > _RS_NSYM:
            return None  # too many erasures for RS to handle

    try:
        decoded = bytes(_RS.decode(raw_bytes, erase_pos=byte_erasures)[0])
        if len(decoded) != DATA_BYTES:
            return None
        return decoded
    except ReedSolomonError:
        return None


# ---------------------------------------------------------------------------
# Verification helpers
# ---------------------------------------------------------------------------


def extract_log_id(decoded_payload: bytes) -> bytes:
    """Extract the 16-byte log_id from a decoded 32-byte payload."""
    return decoded_payload[:LOG_ID_BYTES]


def extract_hmac(decoded_payload: bytes) -> bytes:
    """Extract the 16-byte HMAC from a decoded 32-byte payload."""
    return decoded_payload[LOG_ID_BYTES : LOG_ID_BYTES + HMAC_BYTES]


def verify_hmac(
    decoded_payload: bytes,
    signing_key: bytes,
    sentence_text: str | None = None,
) -> bool:
    """Verify the HMAC in a decoded payload against a signing key.

    Tries content-bound verification first, then content-free fallback.
    """
    log_id = extract_log_id(decoded_payload)
    hmac_received = extract_hmac(decoded_payload)

    def _compute_hmac(include_text: bool) -> bytes:
        h = crypto_hmac.HMAC(signing_key, hashes.SHA256(), backend=default_backend())
        h.update(log_id)
        if include_text and sentence_text is not None:
            nfc_bytes = unicodedata.normalize("NFC", sentence_text).encode("utf-8")
            h.update(hashlib.sha256(nfc_bytes).digest()[:CONTENT_COMMITMENT_BYTES])
        return h.finalize()[:HMAC_BYTES]

    if hmac_received == _compute_hmac(include_text=True):
        return True
    if sentence_text is not None and hmac_received == _compute_hmac(include_text=False):
        return True
    return False
