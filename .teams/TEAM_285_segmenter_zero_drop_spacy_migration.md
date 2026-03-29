# TEAM_285 -- Segmenter Zero-Drop and spaCy Migration

## Session Summary

Investigating short-text signing reliability. Finding: silent segment drops in paragraph/section
segmenters mean short headings and captions get no per-segment ZWC marker. When C2PA
verification falls back to ZWC path (copy-paste scenario), these unsigned segments are
undetectable. Fix: lower min_length defaults to 1 across all three segmenters.

Also found: spaCy is ALREADY the primary sentence segmenter via HierarchicalSegmenter but
3 secondary callers still use the regex fallback. Migrating those for consistency.

## Key Findings

- `sentence.py`: min_length=3 (regex fallback only -- HierarchicalSegmenter already uses spaCy)
- `paragraph.py`: min_length=10, called via HierarchicalSegmenter for signing
- `section.py`: min_length=50, called via HierarchicalSegmenter for signing
- `embed_marker_safely()` handles any non-empty text; no lower bound in embedding layer
- spaCy (`en_core_web_sm`) already installed, loaded at module level in default.py
- `segment_sentences_default` has NO min_length filter (only skips visibly empty spans)

## Secondary Call Sites (segment_sentences, regex)

| File | Lines | Purpose |
|------|-------|---------|
| embedding_service.py | 635, 641 | Merkle location metadata scan |
| verification_logic.py | 361, 364 | Sentence scan during ZWC verification |
| multi_embedding.py | 417, 419 | Sentence scan during multi-embedding cleanup |

## Files Changed

- enterprise_api/app/utils/segmentation/sentence.py (min_length default 3 -> 1)
- enterprise_api/app/utils/segmentation/paragraph.py (min_length default 10 -> 1)
- enterprise_api/app/utils/segmentation/section.py (min_length default 50 -> 1)
- enterprise_api/app/services/embedding_service.py (segment_sentences -> segment_sentences_default)
- enterprise_api/app/utils/multi_embedding.py (segment_sentences -> segment_sentences_default)
- enterprise_api/tests/test_segmentation.py (new zero-drop tests, segment_sentences import)

## Important: verification_logic.py NOT migrated

_extract_sentence_for_signature operates on ZWC-embedded text. spaCy's tokenizer misidentifies
sentence boundaries when zero-width characters appear around terminal punctuation. Regression
confirmed: test_extract_sentence_for_signature_returns_clean_sentence passes with regex, fails
with spaCy on this use case. Keep regex here intentionally.

## Suggested Commit Message

```
fix(segmentation): eliminate silent segment drops and migrate to spaCy

Lower min_length defaults to 1 in sentence.py (3->1), paragraph.py (10->1),
and section.py (50->1) so no content is ever silently unsigned. Short headings,
captions, and list items now receive per-segment ZWC markers, ensuring
copy-paste verification works for all content lengths.

Migrate 3 secondary segment_sentences callers (embedding_service,
verification_logic, multi_embedding) from the regex fallback to
segment_sentences_default (spaCy-backed), matching the primary signing path
already in HierarchicalSegmenter.
```
