#!/usr/bin/env python3
"""
Test Word Joiner (U+2060) as replacement for ZWSP in base-3 encoding.

This tests if Word preserves Word Joiner character during copy/paste.
"""

from uuid import uuid4
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
import hashlib

# Word-safe base-3 characters
ZWNJ = "\u200C"  # 0
ZWJ = "\u200D"   # 1
WJ = "\u2060"    # 2 (Word Joiner - replacement for ZWSP)

# Magic number using Word-safe chars
MAGIC_WORD_SAFE = ZWJ + ZWNJ + ZWJ + WJ


def encode_byte_word_safe(byte_value: int) -> str:
    """Encode byte using ZWNJ/ZWJ/WJ (base-3, Word-safe)."""
    if not 0 <= byte_value <= 255:
        raise ValueError(f"Byte value must be 0-255, got {byte_value}")
    
    result = []
    value = byte_value
    
    for _ in range(6):
        digit = value % 3
        result.append([ZWNJ, ZWJ, WJ][digit])
        value //= 3
    
    return ''.join(result)


def decode_byte_word_safe(encoded: str) -> int:
    """Decode Word-safe base-3 encoded byte."""
    if len(encoded) != 6:
        raise ValueError(f"Expected 6 characters, got {len(encoded)}")
    
    value = 0
    multiplier = 1
    
    for char in encoded:
        if char == ZWNJ:
            digit = 0
        elif char == ZWJ:
            digit = 1
        elif char == WJ:
            digit = 2
        else:
            raise ValueError(f"Invalid character: U+{ord(char):04X}")
        
        value += digit * multiplier
        multiplier *= 3
    
    return value


def create_test_signature_word_safe(uuid_bytes: bytes) -> str:
    """Create minimal signature using Word-safe encoding."""
    # Simple HMAC for testing
    signing_key = b"test_key_32_bytes_long_padding!!"
    
    from cryptography.hazmat.primitives import hashes, hmac as crypto_hmac
    from cryptography.hazmat.backends import default_backend
    
    h = crypto_hmac.HMAC(signing_key, hashes.SHA256(), backend=default_backend())
    h.update(uuid_bytes)
    hmac_truncated = h.finalize()[:16]
    
    # Encode UUID + HMAC
    payload = uuid_bytes + hmac_truncated  # 32 bytes
    encoded = ''.join(encode_byte_word_safe(b) for b in payload)
    
    return MAGIC_WORD_SAFE + encoded  # 4 + 192 = 196 chars


def main():
    print("\n" + "="*70)
    print("WORD JOINER (U+2060) COMPATIBILITY TEST")
    print("="*70)
    print("\nTesting if Word Joiner survives Word copy/paste...\n")
    
    # Create test signature
    test_uuid = uuid4()
    signature = create_test_signature_word_safe(test_uuid.bytes)
    
    # Create test sentence
    sentence = "This is a test sentence for Word compatibility."
    # Insert before period (safe positioning)
    signed_sentence = sentence[:-1] + signature + sentence[-1]
    
    print("Character breakdown:")
    print(f"  ZWNJ (U+200C): {signed_sentence.count(ZWNJ)}")
    print(f"  ZWJ  (U+200D): {signed_sentence.count(ZWJ)}")
    print(f"  WJ   (U+2060): {signed_sentence.count(WJ)}")
    print(f"  Total ZW:      {signed_sentence.count(ZWNJ) + signed_sentence.count(ZWJ) + signed_sentence.count(WJ)}")
    
    print("\nStep 1: COPY THE TEXT BELOW")
    print("-" * 70)
    print(signed_sentence)
    print("-" * 70)
    
    print("\nStep 2: PASTE INTO MICROSOFT WORD")
    print("   - Open Word, paste the text")
    print("   - Verify it looks normal")
    
    print("\nStep 3: COPY FROM WORD AND PASTE BACK HERE")
    print("-" * 70)
    
    try:
        pasted = input()
        
        print("\n" + "="*70)
        print("ANALYSIS")
        print("="*70)
        
        orig_zwnj = signed_sentence.count(ZWNJ)
        orig_zwj = signed_sentence.count(ZWJ)
        orig_wj = signed_sentence.count(WJ)
        
        past_zwnj = pasted.count(ZWNJ)
        past_zwj = pasted.count(ZWJ)
        past_wj = pasted.count(WJ)
        
        print(f"\nOriginal counts:")
        print(f"  ZWNJ: {orig_zwnj}")
        print(f"  ZWJ:  {orig_zwj}")
        print(f"  WJ:   {orig_wj}")
        
        print(f"\nAfter Word:")
        print(f"  ZWNJ: {past_zwnj} ({'+' if past_zwnj >= orig_zwnj else ''}{past_zwnj - orig_zwnj})")
        print(f"  ZWJ:  {past_zwj} ({'+' if past_zwj >= orig_zwj else ''}{past_zwj - orig_zwj})")
        print(f"  WJ:   {past_wj} ({'+' if past_wj >= orig_wj else ''}{past_wj - orig_wj})")
        
        if past_zwnj == orig_zwnj and past_zwj == orig_zwj and past_wj == orig_wj:
            print("\n✅ SUCCESS: All characters preserved!")
            print("   Word Joiner (U+2060) survives Word copy/paste!")
        elif past_wj == 0:
            print("\n❌ FAILED: Word stripped Word Joiner (U+2060)")
            print("   Need to try a different character")
        else:
            print("\n⚠️  PARTIAL: Some characters lost")
            print(f"   Lost {(orig_zwnj + orig_zwj + orig_wj) - (past_zwnj + past_zwj + past_wj)} chars")
        
    except (KeyboardInterrupt, EOFError):
        print("\nTest cancelled")


if __name__ == "__main__":
    main()
