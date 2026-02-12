# TEAM_170 — Verify Response: manifest_mode, Segment Location, Multi-Embedding

## Summary
Three-part enhancement to the verification API:
1. **manifest_mode fix**: Return actual `manifest_mode` (e.g. `micro_ecc_c2pa`) instead of hardcoded `vs256_embedding`
2. **Segment location**: Return paragraph/sentence index for each detected embedding ("paragraph 3, sentence 2")
3. **Multi-signature resolution**: Resolve ALL detected signatures (not just the first) so verifying a copied paragraph shows all embeddings

## Problem
- Verifying `micro_ecc_c2pa` content showed `format: "vs256_embedding"` — wrong
- No segment location info was returned in the public verify response
- Only the first signature was resolved; copying a paragraph lost the other embeddings

## Changes

### enterprise_api/app/api/v1/public/c2pa.py
- Added `SegmentLocationResponse` schema
- Expanded `ZWResolveResponse` with `segment_location`, `total_segments`, `leaf_index`, `manifest_data`
- Extracted shared `_RESOLVE_SQL` and `_row_to_resolve_response()` helper
- **New endpoint**: `POST /zw/resolve` — bulk resolve multiple UUIDs in one call
- Updated GET resolve to use shared SQL/helper

### services/verification-service/app/models/enterprise_schemas.py
- Added `SegmentLocationInfo` and `EmbeddingDetail` schemas
- Added `embeddings`, `total_embeddings`, `total_segments_in_document` to `VerifyVerdict`

### services/verification-service/app/api/v1/endpoints.py
- Added `_bulk_resolve_segment_uuids()` — tries POST bulk endpoint, falls back to sequential GETs
- **ZW fallback**: Resolves ALL ZW signatures via bulk resolve, builds embeddings list
- **VS256 fallback**: Resolves ALL VS256 signatures via bulk resolve, builds embeddings list
- **C2PA info**: Prefers DB-backed manifest (`db_backed_manifest` validation_type) over inline C2PA wrapper
- Wires `embeddings`, `total_embeddings`, `total_segments_in_document` into `VerifyVerdict`

### services/verification-service/tests/test_verify_manifest_mode_format.py (NEW)
- 12 tests: manifest_mode (6), segment location (1), multi-signature (1), C2PA passthrough (2), defaults (2)

### services/verification-service/tests/test_verify_zw_fallback.py
- Updated mock to handle POST for bulk resolve

## Example Verify Response (single copied sentence)
```json
{
  "data": {
    "valid": true,
    "reason_code": "OK",
    "signer_id": "org_acme",
    "c2pa": {
      "validated": true,
      "validation_type": "db_backed_manifest",
      "manifest_hash": "abc123",
      "assertions": [...]
    },
    "embeddings": [
      {
        "segment_uuid": "cc4977c8-...",
        "leaf_index": 7,
        "segment_location": {"paragraph_index": 2, "sentence_in_paragraph": 1},
        "manifest_mode": "micro_ecc_c2pa"
      }
    ],
    "total_embeddings": 1,
    "total_segments_in_document": 15,
    "details": {
      "manifest": {"segment_uuid": "cc4977c8-...", "total_signatures": 1}
    }
  }
}
```

## Test Results
- ✅ 67/67 verification-service tests pass (no regressions)

## Git Commit Message Suggestion
```
feat: verify response returns segment location, multi-embedding, and C2PA manifest

Enhance the public verification API to support the "copy a sentence or
paragraph to verify" use case:

- Return actual manifest_mode instead of hardcoded "vs256_embedding"
- Add segment_location (paragraph_index, sentence_in_paragraph) for each
  detected embedding so the UI can show "paragraph 3, sentence 2"
- Resolve ALL detected signatures (not just the first) via new bulk
  resolve endpoint, returning an embeddings array
- Show DB-backed C2PA manifest first when available (micro_c2pa /
  micro_ecc_c2pa modes)
- Add POST /zw/resolve bulk endpoint to enterprise API
- 12 new tests, 67 total passing

TEAM_170
```
