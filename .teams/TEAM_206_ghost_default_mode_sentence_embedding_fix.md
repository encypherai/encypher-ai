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

## Follow-up Session (Skipped-Card Text Mis-Mapping)
- [x] Reproduced marker mis-mapping where duplicated text in skipped Ghost cards (`kg-code-card`) consumed signed marker insertion before visible paragraph text — ✅ `uv run pytest enterprise_api/tests/test_ghost_integration.py -k skipped_card_text -q` (red → green)
- [x] Added regression test to protect visible-paragraph targeting with duplicated skipped-card text — ✅ `test_embeds_visible_paragraph_not_matching_skipped_card_text`
- [x] Fixed `embed_signed_text_in_html` to perform tokenized HTML traversal with skip-depth handling for Ghost card/script/style/code/pre zones, replacing only eligible visible text nodes in order
- [x] Re-ran focused lint + full Ghost integration tests — ✅ `uv run ruff check enterprise_api/app/services/ghost_integration.py enterprise_api/tests/test_ghost_integration.py` and ✅ `uv run pytest enterprise_api/tests/test_ghost_integration.py` (68 passed)

### Follow-up Handoff Notes
- Root cause: the earlier replacement strategy used global `str.replace(..., 1)` over full HTML, so the first matching duplicate string (inside skipped card/code content) could be mutated before the intended visible paragraph.
- Fix now aligns embedding replacement semantics with extraction semantics by skipping non-signable card/code/script/style/pre regions during replacement traversal.
- This prevents visible text corruption and marker leakage into non-visible card payloads, improving downstream verification reliability.

### Comprehensive Commit Message Suggestion (Session End)
fix(ghost): prevent skipped-card duplicate text from hijacking HTML marker embedding

- add regression test for duplicated content where `kg-code-card` text matches visible paragraph text
- update `embed_signed_text_in_html` to traverse tokenized HTML and apply signed replacements only to visible, non-skipped text nodes
- mirror extraction skip rules (`kg-*` non-text cards + `script/style/code/pre`) during embedding replacement to keep behavior consistent
- preserve HTML structure while avoiding marker insertion into hidden/non-signable card payloads
- verify with:
  - `uv run pytest enterprise_api/tests/test_ghost_integration.py -k skipped_card_text -q` (red → green)
  - `uv run ruff check enterprise_api/app/services/ghost_integration.py enterprise_api/tests/test_ghost_integration.py`
  - `uv run pytest enterprise_api/tests/test_ghost_integration.py` (68 passed)

## Follow-up Session (Ghost html-card wrapper hardening)
- [x] Pulled Ghost documentation references (Admin API create/update, webhooks, breaking changes/Lexical migration) and mapped implications for embedding behavior.
- [x] Added regression tests for Ghost `source=html` wrappers (`<!--kg-card-begin: html-->...<!--kg-card-end: html-->`) in `extractText`, `extractFragments`, and `embedSignedText`.
- [x] Hardened `integrations/ghost-provenance/src/html-utils.ts` to skip wrapped html-card regions during extraction and fragment matching without breaking byte-offset alignment for in-place embedding.
- [x] Added `integrations/ghost-provenance/EDGE_CASE_MATRIX.md` documenting doc-backed edge cases and local replay strategy.
- [x] Verification:
  - `npm test -- html-utils.test.ts` ✅ (56 passed)
  - `npm test` ✅ (69 passed)
  - `npm run lint` ⚠️ still blocked by pre-existing ESLint v9 flat-config migration (`eslint.config.*` missing)

## Follow-up Session (Fixture seeding + default micro/ecc/c2pa assertions)
- [x] Restored explicit signing config fields in TS integration (`ecc`, `embedC2pa`) and wired them into sign payload options (`ecc`, `embed_c2pa`) to guarantee Ghost defaults are passed through.
- [x] Added auto-seeding capability for local replay harness: if `LOCAL_GHOST_REPLAY_POST_ID` is not provided, test creates a published replay post via Ghost Admin API and reuses it for fixture replay.
- [x] Added replay assertions that loaded defaults are `manifestMode=micro`, `segmentationLevel=sentence`, `ecc=true`, `embedC2pa=true`.
- [x] Updated docs/env template with explicit `ECC` and `EMBED_C2PA` defaults plus replay usage instructions.
- [x] Verification:
  - `npm test` ✅ (69 passed, 1 skipped local replay)
  - `npm test -- local-replay.test.ts` ✅ (skipped by default unless `RUN_LOCAL_GHOST_REPLAY=1`)

## Follow-up Session (Live local replay execution + analysis)
- [x] Executed live replay against local Ghost with `RUN_LOCAL_GHOST_REPLAY=1` and fixture auto-seeding enabled.
- [x] Root cause #1 observed live: legacy `MANIFEST_MODE=micro_ecc_c2pa` env values caused API 422 for `manifest_mode` on `/sign` requests.
  - Fix: added TS signer alias normalization (`micro_ecc_c2pa` / `micro_ecc` -> canonical `micro` + explicit `ecc`/`embed_c2pa`).
  - Coverage: new signer regression test for alias normalization.
- [x] Root cause #2 observed live: Ghost `source=html` rewrite of `kg-code-card` fixture to plain `<pre><code>` caused duplicate matching to lose marker visibility in verification path.
  - Fix A: harden fragment extraction to skip non-signable class/tag regions for embedding-plan insertion.
  - Fix B: skip plain `pre/code` in `extractText` (not just class-based cards) so signable visible text remains aligned with verification.
  - Coverage: new regressions in `embedEmbeddingPlanIntoHtml` and `extractText` for duplicate code-card/plain pre-code edge cases.
- [x] Live replay result (post-fix):
  - `RUN_LOCAL_GHOST_REPLAY=1 ... npm test -- local-replay.test.ts` ✅ `Test Files 1 passed`, `Tests 1 passed`
  - `npm test` ✅ `Test Files 3 passed | 1 skipped`, `Tests 72 passed | 1 skipped`

## Follow-up Session (Dashboard onboarding wizard persistence)
- [x] Audited onboarding wizard lifecycle in dashboard layout and traced modal dismissal to transient setup-status payload states unmounting `SetupWizard` mid-flow.
- [x] Added E2E regression test `apps/dashboard/tests/e2e/setup-wizard.persistence.test.mjs` that reproduces the display-name-step drop risk via stale focus refetch + transient malformed `setup-status` response.
- [x] Fixed `DashboardLayout` setup visibility lifecycle by latching wizard open once `setup_completed === false` is observed, and only releasing latch after confirmed completion (`setup_completed === true`).
- [x] Verification:
  - `npm run test:e2e -- tests/e2e/setup-wizard.persistence.test.mjs` ✅ (34/34 passing in current suite run; includes new setup-wizard persistence test)
  - `npm run lint` ✅ (warnings only, pre-existing)
  - `npm run type-check` ✅

### Comprehensive Commit Message Suggestion (Onboarding Fix Session End)
fix(dashboard): keep mandatory setup wizard mounted through transient setup-status glitches

- add e2e regression coverage for onboarding modal persistence at the independent-creator display-name step
- simulate stale refetch + transient malformed `setup-status` payload to verify wizard remains visible
- latch setup wizard visibility in `DashboardLayout` once incomplete setup is detected
- clear latch only after backend confirms `setup_completed === true`
- prevent mid-flow unmounts that reset wizard local state and drop users out of pen-name entry
- verify with dashboard e2e suite invocation, lint, and type-check
