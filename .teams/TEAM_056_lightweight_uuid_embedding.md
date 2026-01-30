# TEAM_056 — Lightweight UUID Embedding

## Session Goal
Implement `manifest_mode="lightweight_uuid"` in `enterprise_api` only, ensuring:
- NFC normalization across `/sign/advanced`.
- Verification `text_span` reports UTF-8 byte offsets (over NFC-normalized text).
- New integration test for lightweight UUID passes.

## Work Log
- Updated `/sign/advanced` execution path to normalize input text to NFC and compute leaf hashes consistently.
- Implemented `manifest_mode="lightweight_uuid"` via `UnicodeMetadata.embed_metadata(metadata_format="manifest")` (enterprise_api only).
- Embedded the document-level lightweight UUID manifest at file end to avoid VS-block collisions with per-sentence embeddings.
- Converted multi-embedding `text_span` outputs to prefer UTF-8 byte offsets, with fallback to legacy char spans for test/mocked embedding objects.
- Updated integrity hashing SSOT: Merkle `compute_leaf_hash` and `/sign` hashes are NFC-normalized and case-sensitive (no lowercasing).
- Added `enterprise_api/tests/test_integrity_hashing.py` to lock NFC equivalence + case sensitivity for integrity hashes.

## Verification Plan
- `uv run pytest enterprise_api/tests/test_sign_advanced_lightweight_uuid.py`
- `uv run ruff check .` (enterprise_api)
- `uv run pytest` (enterprise_api)

## Verification Results
- ✅ `uv run pytest tests/test_sign_advanced_lightweight_uuid.py`
- ✅ `uv run ruff check .`
- ✅ `uv run pytest`
