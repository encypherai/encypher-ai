"""Print Leak Detection - thin-space steganography.

Encodes a compact payload (16 bytes = 128 bits) at inter-word positions using:
  U+0020 REGULAR SPACE = 0-bit
  U+2009 THIN SPACE    = 1-bit

Thin spaces (~5/18 em) are visually identical to regular spaces but produce
measurably different physical letter-spacing in high-quality print. This
fingerprint channel:

  Survives  - PDF copy-paste, high-quality OCR, ZWC stripping (orthogonal channel)
  Lost when - aggressive whitespace normalisation, low-quality OCR, plain-text email

Capacity: 16 bytes x 8 bits = 128 bits -> requires >= 128 inter-word spaces.
A 300-word article has ~299 spaces - sufficient for most content.
"""

import hashlib
import hmac
import logging
from typing import Optional

logger = logging.getLogger(__name__)

REGULAR_SPACE = "\u0020"
THIN_SPACE = "\u2009"  # THIN SPACE - ~5/18 em, Unicode General_Category=Zs

PAYLOAD_BYTES = 16        # 128-bit fingerprint
MIN_SPACES = PAYLOAD_BYTES * 8  # 128 inter-word positions required


def build_payload(org_id: str, document_id: str) -> bytes:
    """Return a 16-byte HMAC-SHA256 fingerprint for an org + document pair.

    Deterministic: same (org_id, document_id) always produces the same payload.
    The payload can be reconstructed by the publisher to confirm which document
    a leaked physical copy came from.
    """
    key = org_id.encode("utf-8")
    msg = document_id.encode("utf-8")
    return hmac.new(key, msg, hashlib.sha256).digest()[:PAYLOAD_BYTES]


def encode_print_fingerprint(text: str, payload: bytes) -> str:
    """Encode *payload* bits into the inter-word spaces of *text*.

    Replaces a REGULAR_SPACE with THIN_SPACE to represent a 1-bit; leaves
    REGULAR_SPACE unchanged for a 0-bit. Uses the first ``len(payload) * 8``
    space positions in the text (left-to-right).

    If the text contains fewer inter-word spaces than required, the text is
    returned **unmodified** and a warning is logged (graceful no-op - no error).
    """
    chars = list(text)
    space_positions = [i for i, c in enumerate(chars) if c == REGULAR_SPACE]

    required = len(payload) * 8
    if len(space_positions) < required:
        logger.warning(
            "print_stego: %d spaces available, %d required for %d-byte payload"
            " - returning text unmodified",
            len(space_positions),
            required,
            len(payload),
        )
        return text

    bit_idx = 0
    for byte_val in payload:
        for bit_pos in range(7, -1, -1):
            if (byte_val >> bit_pos) & 1:
                chars[space_positions[bit_idx]] = THIN_SPACE
            bit_idx += 1

    return "".join(chars)


def decode_print_fingerprint(text: str) -> Optional[bytes]:
    """Scan *text* for a thin-space fingerprint.

    Returns a 16-byte payload if a fingerprint is detected, or ``None`` if:
    - The text contains fewer than 128 space-like characters, or
    - No thin spaces appear in the first 128 space positions (no fingerprint).

    False positives are negligible in practice because U+2009 is rarely used
    in normal prose.
    """
    space_chars = [c for c in text if c in (REGULAR_SPACE, THIN_SPACE)]

    if len(space_chars) < MIN_SPACES:
        return None

    candidate = space_chars[:MIN_SPACES]
    if THIN_SPACE not in candidate:
        return None  # no fingerprint - all spaces are regular

    result = bytearray()
    for byte_idx in range(PAYLOAD_BYTES):
        byte_val = 0
        for bit_pos in range(7, -1, -1):
            idx = byte_idx * 8 + (7 - bit_pos)
            if candidate[idx] == THIN_SPACE:
                byte_val |= 1 << bit_pos
        result.append(byte_val)

    return bytes(result)
