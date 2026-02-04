#!/usr/bin/env python3
"""
Word Copy-Paste Test for ZW Embedding (No Magic Numbers)

This test creates text with invisible signatures and allows you to verify
that they survive copy-paste through Microsoft Word.

Key Features:
- 128-char signatures (no magic number)
- Only ZWNJ, ZWJ, CGJ, MVS (Word-compatible)
- No WJ (appears as space in Word)
- No ZWSP (stripped by Word)
- Contiguous sequence detection
"""

from uuid import uuid4
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from app.utils.zw_crypto import (
    CHARS_BASE4_SET,
    create_minimal_signed_uuid,
    verify_minimal_signed_uuid,
    find_all_minimal_signed_uuids,
    derive_signing_key_from_private_key,
    create_safely_embedded_sentence,
)


def main():
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║              WORD COPY-PASTE TEST - ZW EMBEDDING (NO MAGIC)                  ║
║                                                                              ║
║  This test verifies that invisible signatures survive copy-paste through    ║
║  Microsoft Word using contiguous sequence detection (no magic numbers).     ║
║                                                                              ║
║  Signature: 128 contiguous base-4 characters                                ║
║  Characters: ZWNJ, ZWJ, CGJ, MVS (Word-compatible)                          ║
║  Detection: 128 contiguous invisible chars = signature                      ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    # Generate test key
    print("=" * 80)
    print("STEP 1: GENERATE TEST SIGNATURES")
    print("=" * 80)
    
    private_key = Ed25519PrivateKey.generate()
    signing_key = derive_signing_key_from_private_key(private_key)
    
    # Create 5 test sentences
    sentences = [
        "This is the first sentence with an invisible signature.",
        "Here's a second sentence that also has a hidden signature!",
        "The third sentence demonstrates Word compatibility.",
        "Fourth sentence: copy this into Microsoft Word.",
        "Fifth and final sentence completes the test.",
    ]
    
    print(f"\nCreating {len(sentences)} signed sentences...")
    print(f"Signature size: 128 chars each (no magic number)")
    print(f"Total overhead: {len(sentences) * 128} chars")
    
    # Create signed sentences
    signed_sentences = []
    uuids = []
    
    for i, sentence in enumerate(sentences, 1):
        uuid = uuid4()
        uuids.append(uuid)
        signed = create_safely_embedded_sentence(sentence, uuid, signing_key)
        signed_sentences.append(signed)
        print(f"  [{i}] UUID: {uuid}")
    
    full_text = " ".join(signed_sentences)
    
    # Verify before copy-paste
    print("\n" + "=" * 80)
    print("STEP 2: VERIFY SIGNATURES (BEFORE COPY-PASTE)")
    print("=" * 80)
    
    found_before = find_all_minimal_signed_uuids(full_text)
    print(f"\nSignatures found: {len(found_before)}")
    
    verified_before = 0
    for i, (start, end, sig) in enumerate(found_before, 1):
        is_valid, recovered_uuid = verify_minimal_signed_uuid(sig, signing_key)
        if is_valid and recovered_uuid in uuids:
            verified_before += 1
            print(f"  ✓ Signature {i}: Valid - UUID {recovered_uuid}")
    
    print(f"\nVerification: {verified_before}/{len(found_before)} signatures valid")
    
    # Display text for copy-paste
    print("\n" + "=" * 80)
    print("STEP 3: COPY-PASTE TEST")
    print("=" * 80)
    print("\n" + "▼" * 80)
    print("COPY THE TEXT BELOW (including invisible signatures):")
    print("▼" * 80)
    print()
    print(full_text)
    print()
    print("▲" * 80)
    print("COPY THE TEXT ABOVE")
    print("▲" * 80)
    
    print("\n📋 INSTRUCTIONS:")
    print("  1. Select and copy the text above")
    print("  2. Open Microsoft Word")
    print("  3. Paste the text")
    print("  4. Verify no visible spaces or gaps appear")
    print("  5. Copy the text from Word")
    print("  6. Paste it below when prompted")
    print()
    
    # Wait for user input
    print("Press ENTER when you're ready to paste the text from Word...")
    input()
    
    print("\nPaste the text from Word here (press ENTER twice when done):")
    print("-" * 80)
    
    # Read multi-line input
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
    
    pasted_text = " ".join(pasted_lines).strip()
    
    # Verify after copy-paste
    print("\n" + "=" * 80)
    print("STEP 4: VERIFY SIGNATURES (AFTER COPY-PASTE)")
    print("=" * 80)
    
    if not pasted_text:
        print("\n❌ ERROR: No text pasted!")
        return False
    
    print(f"\nOriginal length: {len(full_text)} chars")
    print(f"Pasted length: {len(pasted_text)} chars")
    print(f"Difference: {len(pasted_text) - len(full_text)} chars")
    
    # Count invisible chars
    invisible_before = sum(1 for c in full_text if c in CHARS_BASE4_SET)
    invisible_after = sum(1 for c in pasted_text if c in CHARS_BASE4_SET)
    
    print(f"\nInvisible chars before: {invisible_before}")
    print(f"Invisible chars after: {invisible_after}")
    print(f"Lost: {invisible_before - invisible_after}")
    
    # Find signatures in pasted text
    found_after = find_all_minimal_signed_uuids(pasted_text)
    print(f"\nSignatures found after copy-paste: {len(found_after)}")
    
    verified_after = 0
    for i, (start, end, sig) in enumerate(found_after, 1):
        is_valid, recovered_uuid = verify_minimal_signed_uuid(sig, signing_key)
        if is_valid and recovered_uuid in uuids:
            verified_after += 1
            idx = uuids.index(recovered_uuid)
            print(f"  ✓ Signature {i}: Valid - Sentence {idx + 1} - UUID {recovered_uuid}")
        else:
            print(f"  ✗ Signature {i}: INVALID")
    
    # Final results
    print("\n" + "=" * 80)
    print("FINAL RESULTS")
    print("=" * 80)
    
    success = (
        len(found_after) == len(sentences) and
        verified_after == len(sentences)
    )
    
    print(f"\nExpected signatures: {len(sentences)}")
    print(f"Found before copy-paste: {len(found_before)}")
    print(f"Found after copy-paste: {len(found_after)}")
    print(f"Verified after copy-paste: {verified_after}")
    
    if success:
        print("\n✅ SUCCESS! All signatures survived copy-paste!")
        print("\n🎉 Key Achievements:")
        print("   - 128-char signatures (no magic number)")
        print("   - Contiguous sequence detection works perfectly")
        print("   - Word-compatible (ZWNJ, ZWJ, CGJ, MVS only)")
        print("   - No visible spaces or gaps in Word")
        print("   - All signatures verified after copy-paste")
    else:
        print("\n❌ FAILURE! Signatures were lost or corrupted.")
        print(f"   Expected: {len(sentences)} signatures")
        print(f"   Found: {len(found_after)} signatures")
        print(f"   Verified: {verified_after} signatures")
        
        if invisible_after < invisible_before:
            print(f"\n⚠️  Lost {invisible_before - invisible_after} invisible characters")
            print("   This suggests Word may have stripped some characters")
    
    return success


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
