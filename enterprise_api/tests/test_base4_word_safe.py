#!/usr/bin/env python3
"""
Test Base-4 encoding using ONLY Word-safe characters (no ZWSP).

Uses: ZWNJ, ZWJ, CGJ, MVS
Avoids: ZWSP (which Word strips)

This should give us 33% size reduction while being Word-compatible.
"""

import sys
from uuid import uuid4
from cryptography.hazmat.primitives import hashes, hmac as crypto_hmac
from cryptography.hazmat.backends import default_backend


# Base-4 Word-safe characters (NO ZWSP!)
ZWNJ = "\u200C"  # 0
ZWJ = "\u200D"   # 1
CGJ = "\u034F"   # 2
MVS = "\u180E"   # 3

CHARS_BASE4_SAFE = [ZWNJ, ZWJ, CGJ, MVS]

# Magic number (no ZWSP)
MAGIC_BASE4_SAFE = ZWJ + ZWNJ + ZWJ + CGJ


def encode_byte_base4_safe(byte_value: int) -> str:
    """Encode byte using base-4 (Word-safe, no ZWSP)."""
    if not 0 <= byte_value <= 255:
        raise ValueError(f"Byte value must be 0-255, got {byte_value}")
    
    result = []
    value = byte_value
    
    # 4^4 = 256, so 4 chars per byte
    for _ in range(4):
        digit = value % 4
        result.append(CHARS_BASE4_SAFE[digit])
        value //= 4
    
    return ''.join(result)


def decode_byte_base4_safe(encoded: str) -> int:
    """Decode base-4 Word-safe encoded byte."""
    if len(encoded) != 4:
        raise ValueError(f"Expected 4 characters, got {len(encoded)}")
    
    value = 0
    multiplier = 1
    
    for char in encoded:
        if char == ZWNJ:
            digit = 0
        elif char == ZWJ:
            digit = 1
        elif char == CGJ:
            digit = 2
        elif char == MVS:
            digit = 3
        else:
            raise ValueError(f"Invalid character: U+{ord(char):04X}")
        
        value += digit * multiplier
        multiplier *= 4
    
    return value


def create_test_signature_base4_safe(uuid_bytes: bytes) -> str:
    """Create minimal signature using base-4 Word-safe encoding."""
    signing_key = b"test_key_32_bytes_long_padding!!"
    
    h = crypto_hmac.HMAC(signing_key, hashes.SHA256(), backend=default_backend())
    h.update(uuid_bytes)
    hmac_truncated = h.finalize()[:16]
    
    # Encode UUID + HMAC (32 bytes)
    payload = uuid_bytes + hmac_truncated
    encoded = ''.join(encode_byte_base4_safe(b) for b in payload)
    
    return MAGIC_BASE4_SAFE + encoded  # 4 + 128 = 132 chars


def main():
    print("\n" + "="*70)
    print("BASE-4 WORD-SAFE ENCODING TEST")
    print("="*70)
    print("\nCharacters used (NO ZWSP):")
    print("  0 = ZWNJ (U+200C) - Zero-Width Non-Joiner")
    print("  1 = ZWJ  (U+200D) - Zero-Width Joiner")
    print("  2 = CGJ  (U+034F) - Combining Grapheme Joiner")
    print("  3 = MVS  (U+180E) - Mongolian Vowel Separator")
    print("\nSignature size: 132 chars (33% smaller than base-3)")
    print("For 50 sentences: 6,600 chars (vs 9,800 with base-3)")
    
    # Test encoding/decoding
    print("\n" + "="*70)
    print("ENCODING TEST")
    print("="*70)
    
    test_values = [0, 1, 127, 128, 255]
    print("\nByte encoding roundtrip test:")
    for val in test_values:
        encoded = encode_byte_base4_safe(val)
        decoded = decode_byte_base4_safe(encoded)
        status = "✅" if decoded == val else "❌"
        print(f"  {val:3d} → {len(encoded)} chars → {decoded:3d} {status}")
    
    # Create test signature
    print("\n" + "="*70)
    print("WORD COMPATIBILITY TEST")
    print("="*70)
    
    test_uuid = uuid4()
    signature = create_test_signature_base4_safe(test_uuid.bytes)
    
    print(f"\nSignature created: {len(signature)} chars")
    print(f"  Magic: {len(MAGIC_BASE4_SAFE)} chars")
    print(f"  Payload: {len(signature) - len(MAGIC_BASE4_SAFE)} chars")
    
    # Character breakdown
    zwsp_char = '\u200B'
    print("\nCharacter counts:")
    print(f"  ZWNJ (U+200C): {signature.count(ZWNJ)}")
    print(f"  ZWJ  (U+200D): {signature.count(ZWJ)}")
    print(f"  CGJ  (U+034F): {signature.count(CGJ)}")
    print(f"  MVS  (U+180E): {signature.count(MVS)}")
    print(f"  ZWSP (U+200B): {signature.count(zwsp_char)} (should be 0!)")
    
    # Create test sentence
    sentence = "This is a base-4 Word-safe test sentence"
    signed_sentence = sentence[:-1] + signature + sentence[-1] + "."
    
    print("\n" + "="*70)
    print("COPY THE TEXT BELOW:")
    print("="*70)
    print(signed_sentence)
    print("="*70)
    
    print("\nInstructions:")
    print("1. Copy the text above")
    print("2. Paste into Microsoft Word")
    print("3. Verify it looks normal (no visible gaps)")
    print("4. Copy from Word")
    print("5. Paste back here and press ENTER")
    print("-" * 70)
    
    try:
        pasted = input()
        
        print("\n" + "="*70)
        print("ANALYSIS")
        print("="*70)
        
        # Check signature
        if signature in pasted:
            print("✅ COMPLETE SIGNATURE SURVIVED")
        else:
            print("❌ Signature was modified or stripped")
        
        # Check character counts
        print("\nCharacter preservation:")
        chars_ok = True
        for char, name in [(ZWNJ, "ZWNJ"), (ZWJ, "ZWJ"), (CGJ, "CGJ"), (MVS, "MVS")]:
            orig = signed_sentence.count(char)
            past = pasted.count(char)
            
            if past == orig:
                status = "✅"
            elif past == 0:
                status = "❌ STRIPPED"
                chars_ok = False
            else:
                status = f"⚠️  PARTIAL ({past}/{orig})"
                chars_ok = False
            
            print(f"  {name} (U+{ord(char):04X}): {orig} → {past} {status}")
        
        # Check for ZWSP contamination
        zwsp_char = '\u200B'
        zwsp_count = pasted.count(zwsp_char)
        if zwsp_count > 0:
            print(f"  ⚠️  WARNING: Found {zwsp_count} ZWSP chars (should be 0!)")
        
        # Final verdict
        print("\n" + "="*70)
        if signature in pasted and chars_ok:
            print("✅ BASE-4 WORD-SAFE ENCODING: FULLY COMPATIBLE")
            print(f"   Signature size: {len(signature)} chars")
            print("   33% smaller than base-3, Word-compatible!")
        elif chars_ok:
            print("⚠️  Characters preserved but signature modified")
        else:
            print("❌ NOT COMPATIBLE - some characters were stripped")
        print("="*70)
        
    except (KeyboardInterrupt, EOFError):
        print("\n\nTest cancelled.")
        sys.exit(0)


if __name__ == "__main__":
    main()
