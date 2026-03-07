#!/usr/bin/env python3
"""
Debug what happens to ZW chars when copied through Word.

This script analyzes the character-by-character differences between
original and Word-corrupted text.
"""

import sys


def analyze_text(text, label):
    """Analyze and display text character by character."""
    print(f"\n{'='*70}")
    print(f"{label}")
    print(f"{'='*70}")
    print(f"Total length: {len(text)} characters\n")
    
    # Count character types
    zwsp_count = text.count('\u200B')
    zwnj_count = text.count('\u200C')
    zwj_count = text.count('\u200D')
    
    print("Zero-width characters:")
    print(f"  ZWSP (U+200B): {zwsp_count}")
    print(f"  ZWNJ (U+200C): {zwnj_count}")
    print(f"  ZWJ  (U+200D): {zwj_count}")
    print(f"  Total ZW:      {zwsp_count + zwnj_count + zwj_count}")
    
    # Show first 100 chars with code points
    print("\nFirst 100 characters (with code points):")
    for i, char in enumerate(text[:100]):
        cp = ord(char)
        if cp == 0x200B:
            name = "ZWSP"
        elif cp == 0x200C:
            name = "ZWNJ"
        elif cp == 0x200D:
            name = "ZWJ"
        elif cp < 32 or cp > 126:
            name = f"U+{cp:04X}"
        else:
            name = char
        
        if cp in (0x200B, 0x200C, 0x200D):
            print(f"  [{i}] {name} (U+{cp:04X})")


def compare_texts(original, corrupted):
    """Compare two texts character by character."""
    print(f"\n{'='*70}")
    print("COMPARISON")
    print(f"{'='*70}")
    
    print(f"Original length:  {len(original)}")
    print(f"Corrupted length: {len(corrupted)}")
    print(f"Difference:       {len(original) - len(corrupted)} chars lost")
    
    # Find where they diverge
    min_len = min(len(original), len(corrupted))
    first_diff = None
    
    for i in range(min_len):
        if original[i] != corrupted[i]:
            first_diff = i
            break
    
    if first_diff is not None:
        print(f"\nFirst difference at position {first_diff}:")
        print(f"  Original:  U+{ord(original[first_diff]):04X}")
        print(f"  Corrupted: U+{ord(corrupted[first_diff]):04X}")
    elif len(original) != len(corrupted):
        print(f"\nTexts match up to position {min_len}, then differ in length")
    else:
        print("\nTexts are identical")


def main():
    print("\n" + "="*70)
    print("WORD CORRUPTION DEBUGGER")
    print("="*70)
    print("\nThis tool analyzes what Word does to zero-width characters.\n")
    
    print("Step 1: Paste the ORIGINAL text (from terminal before Word):")
    print("-" * 70)
    try:
        original = input()
    except (KeyboardInterrupt, EOFError):
        print("\nCancelled.")
        sys.exit(0)
    
    analyze_text(original, "ORIGINAL TEXT (Before Word)")
    
    print("\n" + "="*70)
    print("Step 2: Paste the CORRUPTED text (after copying from Word):")
    print("-" * 70)
    try:
        corrupted = input()
    except (KeyboardInterrupt, EOFError):
        print("\nCancelled.")
        sys.exit(0)
    
    analyze_text(corrupted, "CORRUPTED TEXT (After Word)")
    
    compare_texts(original, corrupted)
    
    # Check if it's a known Word issue
    print("\n" + "="*70)
    print("DIAGNOSIS")
    print("="*70)
    
    orig_zw = original.count('\u200B') + original.count('\u200C') + original.count('\u200D')
    corr_zw = corrupted.count('\u200B') + corrupted.count('\u200C') + corrupted.count('\u200D')
    
    if corr_zw == 0 and orig_zw > 0:
        print("\n❌ ISSUE: Word completely stripped all zero-width characters")
        print("\nThis is a known issue with some Word versions/settings:")
        print("  - Word may strip ZW chars during paste")
        print("  - Word may convert to different encoding")
        print("  - Word may normalize Unicode differently")
        print("\nPossible solutions:")
        print("  1. Use Word's 'Keep Text Only' paste option")
        print("  2. Try Google Docs instead (better ZW support)")
        print("  3. Use redundant embedding (multiple signatures)")
        print("  4. Accept that Word is not compatible")
    elif corr_zw < orig_zw:
        print("\n⚠️  ISSUE: Word partially stripped ZW characters")
        print(f"   Lost {orig_zw - corr_zw} out of {orig_zw} ZW chars")
        print("\nThis suggests selective stripping or encoding issues.")
    else:
        print("\n✓ Zero-width characters survived!")
        print("  The issue may be with signature format, not ZW chars.")


if __name__ == "__main__":
    main()
