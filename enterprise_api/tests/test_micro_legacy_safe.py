"""
Unit and integration tests for legacy_safe marker encoding (base-6 ZWC).

Covers both legacy_safe_crypto (100-char, no ECC) and legacy_safe_rs_crypto
(112-char, RS(36,32) ECC variant).

Test naming convention: test_<module>_<what_is_tested>
"""

import os

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

import app.utils.legacy_safe_crypto as ls
import app.utils.legacy_safe_rs_crypto as lsrs

# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture(scope="module")
def private_key():
    return Ed25519PrivateKey.generate()


@pytest.fixture(scope="module")
def signing_key(private_key):
    return ls.derive_signing_key_from_private_key(private_key)


@pytest.fixture(scope="module")
def log_id():
    return ls.generate_log_id()


# =============================================================================
# 1. CONSTANTS
# =============================================================================


def test_legacy_safe_marker_chars_is_100():
    """legacy_safe base-6 markers are 100 chars (ceil(256 * log2/log6))."""
    assert ls.MARKER_CHARS == 100


def test_legacy_safe_rs_marker_chars_is_112():
    """legacy_safe_rs RS-protected markers are 112 chars (ceil(288 * log2/log6))."""
    assert lsrs.MARKER_CHARS == 112


def test_legacy_safe_log_id_bytes_is_16():
    assert ls.LOG_ID_BYTES == 16


def test_legacy_safe_rs_log_id_bytes_is_16():
    assert lsrs.LOG_ID_BYTES == 16


# =============================================================================
# 2. generate_log_id
# =============================================================================


def test_generate_log_id_length():
    lid = ls.generate_log_id()
    assert isinstance(lid, bytes)
    assert len(lid) == ls.LOG_ID_BYTES


def test_generate_log_id_randomness():
    """Two consecutive calls must not return the same value (birthday safe)."""
    assert ls.generate_log_id() != ls.generate_log_id()


# =============================================================================
# 3. KEY DERIVATION
# =============================================================================


def test_derive_signing_key_length(private_key):
    key = ls.derive_signing_key_from_private_key(private_key)
    assert isinstance(key, bytes)
    assert len(key) == 32


def test_derive_signing_key_deterministic(private_key):
    k1 = ls.derive_signing_key_from_private_key(private_key)
    k2 = ls.derive_signing_key_from_private_key(private_key)
    assert k1 == k2


def test_derive_signing_key_different_keys_differ():
    k1 = ls.derive_signing_key_from_private_key(Ed25519PrivateKey.generate())
    k2 = ls.derive_signing_key_from_private_key(Ed25519PrivateKey.generate())
    assert k1 != k2


# =============================================================================
# 4. ROUND-TRIP: legacy_safe_crypto (100-char, no ECC)
# =============================================================================


def test_ls_round_trip_basic(signing_key, log_id):
    """create_marker -> find_all_markers -> verify_marker returns (True, bytes)."""
    marker = ls.create_marker(log_id, signing_key)

    assert len(marker) == ls.MARKER_CHARS

    text = "Some sentence." + marker + " More text."
    found = ls.find_all_markers(text)
    assert len(found) == 1

    _start, _end, extracted_marker = found[0]
    ok, returned_log_id = ls.verify_marker(extracted_marker, signing_key)

    assert ok is True
    assert isinstance(returned_log_id, bytes)
    assert returned_log_id == log_id


def test_ls_round_trip_content_bound(signing_key, log_id):
    """Content-bound marker verifies with matching sentence text."""
    sentence = "The central bank raised interest rates."
    marker = ls.create_marker(log_id, signing_key, sentence_text=sentence)

    ok, returned_log_id = ls.verify_marker(marker, signing_key, sentence_text=sentence)
    assert ok is True
    assert returned_log_id == log_id


def test_ls_round_trip_no_content_fallback(signing_key, log_id):
    """Marker created without sentence_text verifies when sentence_text is supplied."""
    marker = ls.create_marker(log_id, signing_key, sentence_text=None)

    ok, returned_log_id = ls.verify_marker(marker, signing_key, sentence_text="Any sentence text here.")
    assert ok is True
    assert returned_log_id == log_id


def test_ls_verify_nfc_stability(signing_key, log_id):
    """Content-bound verification holds across NFC-equivalent Unicode forms."""
    sentence_decomposed = "Cafe\u0301 prices rose."  # e + combining acute
    marker = ls.create_marker(log_id, signing_key, sentence_text=sentence_decomposed)

    sentence_composed = "Caf\u00e9 prices rose."  # precomposed e-acute
    ok, returned_log_id = ls.verify_marker(marker, signing_key, sentence_text=sentence_composed)
    assert ok is True
    assert returned_log_id == log_id


# =============================================================================
# 5. ROUND-TRIP: legacy_safe_rs_crypto (112-char, RS ECC)
# =============================================================================


def test_lsrs_round_trip_basic(signing_key, log_id):
    """RS variant: create_marker -> find_all_markers -> verify_marker returns (True, bytes)."""
    marker = lsrs.create_marker(log_id, signing_key)

    assert len(marker) == lsrs.MARKER_CHARS

    text = "Sentence one." + marker + " Sentence two."
    found = lsrs.find_all_markers(text)
    assert len(found) == 1

    _start, _end, extracted_marker = found[0]
    ok, returned_log_id = lsrs.verify_marker(extracted_marker, signing_key)

    assert ok is True
    assert isinstance(returned_log_id, bytes)
    assert returned_log_id == log_id


def test_lsrs_round_trip_content_bound(signing_key, log_id):
    sentence = "Earnings exceeded analyst expectations."
    marker = lsrs.create_marker(log_id, signing_key, sentence_text=sentence)

    ok, returned_log_id = lsrs.verify_marker(marker, signing_key, sentence_text=sentence)
    assert ok is True
    assert returned_log_id == log_id


def test_lsrs_round_trip_no_content_fallback(signing_key, log_id):
    """RS marker created without sentence_text verifies when sentence_text is supplied."""
    marker = lsrs.create_marker(log_id, signing_key, sentence_text=None)

    ok, returned_log_id = lsrs.verify_marker(marker, signing_key, sentence_text="Fallback verification sentence.")
    assert ok is True
    assert returned_log_id == log_id


# =============================================================================
# 6. WRONG KEY: must return (False, ...)
# =============================================================================


def test_ls_wrong_key_fails(signing_key, log_id):
    marker = ls.create_marker(log_id, signing_key)
    wrong_key = os.urandom(32)
    ok, result = ls.verify_marker(marker, wrong_key)
    assert ok is False


def test_ls_wrong_key_with_content_fails(signing_key, log_id):
    sentence = "Content-bound sentence."
    marker = ls.create_marker(log_id, signing_key, sentence_text=sentence)
    wrong_key = os.urandom(32)
    ok, result = ls.verify_marker(marker, wrong_key, sentence_text=sentence)
    assert ok is False


def test_lsrs_wrong_key_fails(signing_key, log_id):
    marker = lsrs.create_marker(log_id, signing_key)
    wrong_key = os.urandom(32)
    ok, result = lsrs.verify_marker(marker, wrong_key)
    assert ok is False


def test_ls_wrong_content_fails(signing_key, log_id):
    """Content-bound marker fails verification when wrong sentence is supplied."""
    sentence = "Original sentence text here."
    marker = ls.create_marker(log_id, signing_key, sentence_text=sentence)
    ok, _ = ls.verify_marker(marker, signing_key, sentence_text="Completely different sentence.")
    assert ok is False


def test_lsrs_wrong_content_fails(signing_key, log_id):
    sentence = "Original RS sentence."
    marker = lsrs.create_marker(log_id, signing_key, sentence_text=sentence)
    ok, _ = lsrs.verify_marker(marker, signing_key, sentence_text="Wrong RS sentence.")
    assert ok is False


# =============================================================================
# 7. embed_marker_safely: result is longer than original text
# =============================================================================


def test_ls_embed_marker_safely_longer(signing_key, log_id):
    sentence = "This is a sample sentence."
    marker = ls.create_marker(log_id, signing_key)
    embedded = ls.embed_marker_safely(sentence, marker)
    assert len(embedded) > len(sentence)
    assert len(embedded) == len(sentence) + ls.MARKER_CHARS


def test_lsrs_embed_marker_safely_longer(signing_key, log_id):
    sentence = "Another sample sentence for RS embedding."
    marker = lsrs.create_marker(log_id, signing_key)
    # embed_marker_safely is re-exported from legacy_safe_crypto in the rs module
    embedded = ls.embed_marker_safely(sentence, marker)
    assert len(embedded) > len(sentence)
    assert len(embedded) == len(sentence) + lsrs.MARKER_CHARS


def test_ls_embed_before_terminal_punctuation(signing_key, log_id):
    """Marker is inserted before trailing period, not after."""
    sentence = "Hello world."
    marker = ls.create_marker(log_id, signing_key)
    embedded = ls.embed_marker_safely(sentence, marker)
    assert embedded.endswith(".")
    assert embedded.startswith("Hello world")


def test_ls_embed_no_punctuation(signing_key, log_id):
    """Marker appended to text when no trailing punctuation."""
    sentence = "No punctuation here"
    marker = ls.create_marker(log_id, signing_key)
    embedded = ls.embed_marker_safely(sentence, marker)
    assert embedded.startswith(sentence)
    assert len(embedded) == len(sentence) + ls.MARKER_CHARS


# =============================================================================
# 8. LENGTH-BASED DETECTION: marker lengths are distinct
# =============================================================================


def test_ls_marker_length_is_100(signing_key, log_id):
    marker = ls.create_marker(log_id, signing_key)
    assert len(marker) == 100


def test_lsrs_marker_length_is_112(signing_key, log_id):
    marker = lsrs.create_marker(log_id, signing_key)
    assert len(marker) == 112


def test_lengths_are_distinct():
    """The two formats must be unambiguously distinguishable by length alone."""
    assert ls.MARKER_CHARS != lsrs.MARKER_CHARS


def test_ls_find_does_not_detect_lsrs_marker(signing_key, log_id):
    """
    A 112-char RS marker embedded in text must not be found by the 100-char scanner.

    The legacy_safe scanner chunks runs in 100-char blocks; a 112-char RS marker
    produces a run of length 112 which yields one 100-char chunk (offset 0) and
    one partial 12-char remainder that is too short, so at most 1 chunk is tested.
    The 100-char chunk lacks LRM/RLM only if all its chars happen to be from
    {ZWNJ, ZWJ, CGJ, MVS} -- statistically near-zero but not guaranteed.
    We simply verify that verify_marker rejects the extracted chunk (if any)
    because it will have an invalid HMAC.
    """
    rs_marker = lsrs.create_marker(log_id, signing_key)
    text = "Prefix " + rs_marker + " suffix."
    found_by_ls = ls.find_all_markers(text)
    # Each found 100-char chunk must fail ls.verify_marker (wrong length or bad HMAC)
    for _s, _e, chunk in found_by_ls:
        ok, _ = ls.verify_marker(chunk, signing_key)
        assert ok is False


def test_lsrs_find_does_not_detect_ls_marker(signing_key, log_id):
    """A 100-char non-RS marker must not be found by the 112-char RS scanner."""
    ls_marker = ls.create_marker(log_id, signing_key)
    text = "Prefix " + ls_marker + " suffix."
    found_by_lsrs = lsrs.find_all_markers(text)
    # 100 chars < 112 MARKER_CHARS, so no complete chunk can be extracted
    assert len(found_by_lsrs) == 0


# =============================================================================
# 9. INVALID INPUT HANDLING
# =============================================================================


def test_ls_verify_wrong_length_fails(signing_key):
    ok, result = ls.verify_marker("x" * 99, signing_key)
    assert ok is False
    assert result is None


def test_ls_verify_empty_string_fails(signing_key):
    ok, result = ls.verify_marker("", signing_key)
    assert ok is False
    assert result is None


def test_ls_create_marker_short_log_id(signing_key):
    with pytest.raises(ValueError, match="log_id must be"):
        ls.create_marker(b"\x00" * 15, signing_key)


def test_ls_create_marker_short_key(log_id):
    with pytest.raises(ValueError, match="signing_key must be at least 32 bytes"):
        ls.create_marker(log_id, b"\x00" * 16)


def test_lsrs_create_marker_short_log_id(signing_key):
    with pytest.raises(ValueError, match="log_id must be"):
        lsrs.create_marker(b"\x00" * 15, signing_key)


def test_lsrs_create_marker_short_key(log_id):
    with pytest.raises(ValueError, match="signing_key must be at least 32 bytes"):
        lsrs.create_marker(log_id, b"\x00" * 16)


# =============================================================================
# 10. find_all_markers / extract_marker / remove_markers
# =============================================================================


def test_ls_find_all_markers_in_text(signing_key, log_id):
    marker = ls.create_marker(log_id, signing_key)
    text = "Before" + marker + "After"
    found = ls.find_all_markers(text)
    assert len(found) == 1
    start, end, chunk = found[0]
    assert chunk == marker
    assert start == len("Before")
    assert end == len("Before") + ls.MARKER_CHARS


def test_ls_find_all_markers_empty_on_clean_text():
    assert ls.find_all_markers("No invisible chars here.") == []


def test_ls_find_multiple_markers(signing_key):
    lids = [ls.generate_log_id() for _ in range(3)]
    markers = [ls.create_marker(lid, signing_key) for lid in lids]
    text = "A" + markers[0] + "B" + markers[1] + "C" + markers[2] + "D"
    found = ls.find_all_markers(text)
    assert len(found) == 3
    for i, (_s, _e, chunk) in enumerate(found):
        assert chunk == markers[i]


def test_ls_extract_marker_returns_first(signing_key, log_id):
    marker = ls.create_marker(log_id, signing_key)
    text = "Start" + marker + "End"
    assert ls.extract_marker(text) == marker


def test_ls_extract_marker_none_on_clean_text():
    assert ls.extract_marker("No markers here.") is None


def test_ls_remove_markers(signing_key, log_id):
    marker = ls.create_marker(log_id, signing_key)
    text = "Hello" + marker + " world."
    clean = ls.remove_markers(text)
    assert clean == "Hello world."
    assert ls.find_all_markers(clean) == []


def test_ls_remove_markers_clean_text_unchanged():
    text = "Nothing to remove."
    assert ls.remove_markers(text) == text


# =============================================================================
# 11. create_embedded_sentence end-to-end
# =============================================================================


def test_ls_create_embedded_sentence_roundtrip(signing_key):
    sentence = "The quick brown fox jumps over the lazy dog."
    log_id_val = ls.generate_log_id()
    embedded = ls.create_embedded_sentence(sentence, log_id_val, signing_key)

    assert embedded.endswith(".")
    found = ls.find_all_markers(embedded)
    assert len(found) == 1
    _, _, chunk = found[0]
    ok, returned_log_id = ls.verify_marker(chunk, signing_key, sentence_text=sentence)
    assert ok is True
    assert returned_log_id == log_id_val


def test_lsrs_create_embedded_sentence_roundtrip(signing_key):
    sentence = "Post-quantum cryptography is the future of secure communications."
    log_id_val = lsrs.generate_log_id()
    embedded = lsrs.create_embedded_sentence(sentence, log_id_val, signing_key)

    assert embedded.endswith(".")
    found = lsrs.find_all_markers(embedded)
    assert len(found) == 1
    _, _, chunk = found[0]
    ok, returned_log_id = lsrs.verify_marker(chunk, signing_key, sentence_text=sentence)
    assert ok is True
    assert returned_log_id == log_id_val


# =============================================================================
# 12. ALPHABET PROPERTIES
# =============================================================================


def test_ls_alphabet_size():
    assert len(ls.CHARS_BASE6) == 6
    assert len(ls.CHARS_BASE6_SET) == 6


def test_ls_lrm_rlm_in_alphabet():
    """LRM and RLM must be in the base-6 alphabet to distinguish from base-4."""
    lrm = "\u200e"
    rlm = "\u200f"
    assert lrm in ls.CHARS_BASE6_SET
    assert rlm in ls.CHARS_BASE6_SET


def test_ls_lrm_rlm_absent_from_base4():
    """LRM/RLM (indices 4-5 of base-6) must not appear in the base-4 subset (indices 0-3)."""
    base4_chars = set(ls.CHARS_BASE6[:4])
    assert "\u200e" not in base4_chars  # LRM
    assert "\u200f" not in base4_chars  # RLM
