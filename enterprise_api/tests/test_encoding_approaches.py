#!/usr/bin/env python3
"""
Test different encoding approaches one by one for Word compatibility.

Tests:
1. Base-3 (ZWSP, ZWNJ, ZWJ) - Current approach
2. Base-4 (ZWSP, ZWNJ, ZWJ, CGJ) - 33% smaller
3. Base-5 (ZWSP, ZWNJ, ZWJ, CGJ, MVS) - 33% smaller
4. Base-2 (ZWNJ, ZWJ) - No ZWSP, safest
"""

import sys
from uuid import uuid4
from cryptography.hazmat.primitives import hashes, hmac as crypto_hmac
from cryptography.hazmat.backends import default_backend


# Character sets for different bases
CHARS_BASE3 = ["\u200B", "\u200C", "\u200D"]  # ZWSP, ZWNJ, ZWJ
CHARS_BASE4 = ["\u200B", "\u200C", "\u200D", "\u034F"]  # + CGJ
CHARS_BASE5 = ["\u200B", "\u200C", "\u200D", "\u034F", "\u180E"]  # + MVS
CHARS_BASE2 = ["\u200C", "\u200D"]  # ZWNJ, ZWJ only (no ZWSP)


def encode_byte(byte_value: int, base: int, chars: list) -> str:
    """Encode a byte using specified base and character set."""
    if base == 2:
        # Binary: 8 bits = 8 chars
        result = []
        for i in range(8):
            bit = (byte_value >> i) & 1
            result.append(chars[bit])
        return ''.join(result)
    else:
        # Base-3, 4, 5: variable length
        result = []
        value = byte_value
        
        # Calculate how many digits needed
        if base == 3:
            digits = 6  # 3^6 = 729 > 256
        elif base == 4:
            digits = 4  # 4^4 = 256
        elif base == 5:
            digits = 4  # 5^4 = 625 > 256
        else:
            raise ValueError(f"Unsupported base: {base}")
        
        for _ in range(digits):
            digit = value % base
            result.append(chars[digit])
            value //= base
        
        return ''.join(result)


def create_test_signature(base: int, chars: list, char_names: str) -> tuple:
    """Create a test signature with the specified encoding."""
    # Generate test UUID
    test_uuid = uuid4()
    
    # Simple HMAC for testing
    signing_key = b"test_key_32_bytes_long_padding!!"
    h = crypto_hmac.HMAC(signing_key, hashes.SHA256(), backend=default_backend())
    h.update(test_uuid.bytes)
    hmac_truncated = h.finalize()[:16]
    
    # Encode UUID + HMAC (32 bytes)
    payload = test_uuid.bytes + hmac_truncated
    encoded = ''.join(encode_byte(b, base, chars) for b in payload)
    
    # Magic number (4 chars using first 4 from charset)
    magic = ''.join(chars[i % len(chars)] for i in range(4))
    
    signature = magic + encoded
    
    # Calculate stats
    if base == 2:
        expected_len = 4 + (32 * 8)  # magic + 32 bytes * 8 bits
    elif base == 3:
        expected_len = 4 + (32 * 6)  # magic + 32 bytes * 6 chars
    elif base == 4 or base == 5:
        expected_len = 4 + (32 * 4)  # magic + 32 bytes * 4 chars
    
    return signature, expected_len, char_names


def run_test(test_num: int, base: int, chars: list, char_names: str):
    """Run a single encoding test."""
    print(f"\n{'='*70}")
    print(f"TEST {test_num}: BASE-{base} ENCODING")
    print(f"{'='*70}")
    print(f"Characters: {char_names}")
    print(f"Code points: {', '.join(f'U+{ord(c):04X}' for c in chars)}")
    
    signature, expected_len, _ = create_test_signature(base, chars, char_names)
    
    print(f"\nSignature size: {len(signature)} chars (expected: {expected_len})")
    
    # Create test sentence
    sentence = f"Test {test_num} (Base-{base}): This tests {char_names} encoding"
    signed_sentence = sentence[:-1] + signature + sentence[-1] + "."
    
    # Character breakdown
    char_counts = {}
    for char in chars:
        count = signed_sentence.count(char)
        char_counts[char] = count
    
    print(f"\nCharacter counts in signature:")
    for i, char in enumerate(chars):
        name = char_names.split(', ')[i] if ', ' in char_names else f"Char{i}"
        print(f"  {name}: {char_counts[char]}")
    
    print(f"\nCOPY THE TEXT BELOW:")
    print("-" * 70)
    print(signed_sentence)
    print("-" * 70)
    
    return signed_sentence, signature, chars


def analyze_result(original: str, pasted: str, signature: str, chars: list, base: int):
    """Analyze test results."""
    print(f"\n{'='*70}")
    print("ANALYSIS")
    print(f"{'='*70}")
    
    # Check if signature survived
    if signature in pasted:
        print("✅ COMPLETE SIGNATURE SURVIVED")
    else:
        print("❌ Signature was modified or stripped")
    
    # Check character counts
    print(f"\nCharacter preservation:")
    all_preserved = True
    for char in chars:
        orig_count = original.count(char)
        past_count = pasted.count(char)
        
        if past_count == orig_count:
            status = "✅"
        elif past_count == 0:
            status = "❌ STRIPPED"
            all_preserved = False
        else:
            status = f"⚠️  PARTIAL ({past_count}/{orig_count})"
            all_preserved = False
        
        print(f"  U+{ord(char):04X}: {orig_count} → {past_count} {status}")
    
    # Overall result
    print(f"\n{'='*70}")
    if all_preserved and signature in pasted:
        print(f"✅ BASE-{base} ENCODING: FULLY COMPATIBLE WITH WORD")
        print(f"   Signature size: {len(signature)} chars")
    elif all_preserved:
        print(f"⚠️  BASE-{base} ENCODING: Characters preserved but signature modified")
    else:
        print(f"❌ BASE-{base} ENCODING: NOT COMPATIBLE (characters stripped)")
    print(f"{'='*70}")


def main():
    print("\n" + "="*70)
    print("ENCODING APPROACH COMPARISON")
    print("="*70)
    print("\nThis tests different encoding approaches one by one.")
    print("Each test is independent - copy/paste each one separately.\n")
    
    tests = [
        (3, CHARS_BASE3, "ZWSP, ZWNJ, ZWJ"),
        (4, CHARS_BASE4, "ZWSP, ZWNJ, ZWJ, CGJ"),
        (5, CHARS_BASE5, "ZWSP, ZWNJ, ZWJ, CGJ, MVS"),
        (2, CHARS_BASE2, "ZWNJ, ZWJ (no ZWSP)"),
    ]
    
    for i, (base, chars, names) in enumerate(tests, 1):
        signed_sentence, signature, char_list = run_test(i, base, chars, names)
        
        print(f"\nPaste into Word, copy back, then paste here and press ENTER:")
        print("-" * 70)
        
        try:
            pasted = input()
            analyze_result(signed_sentence, pasted, signature, char_list, base)
            
            print(f"\nPress ENTER to continue to next test (or Ctrl+C to quit)...")
            input()
            
        except (KeyboardInterrupt, EOFError):
            print("\n\nTests cancelled.")
            sys.exit(0)
    
    print("\n" + "="*70)
    print("ALL TESTS COMPLETE")
    print("="*70)
    print("\nReview the results above to choose the best encoding approach.")
    print("\nRecommendation:")
    print("  - If all work: Use Base-4 or Base-5 (33% smaller)")
    print("  - If only Base-3 works: Stick with current implementation")
    print("  - If Base-2 is safest: Use ZWNJ+ZWJ only (larger but most reliable)")


if __name__ == "__main__":
    main()
