"""Test segmentation on article 0."""
import re
from pathlib import Path

def segment_sentences(text: str, min_length: int = 3):
    """Simple sentence segmentation (same logic as API)."""
    if not text or not text.strip():
        return []
    
    # Common abbreviations
    abbreviations = {
        'Dr.', 'Mr.', 'Mrs.', 'Ms.', 'Prof.', 'Sr.', 'Jr.',
        'vs.', 'etc.', 'i.e.', 'e.g.', 'cf.', 'Inc.', 'Ltd.',
        'Co.', 'Corp.', 'Ave.', 'St.', 'Rd.', 'Blvd.',
        'Jan.', 'Feb.', 'Mar.', 'Apr.', 'Jun.', 'Jul.', 'Aug.', 
        'Sep.', 'Sept.', 'Oct.', 'Nov.', 'Dec.',
        'U.S.', 'U.K.', 'E.U.', 'Ph.D.', 'M.D.', 'B.A.', 'M.A.'
    }
    
    # Protect abbreviations
    protected_text = text
    abbrev_map = {}
    for i, abbrev in enumerate(abbreviations):
        if abbrev in protected_text:
            placeholder = f"__ABBREV_{i}__"
            abbrev_map[placeholder] = abbrev
            protected_text = protected_text.replace(abbrev, placeholder)
    
    # Enhanced pattern that handles:
    # 1. Standard: sentence terminator + whitespace + capital letter
    # 2. Wiki headings: sentence terminator + whitespace + == or ===
    # 3. Markdown headings: sentence terminator + whitespace + # or ##
    # 4. Wiki markup: sentence terminator + whitespace + [[ or {{
    pattern = r'(?<=[.!?])\s+(?=[A-Z]|==|===|#|##|\[\[|\{\{)'
    segments = re.split(pattern, protected_text)
    
    # Also split on sentence terminators followed by newlines (even without capital letter)
    final_segments = []
    for segment in segments:
        # Split on sentence terminator + newline(s) + non-whitespace
        sub_pattern = r'(?<=[.!?])\n+(?=\S)'
        sub_segments = re.split(sub_pattern, segment)
        final_segments.extend(sub_segments)
    
    if not final_segments:
        final_segments = [protected_text]
    
    segments = final_segments
    
    # Restore abbreviations
    for i, segment in enumerate(segments):
        for placeholder, abbrev in abbrev_map.items():
            segment = segment.replace(placeholder, abbrev)
        segments[i] = segment
    
    # Clean and filter
    sentences = []
    for segment in segments:
        segment = segment.strip()
        if segment and len(segment) >= min_length:
            sentences.append(segment)
    
    return sentences

# Read article
article_path = Path('../outputs/wikipedia_prepared/part_00000/article_0000000.txt')
text = article_path.read_text(encoding='utf-8')

print("=" * 80)
print("SEGMENTATION TEST")
print("=" * 80)
print(f"Article: {article_path.name}")
print(f"Original size: {len(text)} chars")
print(f"Original lines: {len(text.splitlines())}")

# Segment
sentences = segment_sentences(text)

print("\nSegmentation Results:")
print(f"  - Total sentences: {len(sentences)}")

# Show first 10 sentences
print("\n" + "=" * 80)
print("FIRST 10 SENTENCES")
print("=" * 80)

for i, sentence in enumerate(sentences[:10]):
    print(f"\n[{i}] ({len(sentence)} chars)")
    # Show first 150 chars
    display = sentence[:150] + "..." if len(sentence) > 150 else sentence
    print(f"    {display}")

# Check the specific area from the image (lines 3-8)
print("\n" + "=" * 80)
print("SENTENCES 3-8 (visible in image)")
print("=" * 80)

for i in range(3, min(9, len(sentences))):
    print(f"\n[{i}] {sentences[i]}")

# Quality check
print("\n" + "=" * 80)
print("QUALITY CHECK")
print("=" * 80)

# Check for sentences that are just wiki markup
markup_only = [s for s in sentences if s.strip().startswith('{{') or s.strip().startswith('[[')]
print(f"  - Markup-only sentences: {len(markup_only)}")
if markup_only:
    print("    Examples:")
    for s in markup_only[:3]:
        print(f"      - {s}")

# Check for very short sentences
short = [s for s in sentences if len(s.strip()) < 20]
print(f"  - Very short (<20 chars): {len(short)}")
if short:
    print("    Examples:")
    for s in short[:3]:
        print(f"      - '{s}'")

# Check for very long sentences
long = [s for s in sentences if len(s.strip()) > 300]
print(f"  - Very long (>300 chars): {len(long)}")
if long:
    print("    Examples:")
    for s in long[:2]:
        print(f"      - {s[:100]}...")

print("\n" + "=" * 80)
