#!/usr/bin/env python3
"""
Interactive Word Compatibility Test

This script creates a test sentence with minimal signed UUID that you can:
1. Copy from terminal
2. Paste into Microsoft Word
3. Copy from Word
4. Paste back into terminal
5. Verify signature survives (or detect tampering)

Usage:
    uv run python tests/interactive_word_test.py
"""

import sys
from uuid import uuid4

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from app.utils.zw_crypto import (
    create_safely_embedded_sentence,
    derive_signing_key_from_private_key,
    extract_minimal_signed_uuid,
    verify_minimal_signed_uuid,
)


def create_test_sentence():
    """Create a test sentence with embedded signature."""
    # Generate test key
    private_key = Ed25519PrivateKey.generate()
    signing_key = derive_signing_key_from_private_key(private_key)
    
    # Create test sentence
    sentence = "This is a test sentence for Word compatibility."
    sentence_uuid = uuid4()
    
    # Embed signature safely (before period)
    signed_sentence = create_safely_embedded_sentence(sentence, sentence_uuid, signing_key)
    
    return signed_sentence, signing_key, sentence_uuid, sentence


def verify_sentence(text, signing_key, original_uuid, original_sentence):
    """Verify a sentence and report results."""
    print("\n" + "="*70)
    print("VERIFICATION RESULTS")
    print("="*70)
    
    # Try to extract signature
    sig = extract_minimal_signed_uuid(text)
    if not sig:
        print("❌ FAILED: No signature found in text")
        print("   The signature was completely removed or corrupted.")
        return False
    
    print(f"✓ Signature found ({len(sig)} chars)")
    
    # Verify signature
    is_valid, extracted_uuid = verify_minimal_signed_uuid(text, signing_key)
    
    if not is_valid:
        print("❌ FAILED: Signature verification failed")
        print("   The signature was tampered with or uses wrong key.")
        return False
    
    print("✓ Signature cryptographically valid")
    
    # Check UUID matches
    if extracted_uuid != original_uuid:
        print(f"❌ FAILED: UUID mismatch")
        print(f"   Expected: {original_uuid}")
        print(f"   Got:      {extracted_uuid}")
        return False
    
    print(f"✓ UUID matches: {extracted_uuid}")
    
    # Check text content
    clean_text = text.replace(sig, '')
    if clean_text == original_sentence:
        print("✓ Text content unchanged")
    else:
        print("⚠️  WARNING: Text content was modified")
        print(f"   Original: {original_sentence}")
        print(f"   Current:  {clean_text}")
    
    print("\n" + "="*70)
    print("✅ SIGNATURE SURVIVED - All checks passed!")
    print("="*70)
    return True


def main():
    print("\n" + "="*70)
    print("ZERO-WIDTH SIGNATURE - WORD COMPATIBILITY TEST")
    print("="*70)
    print("\nThis test verifies that minimal signed UUIDs survive copy/paste")
    print("through Microsoft Word and other editors.\n")
    
    # Create test sentence
    signed_sentence, signing_key, sentence_uuid, original_sentence = create_test_sentence()
    
    print("Step 1: COPY THE TEXT BELOW")
    print("-" * 70)
    print(signed_sentence)
    print("-" * 70)
    print("\nThe text above contains an invisible 196-character signature")
    print("embedded BEFORE the period (safe positioning).\n")
    
    print("Step 2: PASTE INTO MICROSOFT WORD")
    print("   - Open Microsoft Word")
    print("   - Paste the text (Ctrl+V / Cmd+V)")
    print("   - Verify it looks normal (no □ boxes)")
    print("   - You can edit the text if you want to test tampering\n")
    
    print("Step 3: COPY FROM WORD")
    print("   - Select all the text in Word")
    print("   - Copy it (Ctrl+C / Cmd+C)\n")
    
    print("Step 4: PASTE BACK HERE AND PRESS ENTER")
    print("-" * 70)
    
    try:
        # Read pasted text from user
        pasted_text = input()
        
        # Verify
        verify_sentence(pasted_text, signing_key, sentence_uuid, original_sentence)
        
    except KeyboardInterrupt:
        print("\n\nTest cancelled.")
        sys.exit(0)
    except EOFError:
        print("\n\nNo input received.")
        sys.exit(1)


if __name__ == "__main__":
    main()
