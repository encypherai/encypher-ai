# TEAM_206: Ghost Default Mode Sentence Embedding Fix

**Active PRD**: `PRDs/CURRENT/PRD_Ghost_Provenance_Integration.md`
**Working on**: Investigate/fix default Ghost webhook signing mode (`micro_ecc_c2pa`) and sentence-level behavior
**Started**: 2026-02-17 16:48 UTC
**Status**: completed

## Session Progress
- [x] Investigated default mode + segmentation path — ✅ npm test
- [x] Added regression tests for HTML entity-safe embedding + sign payload mode assertions — ✅ npm test
- [x] Fixed root cause in HTML entity decoding for signed text re-embedding — ✅ npm test
- [x] Implemented direct `embedding_plan` codepoint insertion into original HTML (no full round-trip replacement) — ✅ npm test

## Changes Made
- `integrations/ghost-provenance/src/html-utils.ts`: Expanded `decodeHtmlEntities` to handle common named entities (`&mdash;`, `&ndash;`, smart quotes, ellipsis, bullet) plus decimal/hex numeric entities to keep signed-text alignment intact during HTML re-embedding.
- `integrations/ghost-provenance/src/html-utils.ts`: Added `embedEmbeddingPlanIntoHtml()` for direct byte-offset marker insertion from `embedding_plan` codepoint operations, aligned to `extractText` normalization output.
- `integrations/ghost-provenance/tests/html-utils.test.ts`: Added regression test for entity-containing HTML ensuring sentence-level markers are embedded in the correct paragraph/sentence.
- `integrations/ghost-provenance/tests/html-utils.test.ts`: Added tests for direct embedding-plan insertion (cross-paragraph insertion, index `-1` insertion, out-of-range validation).
- `integrations/ghost-provenance/tests/signer.test.ts`: Added assertions that outbound sign payload includes `manifest_mode: micro_ecc_c2pa` and `segmentation_level: sentence`.
- `integrations/ghost-provenance/src/signer.ts`: Updated signing flow to prefer direct `embedding_plan` insertion into HTML, then fallback to reconstructed/returned `signed_text`; C2PA compliance now checks extracted final HTML text.

## Blockers
- None.

## Handoff Notes
- Root cause was not default config: default mode/segmentation were already set correctly. Breakage happened during HTML re-embedding when content used entities like `&mdash;`, causing signed markers to be dropped from expected sentence positions.
- Service now uses a robust primary path that applies `embedding_plan` operations directly against original HTML text-node byte offsets, reducing dependence on signed-text round-trip matching.
- Verification:
  - `npm test` ✅ (66/66)
  - `npm run lint` ⚠️ fails due to missing ESLint v9 flat config (`eslint.config.*`) in this package, pre-existing project setup issue.

### Suggested Commit Message
fix(ghost-provenance): use embedding_plan codepoint insertion for robust HTML marker placement

- add regression test for embedSignedText with entity-containing HTML (`&mdash;`)
- expand HTML entity decoding in signer embedding path (named + numeric entities)
- add direct embedEmbeddingPlanIntoHtml path aligned to extractText codepoint stream
- update signer flow to prefer embedding_plan insertion with signed_text fallback
- assert signer forwards manifest_mode=micro_ecc_c2pa and segmentation_level=sentence
- verify ghost-provenance test suite passes (66/66)
