# TEAM_088: Marketing Site C2PA Text Embedding Compliance

## Status: Complete

## Goal
Ensure the marketing-site sign tool uses the actual C2PA-compliant `C2PATextManifestWrapper` embedding technique per the spec in `docs/c2pa/Manifests_Text.txt`.

## Root Cause
The marketing-site sends `custom_assertions` (provenance) which triggers the **advanced signing path** in the enterprise API (`_needs_advanced_signing` → `_execute_advanced_signing` → `embedding_service.create_embeddings`).

In `create_embeddings`, even with `segmentation_level="document"` (single segment = entire text):
1. Each segment got a per-segment **basic** embedding via `embed_metadata(metadata_format="basic")` with no target → defaults to `MetadataTarget.WHITESPACE` → inserts invisible characters after the first whitespace (mid-text)
2. Segments were re-joined with `" ".join()` destroying original whitespace structure
3. The C2PA wrapper was then correctly appended at the end

The invisible characters before "action" in the user's example were the per-segment basic embedding, NOT the C2PA wrapper.

## Fix
**File**: `enterprise_api/app/services/embedding_service.py`

- Skip per-segment basic embeddings when `len(segments) == 1` (document-level signing) since the C2PA wrapper already covers the entire document
- Preserve original text structure (newlines, paragraph breaks) for document-level signing instead of re-joining with `" ".join()`
- Multi-segment (sentence-level) signing continues to work as before

## Tests
**File**: `enterprise_api/tests/test_document_level_c2pa_placement.py` (5 tests)
- `test_document_level_wrapper_at_end` — wrapper must be after all visible text
- `test_document_level_c2pa_wrapper_decodable` — wrapper must be extractable via `find_and_decode`
- `test_document_level_preserves_newlines` — original whitespace preserved
- `test_document_level_with_custom_assertions` — custom assertions don't cause mid-text insertion
- `test_multi_segment_still_gets_per_segment_embeddings` — multi-segment path unchanged

All 14 embedding tests pass (+ 7 skipped API tests).
