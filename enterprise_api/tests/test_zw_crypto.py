"""
Tests for zero-width cryptographic embedding (zw_crypto module).

Tests the zw_embedding mode that uses only ZWNJ/ZWJ/CGJ/MVS characters
for Word-compatible invisible signatures.

Note: Full-document signing functions (create_zw_signature, verify_zw_signature, etc.)
were removed as they used magic numbers which don't work in Microsoft Word.
Only minimal signed UUID functions (contiguous sequence detection) are supported.
"""

from uuid import uuid4

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from app.utils.zw_crypto import (
    CHARS_BASE4,
    CHARS_BASE4_SET,
    ZWNJ,
    ZWJ,
    CGJ,
    MVS,
    encode_byte_zw,
    decode_byte_zw,
    encode_bytes_zw,
    decode_bytes_zw,
    create_minimal_signed_uuid,
    verify_minimal_signed_uuid,
    extract_minimal_signed_uuid,
    find_all_minimal_signed_uuids,
    embed_signature_safely,
    get_signature_position,
    derive_signing_key_from_private_key,
    create_safely_embedded_sentence,
)

# ZWSP for tampering tests (this char is stripped by Word)
ZWSP = "\u200B"


@pytest.fixture
def test_keypair():
    """Generate a test Ed25519 keypair."""
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    return private_key, public_key


def test_encode_decode_byte():
    """Test byte encoding/decoding roundtrip with base-4."""
    test_values = [0, 1, 2, 3, 15, 16, 127, 128, 255]
    
    for value in test_values:
        encoded = encode_byte_zw(value)
        decoded = decode_byte_zw(encoded)
        
        assert decoded == value, f"Roundtrip failed: {value} -> {encoded} -> {decoded}"
        assert len(encoded) == 4, f"Encoded length should be 4 (base-4), got {len(encoded)}"
        
        # Verify all chars are Word-safe (ZWNJ, ZWJ, CGJ, MVS)
        for char in encoded:
            assert char in CHARS_BASE4, f"Invalid character: U+{ord(char):04X}"


def test_encode_decode_bytes():
    """Test multi-byte encoding/decoding with base-4."""
    test_data = [
        b"Hello",
        b"\x00\x01\x02\xff\xfe",
        b"The quick brown fox",
        bytes(range(256)),  # All possible byte values
    ]
    
    for data in test_data:
        encoded = encode_bytes_zw(data)
        decoded = decode_bytes_zw(encoded)
        
        assert decoded == data, f"Roundtrip failed for {len(data)} bytes"
        assert len(encoded) == len(data) * 4, f"Encoded length should be {len(data) * 4}"
        
        # Verify all chars are Word-safe
        for char in encoded:
            assert char in CHARS_BASE4


# =============================================================================
# MINIMAL SIGNED UUID TESTS
# =============================================================================
# Note: Full-document signing tests (test_magic_number, test_create_zw_signature,
# test_verify_zw_signature, etc.) were removed as those functions used magic
# numbers which don't work in Microsoft Word (WJ appears as visible space).
# =============================================================================


def test_minimal_signed_uuid_creation(test_keypair):
    """Test creating a minimal signed UUID with base-4 encoding (no magic number)."""
    private_key, _ = test_keypair
    signing_key = derive_signing_key_from_private_key(private_key)
    
    sentence_uuid = uuid4()
    signature = create_minimal_signed_uuid(sentence_uuid, signing_key)
    
    # Should be exactly 128 chars (no magic number, just UUID + HMAC)
    assert len(signature) == 128, f"Expected 128 chars, got {len(signature)}"
    
    # Should contain only Word-safe base-4 chars (no ZWSP, no WJ!)
    for char in signature:
        assert char in CHARS_BASE4, f"Non-Word-safe character: U+{ord(char):04X}"
    
    print(f"✓ Minimal signed UUID created: {len(signature)} chars (base-4, Word-safe)")


def test_minimal_signed_uuid_verification(test_keypair):
    """Test verifying a minimal signed UUID."""
    private_key, _ = test_keypair
    signing_key = derive_signing_key_from_private_key(private_key)
    
    sentence_uuid = uuid4()
    signature = create_minimal_signed_uuid(sentence_uuid, signing_key)
    
    # Embed in text
    text = "This is a test sentence."
    signed_text = text + signature
    
    # Extract signature from text first (verify_minimal_signed_uuid expects exactly 128 chars)
    extracted_sig = extract_minimal_signed_uuid(signed_text)
    assert extracted_sig is not None, "Should find signature in text"
    
    # Verify the extracted signature
    is_valid, extracted_uuid = verify_minimal_signed_uuid(extracted_sig, signing_key)
    
    assert is_valid, "Signature should be valid"
    assert extracted_uuid == sentence_uuid, "UUID should match"
    
    print(f"✓ Minimal signed UUID verified: {extracted_uuid}")


def test_minimal_signed_uuid_wrong_key(test_keypair):
    """Test that wrong signing key fails verification."""
    private_key, _ = test_keypair
    signing_key = derive_signing_key_from_private_key(private_key)
    
    # Create with correct key
    sentence_uuid = uuid4()
    signature = create_minimal_signed_uuid(sentence_uuid, signing_key)
    signed_text = "Test sentence." + signature
    
    # Try to verify with wrong key
    wrong_key = b"wrong_key_" * 4  # 40 bytes
    is_valid, _ = verify_minimal_signed_uuid(signed_text, wrong_key)
    
    assert not is_valid, "Should fail with wrong key"
    
    print(f"✓ Wrong key rejected correctly")


def test_minimal_signed_uuid_tampering():
    """Test that tampering with UUID is detected."""
    signing_key = b"test_signing_key_32_bytes_long!!"
    
    sentence_uuid = uuid4()
    signature = create_minimal_signed_uuid(sentence_uuid, signing_key)
    
    # Tamper with one character in the signature
    tampered = signature[:10] + ZWSP + signature[11:]  # Change one char
    
    is_valid, _ = verify_minimal_signed_uuid(tampered, signing_key)
    
    assert not is_valid, "Should detect tampering"
    
    print(f"✓ Tampering detected correctly")


def test_minimal_signed_uuid_sentence_level():
    """Test sentence-level embedding with minimal signed UUIDs."""
    signing_key = b"test_signing_key_32_bytes_long!!"
    
    sentences = [
        "This is the first sentence.",
        "Here is another sentence with more content.",
        "The third sentence concludes the paragraph.",
    ]
    
    # Create signed UUIDs for each sentence
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
    
    print(f"✓ Sentence-level embedding: {len(sentences)} sentences")
    print(f"  Original: {original_len} chars")
    print(f"  With signatures: {total_len} chars")
    print(f"  Overhead: {overhead} ZW chars ({overhead / len(sentences):.0f} per sentence)")


def test_minimal_signed_uuid_word_compatibility():
    """Verify minimal signed UUID uses only Word-compatible chars (no magic, no WJ)."""
    signing_key = b"test_signing_key_32_bytes_long!!"
    sentence_uuid = uuid4()
    
    signature = create_minimal_signed_uuid(sentence_uuid, signing_key)
    
    # Word-safe character code points (base-4 only, no WJ since it appears as space in Word)
    word_safe_cps = {0x200C, 0x200D, 0x034F, 0x180E}  # ZWNJ, ZWJ, CGJ, MVS
    
    # Verify ONLY Word-safe chars (no ZWSP, no WJ, no variation selectors)
    forbidden = set()
    for char in signature:
        cp = ord(char)
        if 0xFE00 <= cp <= 0xFE0F:
            forbidden.add(f"VS{cp - 0xFE00 + 1}")
        elif 0xE0100 <= cp <= 0xE01EF:
            forbidden.add(f"VS{cp - 0xE0100 + 17}")
        elif cp == 0x200B:
            forbidden.add("ZWSP (U+200B) - Word strips this!")
        elif cp == 0x2060:
            forbidden.add("WJ (U+2060) - Appears as space in Word!")
        elif cp not in word_safe_cps:
            forbidden.add(f"U+{cp:04X}")
    
    assert len(forbidden) == 0, f"Found non-Word-safe chars: {forbidden}"
    
    print(f"✓ Word compatibility verified: {len(signature)} chars, all Word-safe")


# =============================================================================
# SAFE EMBEDDING POSITION TESTS
# =============================================================================

def test_safe_embedding_period():
    """Test embedding before period."""
    signature = "[SIG]"  # Placeholder for testing
    
    result = embed_signature_safely("Hello world.", signature)
    assert result == "Hello world[SIG].", f"Got: {result}"
    
    print("✓ Safe embedding before period")


def test_safe_embedding_question():
    """Test embedding before question mark."""
    signature = "[SIG]"
    
    result = embed_signature_safely("What time is it?", signature)
    assert result == "What time is it[SIG]?", f"Got: {result}"
    
    print("✓ Safe embedding before question mark")


def test_safe_embedding_exclamation():
    """Test embedding before exclamation mark."""
    signature = "[SIG]"
    
    result = embed_signature_safely("Wow!", signature)
    assert result == "Wow[SIG]!", f"Got: {result}"
    
    print("✓ Safe embedding before exclamation mark")


def test_safe_embedding_quoted():
    """Test embedding before quoted punctuation."""
    signature = "[SIG]"
    
    # Period inside quotes
    result = embed_signature_safely('She said "Hello."', signature)
    assert result == 'She said "Hello[SIG]."', f"Got: {result}"
    
    # Question with closing quote
    result2 = embed_signature_safely('Did she say "Yes"?', signature)
    assert result2 == 'Did she say "Yes[SIG]"?', f"Got: {result2}"
    
    print("✓ Safe embedding with quotes")


def test_safe_embedding_no_punctuation():
    """Test embedding when no terminal punctuation."""
    signature = "[SIG]"
    
    result = embed_signature_safely("No punctuation here", signature)
    assert result == "No punctuation here[SIG]", f"Got: {result}"
    
    print("✓ Safe embedding without punctuation (appends at end)")


def test_safe_embedding_multiple_punctuation():
    """Test embedding with multiple trailing punctuation."""
    signature = "[SIG]"
    
    # Multiple punctuation marks
    result = embed_signature_safely("Really?!", signature)
    assert result == "Really[SIG]?!", f"Got: {result}"
    
    # Ellipsis-like
    result2 = embed_signature_safely("Wait...", signature)
    assert result2 == "Wait[SIG]...", f"Got: {result2}"
    
    print("✓ Safe embedding with multiple punctuation")


def test_safe_embedding_with_real_signature():
    """Test safe embedding with actual minimal signed UUID."""
    signing_key = b"test_signing_key_32_bytes_long!!"
    sentence_uuid = uuid4()
    
    sentence = "This is a test sentence."
    embedded = create_safely_embedded_sentence(sentence, sentence_uuid, signing_key)
    
    # Should end with period (signature before it)
    assert embedded.endswith("."), f"Should end with period, got: ...{embedded[-10:]}"
    
    # Should contain the signature (detected via contiguous sequence detection)
    found_sigs = find_all_minimal_signed_uuids(embedded)
    assert len(found_sigs) > 0, "Should contain signature"
    
    # Extract and verify signature (verify expects exactly 128 chars)
    sig = extract_minimal_signed_uuid(embedded)
    assert sig is not None, "Should extract signature"
    is_valid, extracted_uuid = verify_minimal_signed_uuid(sig, signing_key)
    assert is_valid, "Signature should be valid"
    assert extracted_uuid == sentence_uuid, "UUID should match"
    
    # Clean text should match original
    clean = embedded.replace(sig, '')
    assert clean == sentence, f"Clean text should match original: {clean}"
    
    print(f"✓ Safe embedding with real signature verified")


def test_get_signature_position():
    """Test getting signature position for various texts."""
    test_cases = [
        ("Hello world.", 11),  # Before period
        ("What?", 4),          # Before question mark
        ("Wow!", 3),           # Before exclamation
        ('Say "Hi."', 7),      # Before quote+period
        ("No punct", 8),       # At end (no punctuation)
        ("", 0),               # Empty string
        ("...", 0),            # All punctuation
    ]
    
    for text, expected_pos in test_cases:
        pos = get_signature_position(text)
        assert pos == expected_pos, f"For '{text}': expected {expected_pos}, got {pos}"
    
    print("✓ Signature position calculation correct")


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
    
    # Join into document
    document = " ".join(embedded_sentences)
    
    # Find all signatures
    found = find_all_minimal_signed_uuids(document)
    assert len(found) == 4, f"Should find 4 signatures, found {len(found)}"
    
    # Verify each
    for i, (start, end, sig) in enumerate(found):
        is_valid, extracted_uuid = verify_minimal_signed_uuid(sig, signing_key)
        assert is_valid, f"Signature {i} should be valid"
        assert extracted_uuid == uuids[i], f"UUID {i} should match"
    
    print(f"✓ Safe embedding sentence-level: {len(sentences)} sentences verified")


if __name__ == "__main__":
    # Run tests
    print("Running ZW Crypto Tests...\n")
    
    # Generate test keypair
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    keypair = (private_key, public_key)
    
    # Base encoding tests
    print("--- Base-4 Encoding Tests ---\n")
    test_encode_decode_byte()
    test_encode_decode_bytes()
    
    # Minimal signed UUID tests (contiguous sequence detection, no magic)
    print("\n--- Minimal Signed UUID Tests ---\n")
    test_minimal_signed_uuid_creation(keypair)
    test_minimal_signed_uuid_verification(keypair)
    test_minimal_signed_uuid_wrong_key(keypair)
    test_minimal_signed_uuid_tampering()
    test_minimal_signed_uuid_sentence_level()
    test_minimal_signed_uuid_word_compatibility()
    
    # Safe embedding tests
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
    
    print("\n✅ All tests passed!")
