"""Check how the text is being segmented into sentences."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path('../enterprise_api').resolve()))

from app.services.segmentation_service import SegmentationService

# Read the original article
article_path = Path('../outputs/wikipedia_prepared/part_00000/article_0000000.txt')
original_text = article_path.read_text(encoding='utf-8')

print("=" * 80)
print("SEGMENTATION ANALYSIS")
print("=" * 80)
print(f"Article: {article_path.name}")
print(f"Original size: {len(original_text)} chars")
print(f"Original lines: {len(original_text.splitlines())}")

# Segment the text
segmenter = SegmentationService()
segments = segmenter.segment_text(original_text, level='sentence')

print(f"\nSegmentation Results:")
print(f"  - Total segments: {len(segments)}")
print(f"  - Segmentation level: sentence")

# Show first 10 segments
print(f"\n" + "=" * 80)
print("FIRST 10 SEGMENTS")
print("=" * 80)

for i, segment in enumerate(segments[:10]):
    print(f"\n[{i}] Length: {len(segment)} chars")
    print(f"    Text: {segment[:100]}{'...' if len(segment) > 100 else ''}")

# Show segments around line 8 from the image
print(f"\n" + "=" * 80)
print("SEGMENTS 5-10 (around the visible area in image)")
print("=" * 80)

for i in range(5, min(10, len(segments))):
    segment = segments[i]
    print(f"\n[{i}] {segment}")
    print(f"    → {len(segment)} chars")

# Check if segmentation matches expected sentence boundaries
print(f"\n" + "=" * 80)
print("SEGMENTATION QUALITY CHECK")
print("=" * 80)

# Count segments that look like proper sentences
proper_sentences = sum(1 for s in segments if s.strip().endswith(('.', '!', '?', ']]')))
print(f"  - Segments ending with sentence punctuation: {proper_sentences}/{len(segments)}")

# Check for very short segments (might indicate over-segmentation)
short_segments = [s for s in segments if len(s.strip()) < 20]
print(f"  - Very short segments (<20 chars): {len(short_segments)}")
if short_segments:
    print(f"    Examples:")
    for s in short_segments[:3]:
        print(f"      - '{s.strip()}'")

# Check for very long segments (might indicate under-segmentation)
long_segments = [s for s in segments if len(s.strip()) > 200]
print(f"  - Very long segments (>200 chars): {len(long_segments)}")
if long_segments:
    print(f"    Examples:")
    for s in long_segments[:3]:
        print(f"      - {s.strip()[:100]}...")

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
