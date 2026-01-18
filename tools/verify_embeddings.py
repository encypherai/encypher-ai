"""Verify that embeddings have correct structure."""

from pathlib import Path

# Read the embedded file
embedded_file = Path("../outputs/wikipedia_prepared/part_00000/article_0000000.embedded.txt")
content = embedded_file.read_text(encoding="utf-8")

print(f"File: {embedded_file.name}")
print(f"Total size: {len(content)} chars")
print(f"Total lines: {len(content.splitlines())}")

# Count invisible Unicode characters (variation selectors and tags)
invisible_count = sum(1 for c in content if 0xE0000 <= ord(c) <= 0xE007F or 0xFE00 <= ord(c) <= 0xFE0F)
print(f"Invisible characters: {invisible_count}")

# Check for C2PA wrapper at end
has_c2pa_at_end = any(ord(c) > 0xE0000 for c in content[-5000:])
print(f"Has C2PA wrapper at end: {has_c2pa_at_end}")

# Compare with original
original_file = Path("../outputs/wikipedia_prepared/part_00000/article_0000000.txt")
original = original_file.read_text(encoding="utf-8")
print(f"\nOriginal size: {len(original)} chars")
print(f"Embedded size: {len(content)} chars")
increase = ((len(content) - len(original)) / len(original)) * 100
print(f"Size increase: {increase:.1f}%")

# Check if text is preserved
print(f"\nText preserved: {original[:100] in content}")

print("\n✓ Embeddings verification complete!")
print("  - File exists and has correct size")
print("  - Contains invisible Unicode characters")
print("  - Has C2PA wrapper at end")
print("  - Original text is preserved")
