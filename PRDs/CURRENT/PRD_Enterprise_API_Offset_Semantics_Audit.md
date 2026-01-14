# PRD — Enterprise API Offset Semantics Audit

## Status
In Progress

## Current Goal
Audit all `enterprise_api` signing and verification endpoints to ensure that any offsets used for hashing / exclusion / signature verification are **UTF-8 byte offsets over NFC-normalized text**, across all supported embedding/manifest types.

## Overview
C2PA text hard-binding requires exclusion ranges to be specified as byte offsets into NFC-normalized UTF-8 text. The Enterprise API also supports non-C2PA embedding formats (basic/manifest) and multi-embedding flows. This PRD inventories all signing/verification entry points and verifies offset semantics are consistent end-to-end.

## Objectives
- Confirm every C2PA hard-binding exclusion range uses byte offsets (not Python char indices).
- Confirm any wrapper extraction or hashing logic never misinterprets char spans as byte offsets.
- Identify any embedding/manifest modes whose implementation is missing or inconsistent with byte-offset semantics.

## Tasks
- [x] 1.0 Inventory endpoints
- [x] 1.1 Enumerate signing entry points (/api/v1/sign, /api/v1/sign/advanced, batch sign)
- [x] 1.2 Enumerate verification entry points (/api/v1/verify, /api/v1/public/extract-and-verify, tools decode, batch verify)
- [x] 2.0 Audit flows
- [x] 2.1 Audit C2PA signing hard-binding exclusion generation (bytes + NFC)
- [x] 2.2 Audit C2PA verification hard-binding exclusion consumption (bytes + NFC)
- [x] 2.3 Audit multi-embedding extraction/verification (C2PA + basic formats)
- [x] 2.4 Audit non-C2PA embedding formats (basic/manifest) for any offset use
- [ ] 3.0 Tests (TDD)
- [ ] 3.1 Add regression tests for any offset semantic violation found
- [x] 3.2 Run `uv run ruff check .` + `uv run pytest` in `enterprise_api` (✅ ruff, ✅ pytest: 563 passed, 62 skipped)

## Success Criteria
- All signing/verification flows either:
  - use byte offsets for offsets that participate in hashing/verification, or
  - clearly avoid offsets (e.g., formats that sign payload bytes only)
- Any violations are covered by tests and fixed.

## Completion Notes

### Endpoint inventory

Signing entry points:
- `/api/v1/sign` -> `services/signing_executor.execute_signing` -> `UnicodeMetadata.embed_metadata(..., metadata_format="c2pa")`
- `/api/v1/sign/advanced` -> `services/embedding_executor.encode_document_with_embeddings` -> `services/embedding_service.EmbeddingService.create_embeddings`
- `/api/v1/batch/sign` -> `services/batch_service.BatchService` -> either `execute_signing` (mode=c2pa) or `encode_document_with_embeddings` (mode=embeddings)
- `/api/v1/stream/sign` -> `routers/streaming.stream_signing` -> `execute_signing`

Verification entry points:
- `/api/v1/verify` -> `services/verification_logic.execute_verification` (single) or `utils/multi_embedding.extract_and_verify_all_embeddings` (multi)
- `/api/v1/batch/verify` -> `services/batch_service` -> `execute_verification`
- `/api/v1/tools/decode` -> `UnicodeMetadata.verify_metadata` + optional “page chrome” extraction using `c2pa.hash.data.v1.exclusions`
- `/api/v1/public/extract-and-verify` -> `UnicodeMetadata.verify_metadata` (invisible embedding verification)

### Offset semantics findings

1) C2PA hard-binding exclusions
- Offsets used for hashing (`c2pa.hash.data.*.exclusions`) are byte offsets into NFC-normalized UTF-8 via `encypher.interop.c2pa.text_hashing.compute_normalized_hash`.
- Wrapper discovery uses `encypher.interop.c2pa.text_wrapper.find_and_decode` / `find_wrapper_info_bytes` and consumes byte offsets from `c2pa_text.find_wrapper_info`.

2) Multi-embedding spans
- `enterprise_api/app/utils/multi_embedding.py` spans (`EmbeddingInfo.span`) are **character indices** for UI/segment slicing.
- These spans are not used as exclusion ranges for hashing.

3) Basic / manifest embedding formats
- Basic-format embeddings verify signatures over embedded payload bytes; there is no exclusion offset semantics participating in hashing.
- Merkle per-sentence hashing uses `sha256(text.encode("utf-8"))` on normalized text, independent from C2PA hard-binding exclusions.

### Blocker: lightweight_uuid / hybrid manifest modes

`EmbeddingService.create_embeddings` calls `UnicodeMetadata.embed_lightweight_uuid(...)` for `manifest_mode="lightweight_uuid"`.
Our vendored `encypher-ai` implementation does **not** define `embed_lightweight_uuid`, so these modes cannot be audited or relied upon.
Decision captured in `.questions/TEAM_054_lightweight_uuid_manifest_mode.md`.

### Verification

- `enterprise_api`: `uv run ruff check .` ✅
- `enterprise_api`: `uv run pytest` ✅ (563 passed, 62 skipped)
