"""
Tests for base-6 legacy-safe zero-width encoding (legacy_safe_crypto module).

Coverage:
- Encode/decode roundtrip for all 256 byte values
- Fixed-length output (always 100 chars)
- Alphabet-only output (only chars from CHARS_BASE6)
- LRM/RLM presence in encoded output
- Marker creation and HMAC verification (correct key)
- HMAC rejection (wrong key)
- Content binding: sentence_text changes fail HMAC
- Content-free fallback: marker created without text verifies without text
- Backward-compatible fallback: content-bound verify falls back to content-free
- Detection in clean text
- Detection in mixed-format text (base-4 markers not flagged as legacy_safe)
- No false positives from pure-base-4 runs (no LRM/RLM)
- extract_marker and remove_markers utilities
- Safe embedding before terminal punctuation
- create_embedded_sentence convenience function
- generate_log_id length and randomness
- derive_signing_key_from_private_key compatibility
"""

import os

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from app.utils.legacy_safe_crypto import (
    CGJ,
    CHARS_BASE6,
    CHARS_BASE6_SET,
    LRM,
    MARKER_CHARS,
    MVS,
    PAYLOAD_BYTES,
    RLM,
    ZWJ,
    ZWNJ,
    _decode_base6,
    _encode_base6,
    create_embedded_sentence,
    create_marker,
    derive_signing_key_from_private_key,
    embed_marker_safely,
    extract_marker,
    find_all_markers,
    generate_log_id,
    remove_markers,
    verify_marker,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def signing_key() -> bytes:
    """32-byte HMAC signing key derived from a fresh Ed25519 key."""
    private_key = Ed25519PrivateKey.generate()
    return derive_signing_key_from_private_key(private_key)


@pytest.fixture
def log_id() -> bytes:
    return generate_log_id()


# ---------------------------------------------------------------------------
# Alphabet constants
# ---------------------------------------------------------------------------


def test_alphabet_length():
    assert len(CHARS_BASE6) == 6


def test_alphabet_contains_lrm_rlm():
    assert LRM in CHARS_BASE6
    assert RLM in CHARS_BASE6


def test_alphabet_contains_original_four():
    for ch in (ZWNJ, ZWJ, CGJ, MVS):
        assert ch in CHARS_BASE6


def test_chars_base6_set_matches_list():
    assert CHARS_BASE6_SET == frozenset(CHARS_BASE6)


# ---------------------------------------------------------------------------
# Big-number base-6 codec
# ---------------------------------------------------------------------------


def test_encode_fixed_length():
    """_encode_base6 always produces exactly MARKER_CHARS characters."""
    for value in [0, 1, 255, 2**64, 2**128, 2**256 - 1]:
        data = value.to_bytes(PAYLOAD_BYTES, "big")
        encoded = _encode_base6(data)
        assert len(encoded) == MARKER_CHARS, f"Expected {MARKER_CHARS}, got {len(encoded)}"


def test_encode_uses_only_alphabet_chars():
    """All encoded characters are from the 6-char alphabet."""
    for _ in range(100):
        data = os.urandom(PAYLOAD_BYTES)
        encoded = _encode_base6(data)
        for ch in encoded:
            assert ch in CHARS_BASE6_SET, f"Unexpected char U+{ord(ch):04X}"


def test_roundtrip_all_zero():
    data = bytes(PAYLOAD_BYTES)
    assert _decode_base6(_encode_base6(data)) == data


def test_roundtrip_all_ff():
    data = bytes([0xFF] * PAYLOAD_BYTES)
    assert _decode_base6(_encode_base6(data)) == data


def test_roundtrip_random_payloads():
    for _ in range(200):
        data = os.urandom(PAYLOAD_BYTES)
        assert _decode_base6(_encode_base6(data)) == data, "roundtrip failed"


def test_decode_invalid_char_raises():
    marker = _encode_base6(os.urandom(PAYLOAD_BYTES))
    # Replace one char with a non-alphabet character
    bad = list(marker)
    bad[0] = "A"
    with pytest.raises(ValueError, match="Invalid base-6 char"):
        _decode_base6("".join(bad))


# ---------------------------------------------------------------------------
# generate_log_id
# ---------------------------------------------------------------------------


def test_log_id_length():
    assert len(generate_log_id()) == 16


def test_log_id_randomness():
    ids = {generate_log_id() for _ in range(20)}
    assert len(ids) == 20, "Expected all unique log IDs"


# ---------------------------------------------------------------------------
# create_marker
# ---------------------------------------------------------------------------


def test_marker_length(log_id, signing_key):
    marker = create_marker(log_id, signing_key)
    assert len(marker) == MARKER_CHARS


def test_marker_contains_only_alphabet(log_id, signing_key):
    marker = create_marker(log_id, signing_key)
    for ch in marker:
        assert ch in CHARS_BASE6_SET


def test_marker_almost_always_contains_lrm_rlm(signing_key):
    """With 100 base-6 digits, probability of no 4/5 digit is (4/6)^100 ~ 2e-18.
    In 1000 trials we expect zero failures."""
    lrm_rlm = frozenset({LRM, RLM})
    for _ in range(1000):
        lid = generate_log_id()
        marker = create_marker(lid, signing_key)
        assert lrm_rlm & set(marker), "Marker contained no LRM or RLM (extremely unlikely)"


def test_marker_wrong_log_id_length(signing_key):
    with pytest.raises(ValueError, match="log_id must be"):
        create_marker(b"\x00" * 15, signing_key)


def test_marker_short_signing_key(log_id):
    with pytest.raises(ValueError, match="signing_key must be at least 32 bytes"):
        create_marker(log_id, b"\x00" * 16)


# ---------------------------------------------------------------------------
# verify_marker
# ---------------------------------------------------------------------------


def test_verify_correct_key_no_text(log_id, signing_key):
    marker = create_marker(log_id, signing_key)
    ok, extracted = verify_marker(marker, signing_key)
    assert ok is True
    assert extracted == log_id


def test_verify_correct_key_with_text(log_id, signing_key):
    sentence = "Hello, world."
    marker = create_marker(log_id, signing_key, sentence_text=sentence)
    ok, extracted = verify_marker(marker, signing_key, sentence_text=sentence)
    assert ok is True
    assert extracted == log_id


def test_verify_wrong_key_fails(log_id, signing_key):
    marker = create_marker(log_id, signing_key)
    wrong_key = os.urandom(32)
    ok, extracted = verify_marker(marker, wrong_key)
    assert ok is False
    assert extracted is None


def test_verify_wrong_text_fails(log_id, signing_key):
    """Marker bound to one sentence should fail if text is different."""
    marker = create_marker(log_id, signing_key, sentence_text="Original sentence.")
    ok, _ = verify_marker(marker, signing_key, sentence_text="Modified sentence.")
    assert ok is False


def test_verify_content_free_fallback(log_id, signing_key):
    """Marker created WITHOUT text should verify even when text supplied."""
    marker = create_marker(log_id, signing_key, sentence_text=None)
    ok, extracted = verify_marker(marker, signing_key, sentence_text="Any text at all")
    assert ok is True
    assert extracted == log_id


def test_verify_tampered_marker(log_id, signing_key):
    marker = create_marker(log_id, signing_key)
    # Flip the first char to a different alphabet char
    chars = list(marker)
    current = chars[0]
    chars[0] = next(c for c in CHARS_BASE6 if c != current)
    tampered = "".join(chars)
    ok, _ = verify_marker(tampered, signing_key)
    assert ok is False


def test_verify_wrong_length_fails(signing_key):
    ok, extracted = verify_marker("x" * 99, signing_key)
    assert ok is False
    assert extracted is None


# ---------------------------------------------------------------------------
# Detection: find_all_markers
# ---------------------------------------------------------------------------


def test_find_markers_in_plain_text(signing_key):
    lid = generate_log_id()
    marker = create_marker(lid, signing_key)
    text = "Before" + marker + "After"
    found = find_all_markers(text)
    assert len(found) == 1
    start, end, m = found[0]
    assert m == marker
    assert start == 6
    assert end == 6 + MARKER_CHARS


def test_find_markers_multiple(signing_key):
    markers = [create_marker(generate_log_id(), signing_key) for _ in range(3)]
    text = "A" + markers[0] + "B" + markers[1] + "C" + markers[2] + "D"
    found = find_all_markers(text)
    assert len(found) == 3
    for i, (_, _, m) in enumerate(found):
        assert m == markers[i]


def test_find_markers_returns_empty_on_clean_text():
    assert find_all_markers("No invisible chars here.") == []


def test_no_false_positives_from_base4_markers():
    """A run of 100 pure base-4 chars (ZWNJ/ZWJ/CGJ/MVS, no LRM/RLM) must NOT
    be detected as a legacy_safe marker (no LRM/RLM present)."""
    base4_chars = [ZWNJ, ZWJ, CGJ, MVS]
    pure_base4_run = "".join(base4_chars[i % 4] for i in range(100))
    # Verify it has no LRM or RLM
    assert LRM not in pure_base4_run
    assert RLM not in pure_base4_run
    # Detection must return empty
    assert find_all_markers(pure_base4_run) == []


def test_base4_char_sequence_not_detected(signing_key):
    """A 128-char sequence of only base-4 chars (ZWNJ/ZWJ/CGJ/MVS, no LRM/RLM) is not detected by legacy_safe."""
    base4_chars = [ZWNJ, ZWJ, CGJ, MVS]
    synthetic_base4 = "".join(base4_chars[i % 4] for i in range(128))
    assert find_all_markers(synthetic_base4) == []


# ---------------------------------------------------------------------------
# extract_marker and remove_markers
# ---------------------------------------------------------------------------


def test_extract_marker_returns_first(signing_key):
    lid = generate_log_id()
    marker = create_marker(lid, signing_key)
    text = "Start" + marker + "End"
    assert extract_marker(text) == marker


def test_extract_marker_none_on_clean_text():
    assert extract_marker("No markers here.") is None


def test_remove_markers(signing_key):
    lid = generate_log_id()
    marker = create_marker(lid, signing_key)
    text = "Hello" + marker + " world" + marker + "."
    clean = remove_markers(text)
    assert clean == "Hello world."
    assert find_all_markers(clean) == []


def test_remove_markers_clean_text_unchanged():
    text = "No invisible chars."
    assert remove_markers(text) == text


# ---------------------------------------------------------------------------
# embed_marker_safely
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "sentence,expected_suffix",
    [
        ("Hello world.", "."),
        ("Hello world!", "!"),
        ("Hello world?", "?"),
        ('She said "Hi."', '"'),
        ("No punctuation", ""),
    ],
)
def test_embed_before_punctuation(sentence, expected_suffix, signing_key):
    lid = generate_log_id()
    marker = create_marker(lid, signing_key)
    embedded = embed_marker_safely(sentence, marker)
    assert embedded.endswith(expected_suffix)
    assert marker in embedded
    # Marker should appear before trailing punctuation, not after
    marker_pos = embedded.index(marker)
    if expected_suffix:
        punct_pos = embedded.rindex(expected_suffix)
        assert marker_pos < punct_pos


def test_embed_empty_text(signing_key):
    lid = generate_log_id()
    marker = create_marker(lid, signing_key)
    result = embed_marker_safely("", marker)
    assert result == marker


# ---------------------------------------------------------------------------
# create_embedded_sentence
# ---------------------------------------------------------------------------


def test_create_embedded_sentence_roundtrip(signing_key):
    sentence = "The quick brown fox jumps over the lazy dog."
    lid = generate_log_id()
    embedded = create_embedded_sentence(sentence, lid, signing_key)
    found = find_all_markers(embedded)
    assert len(found) == 1
    _, _, marker = found[0]
    ok, extracted_id = verify_marker(marker, signing_key, sentence_text=sentence)
    assert ok is True
    assert extracted_id == lid


# ---------------------------------------------------------------------------
# derive_signing_key_from_private_key
# ---------------------------------------------------------------------------


def test_derive_signing_key_length():
    private_key = Ed25519PrivateKey.generate()
    key = derive_signing_key_from_private_key(private_key)
    assert len(key) == 32


def test_derive_signing_key_deterministic():
    """Same private key always produces same signing key."""
    private_key = Ed25519PrivateKey.generate()
    k1 = derive_signing_key_from_private_key(private_key)
    k2 = derive_signing_key_from_private_key(private_key)
    assert k1 == k2


def test_derive_signing_key_different_keys_differ():
    k1 = derive_signing_key_from_private_key(Ed25519PrivateKey.generate())
    k2 = derive_signing_key_from_private_key(Ed25519PrivateKey.generate())
    assert k1 != k2


# ---------------------------------------------------------------------------
# Size guarantee
# ---------------------------------------------------------------------------


def test_marker_chars_is_100():
    """Document the exact marker length for regression detection (hyperscale-safe: 32-byte payload)."""
    assert MARKER_CHARS == 100


def test_payload_bytes_is_32():
    """32 bytes = 16-byte log_id + 16-byte HMAC-SHA256/128 (hyperscale-safe)."""
    assert PAYLOAD_BYTES == 32
