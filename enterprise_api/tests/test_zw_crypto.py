"""
Tests for zero-width cryptographic embedding (zw_crypto module).

Tests the new zw_embedding mode that uses only ZWSP/ZWNJ/ZWJ characters
for Word-compatible invisible signatures.
"""

import hashlib
import json
from datetime import datetime, timezone
from uuid import uuid4

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from app.utils.zw_crypto import (
    ZW_MAGIC_V1,
    ZW_MAGIC_MINI,
    CHARS_BASE4,
    ZWNJ,
    ZWJ,
    CGJ,
    MVS,
    WJ,
    ZWSP,
    encode_byte_zw,
    decode_byte_zw,
    encode_bytes_zw,
    decode_bytes_zw,
    create_zw_signature,
    verify_zw_signature,
    extract_zw_signature,
    remove_zw_signature,
    create_uuid_reference_zw,
    verify_uuid_reference_zw,
    create_minimal_signed_uuid,
    verify_minimal_signed_uuid,
    extract_minimal_signed_uuid,
    find_all_minimal_signed_uuids,
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


def test_magic_number():
    """Test magic number is unique and detectable."""
    from app.utils.zw_crypto import WJ
    
    magic = ZW_MAGIC_V1
    
    # Should be 4 characters
    assert len(magic) == 4
    
    # Should contain only Word-safe chars (no ZWSP!)
    # Magic uses WJ + base-4 chars to prevent accidental matches in encoded data
    ALLOWED_MAGIC_CHARS = CHARS_BASE4 + [WJ]
    for char in magic:
        assert char in ALLOWED_MAGIC_CHARS, f"Magic contains non-Word-safe char: U+{ord(char):04X}"
    
    # Should start with WJ (to prevent accidental matches in base-4 data)
    assert magic[0] == WJ, "Magic should start with WJ to prevent false positives"
    
    # Should be unique pattern (WJ + ZWJ + ZWNJ + CGJ)
    assert magic == WJ + ZWJ + ZWNJ + CGJ
    
    # Should be findable in text
    text = f"Hello {magic} World"
    assert magic in text
    assert text.find(magic) == 6


def test_create_zw_signature(test_keypair):
    """Test creating a ZW signature with base-4 encoding."""
    private_key, public_key = test_keypair
    
    text = "This is a test document."
    signer_id = "test_signer_001"
    
    signature = create_zw_signature(text, private_key, signer_id)
    
    # Should start with magic number
    assert signature.startswith(ZW_MAGIC_V1)
    
    # Should contain only Word-safe chars (no ZWSP!)
    # Magic uses WJ, payload uses base-4
    ALLOWED_CHARS = CHARS_BASE4 + [WJ]
    for char in signature:
        assert char in ALLOWED_CHARS, f"Non-Word-safe character: U+{ord(char):04X}"
    
    # Should be reasonable length with base-4 encoding
    # Minimum: 4 + 4 + 8 + (small payload) + 256 = ~300+ chars
    assert len(signature) > 280
    
    print(f"✓ Signature created: {len(signature)} chars (base-4, Word-safe)")


def test_verify_zw_signature(test_keypair):
    """Test verifying a ZW signature."""
    private_key, public_key = test_keypair
    
    text = "This is a test document."
    signer_id = "test_signer_001"
    metadata = {"document_id": "test_doc_001"}
    
    # Create signature
    signature = create_zw_signature(text, private_key, signer_id, metadata)
    signed_text = text + signature
    
    # Verify signature
    is_valid, payload = verify_zw_signature(signed_text, public_key)
    
    assert is_valid, "Signature should be valid"
    assert payload is not None
    assert payload["signer_id"] == signer_id
    assert "timestamp" in payload
    assert "content_hash" in payload
    assert payload["metadata"] == metadata
    
    # Verify content hash
    expected_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
    assert payload["content_hash"] == expected_hash
    
    print(f"✓ Signature verified successfully")


def test_tamper_detection(test_keypair):
    """Test that content tampering is detected."""
    private_key, public_key = test_keypair
    
    original_text = "This is the original text."
    signer_id = "test_signer_001"
    
    # Create signature
    signature = create_zw_signature(original_text, private_key, signer_id)
    signed_text = original_text + signature
    
    # Tamper with content
    tampered_text = "This is MODIFIED text." + signature
    
    # Verify should fail due to hash mismatch
    is_valid, payload = verify_zw_signature(tampered_text, public_key)
    
    assert not is_valid, "Signature should be invalid for tampered content"
    assert payload is not None
    assert payload.get("content_tampered") == True
    
    print(f"✓ Tampering detected correctly")


def test_wrong_key_verification(test_keypair):
    """Test that verification fails with wrong public key."""
    private_key, public_key = test_keypair
    
    # Generate a different keypair
    wrong_private_key = Ed25519PrivateKey.generate()
    wrong_public_key = wrong_private_key.public_key()
    
    text = "This is a test document."
    signer_id = "test_signer_001"
    
    # Create signature with first key
    signature = create_zw_signature(text, private_key, signer_id)
    signed_text = text + signature
    
    # Try to verify with wrong key
    is_valid, payload = verify_zw_signature(signed_text, wrong_public_key)
    
    assert not is_valid, "Signature should be invalid with wrong key"
    
    print(f"✓ Wrong key rejected correctly")


def test_extract_zw_signature(test_keypair):
    """Test extracting ZW signature from text."""
    private_key, public_key = test_keypair
    
    text = "This is a test document."
    signer_id = "test_signer_001"
    
    signature = create_zw_signature(text, private_key, signer_id)
    signed_text = text + signature
    
    # Extract signature
    extracted = extract_zw_signature(signed_text)
    
    assert extracted is not None
    assert extracted == signature
    
    print(f"✓ Signature extracted: {len(extracted)} chars")


def test_remove_zw_signature(test_keypair):
    """Test removing ZW signature from text."""
    private_key, public_key = test_keypair
    
    text = "This is a test document."
    signer_id = "test_signer_001"
    
    signature = create_zw_signature(text, private_key, signer_id)
    signed_text = text + signature
    
    # Remove signature
    clean_text = remove_zw_signature(signed_text)
    
    assert clean_text == text
    assert ZW_MAGIC_V1 not in clean_text
    
    print(f"✓ Signature removed, clean text recovered")


def test_uuid_reference_creation(test_keypair):
    """Test creating UUID reference with ZW signature."""
    private_key, public_key = test_keypair
    
    text = "This is a test document."
    doc_uuid = uuid4()
    signer_id = "test_signer_001"
    metadata = {"organization_id": "org_test"}
    
    # Create UUID reference
    signed_text = create_uuid_reference_zw(
        text, doc_uuid, private_key, signer_id, metadata
    )
    
    # Should contain original text
    assert text in signed_text
    
    # Should contain ZW signature
    assert ZW_MAGIC_V1 in signed_text
    
    # Should be invisible (only Word-safe chars added, no ZWSP!)
    # Magic uses WJ, payload uses base-4
    added_chars = signed_text[len(text):]
    ALLOWED_CHARS = CHARS_BASE4 + [WJ]
    for char in added_chars:
        assert char in ALLOWED_CHARS, f"Non-Word-safe char: U+{ord(char):04X}"
    
    print(f"✓ UUID reference created: {len(added_chars)} chars (Word-safe)")


def test_uuid_reference_verification(test_keypair):
    """Test verifying UUID reference."""
    private_key, public_key = test_keypair
    
    text = "This is a test document."
    doc_uuid = uuid4()
    signer_id = "test_signer_001"
    metadata = {"organization_id": "org_test"}
    
    # Create UUID reference
    signed_text = create_uuid_reference_zw(
        text, doc_uuid, private_key, signer_id, metadata
    )
    
    # Verify UUID reference
    is_valid, extracted_uuid, payload = verify_uuid_reference_zw(
        signed_text, public_key
    )
    
    if not is_valid:
        print(f"DEBUG: Verification failed")
        print(f"  is_valid: {is_valid}")
        print(f"  extracted_uuid: {extracted_uuid}")
        print(f"  payload: {payload}")
    
    assert is_valid, "UUID reference should be valid"
    assert extracted_uuid == doc_uuid
    assert payload is not None
    assert payload["signer_id"] == signer_id
    # UUID is nested in metadata
    assert payload["metadata"]["uuid"] == str(doc_uuid)
    assert payload["metadata"]["organization_id"] == metadata["organization_id"]
    
    print(f"✓ UUID reference verified: {extracted_uuid}")


def test_multiple_documents(test_keypair):
    """Test signing multiple documents with same key."""
    private_key, public_key = test_keypair
    signer_id = "test_signer_001"
    
    documents = [
        "First document content.",
        "Second document with different text.",
        "Third document is longer and has more content to sign.",
    ]
    
    signed_docs = []
    for doc in documents:
        signature = create_zw_signature(doc, private_key, signer_id)
        signed_docs.append(doc + signature)
    
    # Verify all documents
    for i, signed_doc in enumerate(signed_docs):
        is_valid, payload = verify_zw_signature(signed_doc, public_key)
        assert is_valid, f"Document {i} should be valid"
        
        # Verify content hash matches original
        clean_text = remove_zw_signature(signed_doc)
        expected_hash = hashlib.sha256(clean_text.encode('utf-8')).hexdigest()
        assert payload["content_hash"] == expected_hash
    
    print(f"✓ All {len(documents)} documents verified")


def test_signature_size_analysis(test_keypair):
    """Analyze signature sizes for different payload sizes."""
    private_key, public_key = test_keypair
    signer_id = "test_signer_001"
    
    test_cases = [
        ("Short", "Hello"),
        ("Medium", "This is a medium length document with some content."),
        ("Long", "This is a much longer document. " * 50),
    ]
    
    print("\n=== Signature Size Analysis ===")
    for name, text in test_cases:
        signature = create_zw_signature(text, private_key, signer_id)
        
        # Calculate components
        magic_size = 4
        version_size = 6
        len_size = 12
        sig_size = 64 * 6  # Ed25519 signature = 64 bytes = 384 chars
        payload_size = len(signature) - magic_size - version_size - len_size - sig_size
        
        print(f"\n{name} text ({len(text)} chars):")
        print(f"  Total signature: {len(signature)} ZW chars")
        print(f"  - Magic: {magic_size} chars")
        print(f"  - Version: {version_size} chars")
        print(f"  - Length: {len_size} chars")
        print(f"  - Payload: {payload_size} chars")
        print(f"  - Signature: {sig_size} chars")
        print(f"  Overhead: {len(signature) / len(text):.2f}x")


def test_word_compatibility():
    """
    Test that ZW signatures use only Word-compatible characters.
    
    This is a critical test - if this fails, the signature won't be
    invisible in Microsoft Word.
    
    Word-safe chars: ZWNJ (U+200C), ZWJ (U+200D), CGJ (U+034F), MVS (U+180E)
    NOT Word-safe: ZWSP (U+200B) - Word strips this!
    """
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    
    text = "This text will be tested in Microsoft Word."
    signer_id = "test_signer_001"
    
    signature = create_zw_signature(text, private_key, signer_id)
    
    # Word-safe character code points (base-4 + WJ for magic)
    word_safe_cps = {0x200C, 0x200D, 0x034F, 0x180E, 0x2060}  # ZWNJ, ZWJ, CGJ, MVS, WJ
    
    # Verify ONLY Word-safe chars (no ZWSP, no variation selectors)
    forbidden_chars = set()
    for char in signature:
        cp = ord(char)
        # Check for variation selectors
        if 0xFE00 <= cp <= 0xFE0F:  # VS1-VS16
            forbidden_chars.add(f"VS{cp - 0xFE00 + 1} (U+{cp:04X})")
        elif 0xE0100 <= cp <= 0xE01EF:  # VS17-VS256
            forbidden_chars.add(f"VS{cp - 0xE0100 + 17} (U+{cp:06X})")
        # Check for ZWSP (Word strips this!)
        elif cp == 0x200B:
            forbidden_chars.add("ZWSP (U+200B) - Word strips this!")
        # Only allow Word-safe chars
        elif cp not in word_safe_cps:
            forbidden_chars.add(f"U+{cp:04X}")
    
    assert len(forbidden_chars) == 0, (
        f"Signature contains non-Word-safe characters: {forbidden_chars}"
    )
    
    print(f"✓ Word compatibility verified: {len(signature)} chars, all Word-safe")


def test_copy_paste_preservation():
    """
    Test that signatures are preserved during copy/paste.
    
    This is a manual test - the signature should survive copy/paste
    operations in Word, Google Docs, etc.
    """
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    
    text = "Copy this text into Word and paste it back."
    signer_id = "test_signer_001"
    
    signature = create_zw_signature(text, private_key, signer_id)
    signed_text = text + signature
    
    print("\n=== Copy/Paste Test ===")
    print("1. Copy the text below:")
    print(f"\n{signed_text}\n")
    print("2. Paste into Microsoft Word")
    print("3. Copy from Word and paste back here")
    print("4. Verify signature is still present")
    print(f"\nSignature length: {len(signature)} chars")
    print(f"Total length: {len(signed_text)} chars")


# =============================================================================
# MINIMAL SIGNED UUID TESTS
# =============================================================================

def test_minimal_signed_uuid_creation(test_keypair):
    """Test creating a minimal signed UUID with base-4 encoding."""
    private_key, _ = test_keypair
    signing_key = derive_signing_key_from_private_key(private_key)
    
    sentence_uuid = uuid4()
    signature = create_minimal_signed_uuid(sentence_uuid, signing_key)
    
    # Should be exactly 132 chars (4 magic + 128 payload with base-4)
    assert len(signature) == 132, f"Expected 132 chars, got {len(signature)}"
    
    # Should start with mini magic number
    assert signature.startswith(ZW_MAGIC_MINI)
    
    # Should contain only Word-safe chars (no ZWSP!)
    # Magic uses WJ, payload uses base-4
    ALLOWED_CHARS = CHARS_BASE4 + [WJ]
    for char in signature:
        assert char in ALLOWED_CHARS, f"Non-Word-safe character: U+{ord(char):04X}"
    
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
    
    # Verify
    is_valid, extracted_uuid = verify_minimal_signed_uuid(signed_text, signing_key)
    
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


def test_minimal_signed_uuid_size_comparison():
    """Compare sizes of different signature formats."""
    private_key = Ed25519PrivateKey.generate()
    signing_key = derive_signing_key_from_private_key(private_key)
    
    text = "This is a test sentence."
    sentence_uuid = uuid4()
    
    # Minimal signed UUID
    mini_sig = create_minimal_signed_uuid(sentence_uuid, signing_key)
    
    # Full ZW signature
    full_sig = create_zw_signature(text, private_key, "test_signer")
    
    print(f"\n=== Signature Size Comparison ===")
    print(f"Minimal signed UUID: {len(mini_sig)} ZW chars ({len(mini_sig) // 6} bytes)")
    print(f"Full ZW signature:   {len(full_sig)} ZW chars (~{len(full_sig) // 6} bytes)")
    print(f"Savings: {len(full_sig) - len(mini_sig)} chars ({(1 - len(mini_sig)/len(full_sig))*100:.1f}% smaller)")
    
    # For 50 sentences
    print(f"\nFor 50 sentences:")
    print(f"  Minimal: 50 × {len(mini_sig)} = {50 * len(mini_sig):,} ZW chars")
    print(f"  Full:    50 × {len(full_sig)} = {50 * len(full_sig):,} ZW chars")


def test_minimal_signed_uuid_word_compatibility():
    """Verify minimal signed UUID uses only Word-compatible chars."""
    signing_key = b"test_signing_key_32_bytes_long!!"
    sentence_uuid = uuid4()
    
    signature = create_minimal_signed_uuid(sentence_uuid, signing_key)
    
    # Word-safe character code points (base-4 + WJ for magic)
    word_safe_cps = {0x200C, 0x200D, 0x034F, 0x180E, 0x2060}  # ZWNJ, ZWJ, CGJ, MVS, WJ
    
    # Verify ONLY Word-safe chars (no ZWSP, no variation selectors)
    forbidden = set()
    for char in signature:
        cp = ord(char)
        if 0xFE00 <= cp <= 0xFE0F:
            forbidden.add(f"VS{cp - 0xFE00 + 1}")
        elif 0xE0100 <= cp <= 0xE01EF:
            forbidden.add(f"VS{cp - 0xE0100 + 17}")
        elif cp == 0x200B:
            forbidden.add("ZWSP (U+200B) - Word strips this!")
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
    
    # Should contain the signature
    assert ZW_MAGIC_MINI in embedded, "Should contain magic number"
    
    # Verify signature is valid
    is_valid, extracted_uuid = verify_minimal_signed_uuid(embedded, signing_key)
    assert is_valid, "Signature should be valid"
    assert extracted_uuid == sentence_uuid, "UUID should match"
    
    # Clean text should match original
    sig = extract_minimal_signed_uuid(embedded)
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
    import sys
    
    print("Running ZW Crypto Tests...\n")
    
    # Generate test keypair
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    keypair = (private_key, public_key)
    
    # Run all tests
    test_encode_decode_byte()
    test_encode_decode_bytes()
    test_magic_number()
    test_create_zw_signature(keypair)
    test_verify_zw_signature(keypair)
    test_tamper_detection(keypair)
    test_wrong_key_verification(keypair)
    test_extract_zw_signature(keypair)
    test_remove_zw_signature(keypair)
    test_uuid_reference_creation(keypair)
    test_uuid_reference_verification(keypair)
    test_multiple_documents(keypair)
    test_signature_size_analysis(keypair)
    test_word_compatibility()
    
    # Minimal signed UUID tests
    print("\n--- Minimal Signed UUID Tests ---\n")
    test_minimal_signed_uuid_creation(keypair)
    test_minimal_signed_uuid_verification(keypair)
    test_minimal_signed_uuid_wrong_key(keypair)
    test_minimal_signed_uuid_tampering()
    test_minimal_signed_uuid_sentence_level()
    test_minimal_signed_uuid_size_comparison()
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
