# Ghost Embedding Edge-Case Matrix

## Scope

This matrix tracks high-risk Ghost content patterns that can break extraction or re-embedding, and defines expected behavior plus coverage status.

Primary integration paths:
- Node integration: `integrations/ghost-provenance/src/html-utils.ts`
- Hosted Python integration: `enterprise_api/app/services/ghost_integration.py`

## Documentation Inputs (Ghost)

- Admin API create post (html + lexical; html conversion is lossy):
  - https://docs.ghost.org/admin-api/posts/creating-a-post
- Admin API update post (`updated_at` required for writes):
  - https://docs.ghost.org/admin-api/posts/updating-a-post
- Webhook events:
  - https://docs.ghost.org/webhooks/
- Breaking changes (Mobiledoc deprecation, Lexical migration):
  - https://docs.ghost.org/changes/

## Edge-Case Matrix

| ID | Pattern | Risk | Expected behavior | Coverage |
|---|---|---|---|---|
| GHE-001 | Duplicate visible text where first match is in skipped `kg-code-card` | Marker inserted into wrong node | Marker only in visible signable text | ✅ Python + TS |
| GHE-002 | HTML entities (`&mdash;`, numeric entities) | text/sign mismatch | Entity-safe matching preserves sentence marker placement | ✅ TS + Python |
| GHE-003 | `<!--kg-card-begin: html-->...<!--kg-card-end: html-->` wrapper | Raw html-card payload signed/mutated | Wrapped region excluded from extraction + embedding | ✅ TS |
| GHE-004 | Script/style/code/pre blocks with duplicate text | Hidden content mutated | Hidden/non-signable content untouched | ✅ Python + TS |
| GHE-005 | Bookmark/callout/toggle card text | Missing signable text | Card text extracted and signed | ✅ TS |
| GHE-006 | Multi-paragraph insertion with embedding plan | offset drift | plan inserts at codepoint offsets across boundaries | ✅ TS |
| GHE-007 | insertion index `-1` | pre-first-char errors | marker inserted before first visible char | ✅ TS |
| GHE-008 | Out-of-range plan indices | corruption/crash | reject plan (`null`) and use fallback path | ✅ TS |
| GHE-009 | Legacy Mobiledoc/Lexical migration output | structure drift | signer operates on rendered HTML safely | ✅ TS unit + local replay |
| GHE-010 | Round-trip Ghost reserialization after update | verification regressions | extraction(in) == extraction(out, stripping markers) | ✅ local replay |
| GHE-011 | Unicode graphemes (emoji, ZWJ) | split/index mismatch | codepoint-safe insertion and verification | ✅ TS unit + local replay |
| GHE-012 | Malformed but accepted HTML | parser divergence | no crashes; conservative fallback | ✅ TS unit + local replay |

## Local Replay Hardening Plan (Next)

1. Boot local stack:
   - `./start-dev.sh` (repo root)
   - `docker compose up --build` in `integrations/ghost-provenance`
2. Seed fixture posts representing GHE-001..GHE-012.
3. Trigger publish/update webhooks.
4. Re-read via Ghost Admin API and assert:
   - visible render unchanged except invisible markers
   - skipped/card wrapper regions unchanged
   - verification endpoint returns success
5. Record fixture-by-fixture results in this file.

## Current Hardening Notes

- `source=html` wrapped html-card regions are now explicitly excluded from TS extraction and fragment embedding path, preventing marker insertion into raw html-card payloads.
- This aligns behavior with Ghost docs guidance that source-html conversion can be lossy and should be treated carefully.
- Added migrated-wrapper coverage (`kg-card-begin: markdown`, lexical-like spans, html-card class wrappers), malformed HTML recovery assertions, and Unicode grapheme/ZWJ insertion assertions.
- Live local replay now includes fixtures for migrated wrappers, malformed HTML, and grapheme-heavy content, and all replay fixtures pass with default Ghost micro+ecc+c2pa settings.
