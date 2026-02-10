#!/usr/bin/env python3
"""
Comprehensive test of all invisible Unicode characters for Word compatibility.

Tests each character individually to see:
1. If it appears visible in Word
2. If it survives Word copy/paste

Each test sentence has a unique invisible character repeated 10 times,
making it easy to see which ones are visible and which survive.
"""

import sys


# All candidate invisible characters
CANDIDATES = [
    ("ZWSP", "\u200B", "Zero-Width Space"),
    ("ZWNJ", "\u200C", "Zero-Width Non-Joiner"),
    ("ZWJ", "\u200D", "Zero-Width Joiner"),
    ("WJ", "\u2060", "Word Joiner"),
    ("ZWNBSP", "\uFEFF", "Zero-Width No-Break Space (BOM)"),
    ("CGJ", "\u034F", "Combining Grapheme Joiner"),
    ("MVS", "\u180E", "Mongolian Vowel Separator"),
    ("FUNC_APP", "\u2061", "Function Application"),
    ("INVIS_TIMES", "\u2062", "Invisible Times"),
    ("INVIS_SEP", "\u2063", "Invisible Separator"),
    ("INVIS_PLUS", "\u2064", "Invisible Plus"),
    # Unicode Tag Characters (Plane 14) - under investigation
    ("TAG_SPACE", "\U000E0020", "Tag Space"),
    ("TAG_A", "\U000E0041", "Tag Latin Capital Letter A"),
    ("TAG_a", "\U000E0061", "Tag Latin Small Letter a"),
    ("TAG_0", "\U000E0030", "Tag Digit Zero"),
    ("TAG_CANCEL", "\U000E007F", "Cancel Tag"),
]


def create_test_document():
    """Create a test document with one sentence per character."""
    lines = []
    
    lines.append("="*70)
    lines.append("INVISIBLE CHARACTER TEST FOR MICROSOFT WORD")
    lines.append("="*70)
    lines.append("")
    lines.append("Each sentence below contains 10 copies of a different invisible")
    lines.append("character inserted BEFORE the period.")
    lines.append("")
    lines.append("Instructions:")
    lines.append("1. Copy ALL the text below")
    lines.append("2. Paste into Microsoft Word")
    lines.append("3. Check which sentences show visible gaps/spaces")
    lines.append("4. Copy ALL from Word")
    lines.append("5. Paste back here")
    lines.append("")
    lines.append("="*70)
    lines.append("")
    
    # Create test sentences
    for i, (code, char, name) in enumerate(CANDIDATES, 1):
        # Insert 10 copies of the character before the period
        sentence = f"Test {i} ({code}): This tests {name}{char * 10}."
        lines.append(sentence)
    
    lines.append("")
    lines.append("="*70)
    lines.append("")
    
    return "\n".join(lines)


def analyze_results(original, pasted):
    """Analyze which characters survived Word copy/paste."""
    print("\n" + "="*70)
    print("ANALYSIS RESULTS")
    print("="*70)
    
    results = []
    
    for i, (code, char, name) in enumerate(CANDIDATES, 1):
        orig_count = original.count(char)
        past_count = pasted.count(char)
        
        if orig_count == 0:
            status = "⚠️  NOT IN ORIGINAL"
        elif past_count == orig_count:
            status = "✅ PRESERVED"
        elif past_count == 0:
            status = "❌ STRIPPED"
        else:
            status = f"⚠️  PARTIAL ({past_count}/{orig_count})"
        
        results.append({
            "num": i,
            "code": code,
            "name": name,
            "char": char,
            "orig": orig_count,
            "past": past_count,
            "status": status,
        })
        
        print(f"\n{i}. {code} - {name}")
        print(f"   Code point: U+{ord(char):04X}")
        print(f"   Original:   {orig_count} chars")
        print(f"   After Word: {past_count} chars")
        print(f"   Status:     {status}")
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    preserved = [r for r in results if r["past"] == r["orig"] and r["orig"] > 0]
    stripped = [r for r in results if r["past"] == 0 and r["orig"] > 0]
    partial = [r for r in results if 0 < r["past"] < r["orig"]]
    
    print(f"\n✅ PRESERVED ({len(preserved)}):")
    for r in preserved:
        print(f"   - {r['code']} ({r['name']})")
    
    if stripped:
        print(f"\n❌ STRIPPED ({len(stripped)}):")
        for r in stripped:
            print(f"   - {r['code']} ({r['name']})")
    
    if partial:
        print(f"\n⚠️  PARTIAL ({len(partial)}):")
        for r in partial:
            print(f"   - {r['code']} ({r['name']}) - {r['past']}/{r['orig']}")
    
    # Recommendation
    print("\n" + "="*70)
    print("RECOMMENDATION FOR BASE-3 ENCODING")
    print("="*70)
    
    if len(preserved) >= 3:
        print(f"\n✅ Found {len(preserved)} preserved characters!")
        print("\nBest 3 for base-3 encoding:")
        for i, r in enumerate(preserved[:3]):
            print(f"   {i} = {r['code']} (U+{ord(r['char']):04X}) - {r['name']}")
        
        print("\nYou can use these for Word-compatible base-3 encoding!")
    elif len(preserved) >= 2:
        print(f"\n⚠️  Only {len(preserved)} preserved characters found.")
        print("You'll need to use base-2 (binary) encoding instead of base-3.")
        print("\nBest 2 for base-2 encoding:")
        for i, r in enumerate(preserved[:2]):
            print(f"   {i} = {r['code']} (U+{ord(r['char']):04X}) - {r['name']}")
    else:
        print("\n❌ Insufficient preserved characters for encoding.")
        print("Word may not be compatible with invisible character embedding.")


def main():
    print("\n" + "="*70)
    print("COMPREHENSIVE INVISIBLE CHARACTER TEST")
    print("="*70)
    print(f"\nTesting {len(CANDIDATES)} different invisible Unicode characters")
    print("to find which ones:")
    print("  1. Appear invisible in Word (no gaps/spaces)")
    print("  2. Survive Word copy/paste operations")
    print("")
    
    # Generate test document
    test_doc = create_test_document()
    
    print("STEP 1: COPY THE TEXT BELOW")
    print("="*70)
    print(test_doc)
    print("="*70)
    
    print("\nSTEP 2: PASTE INTO MICROSOFT WORD")
    print("   - Look at each sentence")
    print("   - Note which ones show visible gaps/spaces before the period")
    print("   - Those characters are NOT truly invisible in Word")
    
    print("\nSTEP 3: COPY ALL TEXT FROM WORD")
    
    print("\nSTEP 4: PASTE BACK HERE AND PRESS ENTER")
    print("-" * 70)
    
    try:
        pasted = input()
        
        # Analyze
        analyze_results(test_doc, pasted)
        
    except (KeyboardInterrupt, EOFError):
        print("\n\nTest cancelled.")
        sys.exit(0)


if __name__ == "__main__":
    main()
