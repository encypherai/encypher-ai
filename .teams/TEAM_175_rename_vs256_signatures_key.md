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

## Investigation & Fix: "13 of 27 segments" Mismatch

Root cause: WordPress plugin sent raw HTML (with `<!-- wp:paragraph -->` block comments) to `/sign`. The segmenter treated HTML fragments as sentences, inflating the count from 18 actual sentences to ~27 "segments". Only 13 of those were real sentences that got VS256 signatures.

### WordPress Plugin Changes (`class-encypher-provenance-rest.php`)

Implemented the same extract→sign→embed pattern as `tools/encypher-cms-signing-kit`:

1. **`extract_text_from_html($html)`** — strips WP block comments, walks DOM text nodes, joins paragraphs with spaces. Uses DOMDocument for proper HTML parsing.
2. **`embed_signed_text_in_html($html, $signed)`** — string-based approach (avoids DOMDocument::saveHTML mangling). Extracts text fragments with byte offsets, matches against signed text, does direct substr_replace.
3. **`extract_html_text_fragments($html)`** — finds text runs between HTML tags/comments with byte offsets.
4. **Helper methods:** `walk_dom_for_text`, `collect_text_nodes`, `mb_str_split_safe`, `is_vs_char`, `is_vs_or_whitespace`
5. **`handle_sign_request`** updated to call extract→sign→embed flow.

### Results (post 36 "test post 1")

| Metric | Before | After |
|--------|--------|-------|
| DB total_segments | 27 | 18 |
| VS256 signatures in content | 13 | 18 |
| HTML structure preserved | n/a (was plain text) | ✅ wp:paragraph, `<p>` tags |
| Text fragments matched | n/a | 8/8 |

### Test Results
- ✅ PHP syntax check: passed
- ✅ 26/26 unit tests pass (`test-html-text-extraction.php`)
- ✅ Integration: re-signed post 36, 18 sigs = 18 DB segments
- ✅ HTML structure preserved after signing

Also updated display wording: "X of Y segments verified from this content" → "X verified from the original Y signed segments".

## Git Commit Message Suggestion
```
fix(wordpress-plugin): extract plain text from HTML before signing

WordPress plugin was sending raw HTML (with block comments like
<!-- wp:paragraph -->) to the /sign endpoint. The sentence segmenter
treated HTML fragments as sentences, inflating segment count from 18
actual sentences to 27. Only 13 got VS256 signatures.

Fix follows the same pattern as tools/encypher-cms-signing-kit:
- extract_text_from_html: strip WP block comments, walk DOM text nodes
- embed_signed_text_in_html: map signed text back into HTML text nodes
  using string-based replacement (avoids DOMDocument::saveHTML mangling)
- extract_html_text_fragments: find text runs with byte offsets

Results for test post: 18 sigs = 18 DB segments (was 13/27).
HTML structure (tags, comments, attributes) fully preserved.

Added 26 unit tests for extraction and embedding.

TEAM_175
```
