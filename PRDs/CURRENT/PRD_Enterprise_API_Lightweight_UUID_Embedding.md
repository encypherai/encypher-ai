# PRD — Enterprise API Lightweight UUID Embedding

## Status
Completed

## Current Goal
Implement `manifest_mode="lightweight_uuid"` in `enterprise_api` only, ensuring NFC normalization and UTF-8 byte offset semantics for `text_span` in verification results.

## Overview
`/api/v1/sign/advanced` supports multiple embedding/manifest modes. We need a lightweight UUID-based mode that works without upstream `encypher-ai` changes, normalizes all text to NFC before embedding, and reports verification spans as UTF-8 byte offsets over NFC-normalized text.

## Objectives
- Add working `manifest_mode="lightweight_uuid"` embedding support in `enterprise_api`.
- Normalize text to NFC across all `/sign/advanced` embedding modes.
- Ensure multi-embedding `/verify` returns `text_span` as UTF-8 byte offsets.
- Provide tests that validate NFC normalization + byte span semantics and verify round-trip.

## Tasks
- [x] 1.0 Tests (TDD)
- [x] 1.1 Add integration test for `/api/v1/sign/advanced` using `manifest_mode="lightweight_uuid"` and asserting NFC normalization + byte-offset spans
- [x] 2.0 Implementation
- [x] 2.1 Normalize `/sign/advanced` input to NFC before segmentation/hashing
- [x] 2.2 Implement `manifest_mode="lightweight_uuid"` in `EmbeddingService` using `UnicodeMetadata.embed_metadata(metadata_format="manifest")`
- [x] 2.3 Return multi-embedding `text_span` as UTF-8 byte offsets (NFC) for `/api/v1/verify` and `/api/v1/tools/decode`
- [x] 3.0 Verification
- [x] 3.1 Task — ✅ pytest ✅ ruff (enterprise_api)

## Success Criteria
- `enterprise_api/tests/test_sign_advanced_lightweight_uuid.py` passes.
- `uv run ruff check .` passes for `enterprise_api`.
- `uv run pytest` passes for `enterprise_api`.
- `/api/v1/verify` multi-embedding results return `text_span` as UTF-8 byte offsets over NFC-normalized text.

## Completion Notes

- Verified collision-free multi-embedding extraction by embedding the document-level lightweight UUID manifest at file end.
- Ensured `/api/v1/verify` and `/api/v1/tools/decode` prefer UTF-8 byte spans while remaining compatible with older embedding objects that only provide char spans.
- ✅ `uv run ruff check .` (enterprise_api)
- ✅ `uv run pytest` (enterprise_api)
