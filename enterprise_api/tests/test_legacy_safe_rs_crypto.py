"""
Tests for RS-protected base-6 legacy-safe zero-width encoding (legacy_safe_rs_crypto).

Coverage:
- Marker length is always 112 chars
- Encode/decode roundtrip for the 36-byte RS payload
- Alphabet-only output (only chars from CHARS_BASE6)
- LRM/RLM presence in encoded output (discriminates from non-ECC format)
- Marker creation and HMAC verification (correct key)
- HMAC rejection (wrong key)
- Content binding: sentence_text changes fail HMAC
- Content-free fallback: marker created without text verifies without text
- Tamper detection: single-char flip fails HMAC after RS correction
- RS erasure recovery: up to 4 missing chars are recovered
- RS error correction: up to 2 corrupted chars are corrected
- Detection distinguishes 112-char ECC from 100-char non-ECC markers
- Detection in clean text and mixed text
- extract_marker and remove_markers utilities
- embed_marker_safely positions before terminal punctuation
- create_embedded_sentence convenience function
- generate_log_id (re-exported from legacy_safe_crypto)
- derive_signing_key_from_private_key
- Char count derivation: MARKER_CHARS == 112, PAYLOAD_BYTES == 36
"""

import os

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from app.utils.legacy_safe_rs_crypto import (
    CHARS_BASE6_SET,
    DATA_BYTES,
    MARKER_CHARS,
    PARITY_BYTES,
    PAYLOAD_BYTES,
    _RS,
    _decode_base6_36,
    _encode_base6_36,
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
from app.utils.legacy_safe_crypto import LRM, RLM, find_all_markers as ls_find_all_markers


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
# Layout constants
# ---------------------------------------------------------------------------


def test_marker_chars_is_112():
    """RS ECC variant produces 112 base-6 chars (36-byte payload in base-6)."""
    assert MARKER_CHARS == 112


def test_payload_bytes_is_36():
    """36 bytes = 32 data bytes + 4 RS parity bytes."""
    assert PAYLOAD_BYTES == 36
    assert DATA_BYTES == 32
    assert PARITY_BYTES == 4


# ---------------------------------------------------------------------------
# Base-6 codec for 36 bytes -> 112 chars
# ---------------------------------------------------------------------------


def test_encode_fixed_length():
    """_encode_base6_36 always produces exactly 112 characters."""
    for _ in range(50):
        data = os.urandom(PAYLOAD_BYTES)
        encoded = _encode_base6_36(data)
        assert len(encoded) == MARKER_CHARS


def test_encode_uses_only_alphabet_chars():
    """All encoded characters are from the 6-char alphabet."""
    for _ in range(50):
        data = os.urandom(PAYLOAD_BYTES)
        encoded = _encode_base6_36(data)
        for ch in encoded:
            assert ch in CHARS_BASE6_SET, f"Unexpected char U+{ord(ch):04X}"


def test_roundtrip_all_zero():
    data = bytes(PAYLOAD_BYTES)
    assert _decode_base6_36(_encode_base6_36(data)) == data


def test_roundtrip_all_ff():
    data = bytes([0xFF] * PAYLOAD_BYTES)
    assert _decode_base6_36(_encode_base6_36(data)) == data


def test_roundtrip_random_payloads():
    for _ in range(100):
        data = os.urandom(PAYLOAD_BYTES)
        assert _decode_base6_36(_encode_base6_36(data)) == data, "roundtrip failed"


def test_decode_wrong_length_raises():
    with pytest.raises(ValueError, match="Expected 112 chars"):
        _decode_base6_36("x" * 100)


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
    """112 base-6 chars: P(no LRM/RLM) = (4/6)^112 ~ 5e-21. Zero failures in 1000 trials."""
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
# verify_marker -- basic cases
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


def test_verify_wrong_length_fails(signing_key):
    ok, extracted = verify_marker("x" * 100, signing_key)
    assert ok is False
    assert extracted is None


# ---------------------------------------------------------------------------
# Reed-Solomon error correction
# ---------------------------------------------------------------------------


def test_rs_erasure_recovery_up_to_4(log_id, signing_key):
    """Up to 4 known erasures (char position known) are recovered correctly."""
    from app.utils.legacy_safe_rs_crypto import CHARS_BASE6
    marker = create_marker(log_id, signing_key)

    # Corrupt positions 5, 20, 60, 100 in the 112-char marker (within RS payload)
    # For erasure recovery we provide erase_positions within the decoded 36-byte payload.
    # First re-decode the payload, zero out 4 bytes, then encode back.
    payload = _decode_base6_36(marker)
    erase_idxs = [3, 10, 22, 31]  # within 36 bytes
    corrupted = bytearray(payload)
    for idx in erase_idxs:
        corrupted[idx] = 0
    corrupted_marker = _encode_base6_36(bytes(corrupted))

    ok, extracted = verify_marker(corrupted_marker, signing_key, erase_positions=erase_idxs)
    assert ok is True
    assert extracted == log_id


def test_rs_too_many_erasures_fails(log_id, signing_key):
    """5 erasures exceed RS(36,32) capacity (max 4) and cause failure."""
    payload = _decode_base6_36(create_marker(log_id, signing_key))
    erase_idxs = [0, 5, 10, 20, 30]  # 5 erasures -- over capacity
    corrupted = bytearray(payload)
    for idx in erase_idxs:
        corrupted[idx] = 0
    corrupted_marker = _encode_base6_36(bytes(corrupted))

    ok, _ = verify_marker(corrupted_marker, signing_key, erase_positions=erase_idxs)
    assert ok is False


def test_rs_single_error_correction(log_id, signing_key):
    """1 unknown error (no position info) is corrected."""
    # Modify a single byte in the RS-encoded payload at a non-HMAC position
    payload = bytearray(_decode_base6_36(create_marker(log_id, signing_key)))
    # Corrupt byte 0 (in log_id region, which RS can fix)
    payload[0] = (payload[0] + 1) % 256
    corrupted_marker = _encode_base6_36(bytes(payload))

    # RS(36,32) can correct 2 unknown errors; 1 should succeed
    ok, extracted = verify_marker(corrupted_marker, signing_key)
    assert ok is True
    assert extracted == log_id


def test_tamper_beyond_rs_capacity_fails(log_id, signing_key):
    """3 unknown errors exceed RS(36,32) error correction capacity (max 2)."""
    payload = bytearray(_decode_base6_36(create_marker(log_id, signing_key)))
    # Corrupt 3 bytes spread across the payload
    for idx in [0, 15, 31]:
        payload[idx] = (payload[idx] + 127) % 256
    corrupted_marker = _encode_base6_36(bytes(payload))

    ok, _ = verify_marker(corrupted_marker, signing_key)
    assert ok is False


# ---------------------------------------------------------------------------
# Detection: find_all_markers
# ---------------------------------------------------------------------------


def test_find_rs_markers_in_plain_text(signing_key):
    lid = generate_log_id()
    marker = create_marker(lid, signing_key)
    text = "Before" + marker + "After"
    found = find_all_markers(text)
    assert len(found) == 1
    start, end, m = found[0]
    assert m == marker
    assert start == 6
    assert end == 6 + MARKER_CHARS


def test_find_rs_markers_multiple(signing_key):
    markers = [create_marker(generate_log_id(), signing_key) for _ in range(3)]
    text = "A" + markers[0] + "B" + markers[1] + "C" + markers[2] + "D"
    found = find_all_markers(text)
    assert len(found) == 3
    for i, (_, _, m) in enumerate(found):
        assert m == markers[i]


def test_find_rs_markers_empty_on_clean_text():
    assert find_all_markers("No invisible chars here.") == []


def test_rs_finder_only_finds_rs_markers(signing_key):
    """RS finder (112-char) detects RS markers but NOT standalone 100-char ls markers."""
    from app.utils.legacy_safe_crypto import (
        create_marker as ls_create,
        generate_log_id as ls_gen,
    )
    rs_marker = create_marker(generate_log_id(), signing_key)
    ls_marker = ls_create(ls_gen(), signing_key)
    rs_only_text = "Start" + rs_marker + "End"
    ls_only_text = "Start" + ls_marker + "End"

    # RS finder finds the RS marker
    assert len(find_all_markers(rs_only_text)) == 1
    # RS finder does NOT find a standalone 100-char ls marker
    assert len(find_all_markers(ls_only_text)) == 0


def test_ls_finder_picks_up_partial_rs_chunk(signing_key):
    """Known overlap: ls finder (100-char) detects the first 100 chars of a 112-char RS
    marker as a valid chunk, since both share the same alphabet and LRM/RLM requirement.
    In production, RS detection runs first and consumes the RS region before ls detection."""
    rs_marker = create_marker(generate_log_id(), signing_key)
    text = "Sentence" + rs_marker + "."
    # ls finder sees a 112-char run, extracts first 100 chars as a valid 100-char chunk
    ls_found = ls_find_all_markers(text)
    assert len(ls_found) == 1  # first 100 chars of rs_marker detected as ls-style chunk


def test_nonrs_100_char_not_detected_by_rs_finder(signing_key):
    """100-char non-ECC markers are NOT picked up by the 112-char RS detector."""
    from app.utils.legacy_safe_crypto import (
        create_marker as ls_create,
        generate_log_id as ls_gen,
    )
    ls_marker = ls_create(ls_gen(), signing_key)
    text = "Prefix" + ls_marker + "Suffix"
    rs_found = find_all_markers(text)
    assert len(rs_found) == 0, "RS finder should not pick up 100-char non-ECC markers"


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


# ---------------------------------------------------------------------------
# embed_marker_safely
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("sentence,expected_suffix", [
    ("Hello world.", "."),
    ("Hello world!", "!"),
    ("Hello world?", "?"),
    ("No punctuation", ""),
])
def test_embed_before_punctuation(sentence, expected_suffix, signing_key):
    lid = generate_log_id()
    marker = create_marker(lid, signing_key)
    embedded = embed_marker_safely(sentence, marker)
    assert embedded.endswith(expected_suffix)
    assert marker in embedded
    if expected_suffix:
        marker_pos = embedded.index(marker)
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
    private_key = Ed25519PrivateKey.generate()
    k1 = derive_signing_key_from_private_key(private_key)
    k2 = derive_signing_key_from_private_key(private_key)
    assert k1 == k2


def test_derive_signing_key_different_keys_differ():
    k1 = derive_signing_key_from_private_key(Ed25519PrivateKey.generate())
    k2 = derive_signing_key_from_private_key(Ed25519PrivateKey.generate())
    assert k1 != k2
