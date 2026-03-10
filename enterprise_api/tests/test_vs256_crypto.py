"""
Tests for base-256 Variation Selector cryptographic embedding (vs256_crypto module).

Tests the VS256 mode that uses all 256 Unicode Variation Selectors
(VS1-VS256) for maximum density invisible signatures.

Density: 1 byte per character (vs 6 chars per byte in legacy_safe/ZW6).
Result: 36 chars per signature (vs 100 in legacy_safe) -- a 2.8x improvement.
"""

import os

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from app.utils.vs256_crypto import (
    BYTE_TO_VS,
    LOG_ID_BYTES,
    MAGIC_PREFIX,
    MAGIC_PREFIX_LEN,
    PAYLOAD_CHARS,
    SIGNATURE_CHARS,
    VS_BMP_END,
    VS_BMP_START,
    VS_CHAR_SET,
    VS_SUPP_END,
    VS_SUPP_START,
    VS_TO_BYTE,
    create_embedded_sentence,
    create_signed_marker,
    decode_byte_vs256,
    decode_bytes_vs256,
    derive_signing_key_from_private_key,
    embed_signature_safely,
    encode_byte_vs256,
    encode_bytes_vs256,
    extract_marker,
    find_all_markers,
    generate_log_id,
    get_signature_position,
    remove_markers,
    verify_signed_marker,
)


@pytest.fixture
def test_keypair():
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    return private_key, public_key


@pytest.fixture
def signing_key(test_keypair):
    private_key, _ = test_keypair
    return derive_signing_key_from_private_key(private_key)


@pytest.fixture
def log_id():
    return generate_log_id()


# =============================================================================
# ALPHABET & ENCODING TESTS
# =============================================================================


def test_alphabet_completeness():
    """Verify the VS256 alphabet has exactly 256 unique characters."""
    assert len(BYTE_TO_VS) == 256
    assert len(VS_TO_BYTE) == 256
    assert len(VS_CHAR_SET) == 256
    assert len(set(BYTE_TO_VS)) == 256, "VS characters are not unique"


def test_bmp_vs_supplementary_split():
    """Verify BMP chars (0-15) and supplementary chars (16-255) are correct ranges."""
    for i in range(16):
        cp = ord(BYTE_TO_VS[i])
        assert VS_BMP_START <= cp <= VS_BMP_END, f"Byte {i} maps to U+{cp:04X}"

    for i in range(16, 256):
        cp = ord(BYTE_TO_VS[i])
        assert VS_SUPP_START <= cp <= VS_SUPP_END, f"Byte {i} maps to U+{cp:05X}"


def test_no_overlap_with_legacy_safe_chars():
    """Verify VS256 alphabet is disjoint from legacy_safe base-6 alphabet."""
    from app.utils.legacy_safe_crypto import CHARS_BASE6_SET

    overlap = VS_CHAR_SET & CHARS_BASE6_SET
    assert len(overlap) == 0, f"VS256 and legacy_safe alphabets overlap: {overlap}"


def test_encode_decode_byte():
    for value in range(256):
        encoded = encode_byte_vs256(value)
        decoded = decode_byte_vs256(encoded)
        assert decoded == value
        assert len(encoded) == 1
        assert encoded in VS_CHAR_SET


def test_encode_decode_boundary_values():
    encoded_15 = encode_byte_vs256(15)
    assert ord(encoded_15) == VS_BMP_END
    assert decode_byte_vs256(encoded_15) == 15

    encoded_16 = encode_byte_vs256(16)
    assert ord(encoded_16) == VS_SUPP_START
    assert decode_byte_vs256(encoded_16) == 16

    encoded_0 = encode_byte_vs256(0)
    assert ord(encoded_0) == VS_BMP_START

    encoded_255 = encode_byte_vs256(255)
    assert ord(encoded_255) == VS_SUPP_END


def test_encode_decode_bytes():
    test_data = [b"Hello", b"\x00\x01\x02\xff\xfe", bytes(range(256))]
    for data in test_data:
        encoded = encode_bytes_vs256(data)
        decoded = decode_bytes_vs256(encoded)
        assert decoded == data
        assert len(encoded) == len(data)
        for char in encoded:
            assert char in VS_CHAR_SET


def test_encode_byte_out_of_range():
    with pytest.raises(ValueError):
        encode_byte_vs256(-1)
    with pytest.raises(ValueError):
        encode_byte_vs256(256)


def test_decode_byte_invalid_char():
    with pytest.raises(ValueError):
        decode_byte_vs256("A")
    with pytest.raises(ValueError):
        decode_byte_vs256("\u200c")  # ZWNJ is not a VS char


# =============================================================================
# SUPPLEMENTARY CHAR HANDLING
# =============================================================================


def test_supplementary_char_length():
    ch = chr(0xE0100)  # VS17
    assert len(ch) == 1
    ch2 = chr(0xE01EF)  # VS256
    assert len(ch2) == 1


def test_string_slicing_supplementary():
    data = bytes(range(16, 26))
    encoded = encode_bytes_vs256(data)
    assert len(encoded) == 10
    assert decode_byte_vs256(encoded[0]) == 16
    assert decode_byte_vs256(encoded[9]) == 25
    assert decode_bytes_vs256(encoded[3:7]) == bytes(range(19, 23))


def test_utf8_encoding_size():
    bmp_char = chr(VS_BMP_START)
    assert len(bmp_char.encode("utf-8")) == 3  # BMP = 3 bytes

    supp_char = chr(VS_SUPP_START)
    assert len(supp_char.encode("utf-8")) == 4  # Supplementary = 4 bytes


# =============================================================================
# MAGIC PREFIX TESTS
# =============================================================================


def test_magic_prefix_structure():
    assert len(MAGIC_PREFIX) == 4
    for ch in MAGIC_PREFIX:
        cp = ord(ch)
        assert VS_SUPP_START <= cp <= VS_SUPP_END, f"Magic prefix char U+{cp:05X} not in supplementary VS range"


def test_no_false_positives_on_natural_vs():
    """Text with emoji VS usage should not trigger false detection."""
    text_with_emoji_vs = "Hello \u2764\ufe0f world \u2600\ufe0f today"
    found = find_all_markers(text_with_emoji_vs)
    assert len(found) == 0


# =============================================================================
# SIGNED MARKER TESTS
# =============================================================================


def test_signed_marker_creation(signing_key, log_id):
    signature = create_signed_marker(log_id, signing_key)
    assert len(signature) == SIGNATURE_CHARS
    assert signature[:MAGIC_PREFIX_LEN] == MAGIC_PREFIX
    for char in signature:
        assert char in VS_CHAR_SET


def test_signed_marker_wrong_log_id_length(signing_key):
    with pytest.raises(ValueError, match="log_id must be"):
        create_signed_marker(b"\x00" * 15, signing_key)


def test_signed_marker_short_key(log_id):
    with pytest.raises(ValueError, match="Signing key must be at least 32 bytes"):
        create_signed_marker(log_id, b"\x00" * 16)


def test_verify_correct_key(signing_key, log_id):
    signature = create_signed_marker(log_id, signing_key)
    ok, extracted = verify_signed_marker(signature, signing_key)
    assert ok is True
    assert extracted == log_id


def test_verify_returns_bytes(signing_key, log_id):
    signature = create_signed_marker(log_id, signing_key)
    ok, extracted = verify_signed_marker(signature, signing_key)
    assert ok is True
    assert isinstance(extracted, bytes)
    assert len(extracted) == LOG_ID_BYTES


def test_verify_wrong_key_fails(signing_key, log_id):
    signature = create_signed_marker(log_id, signing_key)
    wrong_key = os.urandom(32)
    ok, extracted = verify_signed_marker(signature, wrong_key)
    assert ok is False
    assert extracted is None


def test_verify_content_binding_correct_text(signing_key, log_id):
    sentence = "The central bank raised rates."
    signature = create_signed_marker(log_id, signing_key, sentence_text=sentence)
    ok, extracted = verify_signed_marker(signature, signing_key, sentence_text=sentence)
    assert ok is True
    assert extracted == log_id


def test_verify_content_binding_wrong_text_fails(signing_key, log_id):
    sentence = "The central bank raised rates."
    signature = create_signed_marker(log_id, signing_key, sentence_text=sentence)
    ok, _ = verify_signed_marker(signature, signing_key, sentence_text="The central bank cut rates.")
    assert ok is False


def test_verify_content_free_fallback(signing_key, log_id):
    """Marker created WITHOUT sentence_text should still verify when text is supplied."""
    signature = create_signed_marker(log_id, signing_key, sentence_text=None)
    ok, extracted = verify_signed_marker(signature, signing_key, sentence_text="Any text")
    assert ok is True
    assert extracted == log_id


def test_verify_nfc_stability(signing_key, log_id):
    """Content-bound signatures should verify across NFC-equivalent forms."""
    sentence_nfc = "Cafe\u0301 prices increased."  # decomposed
    signature = create_signed_marker(log_id, signing_key, sentence_text=sentence_nfc)
    # composed equivalent
    ok, extracted = verify_signed_marker(signature, signing_key, sentence_text="Caf\u00e9 prices increased.")
    assert ok is True
    assert extracted == log_id


def test_verify_tampering_detected(signing_key):
    log_id_val = generate_log_id()
    signature = create_signed_marker(log_id_val, signing_key)
    tampered = list(signature)
    target_idx = MAGIC_PREFIX_LEN + 5
    original_byte = VS_TO_BYTE[tampered[target_idx]]
    tampered[target_idx] = BYTE_TO_VS[(original_byte + 1) % 256]
    ok, _ = verify_signed_marker("".join(tampered), signing_key)
    assert ok is False


def test_verify_wrong_length_fails(signing_key):
    ok, extracted = verify_signed_marker("x" * 35, signing_key)
    assert ok is False
    assert extracted is None


# =============================================================================
# DETECTION IN TEXT
# =============================================================================


def test_find_markers_in_plain_text(signing_key, log_id):
    signature = create_signed_marker(log_id, signing_key)
    text = f"Before{signature}After"
    found = find_all_markers(text)
    assert len(found) == 1
    start, end, sig = found[0]
    assert sig == signature
    assert start == 6
    assert end == 6 + SIGNATURE_CHARS


def test_find_multiple_markers(signing_key):
    sigs = [create_signed_marker(generate_log_id(), signing_key) for _ in range(3)]
    text = "A" + sigs[0] + "B" + sigs[1] + "C" + sigs[2] + "D"
    found = find_all_markers(text)
    assert len(found) == 3
    for i, (_, _, sig) in enumerate(found):
        assert sig == sigs[i]


def test_find_markers_empty_on_clean_text():
    assert find_all_markers("No invisible chars here.") == []


def test_sentence_level_multi_embedding(signing_key):
    sentences = [
        "This is the first sentence.",
        "Here is another sentence with more content.",
        "The third sentence concludes the paragraph.",
    ]
    log_ids = []
    signed_sentences = []
    for sentence in sentences:
        lid = generate_log_id()
        log_ids.append(lid)
        sig = create_signed_marker(lid, signing_key)
        signed_sentences.append(sentence + sig)

    document = " ".join(signed_sentences)
    found = find_all_markers(document)
    assert len(found) == 3

    for i, (_, _, sig) in enumerate(found):
        ok, extracted = verify_signed_marker(sig, signing_key)
        assert ok is True
        assert extracted == log_ids[i]


# =============================================================================
# EXTRACT AND REMOVE
# =============================================================================


def test_extract_marker_returns_first(signing_key, log_id):
    signature = create_signed_marker(log_id, signing_key)
    text = "Start" + signature + "End"
    assert extract_marker(text) == signature


def test_extract_marker_none_on_clean_text():
    assert extract_marker("No markers here.") is None


def test_remove_markers(signing_key, log_id):
    sig = create_signed_marker(log_id, signing_key)
    text = "Hello" + sig + " world."
    clean = remove_markers(text)
    assert clean == "Hello world."
    assert find_all_markers(clean) == []


def test_remove_markers_clean_text_unchanged():
    text = "No invisible chars."
    assert remove_markers(text) == text


# =============================================================================
# SAFE EMBEDDING
# =============================================================================


def test_safe_embedding_period():
    result = embed_signature_safely("Hello world.", "[SIG]")
    assert result == "Hello world[SIG]."


def test_safe_embedding_question():
    result = embed_signature_safely("What time is it?", "[SIG]")
    assert result == "What time is it[SIG]?"


def test_safe_embedding_exclamation():
    result = embed_signature_safely("Wow!", "[SIG]")
    assert result == "Wow[SIG]!"


def test_safe_embedding_quoted():
    result = embed_signature_safely('She said "Hello."', "[SIG]")
    assert result == 'She said "Hello[SIG]."'


def test_safe_embedding_no_punctuation():
    result = embed_signature_safely("No punctuation here", "[SIG]")
    assert result == "No punctuation here[SIG]"


def test_safe_embedding_with_real_signature(signing_key):
    log_id_val = generate_log_id()
    sentence = "This is a test sentence."
    embedded = create_embedded_sentence(sentence, log_id_val, signing_key)

    assert embedded.endswith(".")
    found = find_all_markers(embedded)
    assert len(found) == 1

    _, _, sig = found[0]
    ok, extracted = verify_signed_marker(sig, signing_key, sentence_text=sentence)
    assert ok is True
    assert extracted == log_id_val


def test_get_signature_position():
    test_cases = [
        ("Hello world.", 11),
        ("What?", 4),
        ("Wow!", 3),
        ('Say "Hi."', 7),
        ("No punct", 8),
        ("", 0),
        ("...", 0),
    ]
    for text, expected_pos in test_cases:
        pos = get_signature_position(text)
        assert pos == expected_pos, f"For '{text}': expected {expected_pos}, got {pos}"


def test_create_embedded_sentence_roundtrip(signing_key):
    sentence = "The quick brown fox jumps over the lazy dog."
    log_id_val = generate_log_id()
    embedded = create_embedded_sentence(sentence, log_id_val, signing_key)

    found = find_all_markers(embedded)
    assert len(found) == 1
    _, _, sig = found[0]
    ok, extracted = verify_signed_marker(sig, signing_key, sentence_text=sentence)
    assert ok is True
    assert extracted == log_id_val


# =============================================================================
# CROSS-COMPATIBILITY: VS256 does not interfere with ZW
# =============================================================================


def test_vs256_does_not_interfere_with_legacy_safe(signing_key):
    from app.utils.legacy_safe_crypto import (
        create_marker as ls_create,
    )
    from app.utils.legacy_safe_crypto import (
        find_all_markers as ls_find_all,
    )
    from app.utils.legacy_safe_crypto import (
        generate_log_id as ls_generate_log_id,
    )

    ls_sig = ls_create(ls_generate_log_id(), signing_key)
    vs_sig = create_signed_marker(generate_log_id(), signing_key)
    text = f"First{ls_sig}. Second{vs_sig}."

    ls_found = ls_find_all(text)
    assert len(ls_found) == 1

    vs_found = find_all_markers(text)
    assert len(vs_found) == 1


# =============================================================================
# KEY DERIVATION
# =============================================================================


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


# =============================================================================
# SIZE CONSTANTS
# =============================================================================


def test_signature_chars_is_36():
    """36 = 4 magic prefix + 32 payload (16-byte log_id + 16-byte HMAC)."""
    assert SIGNATURE_CHARS == 36


def test_payload_chars_is_32():
    assert PAYLOAD_CHARS == 32


def test_log_id_bytes_is_16():
    """16-byte log_id provides 128-bit uniqueness (hyperscale-safe)."""
    assert LOG_ID_BYTES == 16
