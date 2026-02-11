"""
Tests for base-256 Variation Selector cryptographic embedding (vs256_crypto module).

Tests the vs256_embedding mode that uses all 256 Unicode Variation Selectors
(VS1-VS256) for maximum density invisible signatures.

Density: 1 byte per character (vs 4 chars per byte in zw_embedding).
Result: 36 chars per signature (vs 128 in zw_embedding) — a 3.6x improvement.
"""

from uuid import uuid4

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from app.utils.vs256_crypto import (
    BYTE_TO_VS,
    VS_TO_BYTE,
    VS_CHAR_SET,
    VS_BMP_START,
    VS_BMP_END,
    VS_SUPP_START,
    VS_SUPP_END,
    MAGIC_PREFIX,
    MAGIC_PREFIX_LEN,
    SIGNATURE_CHARS,
    PAYLOAD_CHARS,
    encode_byte_vs256,
    decode_byte_vs256,
    encode_bytes_vs256,
    decode_bytes_vs256,
    create_minimal_signed_uuid,
    verify_minimal_signed_uuid,
    extract_minimal_signed_uuid,
    find_all_minimal_signed_uuids,
    remove_minimal_signed_uuid,
    embed_signature_safely,
    get_signature_position,
    derive_signing_key_from_private_key,
    create_safely_embedded_sentence,
)


@pytest.fixture
def test_keypair():
    """Generate a test Ed25519 keypair."""
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    return private_key, public_key


# =============================================================================
# ALPHABET & ENCODING TESTS
# =============================================================================


def test_alphabet_completeness():
    """Verify the VS256 alphabet has exactly 256 unique characters."""
    assert len(BYTE_TO_VS) == 256, f"Expected 256 VS chars, got {len(BYTE_TO_VS)}"
    assert len(VS_TO_BYTE) == 256, f"Expected 256 VS mappings, got {len(VS_TO_BYTE)}"
    assert len(VS_CHAR_SET) == 256, f"Expected 256 unique chars, got {len(VS_CHAR_SET)}"

    # All chars should be unique
    assert len(set(BYTE_TO_VS)) == 256, "VS characters are not unique"


def test_bmp_vs_supplementary_split():
    """Verify BMP chars (0-15) and supplementary chars (16-255) are correct ranges."""
    # First 16: BMP range U+FE00-U+FE0F
    for i in range(16):
        cp = ord(BYTE_TO_VS[i])
        assert VS_BMP_START <= cp <= VS_BMP_END, (
            f"Byte {i} maps to U+{cp:04X}, expected BMP range U+FE00-U+FE0F"
        )

    # Next 240: Supplementary range U+E0100-U+E01EF
    for i in range(16, 256):
        cp = ord(BYTE_TO_VS[i])
        assert VS_SUPP_START <= cp <= VS_SUPP_END, (
            f"Byte {i} maps to U+{cp:05X}, expected supplementary range U+E0100-U+E01EF"
        )


def test_no_overlap_with_zw_chars():
    """Verify VS256 alphabet is disjoint from ZW base-4 alphabet."""
    from app.utils.zw_crypto import CHARS_BASE4_SET

    overlap = VS_CHAR_SET & CHARS_BASE4_SET
    assert len(overlap) == 0, f"VS256 and ZW alphabets overlap: {overlap}"


def test_encode_decode_byte():
    """Test byte encoding/decoding roundtrip for all 256 values."""
    for value in range(256):
        encoded = encode_byte_vs256(value)
        decoded = decode_byte_vs256(encoded)

        assert decoded == value, f"Roundtrip failed: {value} -> U+{ord(encoded):04X} -> {decoded}"
        assert len(encoded) == 1, f"Encoded length should be 1, got {len(encoded)}"
        assert encoded in VS_CHAR_SET, f"Invalid character: U+{ord(encoded):04X}"


def test_encode_decode_boundary_values():
    """Test encoding at BMP/supplementary boundary (15/16)."""
    # Last BMP char (VS16)
    encoded_15 = encode_byte_vs256(15)
    assert ord(encoded_15) == VS_BMP_END, f"Byte 15 should be VS16 (U+FE0F)"
    assert decode_byte_vs256(encoded_15) == 15

    # First supplementary char (VS17)
    encoded_16 = encode_byte_vs256(16)
    assert ord(encoded_16) == VS_SUPP_START, f"Byte 16 should be VS17 (U+E0100)"
    assert decode_byte_vs256(encoded_16) == 16

    # Byte 0 (VS1)
    encoded_0 = encode_byte_vs256(0)
    assert ord(encoded_0) == VS_BMP_START, f"Byte 0 should be VS1 (U+FE00)"

    # Byte 255 (VS256)
    encoded_255 = encode_byte_vs256(255)
    assert ord(encoded_255) == VS_SUPP_END, f"Byte 255 should be VS256 (U+E01EF)"


def test_encode_decode_bytes():
    """Test multi-byte encoding/decoding roundtrip."""
    test_data = [
        b"Hello",
        b"\x00\x01\x02\xff\xfe",
        b"The quick brown fox",
        bytes(range(256)),  # All possible byte values
    ]

    for data in test_data:
        encoded = encode_bytes_vs256(data)
        decoded = decode_bytes_vs256(encoded)

        assert decoded == data, f"Roundtrip failed for {len(data)} bytes"
        assert len(encoded) == len(data), (
            f"Encoded length should be {len(data)} (1:1 ratio), got {len(encoded)}"
        )

        # Verify all chars are VS
        for char in encoded:
            assert char in VS_CHAR_SET


def test_encode_byte_out_of_range():
    """Test that out-of-range byte values raise ValueError."""
    with pytest.raises(ValueError):
        encode_byte_vs256(-1)
    with pytest.raises(ValueError):
        encode_byte_vs256(256)


def test_decode_byte_invalid_char():
    """Test that non-VS characters raise ValueError."""
    with pytest.raises(ValueError):
        decode_byte_vs256("A")
    with pytest.raises(ValueError):
        decode_byte_vs256("\u200C")  # ZWNJ is not a VS char


# =============================================================================
# PYTHON SUPPLEMENTARY CHAR HANDLING
# =============================================================================


def test_supplementary_char_length():
    """Verify Python treats supplementary VS chars as single characters."""
    ch = chr(0xE0100)  # VS17
    assert len(ch) == 1, f"Supplementary char should be length 1, got {len(ch)}"

    ch2 = chr(0xE01EF)  # VS256
    assert len(ch2) == 1, f"Last supplementary char should be length 1, got {len(ch2)}"


def test_string_slicing_supplementary():
    """Verify string slicing works correctly with supplementary VS chars."""
    # Create a string of 10 supplementary VS chars (byte values 16-25)
    data = bytes(range(16, 26))
    encoded = encode_bytes_vs256(data)

    assert len(encoded) == 10
    # Slicing should work by code points
    assert decode_byte_vs256(encoded[0]) == 16
    assert decode_byte_vs256(encoded[9]) == 25
    assert decode_bytes_vs256(encoded[3:7]) == bytes(range(19, 23))


def test_utf8_encoding_size():
    """Verify UTF-8 byte sizes for BMP vs supplementary VS chars."""
    # BMP VS chars (U+FE00-U+FE0F) are 3 bytes in UTF-8
    bmp_char = chr(VS_BMP_START)
    assert len(bmp_char.encode("utf-8")) == 3

    # Supplementary VS chars (U+E0100+) are 4 bytes in UTF-8
    supp_char = chr(VS_SUPP_START)
    assert len(supp_char.encode("utf-8")) == 4


# =============================================================================
# MAGIC PREFIX TESTS
# =============================================================================


def test_magic_prefix_structure():
    """Verify magic prefix uses supplementary-plane VS chars."""
    assert len(MAGIC_PREFIX) == 4

    for ch in MAGIC_PREFIX:
        cp = ord(ch)
        assert VS_SUPP_START <= cp <= VS_SUPP_END, (
            f"Magic prefix char U+{cp:05X} not in supplementary VS range"
        )


def test_no_false_positives_on_natural_vs():
    """Text with emoji VS usage should not trigger false detection."""
    # Emoji with VS16 (text presentation selector) — common in natural text
    text_with_emoji_vs = "Hello \u2764\uFE0F world \u2600\uFE0F today"

    found = find_all_minimal_signed_uuids(text_with_emoji_vs)
    assert len(found) == 0, "Emoji VS usage should not trigger detection"


# =============================================================================
# MINIMAL SIGNED UUID TESTS
# =============================================================================


def test_minimal_signed_uuid_creation(test_keypair):
    """Test creating a VS256 minimal signed UUID."""
    private_key, _ = test_keypair
    signing_key = derive_signing_key_from_private_key(private_key)

    sentence_uuid = uuid4()
    signature = create_minimal_signed_uuid(sentence_uuid, signing_key)

    # Should be exactly 36 chars (4 magic + 32 payload)
    assert len(signature) == SIGNATURE_CHARS, (
        f"Expected {SIGNATURE_CHARS} chars, got {len(signature)}"
    )

    # Should start with magic prefix
    assert signature[:MAGIC_PREFIX_LEN] == MAGIC_PREFIX

    # All chars should be VS characters
    for char in signature:
        assert char in VS_CHAR_SET, f"Non-VS character: U+{ord(char):04X}"

    print(f"✓ VS256 minimal signed UUID created: {len(signature)} chars")


def test_minimal_signed_uuid_verification(test_keypair):
    """Test verifying a VS256 minimal signed UUID."""
    private_key, _ = test_keypair
    signing_key = derive_signing_key_from_private_key(private_key)

    sentence_uuid = uuid4()
    signature = create_minimal_signed_uuid(sentence_uuid, signing_key)

    # Embed in text
    text = "This is a test sentence."
    signed_text = text + signature

    # Extract signature from text
    extracted_sig = extract_minimal_signed_uuid(signed_text)
    assert extracted_sig is not None, "Should find signature in text"

    # Verify the extracted signature
    is_valid, extracted_uuid = verify_minimal_signed_uuid(extracted_sig, signing_key)

    assert is_valid, "Signature should be valid"
    assert extracted_uuid == sentence_uuid, "UUID should match"

    print(f"✓ VS256 minimal signed UUID verified: {extracted_uuid}")


def test_minimal_signed_uuid_wrong_key(test_keypair):
    """Test that wrong signing key fails verification."""
    private_key, _ = test_keypair
    signing_key = derive_signing_key_from_private_key(private_key)

    sentence_uuid = uuid4()
    signature = create_minimal_signed_uuid(sentence_uuid, signing_key)

    # Try to verify with wrong key
    wrong_key = b"wrong_key_" * 4  # 40 bytes
    is_valid, _ = verify_minimal_signed_uuid(signature, wrong_key)

    assert not is_valid, "Should fail with wrong key"

    print("✓ Wrong key rejected correctly")


def test_minimal_signed_uuid_tampering():
    """Test that tampering with signature is detected."""
    signing_key = b"test_signing_key_32_bytes_long!!"

    sentence_uuid = uuid4()
    signature = create_minimal_signed_uuid(sentence_uuid, signing_key)

    # Tamper: replace one payload char with a different VS char
    tampered = list(signature)
    # Change a payload char (after magic prefix)
    target_idx = MAGIC_PREFIX_LEN + 5
    original_byte = VS_TO_BYTE[tampered[target_idx]]
    replacement_byte = (original_byte + 1) % 256
    tampered[target_idx] = BYTE_TO_VS[replacement_byte]
    tampered_sig = "".join(tampered)

    is_valid, _ = verify_minimal_signed_uuid(tampered_sig, signing_key)

    assert not is_valid, "Should detect tampering"

    print("✓ Tampering detected correctly")


def test_minimal_signed_uuid_sentence_level():
    """Test sentence-level embedding with VS256 minimal signed UUIDs."""
    signing_key = b"test_signing_key_32_bytes_long!!"

    sentences = [
        "This is the first sentence.",
        "Here is another sentence with more content.",
        "The third sentence concludes the paragraph.",
    ]

    signed_sentences = []
    uuid_map = {}

    for sentence in sentences:
        sentence_uuid = uuid4()
        signature = create_minimal_signed_uuid(sentence_uuid, signing_key)
        signed_sentence = sentence + signature
        signed_sentences.append(signed_sentence)
        uuid_map[sentence_uuid] = sentence

    # Join into document
    document = " ".join(signed_sentences)

    # Find all signatures
    found = find_all_minimal_signed_uuids(document)

    assert len(found) == 3, f"Should find 3 signatures, found {len(found)}"

    # Verify each signature
    for start, end, sig in found:
        is_valid, extracted_uuid = verify_minimal_signed_uuid(sig, signing_key)
        assert is_valid, "Each signature should be valid"
        assert extracted_uuid in uuid_map, "UUID should be in our map"

    # Calculate overhead
    original_len = sum(len(s) for s in sentences) + 2  # +2 for spaces
    total_len = len(document)
    overhead = total_len - original_len

    print(f"✓ VS256 sentence-level embedding: {len(sentences)} sentences")
    print(f"  Original: {original_len} chars")
    print(f"  With signatures: {total_len} chars")
    print(f"  Overhead: {overhead} VS chars ({overhead / len(sentences):.0f} per sentence)")


def test_remove_minimal_signed_uuid():
    """Test removing all VS256 signatures from text."""
    signing_key = b"test_signing_key_32_bytes_long!!"

    original = "Hello world. This is a test."
    uuid1 = uuid4()
    sig1 = create_minimal_signed_uuid(uuid1, signing_key)

    signed = original + sig1
    cleaned = remove_minimal_signed_uuid(signed)

    assert cleaned == original, f"Cleaned text should match original"


# =============================================================================
# SAFE EMBEDDING POSITION TESTS
# =============================================================================


def test_safe_embedding_period():
    """Test embedding before period."""
    signature = "[SIG]"
    result = embed_signature_safely("Hello world.", signature)
    assert result == "Hello world[SIG].", f"Got: {result}"


def test_safe_embedding_question():
    """Test embedding before question mark."""
    signature = "[SIG]"
    result = embed_signature_safely("What time is it?", signature)
    assert result == "What time is it[SIG]?", f"Got: {result}"


def test_safe_embedding_exclamation():
    """Test embedding before exclamation mark."""
    signature = "[SIG]"
    result = embed_signature_safely("Wow!", signature)
    assert result == "Wow[SIG]!", f"Got: {result}"


def test_safe_embedding_quoted():
    """Test embedding before quoted punctuation."""
    signature = "[SIG]"

    result = embed_signature_safely('She said "Hello."', signature)
    assert result == 'She said "Hello[SIG]."', f"Got: {result}"

    result2 = embed_signature_safely('Did she say "Yes"?', signature)
    assert result2 == 'Did she say "Yes[SIG]"?', f"Got: {result2}"


def test_safe_embedding_no_punctuation():
    """Test embedding when no terminal punctuation."""
    signature = "[SIG]"
    result = embed_signature_safely("No punctuation here", signature)
    assert result == "No punctuation here[SIG]", f"Got: {result}"


def test_safe_embedding_multiple_punctuation():
    """Test embedding with multiple trailing punctuation."""
    signature = "[SIG]"

    result = embed_signature_safely("Really?!", signature)
    assert result == "Really[SIG]?!", f"Got: {result}"

    result2 = embed_signature_safely("Wait...", signature)
    assert result2 == "Wait[SIG]...", f"Got: {result2}"


def test_safe_embedding_with_real_signature():
    """Test safe embedding with actual VS256 minimal signed UUID."""
    signing_key = b"test_signing_key_32_bytes_long!!"
    sentence_uuid = uuid4()

    sentence = "This is a test sentence."
    embedded = create_safely_embedded_sentence(sentence, sentence_uuid, signing_key)

    # Should end with period (signature before it)
    assert embedded.endswith("."), f"Should end with period"

    # Should contain the signature
    found_sigs = find_all_minimal_signed_uuids(embedded)
    assert len(found_sigs) > 0, "Should contain signature"

    # Extract and verify
    sig = extract_minimal_signed_uuid(embedded)
    assert sig is not None
    is_valid, extracted_uuid = verify_minimal_signed_uuid(sig, signing_key)
    assert is_valid, "Signature should be valid"
    assert extracted_uuid == sentence_uuid, "UUID should match"

    # Clean text should match original
    clean = embedded.replace(sig, "")
    assert clean == sentence

    print("✓ VS256 safe embedding with real signature verified")


def test_get_signature_position():
    """Test getting signature position for various texts."""
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


def test_safe_embedding_sentence_level():
    """Test safe embedding for multiple sentences."""
    signing_key = b"test_signing_key_32_bytes_long!!"

    sentences = [
        "This is the first sentence.",
        "Is this a question?",
        "What an exclamation!",
        "No punctuation here",
    ]

    embedded_sentences = []
    uuids = []

    for sentence in sentences:
        sentence_uuid = uuid4()
        uuids.append(sentence_uuid)
        embedded = create_safely_embedded_sentence(sentence, sentence_uuid, signing_key)
        embedded_sentences.append(embedded)

    document = " ".join(embedded_sentences)

    found = find_all_minimal_signed_uuids(document)
    assert len(found) == 4, f"Should find 4 signatures, found {len(found)}"

    for i, (start, end, sig) in enumerate(found):
        is_valid, extracted_uuid = verify_minimal_signed_uuid(sig, signing_key)
        assert is_valid, f"Signature {i} should be valid"
        assert extracted_uuid == uuids[i], f"UUID {i} should match"

    print(f"✓ VS256 safe embedding sentence-level: {len(sentences)} sentences verified")


# =============================================================================
# CROSS-COMPATIBILITY TESTS
# =============================================================================


def test_vs256_does_not_interfere_with_zw():
    """VS256 signatures should not interfere with ZW signature detection."""
    from app.utils.zw_crypto import (
        create_minimal_signed_uuid as zw_create,
        find_all_minimal_signed_uuids as zw_find_all,
        derive_signing_key_from_private_key as zw_derive_key,
    )

    private_key = Ed25519PrivateKey.generate()
    signing_key = zw_derive_key(private_key)

    # Create both types of signatures
    uuid_zw = uuid4()
    uuid_vs = uuid4()
    zw_sig = zw_create(uuid_zw, signing_key)
    vs_sig = create_minimal_signed_uuid(uuid_vs, signing_key)

    # Embed both in text
    text = f"First sentence{zw_sig}. Second sentence{vs_sig}."

    # ZW detection should only find ZW signatures
    zw_found = zw_find_all(text)
    assert len(zw_found) == 1, f"ZW should find 1 signature, found {len(zw_found)}"

    # VS256 detection should only find VS256 signatures
    vs_found = find_all_minimal_signed_uuids(text)
    assert len(vs_found) == 1, f"VS256 should find 1 signature, found {len(vs_found)}"


def test_zw_does_not_interfere_with_vs256():
    """ZW signatures in text should not affect VS256 detection/verification."""
    from app.utils.zw_crypto import (
        create_minimal_signed_uuid as zw_create,
        verify_minimal_signed_uuid as zw_verify,
        derive_signing_key_from_private_key as zw_derive_key,
    )

    private_key = Ed25519PrivateKey.generate()
    signing_key = zw_derive_key(private_key)

    uuid_zw = uuid4()
    uuid_vs = uuid4()
    zw_sig = zw_create(uuid_zw, signing_key)
    vs_sig = create_minimal_signed_uuid(uuid_vs, signing_key)

    # Mix both in a document
    text = f"Sentence A{zw_sig}. Sentence B{vs_sig}. Sentence C."

    # Verify VS256 signature independently
    vs_found = find_all_minimal_signed_uuids(text)
    assert len(vs_found) == 1
    is_valid, extracted = verify_minimal_signed_uuid(vs_found[0][2], signing_key)
    assert is_valid
    assert extracted == uuid_vs

    # Verify ZW signature independently
    from app.utils.zw_crypto import find_all_minimal_signed_uuids as zw_find_all

    zw_found = zw_find_all(text)
    assert len(zw_found) == 1
    is_valid_zw, extracted_zw = zw_verify(zw_found[0][2], signing_key)
    assert is_valid_zw
    assert extracted_zw == uuid_zw


# =============================================================================
# PAYLOAD SIZE COMPARISON TESTS
# =============================================================================


def test_payload_size_comparison():
    """Compare payload sizes across VS256, ZW, and basic-format VS embeddings."""
    from app.utils.zw_crypto import (
        create_minimal_signed_uuid as zw_create,
        derive_signing_key_from_private_key as zw_derive_key,
    )

    private_key = Ed25519PrivateKey.generate()
    signing_key = zw_derive_key(private_key)
    sentence_uuid = uuid4()

    # VS256 signature
    vs256_sig = create_minimal_signed_uuid(sentence_uuid, signing_key)

    # ZW base-4 signature
    zw_sig = zw_create(sentence_uuid, signing_key)

    # Basic-format VS embedding (used by minimal_uuid/lightweight_uuid modes)
    # This embeds JSON metadata as VS characters via UnicodeMetadata
    from encypher.core.unicode_metadata import UnicodeMetadata

    sample_text = "The quick brown fox jumps over the lazy dog."
    basic_embedded = UnicodeMetadata.embed_metadata(
        text=sample_text,
        private_key=private_key,
        signer_id="test_signer",
        metadata_format="basic",
    )
    basic_overhead_chars = len(basic_embedded) - len(sample_text)

    # Compute sizes
    vs256_chars = len(vs256_sig)
    vs256_utf8 = len(vs256_sig.encode("utf-8"))
    vs256_utf16 = len(vs256_sig.encode("utf-16-le"))

    zw_chars = len(zw_sig)
    zw_utf8 = len(zw_sig.encode("utf-8"))
    zw_utf16 = len(zw_sig.encode("utf-16-le"))

    # Print comparison table
    print("\n" + "=" * 72)
    print("PAYLOAD SIZE COMPARISON (per sentence)")
    print("=" * 72)
    print(f"{'Mode':<25} {'Chars':>8} {'UTF-8 B':>10} {'UTF-16 B':>10}")
    print("-" * 72)
    print(f"{'VS256 (base-256)':.<25} {vs256_chars:>8} {vs256_utf8:>10} {vs256_utf16:>10}")
    print(f"{'ZW (base-4)':.<25} {zw_chars:>8} {zw_utf8:>10} {zw_utf16:>10}")
    print(f"{'Basic VS (JSON payload)':.<25} {basic_overhead_chars:>8} {'varies':>10} {'varies':>10}")
    print("-" * 72)
    print(f"{'VS256 vs ZW improvement':.<25} {zw_chars / vs256_chars:>7.1f}x {zw_utf8 / vs256_utf8:>9.1f}x {zw_utf16 / vs256_utf16:>9.1f}x")
    print(f"{'VS256 vs Basic improvement':.<25} {basic_overhead_chars / vs256_chars:>7.1f}x")
    print("=" * 72)

    # Assertions
    assert vs256_chars == SIGNATURE_CHARS, f"VS256 should be {SIGNATURE_CHARS} chars"
    assert zw_chars == 128, "ZW should be 128 chars"
    assert vs256_chars < zw_chars, "VS256 should be smaller than ZW"
    assert vs256_chars < basic_overhead_chars, "VS256 should be smaller than basic VS"

    # Verify the ratio
    ratio = zw_chars / vs256_chars
    assert ratio > 3.0, f"VS256 should be at least 3x smaller than ZW, got {ratio:.1f}x"


def test_payload_size_scaling():
    """Compare total overhead as sentence count scales: 1, 5, 10, 50 sentences."""
    from app.utils.zw_crypto import (
        create_minimal_signed_uuid as zw_create,
        embed_signature_safely as zw_embed,
        derive_signing_key_from_private_key as zw_derive_key,
    )

    private_key = Ed25519PrivateKey.generate()
    signing_key = zw_derive_key(private_key)

    sample_sentence = "The quick brown fox jumps over the lazy dog."
    sentence_counts = [1, 5, 10, 50]

    print("\n" + "=" * 72)
    print("OVERHEAD SCALING COMPARISON")
    print("=" * 72)
    print(f"{'Sentences':>10} {'VS256 chars':>14} {'ZW chars':>12} {'VS256 UTF-8':>14} {'ZW UTF-8':>12}")
    print("-" * 72)

    for count in sentence_counts:
        vs256_total_chars = 0
        vs256_total_utf8 = 0
        zw_total_chars = 0
        zw_total_utf8 = 0

        for _ in range(count):
            uid = uuid4()

            vs_sig = create_minimal_signed_uuid(uid, signing_key)
            vs256_total_chars += len(vs_sig)
            vs256_total_utf8 += len(vs_sig.encode("utf-8"))

            zw_sig = zw_create(uid, signing_key)
            zw_total_chars += len(zw_sig)
            zw_total_utf8 += len(zw_sig.encode("utf-8"))

        source_chars = len(sample_sentence) * count
        vs256_pct = (vs256_total_chars / source_chars) * 100
        zw_pct = (zw_total_chars / source_chars) * 100

        print(
            f"{count:>10} {vs256_total_chars:>10} ({vs256_pct:>4.1f}%)"
            f" {zw_total_chars:>8} ({zw_pct:>4.1f}%)"
            f" {vs256_total_utf8:>10}"
            f" {zw_total_utf8:>12}"
        )

        # VS256 should always be smaller
        assert vs256_total_chars < zw_total_chars

    print("=" * 72)


# =============================================================================
# MAIN RUNNER
# =============================================================================


if __name__ == "__main__":
    print("Running VS256 Crypto Tests...\n")

    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    keypair = (private_key, public_key)

    print("--- Alphabet & Encoding Tests ---\n")
    test_alphabet_completeness()
    test_bmp_vs_supplementary_split()
    test_no_overlap_with_zw_chars()
    test_encode_decode_byte()
    test_encode_decode_boundary_values()
    test_encode_decode_bytes()
    test_supplementary_char_length()
    test_string_slicing_supplementary()
    test_utf8_encoding_size()

    print("\n--- Magic Prefix Tests ---\n")
    test_magic_prefix_structure()
    test_no_false_positives_on_natural_vs()

    print("\n--- Minimal Signed UUID Tests ---\n")
    test_minimal_signed_uuid_creation(keypair)
    test_minimal_signed_uuid_verification(keypair)
    test_minimal_signed_uuid_wrong_key(keypair)
    test_minimal_signed_uuid_tampering()
    test_minimal_signed_uuid_sentence_level()
    test_remove_minimal_signed_uuid()

    print("\n--- Safe Embedding Position Tests ---\n")
    test_safe_embedding_period()
    test_safe_embedding_question()
    test_safe_embedding_exclamation()
    test_safe_embedding_quoted()
    test_safe_embedding_no_punctuation()
    test_safe_embedding_multiple_punctuation()
    test_safe_embedding_with_real_signature()
    test_get_signature_position()
    test_safe_embedding_sentence_level()

    print("\n--- Cross-Compatibility Tests ---\n")
    test_vs256_does_not_interfere_with_zw()
    test_zw_does_not_interfere_with_vs256()

    print("\n--- Payload Size Comparison Tests ---\n")
    test_payload_size_comparison()
    test_payload_size_scaling()

    print("\n✅ All VS256 Crypto tests passed!")
