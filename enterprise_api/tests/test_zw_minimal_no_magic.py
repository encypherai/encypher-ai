#!/usr/bin/env python3
"""
Tests for ZW embedding with contiguous sequence detection (no magic numbers).

This tests the new approach where signatures are detected by finding
128 contiguous base-4 characters, eliminating the need for magic numbers.
"""

from uuid import uuid4
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from app.utils.zw_crypto import (
    CHARS_BASE4,
    CHARS_BASE4_SET,
    ZWNJ,
    ZWJ,
    CGJ,
    MVS,
    create_minimal_signed_uuid,
    verify_minimal_signed_uuid,
    find_all_minimal_signed_uuids,
    derive_signing_key_from_private_key,
    create_safely_embedded_sentence,
)


def test_signature_size():
    """Test that signatures are exactly 128 chars (no magic number)."""
    private_key = Ed25519PrivateKey.generate()
    signing_key = derive_signing_key_from_private_key(private_key)
    
    sentence_uuid = uuid4()
    signature = create_minimal_signed_uuid(sentence_uuid, signing_key)
    
    assert len(signature) == 128, f"Expected 128 chars, got {len(signature)}"
    
    # Verify all chars are base-4
    for char in signature:
        assert char in CHARS_BASE4_SET, f"Non-base-4 char: U+{ord(char):04X}"
    
    print(f"✓ Signature size: 128 chars (no magic number)")


def test_contiguous_detection():
    """Test that signatures are found by contiguous sequence detection."""
    private_key = Ed25519PrivateKey.generate()
    signing_key = derive_signing_key_from_private_key(private_key)
    
    # Create 3 sentences with signatures
    sentences = [
        "First sentence.",
        "Second sentence!",
        "Third sentence?",
    ]
    
    uuids = []
    signed_sentences = []
    
    for sentence in sentences:
        uuid = uuid4()
        uuids.append(uuid)
        sig = create_minimal_signed_uuid(uuid, signing_key)
        signed_sentences.append(sentence + sig)
    
    full_text = " ".join(signed_sentences)
    
    # Find signatures using contiguous detection
    found = find_all_minimal_signed_uuids(full_text)
    
    assert len(found) == 3, f"Expected 3 signatures, found {len(found)}"
    
    # Verify each signature
    for i, (start, end, sig) in enumerate(found):
        assert len(sig) == 128, f"Signature {i+1} wrong length: {len(sig)}"
        is_valid, recovered_uuid = verify_minimal_signed_uuid(sig, signing_key)
        assert is_valid, f"Signature {i+1} invalid"
        assert recovered_uuid in uuids, f"Signature {i+1} UUID not found"
    
    print(f"✓ Contiguous detection: 3/3 signatures found and verified")


def test_word_safe_chars_only():
    """Test that only Word-safe characters are used (no WJ, no ZWSP)."""
    private_key = Ed25519PrivateKey.generate()
    signing_key = derive_signing_key_from_private_key(private_key)
    
    sentence_uuid = uuid4()
    signature = create_minimal_signed_uuid(sentence_uuid, signing_key)
    
    # Check for forbidden characters
    ZWSP = '\u200B'  # Stripped by Word
    WJ = '\u2060'    # Appears as space in Word
    
    for char in signature:
        assert char != ZWSP, "Found ZWSP (Word strips this!)"
        assert char != WJ, "Found WJ (appears as space in Word!)"
        assert char in CHARS_BASE4_SET, f"Non-base-4 char: U+{ord(char):04X}"
    
    print(f"✓ Word-safe: Only ZWNJ, ZWJ, CGJ, MVS (no ZWSP, no WJ)")


def test_no_false_positives():
    """Test that natural text doesn't trigger false positives."""
    private_key = Ed25519PrivateKey.generate()
    signing_key = derive_signing_key_from_private_key(private_key)
    
    # Natural text without signatures
    natural_text = "This is normal text. It has multiple sentences! No invisible characters?"
    
    found = find_all_minimal_signed_uuids(natural_text)
    assert len(found) == 0, f"False positive: found {len(found)} signatures in natural text"
    
    # Text with some base-4 chars but not 128 contiguous
    text_with_few = "Hello" + ZWNJ * 50 + "World"
    found = find_all_minimal_signed_uuids(text_with_few)
    assert len(found) == 0, f"False positive: found {len(found)} signatures with only 50 chars"
    
    print(f"✓ No false positives in natural text")


def test_multiple_signatures():
    """Test handling of multiple signatures in one document."""
    private_key = Ed25519PrivateKey.generate()
    signing_key = derive_signing_key_from_private_key(private_key)
    
    # Create 5 sentences
    num_sentences = 5
    uuids = []
    text_parts = []
    
    for i in range(num_sentences):
        sentence = f"Sentence {i+1} with signature."
        uuid = uuid4()
        uuids.append(uuid)
        sig = create_minimal_signed_uuid(uuid, signing_key)
        text_parts.append(sentence + sig)
    
    full_text = " ".join(text_parts)
    
    # Find all signatures
    found = find_all_minimal_signed_uuids(full_text)
    assert len(found) == num_sentences, f"Expected {num_sentences}, found {len(found)}"
    
    # Verify all
    verified = 0
    for start, end, sig in found:
        is_valid, recovered_uuid = verify_minimal_signed_uuid(sig, signing_key)
        if is_valid and recovered_uuid in uuids:
            verified += 1
    
    assert verified == num_sentences, f"Only {verified}/{num_sentences} verified"
    
    print(f"✓ Multiple signatures: {num_sentences}/{num_sentences} found and verified")


def test_safe_embedding():
    """Test safe embedding before terminal punctuation."""
    private_key = Ed25519PrivateKey.generate()
    signing_key = derive_signing_key_from_private_key(private_key)
    
    test_cases = [
        ("Hello world.", "Hello world", "."),
        ("What time?", "What time", "?"),
        ("Amazing!", "Amazing", "!"),
        ('She said "Hello."', 'She said "Hello', '."'),
    ]
    
    for original, expected_prefix, expected_suffix in test_cases:
        uuid = uuid4()
        embedded = create_safely_embedded_sentence(original, uuid, signing_key)
        
        # Signature should be before terminal punctuation
        assert embedded.startswith(expected_prefix), f"Prefix mismatch: {embedded[:20]}"
        assert embedded.endswith(expected_suffix), f"Suffix mismatch: {embedded[-5:]}"
        
        # Should contain exactly 128 invisible chars
        invisible_count = sum(1 for c in embedded if c in CHARS_BASE4_SET)
        assert invisible_count == 128, f"Expected 128 invisible chars, got {invisible_count}"
    
    print(f"✓ Safe embedding: signatures placed before terminal punctuation")


if __name__ == "__main__":
    print("=" * 80)
    print("ZW EMBEDDING TESTS (No Magic Numbers, Contiguous Detection)")
    print("=" * 80)
    
    test_signature_size()
    test_contiguous_detection()
    test_word_safe_chars_only()
    test_no_false_positives()
    test_multiple_signatures()
    test_safe_embedding()
    
    print("\n" + "=" * 80)
    print("✅ ALL TESTS PASSED")
    print("=" * 80)
    print("\nKey Features:")
    print("  - 128 chars per signature (no magic number)")
    print("  - Contiguous sequence detection (no false positives)")
    print("  - Word-compatible (ZWNJ, ZWJ, CGJ, MVS only)")
    print("  - No WJ (appears as space in Word)")
    print("  - No ZWSP (stripped by Word)")
