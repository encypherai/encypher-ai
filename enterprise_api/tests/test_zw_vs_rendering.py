"""
Test zero-width character + variation selector combinations for cross-platform rendering.

This test validates that ZW+VS combinations remain invisible and zero-width
across different rendering engines (PDF, Word, browsers, terminals).
"""

import unicodedata
from typing import List, Tuple


# Zero-width base characters
ZWSP = "\u200B"  # Zero Width Space
ZWNJ = "\u200C"  # Zero Width Non-Joiner
ZWJ = "\u200D"  # Zero Width Joiner

# Variation selectors (standard range)
VS1 = "\uFE00"
VS2 = "\uFE01"
VS3 = "\uFE02"
VS16 = "\uFE0F"

# Variation selectors (supplement range - for extended encoding)
VS17 = "\U000E0100"
VS256 = "\U000E01EF"


def create_magic_number(version: int = 1) -> str:
    """
    Create a magic number signature using ZW+VS combinations.
    
    This serves as a detectable header for embedded metadata while
    remaining invisible in rendered output.
    
    Args:
        version: Magic number version (for future compatibility)
    
    Returns:
        Magic number string (invisible in rendering)
    """
    if version == 1:
        # Version 1: ZWSP+VS1 + ZWSP+VS2 (4 chars, ~0 width)
        return ZWSP + VS1 + ZWSP + VS2
    elif version == 2:
        # Version 2: ZWNJ+VS1 + ZWJ+VS2 (different pattern)
        return ZWNJ + VS1 + ZWJ + VS2
    else:
        raise ValueError(f"Unknown magic number version: {version}")


def encode_byte_to_zw_vs(byte_value: int) -> str:
    """
    Encode a single byte (0-255) using ZW+VS combinations.
    
    Strategy:
    - Use 3 ZW chars (ZWSP, ZWNJ, ZWJ) as base
    - Use 16 VS (VS1-VS16) as modifiers
    - Total combinations: 3 * 16 = 48 unique sequences
    - For 256 values, use 2-char encoding: 16 * 16 = 256
    
    Args:
        byte_value: Integer 0-255
    
    Returns:
        2-character invisible string (ZW+VS + ZW+VS)
    """
    if not 0 <= byte_value <= 255:
        raise ValueError(f"Byte value must be 0-255, got {byte_value}")
    
    # Split into high nibble (0-15) and low nibble (0-15)
    high = byte_value >> 4  # Upper 4 bits
    low = byte_value & 0x0F  # Lower 4 bits
    
    # Map to VS (VS1 = 0xFE00, so VS1-VS16 = 0-15)
    vs_high = chr(0xFE00 + high)
    vs_low = chr(0xFE00 + low)
    
    # Use ZWSP for both (consistent base character)
    return ZWSP + vs_high + ZWSP + vs_low


def decode_zw_vs_to_byte(encoded: str) -> int:
    """
    Decode a ZW+VS encoded byte back to integer.
    
    Args:
        encoded: 4-character string (ZW+VS + ZW+VS)
    
    Returns:
        Decoded byte value (0-255)
    """
    if len(encoded) != 4:
        raise ValueError(f"Expected 4 characters, got {len(encoded)}")
    
    # Extract VS code points (skip ZW base chars)
    vs_high = ord(encoded[1])
    vs_low = ord(encoded[3])
    
    # Convert VS to nibbles
    high = vs_high - 0xFE00
    low = vs_low - 0xFE00
    
    # Combine nibbles into byte
    return (high << 4) | low


def encode_data_with_magic(data: bytes, version: int = 1) -> str:
    """
    Encode arbitrary binary data with magic number header.
    
    Args:
        data: Binary data to encode
        version: Magic number version
    
    Returns:
        Invisible string containing magic number + encoded data
    """
    magic = create_magic_number(version)
    encoded_bytes = "".join(encode_byte_to_zw_vs(b) for b in data)
    return magic + encoded_bytes


def detect_magic_number(text: str) -> List[Tuple[int, int, int]]:
    """
    Detect magic number patterns in text.
    
    Args:
        text: Text to search
    
    Returns:
        List of (start_index, end_index, version) tuples
    """
    results = []
    
    # Search for version 1 magic number
    v1_magic = create_magic_number(1)
    idx = 0
    while idx < len(text):
        pos = text.find(v1_magic, idx)
        if pos == -1:
            break
        results.append((pos, pos + len(v1_magic), 1))
        idx = pos + 1
    
    return results


def test_magic_number_creation():
    """Test that magic numbers are created correctly."""
    magic_v1 = create_magic_number(1)
    
    # Should be 4 characters
    assert len(magic_v1) == 4
    
    # Should contain ZWSP and VS
    assert ZWSP in magic_v1
    assert VS1 in magic_v1
    assert VS2 in magic_v1
    
    # Should be different from plain ZWSP
    assert magic_v1 != ZWSP * 4
    
    print(f"✓ Magic number v1: {len(magic_v1)} chars")
    print(f"  Code points: {[hex(ord(c)) for c in magic_v1]}")


def test_byte_encoding_roundtrip():
    """Test that byte encoding/decoding works correctly."""
    test_values = [0, 1, 15, 16, 127, 128, 255]
    
    for value in test_values:
        encoded = encode_byte_to_zw_vs(value)
        decoded = decode_zw_vs_to_byte(encoded)
        
        assert decoded == value, f"Roundtrip failed: {value} -> {encoded} -> {decoded}"
        assert len(encoded) == 4, f"Encoded length should be 4, got {len(encoded)}"
        
        # Verify all chars are zero-width or VS
        for char in encoded:
            cp = ord(char)
            is_zw = cp in (0x200B, 0x200C, 0x200D)
            is_vs = 0xFE00 <= cp <= 0xFE0F
            assert is_zw or is_vs, f"Invalid character: U+{cp:04X}"
    
    print(f"✓ Byte encoding roundtrip: {len(test_values)} values tested")


def test_data_encoding_with_magic():
    """Test encoding arbitrary data with magic number."""
    test_data = b"Hello, World!"
    
    encoded = encode_data_with_magic(test_data, version=1)
    
    # Should start with magic number
    magic = create_magic_number(1)
    assert encoded.startswith(magic)
    
    # Should be invisible (all ZW or VS)
    for char in encoded:
        cp = ord(char)
        is_zw = cp in (0x200B, 0x200C, 0x200D)
        is_vs = 0xFE00 <= cp <= 0xFE0F
        assert is_zw or is_vs, f"Non-invisible character: U+{cp:04X}"
    
    # Calculate expected length: magic (4) + data (13 bytes * 4 chars/byte)
    expected_len = 4 + (len(test_data) * 4)
    assert len(encoded) == expected_len
    
    print(f"✓ Data encoding: {len(test_data)} bytes -> {len(encoded)} chars")


def test_magic_number_detection():
    """Test detecting magic numbers in text."""
    # Create text with embedded magic number
    magic = create_magic_number(1)
    text = f"Hello {magic} World"
    
    detected = detect_magic_number(text)
    
    assert len(detected) == 1
    start, end, version = detected[0]
    assert version == 1
    assert text[start:end] == magic
    
    print(f"✓ Magic number detection: found at position {start}")


def test_rendering_properties():
    """Test that ZW+VS combinations have expected Unicode properties."""
    magic = create_magic_number(1)
    
    # Check Unicode categories
    for char in magic:
        category = unicodedata.category(char)
        # Should be Format (Cf) or Mark (Mn)
        assert category in ("Cf", "Mn"), f"Unexpected category: {category} for U+{ord(char):04X}"
    
    # Check width (East Asian Width property)
    for char in magic:
        width = unicodedata.east_asian_width(char)
        # Should be Neutral (N) - zero-width
        # Note: VS may be Ambiguous (A), but should still render as zero-width
        assert width in ("N", "A"), f"Unexpected width: {width} for U+{ord(char):04X}"
    
    print(f"✓ Unicode properties validated")


def test_visual_rendering():
    """
    Visual test: print text with ZW+VS to verify invisibility.
    
    This test should be run manually to verify rendering in terminal.
    """
    magic = create_magic_number(1)
    encoded_data = encode_data_with_magic(b"SECRET", version=1)
    
    print("\n=== Visual Rendering Test ===")
    print(f"Plain text: 'Hello World'")
    print(f"With magic: 'Hello{magic}World'")
    print(f"With data:  'Hello{encoded_data}World'")
    print("\nExpected: All three lines should look identical")
    print("If you see extra characters or spacing, ZW+VS is not rendering correctly.\n")


def test_pdf_word_compatibility():
    """
    Generate test strings for manual PDF/Word testing.
    
    Copy these strings into PDF and Word documents to verify rendering.
    """
    magic = create_magic_number(1)
    test_string = f"The quick{magic}brown fox jumps over the lazy dog."
    
    print("\n=== PDF/Word Compatibility Test ===")
    print("Copy the following text into:")
    print("1. Microsoft Word")
    print("2. Google Docs")
    print("3. PDF viewer (after saving from Word)")
    print("\nTest string:")
    print(test_string)
    print("\nExpected: Should look like normal sentence with no gaps or symbols")
    print(f"Character count: {len(test_string)} (includes {len(magic)} invisible chars)")
    
    # Also provide hex dump for verification
    print("\nHex dump of invisible section:")
    for i, char in enumerate(magic):
        print(f"  Char {i}: U+{ord(char):04X} ({unicodedata.name(char, 'UNKNOWN')})")


if __name__ == "__main__":
    print("Running ZW+VS rendering tests...\n")
    
    test_magic_number_creation()
    test_byte_encoding_roundtrip()
    test_data_encoding_with_magic()
    test_magic_number_detection()
    test_rendering_properties()
    test_visual_rendering()
    test_pdf_word_compatibility()
    
    print("\n✅ All automated tests passed!")
    print("\n⚠️  Manual testing required:")
    print("   1. Run visual rendering test in terminal")
    print("   2. Test in PDF viewer (copy test string to Word, save as PDF)")
    print("   3. Test in Microsoft Word")
    print("   4. Test in Google Docs")
    print("   5. Test in web browsers (paste into contenteditable div)")
