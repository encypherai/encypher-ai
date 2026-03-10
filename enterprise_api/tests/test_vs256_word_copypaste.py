#!/usr/bin/env python3
"""
Variation Selector (VS1-VS256) Word Copy-Paste Compatibility Test

Tests whether Variation Selector characters survive Microsoft Word's
copy/paste operations, and whether VS256 cryptographic signatures
remain intact and verifiable after a Word roundtrip.

Background:
- VS1-VS16  (U+FE00 - U+FE0F): BMP, commonly used with emoji
- VS17-VS256 (U+E0100 - U+E01EF): Supplementary Plane, rarely used
- Previous research (ZW_VS_RENDERING_RESEARCH.md) found VS chars
  show visible box glyphs in Word — this test verifies that finding
  and checks whether the *data* survives even if visible.

Key Questions:
1. Do VS1-VS16 (BMP) survive Word copy/paste?
2. Do VS17-VS256 (supplementary) survive Word copy/paste?
3. Are VS chars visible in Word (box glyphs, spaces)?
4. Does a full VS256 cryptographic signature survive a roundtrip?

Usage:
    cd enterprise_api
    uv run python tests/test_vs256_word_copypaste.py
"""

import sys
import unicodedata

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from app.utils.vs256_crypto import generate_log_id

# Import VS256 crypto module
sys.path.insert(0, ".")
from app.utils.vs256_crypto import (
    MAGIC_PREFIX,
    SIGNATURE_CHARS,
    VS_TO_BYTE,
    create_embedded_sentence,
    derive_signing_key_from_private_key,
    find_all_markers,
    verify_signed_marker,
)

# ──────────────────────────────────────────────────────────────────────
# VS Character Properties
# ──────────────────────────────────────────────────────────────────────


def print_vs_properties():
    """Print Unicode properties of representative VS characters."""
    print("=" * 78)
    print("UNICODE PROPERTIES OF VARIATION SELECTOR CHARACTERS")
    print("=" * 78)

    test_chars = [
        (0xFE00, "VS1 (BMP start)"),
        (0xFE01, "VS2"),
        (0xFE0E, "VS15 (text presentation)"),
        (0xFE0F, "VS16 (emoji presentation)"),
        (0xE0100, "VS17 (supplementary start)"),
        (0xE0101, "VS18"),
        (0xE0110, "VS33"),
        (0xE0150, "VS97"),
        (0xE018F, "VS160 (magic prefix byte 239)"),
        (0xE0190, "VS161 (magic prefix byte 240)"),
        (0xE01EE, "VS255"),
        (0xE01EF, "VS256 (supplementary end)"),
    ]

    print(f"\n{'Code Point':<14} {'Name':<40} {'Cat':<5} {'UTF-8':<7} {'UTF-16'}")
    print("-" * 78)

    for cp, label in test_chars:
        char = chr(cp)
        try:
            name = unicodedata.name(char)
        except ValueError:
            name = label
        category = unicodedata.category(char)
        utf8_bytes = len(char.encode("utf-8"))
        utf16_bytes = len(char.encode("utf-16-le"))

        print(f"U+{cp:05X}      {name:<40} {category:<5} {utf8_bytes}B     {utf16_bytes}B")

    # Known-good ZW chars for comparison
    print(f"\n{'--- Known Word-Safe Characters (ZW base-4) for Comparison ---':^78}")
    print(f"{'Code Point':<14} {'Name':<40} {'Cat':<5} {'UTF-8':<7} {'UTF-16'}")
    print("-" * 78)

    zw_controls = [
        ("\u200c", "ZWNJ (Word-safe, ZW byte 0)"),
        ("\u200d", "ZWJ (Word-safe, ZW byte 1)"),
        ("\u034f", "CGJ (Word-safe, ZW byte 2)"),
        ("\u180e", "MVS (Word-safe, ZW byte 3)"),
        ("\u200b", "ZWSP (STRIPPED by Word!)"),
    ]

    for char, label in zw_controls:
        cp = ord(char)
        try:
            name = unicodedata.name(char)
        except ValueError:
            name = label
        category = unicodedata.category(char)
        utf8_bytes = len(char.encode("utf-8"))
        utf16_bytes = len(char.encode("utf-16-le"))

        print(f"U+{cp:04X}       {name:<40} {category:<5} {utf8_bytes}B     {utf16_bytes}B")

    print()
    print("Key observations:")
    print("  - VS1-VS16 are BMP (3 bytes UTF-8, 2 bytes UTF-16)")
    print("  - VS17-VS256 are supplementary (4 bytes UTF-8, 4 bytes UTF-16 surrogate pair)")
    print("  - VS chars have General_Category: Mn (Nonspacing Mark)")
    print("  - Word internally uses UTF-16 — supplementary chars need surrogate pairs")
    print("  - Previous research: VS chars show visible box glyphs in Word")
    print()


# ──────────────────────────────────────────────────────────────────────
# Test Document Generation
# ──────────────────────────────────────────────────────────────────────


def create_visibility_test_document():
    """Create a test document to check VS visibility and preservation in Word."""
    lines = []
    lines.append("=" * 70)
    lines.append("VARIATION SELECTOR WORD COPY-PASTE TEST")
    lines.append("=" * 70)
    lines.append("")
    lines.append("Each sentence below contains invisible VS characters embedded")
    lines.append("before the period. If you see boxes, gaps, or spaces before the")
    lines.append("period, those VS chars are VISIBLE (not truly invisible).")
    lines.append("")
    lines.append("Instructions:")
    lines.append("  1. Copy ALL text from START MARKER to END MARKER")
    lines.append("  2. Paste into Microsoft Word")
    lines.append("  3. Note any visible artifacts (boxes, spaces) before periods")
    lines.append("  4. Select ALL text in Word (Ctrl+A) and copy")
    lines.append("  5. Paste back into this terminal when prompted")
    lines.append("")
    lines.append(">>> START MARKER <<<")
    lines.append("")

    # Representative VS characters to test (BMP and supplementary)
    vs_test_set = [
        ("VS1", 0xFE00, "Variation Selector 1 (BMP)"),
        ("VS2", 0xFE01, "Variation Selector 2"),
        ("VS15", 0xFE0E, "Text presentation selector"),
        ("VS16", 0xFE0F, "Emoji presentation selector"),
        ("VS17", 0xE0100, "First supplementary VS"),
        ("VS18", 0xE0101, "Second supplementary VS"),
        ("VS33", 0xE0110, "Mid-range supplementary"),
        ("VS97", 0xE0150, "Mid-range supplementary"),
        ("VS160", 0xE018F, "Magic prefix byte 239"),
        ("VS161", 0xE0190, "Magic prefix byte 240"),
        ("VS240", 0xE01CF, "High supplementary"),
        ("VS256", 0xE01EF, "Last supplementary VS"),
    ]

    # Control chars (known behavior)
    controls = [
        ("ZWNJ", "\u200c", "Word-safe control"),
        ("ZWJ", "\u200d", "Word-safe control"),
        ("ZWSP", "\u200b", "Known STRIPPED by Word"),
    ]

    lines.append("--- VARIATION SELECTORS (under test) ---")
    lines.append("")
    for i, (label, cp, desc) in enumerate(vs_test_set, 1):
        char = chr(cp)
        # Embed 8 copies before the period
        sentence = f"Test {i:2d} ({label:>6s}): Testing {desc}{char * 8}."
        lines.append(sentence)

    lines.append("")
    lines.append("--- CONTROL CHARACTERS (known behavior) ---")
    lines.append("")
    for i, (label, char, desc) in enumerate(controls, len(vs_test_set) + 1):
        sentence = f"Test {i:2d} ({label:>6s}): Control {desc}{char * 8}."
        lines.append(sentence)

    lines.append("")

    # Actual VS256 cryptographic signature test
    lines.append("--- VS256 CRYPTOGRAPHIC SIGNATURE TEST ---")
    lines.append("")

    private_key = Ed25519PrivateKey.generate()
    signing_key = derive_signing_key_from_private_key(private_key)

    sig_sentences = [
        "This sentence has a real VS256 cryptographic signature.",
        "Can this signature survive a Word roundtrip?",
        "The third signed sentence for verification!",
    ]

    sig_uuids = []
    for sentence in sig_sentences:
        uid = generate_log_id()
        sig_uuids.append(uid)
        embedded = create_embedded_sentence(sentence, uid, signing_key)
        lines.append(embedded)

    lines.append("")
    lines.append(">>> END MARKER <<<")

    return (
        "\n".join(lines),
        vs_test_set,
        controls,
        private_key,
        signing_key,
        sig_sentences,
        sig_uuids,
    )


# ──────────────────────────────────────────────────────────────────────
# Result Analysis
# ──────────────────────────────────────────────────────────────────────


def analyze_vs_results(original, pasted, vs_test_set, controls):
    """Analyze which VS characters survived Word copy/paste."""
    print("\n" + "=" * 78)
    print("VARIATION SELECTOR PRESERVATION ANALYSIS")
    print("=" * 78)

    all_tests = [(label, chr(cp), desc) for label, cp, desc in vs_test_set]
    all_tests += [(label, char, desc) for label, char, desc in controls]

    vs_results = []
    ctrl_results = []

    for i, (label, char, desc) in enumerate(all_tests, 1):
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

        cp = ord(char)
        entry = {
            "num": i,
            "label": label,
            "desc": desc,
            "char": char,
            "codepoint": f"U+{cp:05X}" if cp > 0xFFFF else f"U+{cp:04X}",
            "orig": orig_count,
            "past": past_count,
            "status": status,
            "symbol": symbol,
            "is_bmp": cp <= 0xFFFF,
        }

        if i <= len(vs_test_set):
            vs_results.append(entry)
        else:
            ctrl_results.append(entry)

        print(f"\n{i:2d}. {label:>6s} ({entry['codepoint']}) - {desc}")
        print(f"    Original: {orig_count} chars | After Word: {past_count} chars")
        print(f"    Status: [{symbol}] {status}")

    # Summary
    print("\n" + "=" * 78)
    print("SUMMARY")
    print("=" * 78)

    preserved_bmp = [r for r in vs_results if r["status"] == "PRESERVED" and r["is_bmp"]]
    preserved_supp = [r for r in vs_results if r["status"] == "PRESERVED" and not r["is_bmp"]]
    stripped_bmp = [r for r in vs_results if r["status"] == "STRIPPED" and r["is_bmp"]]
    stripped_supp = [r for r in vs_results if r["status"] == "STRIPPED" and not r["is_bmp"]]

    print("\n  BMP VS (VS1-VS16, U+FE00-FE0F):")
    bmp_tested = [r for r in vs_results if r["is_bmp"]]
    print(f"    Preserved: {len(preserved_bmp)}/{len(bmp_tested)}")
    print(f"    Stripped:  {len(stripped_bmp)}/{len(bmp_tested)}")

    print("\n  Supplementary VS (VS17-VS256, U+E0100-E01EF):")
    supp_tested = [r for r in vs_results if not r["is_bmp"]]
    print(f"    Preserved: {len(preserved_supp)}/{len(supp_tested)}")
    print(f"    Stripped:  {len(stripped_supp)}/{len(supp_tested)}")

    print("\n  Control Characters:")
    for r in ctrl_results:
        print(f"    [{r['symbol']}] {r['label']} ({r['codepoint']}) - {r['status']}")

    return vs_results, ctrl_results


def analyze_signature_results(pasted, signing_key, sig_sentences, sig_uuids):
    """Analyze whether VS256 cryptographic signatures survived Word roundtrip."""
    print("\n" + "=" * 78)
    print("VS256 CRYPTOGRAPHIC SIGNATURE VERIFICATION (post-Word)")
    print("=" * 78)

    # Try to find signatures in the pasted text
    found_sigs = find_all_markers(pasted)
    print(f"\n  Signatures expected: {len(sig_sentences)}")
    print(f"  Signatures found:   {len(found_sigs)}")

    if len(found_sigs) == 0:
        print("\n  [XX] NO SIGNATURES FOUND IN PASTED TEXT")
        print("  Word has either stripped or corrupted the VS characters.")
        print("  VS256 embedding is NOT Word-compatible (as expected).")

        # Check if any VS characters remain at all
        vs_count = sum(1 for ch in pasted if ch in VS_TO_BYTE)
        print(f"\n  Total VS characters found in pasted text: {vs_count}")
        if vs_count == 0:
            print("  Word completely stripped all Variation Selector characters.")
        else:
            print(f"  Some VS chars remain ({vs_count}), but signatures are corrupted.")

        # Check magic prefix specifically
        magic_count = pasted.count(MAGIC_PREFIX)
        print(f"  Magic prefix occurrences: {magic_count}")
        return

    verified_count = 0
    for i, (start, end, sig) in enumerate(found_sigs):
        is_valid, extracted_uuid = verify_signed_marker(sig, signing_key)

        if is_valid:
            uuid_match = extracted_uuid in sig_uuids
            print(f"\n  Signature {i + 1}: [{('OK' if uuid_match else '!!')}]")
            print(f"    Position: chars {start}-{end}")
            print("    HMAC: VALID")
            print(f"    UUID: {extracted_uuid}")
            print(f"    UUID match: {'YES' if uuid_match else 'NO (unknown UUID)'}")
            if uuid_match:
                verified_count += 1
        else:
            print(f"\n  Signature {i + 1}: [XX]")
            print(f"    Position: chars {start}-{end}")
            print("    HMAC: INVALID (signature corrupted)")

    print(f"\n  RESULT: {verified_count}/{len(sig_sentences)} signatures verified")

    if verified_count == len(sig_sentences):
        print("\n  [OK] ALL VS256 SIGNATURES SURVIVED WORD ROUNDTRIP!")
        print("  This is unexpected — VS chars typically show box glyphs in Word.")
        print("  Update ZW_VS_RENDERING_RESEARCH.md with this finding!")
    elif verified_count > 0:
        print(f"\n  [!!] PARTIAL: {verified_count}/{len(sig_sentences)} survived")
        print("  Some signatures were corrupted during Word copy/paste.")
    else:
        print("\n  [XX] NO SIGNATURES VERIFIED — VS256 IS NOT WORD-COMPATIBLE")
        print("  This confirms the expected behavior: use legacy_safe mode for Word workflows.")


# ──────────────────────────────────────────────────────────────────────
# Automated Test (no Word needed)
# ──────────────────────────────────────────────────────────────────────


def run_automated_roundtrip_test():
    """Run programmatic VS256 signature roundtrip (no Word needed)."""
    print("\n" + "=" * 78)
    print("AUTOMATED VS256 ROUNDTRIP TEST (no Word needed)")
    print("=" * 78)

    private_key = Ed25519PrivateKey.generate()
    signing_key = derive_signing_key_from_private_key(private_key)

    sentences = [
        "The quick brown fox jumps over the lazy dog.",
        "How much wood would a woodchuck chuck?",
        "Pack my box with five dozen liquor jugs!",
    ]

    print(f"\n  Testing {len(sentences)} sentences with VS256 signatures...")

    # Sign
    embedded_parts = []
    uuids = []
    for sentence in sentences:
        uid = generate_log_id()
        uuids.append(uid)
        embedded = create_embedded_sentence(sentence, uid, signing_key)
        embedded_parts.append(embedded)

    document = " ".join(embedded_parts)

    # Verify
    found = find_all_markers(document)
    assert len(found) == len(sentences), f"Expected {len(sentences)} sigs, found {len(found)}"

    for i, (start, end, sig) in enumerate(found):
        is_valid, extracted_uuid = verify_signed_marker(sig, signing_key)
        assert is_valid, f"Signature {i + 1} failed verification"
        assert extracted_uuid == uuids[i], f"UUID mismatch for sig {i + 1}"

    # Size stats
    original_len = sum(len(s) for s in sentences) + len(sentences) - 1
    sig_overhead = len(document) - original_len
    sig_utf8 = sum(len(sig.encode("utf-8")) for _, _, sig in found)
    zw_utf8 = len(sentences) * 100

    print(f"  [OK] All {len(sentences)} signatures created, embedded, and verified")
    print("\n  Size stats:")
    print(f"    Original text:     {original_len} chars")
    print(f"    With signatures:   {len(document)} chars")
    print(f"    Signature overhead: {sig_overhead} chars ({SIGNATURE_CHARS} per sentence)")
    print(f"    Signature UTF-8:   {sig_utf8} bytes ({sig_utf8 // len(sentences)} per sentence)")
    print(f"    Overhead ratio:    {sig_overhead / original_len * 100:.1f}%")

    # Simulate what Word might do: strip all VS characters
    print("\n  Simulating Word-like VS stripping...")
    stripped_doc = "".join(ch for ch in document if ch not in VS_TO_BYTE)
    stripped_found = find_all_markers(stripped_doc)
    print(f"    Signatures after stripping: {len(stripped_found)} (expected 0)")
    assert len(stripped_found) == 0, "Should find no sigs after VS stripping"
    print("    [OK] Confirmed: VS stripping destroys signatures")

    print("\n  Comparison with legacy_safe encoding (base-6, Word-compatible):")
    print(f"    {'Chars per signature':>25} VS256: {SIGNATURE_CHARS}  legacy_safe: 100")
    print(f"    {'Total UTF-8 bytes':>25} {sig_utf8:>10} {zw_utf8:>12} {zw_utf8 / sig_utf8:>7.1f}x")
    print(f"    {'Word compatible':>25} {'NO':>10} {'YES':>12}")
    print()


# ──────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────


def main():
    print()
    print("=" * 78)
    print("  VARIATION SELECTOR (VS1-VS256) WORD COPY-PASTE TEST")
    print("  VS256 Cryptographic Embedding Compatibility Check")
    print("=" * 78)
    print()
    print("This script tests whether VS characters used in vs256_embedding mode")
    print("survive Microsoft Word copy/paste operations.")
    print()
    print("Expected result: VS chars show box glyphs in Word and may be stripped.")
    print("vs256_embedding is designed for Google Docs, PDF, and browser use — NOT Word.")
    print()

    # Step 1: Print VS properties
    print_vs_properties()

    # Step 2: Automated roundtrip (always runs)
    run_automated_roundtrip_test()

    # Step 3: Interactive Word test
    print("\n" + "=" * 78)
    print("INTERACTIVE WORD COPY-PASTE TEST")
    print("=" * 78)
    print()
    print("This test requires Microsoft Word. It will:")
    print("  1. Generate text with embedded VS characters and VS256 signatures")
    print("  2. Ask you to paste into Word and copy back")
    print("  3. Analyze which characters survived the roundtrip")
    print()

    response = input("Run interactive Word copy-paste test? [y/N]: ").strip().lower()
    if response != "y":
        print("\nSkipping interactive test.")
        print("Run with 'y' to test Word compatibility manually.\n")
        return

    # Generate test document
    (
        test_doc,
        vs_test_set,
        controls,
        private_key,
        signing_key,
        sig_sentences,
        sig_uuids,
    ) = create_visibility_test_document()

    print("\n" + "=" * 78)
    print("STEP 1: COPY THE TEXT BELOW (from START MARKER to END MARKER)")
    print("=" * 78)
    print()
    print(test_doc)
    print()
    print("=" * 78)

    print("\nSTEP 2: Paste into Microsoft Word")
    print("  - Look for visible box glyphs or spaces before periods")
    print("  - Note which test sentences show visible artifacts")
    print("  - Check if the signed sentences look different from unsigned text")

    print("\nSTEP 3: In Word, select ALL text (Ctrl+A), then Copy (Ctrl+C)")
    print("  Press ENTER when ready to paste from Word...")
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

    # Analyze VS character preservation
    vs_results, ctrl_results = analyze_vs_results(test_doc, pasted_text, vs_test_set, controls)

    # Analyze cryptographic signature survival
    analyze_signature_results(pasted_text, signing_key, sig_sentences, sig_uuids)

    # Final verdict
    print("\n" + "=" * 78)
    print("FINAL VERDICT")
    print("=" * 78)

    preserved_vs = [r for r in vs_results if r["status"] == "PRESERVED"]
    total_vs = len(vs_results)

    if len(preserved_vs) == total_vs:
        print("\n  ALL VS CHARACTERS SURVIVED WORD ROUNDTRIP!")
        print("  This is unexpected — previous research showed box glyphs.")
        print("  vs256_embedding may be Word-compatible after all!")
        print("  => Update ZW_VS_RENDERING_RESEARCH.md with this finding!")
    elif len(preserved_vs) > 0:
        print(f"\n  PARTIAL: {len(preserved_vs)}/{total_vs} VS chars preserved")
        preserved_bmp = [r for r in preserved_vs if r["is_bmp"]]
        preserved_supp = [r for r in preserved_vs if not r["is_bmp"]]
        print(f"    BMP (VS1-VS16): {len(preserved_bmp)} preserved")
        print(f"    Supplementary (VS17-VS256): {len(preserved_supp)} preserved")
        if len(preserved_supp) == 0 and len(preserved_bmp) > 0:
            print("  => Word may strip supplementary VS but keep BMP VS")
    else:
        print("\n  NO VS CHARACTERS SURVIVED — CONFIRMED NOT WORD-COMPATIBLE")
        print("  This confirms the expected behavior:")
        print("    - Use VS256 (micro mode) for Google Docs, PDF, browser (max density)")
        print("    - Use legacy_safe mode for Word workflows (Word-safe)")

    print()


if __name__ == "__main__":
    main()
