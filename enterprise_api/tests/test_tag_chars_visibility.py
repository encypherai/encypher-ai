#!/usr/bin/env python3
"""
Unicode Tag Character (U+E0000 - U+E007F) Visibility & Word Compatibility Test

Investigates whether Unicode Tag Characters from the "Tags" block (Plane 14)
could be used as an alternative or supplement to the current base-4 encoding
characters (ZWNJ, ZWJ, CGJ, MVS) for invisible text embedding.

Tag Characters Background:
- Range: U+E0000 to U+E007F (128 code points)
- Block: "Tags" in Supplementary Special-purpose Plane (Plane 14)
- Originally for language tagging in plain text (deprecated for that use)
- Now used in emoji tag sequences (e.g., flag subdivision emoji)
- General_Category: Format (Cf) — same as ZWNJ/ZWJ
- Default_Ignorable_Code_Point: Yes — renderers SHOULD make them invisible
- These are supplementary characters (above U+FFFF), requiring surrogate
  pairs in UTF-16 (relevant since Word uses UTF-16 internally)

Key Questions:
1. Does Microsoft Word preserve tag characters during copy/paste?
2. Are tag characters truly invisible in Word (no boxes, no spaces)?
3. Do they survive round-trips through Google Docs, PDF, email?
4. Could they supplement the existing base-4 charset for higher density?

Usage:
    cd enterprise_api
    uv run python tests/test_tag_chars_visibility.py
"""

import sys
import unicodedata


# ──────────────────────────────────────────────────────────────────────
# Unicode Tag Characters (U+E0000 - U+E007F)
# ──────────────────────────────────────────────────────────────────────

# Named tag characters
TAG_CHARS = {
    "TAG_LANG":   "\U000E0001",  # U+E0001 LANGUAGE TAG
    "TAG_SPACE":  "\U000E0020",  # U+E0020 TAG SPACE
    "TAG_EXCLAM": "\U000E0021",  # U+E0021 TAG EXCLAMATION MARK
    "TAG_A":      "\U000E0041",  # U+E0041 TAG LATIN CAPITAL LETTER A
    "TAG_a":      "\U000E0061",  # U+E0061 TAG LATIN SMALL LETTER A
    "TAG_0":      "\U000E0030",  # U+E0030 TAG DIGIT ZERO
    "TAG_CANCEL": "\U000E007F",  # U+E007F CANCEL TAG
}

# The usable range for encoding: TAG SPACE (U+E0020) through TAG TILDE (U+E007E)
# These are tag versions of printable ASCII (0x20-0x7E) = 95 characters
TAG_PRINTABLE_START = 0xE0020
TAG_PRINTABLE_END = 0xE007E
TAG_PRINTABLE_CHARS = [chr(cp) for cp in range(TAG_PRINTABLE_START, TAG_PRINTABLE_END + 1)]

# Full block for completeness
TAG_BLOCK_START = 0xE0000
TAG_BLOCK_END = 0xE007F
ALL_TAG_CHARS = [chr(cp) for cp in range(TAG_BLOCK_START, TAG_BLOCK_END + 1)]

# Current base-4 chars for comparison
CURRENT_BASE4 = {
    "ZWNJ": "\u200C",  # U+200C Zero-Width Non-Joiner
    "ZWJ":  "\u200D",  # U+200D Zero-Width Joiner
    "CGJ":  "\u034F",  # U+034F Combining Grapheme Joiner
    "MVS":  "\u180E",  # U+180E Mongolian Vowel Separator
}


def print_tag_char_properties():
    """Print Unicode properties of key tag characters."""
    print("=" * 78)
    print("UNICODE PROPERTIES OF TAG CHARACTERS")
    print("=" * 78)

    test_chars = [
        (0xE0001, "LANGUAGE TAG"),
        (0xE0020, "TAG SPACE"),
        (0xE0021, "TAG EXCLAMATION MARK"),
        (0xE0030, "TAG DIGIT ZERO"),
        (0xE0041, "TAG LATIN CAPITAL LETTER A"),
        (0xE0061, "TAG LATIN SMALL LETTER A"),
        (0xE007E, "TAG TILDE"),
        (0xE007F, "CANCEL TAG"),
    ]

    print(f"\n{'Code Point':<14} {'Name':<35} {'Category':<6} {'Bytes(UTF-8)'}")
    print("-" * 78)

    for cp, expected_name in test_chars:
        char = chr(cp)
        try:
            name = unicodedata.name(char)
        except ValueError:
            name = f"<{expected_name}>"
        category = unicodedata.category(char)
        utf8_bytes = len(char.encode("utf-8"))
        utf16_units = len(char.encode("utf-16-le")) // 2  # surrogate pair count

        print(f"U+{cp:05X}      {name:<35} {category:<6} {utf8_bytes} bytes / {utf16_units} UTF-16 units")

    # Compare with current base-4 chars
    print(f"\n{'--- Current Base-4 Characters for Comparison ---':^78}")
    print(f"{'Code Point':<14} {'Name':<35} {'Category':<6} {'Bytes(UTF-8)'}")
    print("-" * 78)

    for label, char in CURRENT_BASE4.items():
        cp = ord(char)
        try:
            name = unicodedata.name(char)
        except ValueError:
            name = label
        category = unicodedata.category(char)
        utf8_bytes = len(char.encode("utf-8"))
        utf16_units = len(char.encode("utf-16-le")) // 2

        print(f"U+{cp:04X}       {name:<35} {category:<6} {utf8_bytes} bytes / {utf16_units} UTF-16 units")

    print()
    print("Key observations:")
    print("  - Tag chars are General_Category: Cf (Format) — same as ZWNJ/ZWJ")
    print("  - Tag chars are 4 bytes in UTF-8 (vs 2-3 bytes for current chars)")
    print("  - Tag chars require surrogate pairs in UTF-16 (Word is UTF-16-based)")
    print("  - There are 95 printable tag chars (U+E0020-E007E) — enough for base-95!")
    print()


def create_visibility_test_document():
    """Create a test document to check visibility in Word and other platforms."""
    lines = []
    lines.append("=" * 70)
    lines.append("UNICODE TAG CHARACTER VISIBILITY TEST")
    lines.append("=" * 70)
    lines.append("")
    lines.append("Each sentence below contains 10 copies of a different tag character")
    lines.append("inserted BEFORE the period. If you see gaps, spaces, or boxes")
    lines.append("before the period, that character is NOT invisible.")
    lines.append("")
    lines.append("Instructions:")
    lines.append("  1. Copy ALL text from START MARKER to END MARKER")
    lines.append("  2. Paste into Microsoft Word")
    lines.append("  3. Check each sentence for visible artifacts before the period")
    lines.append("  4. Copy ALL text from Word")
    lines.append("  5. Paste back into terminal when prompted")
    lines.append("")
    lines.append(">>> START MARKER <<<")
    lines.append("")

    # Test a representative subset of tag characters
    test_set = [
        ("TAG_LANG",   "\U000E0001", "Language Tag"),
        ("TAG_SPACE",  "\U000E0020", "Tag Space"),
        ("TAG_EXCLAM", "\U000E0021", "Tag Exclamation Mark"),
        ("TAG_HASH",   "\U000E0023", "Tag Number Sign"),
        ("TAG_0",      "\U000E0030", "Tag Digit Zero"),
        ("TAG_1",      "\U000E0031", "Tag Digit One"),
        ("TAG_9",      "\U000E0039", "Tag Digit Nine"),
        ("TAG_A",      "\U000E0041", "Tag Capital A"),
        ("TAG_Z",      "\U000E005A", "Tag Capital Z"),
        ("TAG_a",      "\U000E0061", "Tag Small a"),
        ("TAG_z",      "\U000E007A", "Tag Small z"),
        ("TAG_TILDE",  "\U000E007E", "Tag Tilde"),
        ("TAG_CANCEL", "\U000E007F", "Cancel Tag"),
    ]

    # Also add current base-4 chars as controls
    controls = [
        ("ZWNJ",  "\u200C", "Zero-Width Non-Joiner (current)"),
        ("ZWJ",   "\u200D", "Zero-Width Joiner (current)"),
        ("CGJ",   "\u034F", "Combining Grapheme Joiner (current)"),
        ("MVS",   "\u180E", "Mongolian Vowel Separator (current)"),
        ("ZWSP",  "\u200B", "Zero-Width Space (known stripped by Word)"),
    ]

    lines.append("--- TAG CHARACTERS (under investigation) ---")
    lines.append("")
    for i, (code, char, name) in enumerate(test_set, 1):
        sentence = f"Test {i:2d} ({code:>12s}): This tests {name}{char * 10}."
        lines.append(sentence)

    lines.append("")
    lines.append("--- CONTROL CHARACTERS (known behavior) ---")
    lines.append("")
    for i, (code, char, name) in enumerate(controls, len(test_set) + 1):
        sentence = f"Test {i:2d} ({code:>12s}): Control test {name}{char * 10}."
        lines.append(sentence)

    lines.append("")
    lines.append(">>> END MARKER <<<")

    return "\n".join(lines), test_set, controls


def analyze_results(original, pasted, test_set, controls):
    """Analyze which tag characters survived Word copy/paste."""
    print("\n" + "=" * 78)
    print("ANALYSIS RESULTS")
    print("=" * 78)

    all_chars = test_set + controls

    tag_results = []
    ctrl_results = []

    for i, (code, char, name) in enumerate(all_chars, 1):
        orig_count = original.count(char)
        past_count = pasted.count(char)

        if orig_count == 0:
            status = "NOT IN ORIGINAL"
            symbol = "??"
        elif past_count == orig_count:
            status = "PRESERVED"
            symbol = "OK"
        elif past_count == 0:
            status = "STRIPPED"
            symbol = "XX"
        else:
            status = f"PARTIAL ({past_count}/{orig_count})"
            symbol = "!!"

        entry = {
            "num": i,
            "code": code,
            "name": name,
            "char": char,
            "codepoint": f"U+{ord(char):05X}" if ord(char) > 0xFFFF else f"U+{ord(char):04X}",
            "orig": orig_count,
            "past": past_count,
            "status": status,
            "symbol": symbol,
        }

        if i <= len(test_set):
            tag_results.append(entry)
        else:
            ctrl_results.append(entry)

        print(f"\n{i:2d}. {code:>12s} ({entry['codepoint']}) - {name}")
        print(f"    Original: {orig_count} chars | After Word: {past_count} chars")
        print(f"    Status: [{symbol}] {status}")

    # Summary tables
    print("\n" + "=" * 78)
    print("SUMMARY: TAG CHARACTERS")
    print("=" * 78)

    preserved = [r for r in tag_results if r["status"] == "PRESERVED"]
    stripped = [r for r in tag_results if r["status"] == "STRIPPED"]
    partial = [r for r in tag_results if r["status"].startswith("PARTIAL")]

    print(f"\n  [OK] PRESERVED ({len(preserved)}):")
    for r in preserved:
        print(f"       - {r['code']} ({r['codepoint']}) {r['name']}")

    if stripped:
        print(f"\n  [XX] STRIPPED ({len(stripped)}):")
        for r in stripped:
            print(f"       - {r['code']} ({r['codepoint']}) {r['name']}")

    if partial:
        print(f"\n  [!!] PARTIAL ({len(partial)}):")
        for r in partial:
            print(f"       - {r['code']} ({r['codepoint']}) {r['name']} - {r['past']}/{r['orig']}")

    print("\n  CONTROL CHARACTERS:")
    for r in ctrl_results:
        print(f"       [{r['symbol']}] {r['code']} ({r['codepoint']}) - {r['status']}")

    # Encoding potential
    print("\n" + "=" * 78)
    print("ENCODING POTENTIAL ANALYSIS")
    print("=" * 78)

    if len(preserved) >= 2:
        print(f"\n  {len(preserved)} tag characters preserved!")
        print("\n  Encoding options if tag chars are Word-compatible:")
        print(f"    - Base-{len(preserved)}: {len(preserved)} tag chars")
        print(f"    - Combined with current base-4: base-{4 + len(preserved)} possible")

        if len(preserved) >= 95:
            print("\n  BASE-95 ENCODING POSSIBLE!")
            print("    - 95 tag chars (U+E0020 to U+E007E)")
            print("    - ceil(log95(256)) = 2 chars per byte")
            print("    - That's 50% fewer chars than base-4 (4 chars/byte)")
            print("    - 32-byte UUID+HMAC = 64 chars (vs 128 with base-4)")
            print("    BUT: Each char is 4 UTF-8 bytes vs 2-3 for current set")
            print("    Net byte overhead: 64 * 4 = 256 bytes vs 128 * 3 = 384 bytes")
            print("    => Tag chars would be ~33% SMALLER in bytes too!")
        elif len(preserved) >= 16:
            print("\n  BASE-16 (HEX) ENCODING POSSIBLE!")
            print(f"    - {len(preserved)} tag chars available, need 16 for hex")
            print("    - 2 chars per byte (each char = one hex nibble)")
            print("    - 32-byte UUID+HMAC = 64 chars")
            print("    - 50% fewer chars than current base-4")
        elif len(preserved) >= 4:
            print("\n  Could replace current base-4 with tag-char base-4:")
            print("    - Same density (4 chars/byte)")
            print("    - But tag chars are 4 UTF-8 bytes each (vs 2-3)")
            print("    - Net: more bytes per signature")
            print("    => Not beneficial unless combined with current set")

    else:
        print(f"\n  Only {len(preserved)} tag characters preserved.")
        print("  Tag characters are NOT viable for Word-compatible encoding.")

    # Comparison table
    print("\n" + "=" * 78)
    print("SIZE COMPARISON (32-byte payload: UUID + HMAC)")
    print("=" * 78)
    print(f"\n  {'Encoding':<25} {'Chars':<8} {'Bytes(UTF-8)':<14} {'Notes'}")
    print(f"  {'-'*25} {'-'*8} {'-'*14} {'-'*30}")
    print(f"  {'Current Base-4':<25} {'128':<8} {'~384':<14} {'ZWNJ/ZWJ/CGJ/MVS'}")
    print(f"  {'Tag Base-95':<25} {'64':<8} {'256':<14} {'If all tag chars survive'}")
    print(f"  {'Tag Base-16':<25} {'64':<8} {'256':<14} {'If 16+ tag chars survive'}")
    print(f"  {'Tag Base-4':<25} {'128':<8} {'512':<14} {'If only 4 tag chars survive'}")
    print(f"  {'Hybrid (4 + tags)':<25} {'var':<8} {'var':<14} {'Mix current + tag chars'}")

    return preserved, stripped


def run_encoding_roundtrip_test():
    """Run a programmatic encoding roundtrip test using tag characters."""
    print("\n" + "=" * 78)
    print("AUTOMATED ROUNDTRIP TEST (no Word needed)")
    print("=" * 78)

    # Use first 4 tag chars for a base-4 test
    tag_base4 = [
        chr(0xE0020),  # TAG SPACE
        chr(0xE0021),  # TAG EXCLAMATION MARK
        chr(0xE0022),  # TAG QUOTATION MARK
        chr(0xE0023),  # TAG NUMBER SIGN
    ]

    print(f"\nTest charset: {', '.join(f'U+{ord(c):05X}' for c in tag_base4)}")

    # Encode/decode 0-255
    errors = 0
    for byte_val in range(256):
        # Encode
        value = byte_val
        encoded = []
        for _ in range(4):  # base-4: 4^4 = 256
            encoded.append(tag_base4[value % 4])
            value //= 4

        # Decode
        decoded = 0
        for i, char in enumerate(encoded):
            idx = tag_base4.index(char)
            decoded += idx * (4 ** i)

        if decoded != byte_val:
            errors += 1
            if errors <= 5:
                print(f"  MISMATCH: {byte_val} encoded then decoded as {decoded}")

    if errors == 0:
        print("  [OK] All 256 byte values roundtrip correctly with tag base-4")
    else:
        print(f"  [XX] {errors} roundtrip failures")

    # Test with base-95
    tag_base95 = [chr(cp) for cp in range(0xE0020, 0xE007F)]  # 95 chars
    print(f"\n  Tag base-95 charset size: {len(tag_base95)}")

    errors_95 = 0
    for byte_val in range(256):
        # Encode in base-95: ceil(log95(256)) = 2 chars
        d0 = byte_val % 95
        d1 = byte_val // 95
        encoded_95 = tag_base95[d0] + tag_base95[d1]

        # Decode
        decoded_95 = tag_base95.index(encoded_95[0]) + tag_base95.index(encoded_95[1]) * 95
        if decoded_95 != byte_val:
            errors_95 += 1

    if errors_95 == 0:
        print("  [OK] All 256 byte values roundtrip correctly with tag base-95")
        print("       2 chars per byte (vs 4 for base-4) = 50% fewer chars")
        print("       32-byte payload = 64 tag chars = 256 UTF-8 bytes")
    else:
        print(f"  [XX] {errors_95} roundtrip failures with base-95")

    # UTF-8/UTF-16 size analysis
    sample_char = chr(0xE0041)  # TAG LATIN CAPITAL LETTER A
    print("\n  Size analysis for tag char U+E0041:")
    print(f"    UTF-8:  {len(sample_char.encode('utf-8'))} bytes")
    print(f"    UTF-16: {len(sample_char.encode('utf-16-le'))} bytes (surrogate pair)")

    current_sample = "\u200C"  # ZWNJ
    print("\n  Size analysis for current ZWNJ U+200C:")
    print(f"    UTF-8:  {len(current_sample.encode('utf-8'))} bytes")
    print(f"    UTF-16: {len(current_sample.encode('utf-16-le'))} bytes")

    print("\n  Net byte comparison for 32-byte UUID+HMAC payload:")
    base4_chars = 128
    base4_bytes_utf8 = base4_chars * 3  # average ~3 bytes per current char
    base95_chars = 64
    base95_bytes_utf8 = base95_chars * 4  # 4 bytes per tag char
    print(f"    Current base-4:  {base4_chars} chars x ~3 bytes = ~{base4_bytes_utf8} UTF-8 bytes")
    print(f"    Tag base-95:     {base95_chars} chars x  4 bytes =  {base95_bytes_utf8} UTF-8 bytes")
    print(f"    Difference:      {base4_bytes_utf8 - base95_bytes_utf8} bytes saved with tag base-95")


def create_hybrid_encoding_test():
    """Test combining current base-4 chars with tag characters for higher base."""
    print("\n" + "=" * 78)
    print("HYBRID ENCODING ANALYSIS")
    print("=" * 78)
    print("\nIf tag characters ARE Word-compatible, we could combine them with")
    print("the current 4 chars (ZWNJ/ZWJ/CGJ/MVS) for a higher-base encoding:\n")

    current_4 = list(CURRENT_BASE4.values())

    # Hybrid: 4 current + N tag chars
    combos = [
        ("current 4 only",       4, 4),
        ("4 current + 4 tags",   8, 3),
        ("4 current + 12 tags", 16, 2),
        ("4 current + 91 tags", 95, 2),
        ("95 tag chars only",   95, 2),
    ]

    print(f"  {'Combo':<25} {'Base':<6} {'Chars/Byte':<12} {'32B Payload':<12} {'UTF-8 est.'}")
    print(f"  {'-'*25} {'-'*6} {'-'*12} {'-'*12} {'-'*12}")

    for name, base, chars_per_byte in combos:
        payload_chars = 32 * chars_per_byte
        # Estimate: current chars ~3 bytes UTF-8, tag chars ~4 bytes UTF-8
        if "tag" in name.lower() and "current" not in name.lower():
            avg_utf8 = 4.0
        elif "current" in name.lower() and "tag" in name.lower():
            # Mix of 2-3 byte and 4 byte chars
            tag_count = base - 4
            current_frac = 4 / base
            avg_utf8 = current_frac * 3.0 + (1 - current_frac) * 4.0
        else:
            avg_utf8 = 3.0
        utf8_est = int(payload_chars * avg_utf8)
        print(f"  {name:<25} {base:<6} {chars_per_byte:<12} {payload_chars:<12} ~{utf8_est}")


def main():
    print()
    print("=" * 78)
    print("  UNICODE TAG CHARACTER (U+E0000 - U+E007F) INVESTIGATION")
    print("  Word Compatibility & Invisible Embedding Potential")
    print("=" * 78)
    print()
    print("This script investigates whether Unicode Tag Characters could be used")
    print("for invisible text embedding, similar to our current ZWNJ/ZWJ/CGJ/MVS")
    print("base-4 approach documented in ZW_EMBEDDING_MODE.md")
    print()

    # Step 1: Print properties
    print_tag_char_properties()

    # Step 2: Automated roundtrip tests (no Word needed)
    run_encoding_roundtrip_test()

    # Step 3: Hybrid encoding analysis
    create_hybrid_encoding_test()

    # Step 4: Interactive Word visibility test
    print("\n" + "=" * 78)
    print("INTERACTIVE WORD COPY-PASTE TEST")
    print("=" * 78)
    print()

    response = input("Run interactive Word copy-paste test? [y/N]: ").strip().lower()
    if response != "y":
        print("\nSkipping interactive test. Run with 'y' to test Word compatibility.")
        print("You can also paste the test text manually into Word for inspection.\n")

        # Still generate and display the test document
        test_doc, test_set, controls = create_visibility_test_document()
        print("\nTest document (copy into Word manually if desired):\n")
        print(test_doc)
        return

    # Generate test document
    test_doc, test_set, controls = create_visibility_test_document()

    print("\nSTEP 1: COPY THE TEXT BELOW")
    print("=" * 78)
    print(test_doc)
    print("=" * 78)

    print("\nSTEP 2: Paste into Microsoft Word")
    print("  - Look for visible gaps, spaces, or boxes before periods")
    print("  - Note which test sentences show visible artifacts")

    print("\nSTEP 3: Copy ALL text from Word, then paste below")
    print("  Press ENTER when ready to paste...")
    input()

    print("\nPaste the text from Word here (press ENTER twice when done):")
    print("-" * 78)

    pasted_lines = []
    empty_count = 0
    while True:
        try:
            line = input()
            if line == "":
                empty_count += 1
                if empty_count >= 2:
                    break
            else:
                empty_count = 0
            pasted_lines.append(line)
        except EOFError:
            break

    pasted_text = "\n".join(pasted_lines).strip()

    if not pasted_text:
        print("\nNo text pasted. Exiting.")
        return

    # Analyze
    preserved, stripped = analyze_results(test_doc, pasted_text, test_set, controls)

    # Final verdict
    print("\n" + "=" * 78)
    print("FINAL VERDICT")
    print("=" * 78)

    tag_preserved = [r for r in (preserved or []) if ord(r["char"]) >= 0xE0000]

    if len(tag_preserved) >= 13:  # All tag test chars survived
        print("\n  TAG CHARACTERS ARE WORD-COMPATIBLE!")
        print("  => Investigate base-95 encoding for 50% char reduction")
        print("  => Update ZW_EMBEDDING_MODE.md with findings")
    elif len(tag_preserved) > 0:
        print(f"\n  PARTIAL COMPATIBILITY: {len(tag_preserved)}/13 tag chars preserved")
        print("  => Some tag characters may be usable, needs further investigation")
    else:
        print("\n  TAG CHARACTERS ARE NOT WORD-COMPATIBLE")
        print("  => Stick with current ZWNJ/ZWJ/CGJ/MVS base-4 encoding")

    print()


if __name__ == "__main__":
    main()
