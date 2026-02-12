# TEAM_175 — Clean up API responses & C2PA manifest: remove internal details

## Summary
Multiple internal implementation details were leaking through the public API:
1. Verify response: `total_vs256_signatures` / `total_zw_signatures` keys, `format` field
2. Verify response: marketing site showed only basic manifest, not rich C2PA info
3. C2PA manifest assertions: org ID in `softwareAgent`, `manifest_mode` in metadata, org ID in `publisher.identifier`

## Changes

### enterprise-api (C2PA manifest content)
1. **`app/services/embedding_service.py`** — removed `manifest_mode` from `document_metadata_jsonld`; replaced org ID with org name in `publisher.identifier`; removed org ID from `softwareAgent` in `c2pa.created` action
2. **`app/services/embedding_executor.py`** — thread `organization_name` through to `create_embeddings`
3. **`tests/test_c2pa_conformance_sign_verify.py`** — updated test to assert `manifest_mode` absent; added regression test `test_c2pa_manifest_does_not_leak_internal_details`

### verification-service
4. **`app/api/v1/endpoints.py`** — removed `format` from both ZW and VS256 manifest dicts; renamed `total_zw_signatures` → `total_signatures`
5. **`tests/test_verify_manifest_mode_format.py`** — updated all manifest_mode tests to assert `format` absent; added regression test for `total_signatures`

### marketing-site
6. **`src/components/tools/EncodeDecodeTool.tsx`** — rewrote "C2PA Manifest Data" section to display rich C2PA info; removed `manifest_mode` badge; changed "document" → "content"
7. **`src/lib/enterpriseApiTools.ts`** — fixed `embeddingsFound` to prefer `total_embeddings` from upstream
8. **`src/lib/enterpriseApiTools.test.ts`** — updated fixtures; added `total_embeddings` priority test

### docs
9. **`.teams/TEAM_170_verify_manifest_mode_format.md`** — updated example response

## C2PA Manifest (before → after)

| Field | Before | After |
|-------|--------|-------|
| `c2pa.actions[0].softwareAgent` | `Encypher Enterprise API/org_07dd...` | `Encypher Enterprise API` |
| `c2pa.metadata.manifest_mode` | `micro_ecc_c2pa` | *(removed)* |
| `c2pa.metadata.publisher.identifier` | `org_07dd7ff77fa7e949` | `Demo Organization` (org name) |
| verify `details.manifest.format` | `micro_ecc_c2pa` | *(removed)* |
| verify `details.manifest.total_zw_signatures` | `13` | renamed to `total_signatures` |

## Test Results
- ✅ 128/128 enterprise-api tests pass (incl. new regression test)
- ✅ 11/11 manifest mode format tests pass (verification-service)
- ✅ 68/68 total verification-service tests pass
- ✅ 86/86 marketing-site tests pass

## Investigation: "13 of 27 segments" Mismatch

Root cause identified: WordPress plugin sends raw HTML (with `<!-- wp:paragraph -->` block comments) to `/sign`. The segmenter treats HTML fragments as sentences, inflating the count from 18 actual sentences to ~27 "segments". Only 13 of those are real sentences that get VS256 signatures.

**Fix:** Extract plain text from HTML before signing (same pattern as `tools/encypher-cms-signing-kit`). PRD created: `PRDs/CURRENT/PRD_WordPress_HTML_Text_Extraction.md`.

Also updated display wording: "X of Y segments verified from this content" → "X verified from the original Y signed segments".

## Git Commit Message Suggestion
```
fix(enterprise-api,verification-service,marketing-site): remove internal details from public API

C2PA manifest:
- Remove org ID from softwareAgent in c2pa.created action
- Remove manifest_mode from c2pa.metadata assertion
- Use org name instead of org ID in publisher.identifier

Verify response:
- Remove `format` field from manifest dict (leaked embedding method)
- Rename total_vs256_signatures / total_zw_signatures → total_signatures
- Fix embeddings_found count: use total_embeddings from upstream
- Marketing site: display rich C2PA info, change "document" → "content"

Added regression tests across all three services.

TEAM_175
```
