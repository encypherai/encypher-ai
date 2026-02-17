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
- [x] Investigated hosted Ghost webhook ingress + signing failures — ✅ uv run pytest enterprise_api/tests/test_ghost_integration.py
- [x] Fixed hosted webhook URL generation to always use API base domain — ✅ uv run pytest enterprise_api/tests/test_ghost_integration.py
- [x] Migrated Ghost hosted integration schema to canonical sign options (`micro` + `ecc` + `embed_c2pa`) with DB migration — ✅ uv run pytest enterprise_api/tests/test_ghost_integration.py

## Changes Made
- `integrations/ghost-provenance/src/html-utils.ts`: Expanded `decodeHtmlEntities` to handle common named entities (`&mdash;`, `&ndash;`, smart quotes, ellipsis, bullet) plus decimal/hex numeric entities to keep signed-text alignment intact during HTML re-embedding.
- `integrations/ghost-provenance/src/html-utils.ts`: Added `embedEmbeddingPlanIntoHtml()` for direct byte-offset marker insertion from `embedding_plan` codepoint operations, aligned to `extractText` normalization output.
- `integrations/ghost-provenance/tests/html-utils.test.ts`: Added regression test for entity-containing HTML ensuring sentence-level markers are embedded in the correct paragraph/sentence.
- `integrations/ghost-provenance/tests/html-utils.test.ts`: Added tests for direct embedding-plan insertion (cross-paragraph insertion, index `-1` insertion, out-of-range validation).
- `integrations/ghost-provenance/tests/signer.test.ts`: Added assertions that outbound sign payload includes `manifest_mode: micro_ecc_c2pa` and `segmentation_level: sentence`.
- `integrations/ghost-provenance/src/signer.ts`: Updated signing flow to prefer direct `embedding_plan` insertion into HTML, then fallback to reconstructed/returned `signed_text`; C2PA compliance now checks extracted final HTML text.
- `enterprise_api/app/routers/integrations.py`: Updated webhook URL builder to always use configured `api_base_url`, preventing issuance of non-routable `encypherai.com` webhook URLs for Ghost.
- `enterprise_api/app/services/ghost_integration.py`: Added legacy manifest alias normalization at sign boundary and canonical micro option passthrough (`ecc`, `embed_c2pa`) to `SignOptions`.
- `enterprise_api/app/schemas/integration_schemas.py`: Switched Ghost manifest/segmentation validation to signing SSOT constants and added canonical micro flags (`ecc`, `embed_c2pa`) to create/response schemas.
- `enterprise_api/app/models/ghost_integration.py`: Added persisted `ecc` and `embed_c2pa` columns for hosted Ghost integration config.
- `enterprise_api/alembic/versions/20260217_182300_ghost_integration_sign_options_alignment.py`: Added forward migration to create `ecc`/`embed_c2pa` columns and normalize legacy `manifest_mode` values (`micro_ecc_c2pa`, `micro_ecc`) to canonical `micro`.
- `enterprise_api/tests/test_ghost_integration.py`: Added regression tests for legacy mode normalization and explicit micro flags passthrough; updated schema tests for new canonical fields.

## Blockers
- None.

## Handoff Notes
- Root cause was not default config: default mode/segmentation were already set correctly. Breakage happened during HTML re-embedding when content used entities like `&mdash;`, causing signed markers to be dropped from expected sentence positions.
- Service now uses a robust primary path that applies `embedding_plan` operations directly against original HTML text-node byte offsets, reducing dependence on signed-text round-trip matching.
- Verification:
  - `npm test` ✅ (66/66)
  - `npm run lint` ⚠️ fails due to missing ESLint v9 flat config (`eslint.config.*`) in this package, pre-existing project setup issue.
  - `uv run pytest enterprise_api/tests/test_ghost_integration.py` ✅ (66 passed)
  - `uv run ruff check enterprise_api/app/schemas/integration_schemas.py enterprise_api/app/models/ghost_integration.py enterprise_api/app/routers/integrations.py enterprise_api/app/services/ghost_integration.py enterprise_api/tests/test_ghost_integration.py enterprise_api/alembic/versions/20260217_182300_ghost_integration_sign_options_alignment.py` ✅

### Suggested Commit Message
fix(ghost): align hosted integration with canonical sign schema and unblock webhook signing

- force generated Ghost webhook URLs to configured API domain (`api_base_url`) to avoid host-routing mismatches
- add legacy manifest alias normalization for persisted `micro_ecc_c2pa`/`micro_ecc` values at sign boundary
- extend hosted Ghost integration config with canonical micro controls (`ecc`, `embed_c2pa`)
- switch Ghost integration schema validators to signing SSOT constants (`MANIFEST_MODES`, `SEGMENTATION_LEVELS`)
- add Alembic migration to persist `ecc`/`embed_c2pa` and normalize legacy `manifest_mode` values to `micro`
- pass canonical micro flags through webhook and manual-sign orchestration into `SignOptions`
- add regression tests for legacy alias coercion and explicit micro flag passthrough
- verify with `uv run pytest enterprise_api/tests/test_ghost_integration.py` and focused `ruff check`
