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

## Follow-up Session (WordPress v1 launch UX addendum)
- [x] Created PRD addendum `PRDs/CURRENT/PRD_WordPress_V1_Launch_UX_Addendum.md` with launch-critical UX objectives and acceptance criteria.
- [x] Added test-first contract coverage in `enterprise_api/tests/test_wordpress_provenance_plugin_contract.py` for:
  - settings launch readiness checklist + health card strings
  - expanded content provenance status labels + remediation guidance copy
- [x] Implemented settings launch UX panel in plugin admin settings page:
  - checklist steps + progress counter
  - connection health card (Connected and ready / Auth required / Disconnected)
  - API URL, tier, organization, last check, and remediation links
- [x] Added JS behavior in `assets/js/settings-page.js`:
  - dynamic checklist state updates
  - health card updates from connection checks
  - persisted hidden fields for `connection_last_status` + `connection_last_checked_at`
- [x] Expanded content table status UX in `class-encypher-provenance-admin.php`:
  - `Unsigned (needs signing)`
  - `Modified since signing`
  - `Verification failed`
  - per-row guidance (`Re-sign by updating this post.`, `Run Verify to refresh status.`)
- [x] Added styles for launch cards/checklist/health state in `assets/css/settings-page.css`.
- [x] Validation:
  - `uv run pytest enterprise_api/tests/test_wordpress_provenance_plugin_contract.py -q` ✅ (25 passed)
  - `uv run ruff check enterprise_api/tests/test_wordpress_provenance_plugin_contract.py` ✅
  - Puppeteer manual checks:
    - settings page shows checklist + connection health (`3 of 3 launch steps complete`, `Connected and ready`)
    - content page shows modified/failed/unsigned states + guidance
    - Verify/Edit actions still present

### Comprehensive Commit Message Suggestion (WordPress Launch UX Addendum Session End)
feat(wordpress): harden v1 launch UX with setup checklist, connection health, and content-state recovery guidance

- add launch-readiness checklist and progress state to Encypher settings page
- add connection health card with connected/auth-required/disconnected states and last-check metadata
- persist connection health fields in settings (`connection_last_status`, `connection_last_checked_at`)
- enhance settings JS to update checklist and health card from test-connection outcomes
- add settings-page styles for launch cards and health/checklist visualization
- expand content management statuses to unsigned/modified/verification-failed with actionable guidance copy
- preserve existing Verify/Edit actions while improving remediation discoverability
- add contract tests for launch checklist/health and expanded content status labels
- verify with `uv run pytest enterprise_api/tests/test_wordpress_provenance_plugin_contract.py -q` and Puppeteer admin-page checks

## Follow-up Session (WordPress optional polish pass)
- [x] Scoped optional polish to accessibility + terminology clarity + fallback guidance (no behavioral risk).
- [x] Added test-first contract assertions for:
  - live-region accessibility attributes on settings connection feedback surfaces
  - explanatory help copy for BYOK and hard binding
  - content table no-verification-link fallback copy
- [x] Implemented optional polish in `class-encypher-provenance-admin.php`:
  - `role="status" aria-live="polite"` on `#connection-status`, `#test-connection-result`, and `#encypher-connection-health-state`
  - BYOK explainer copy (`What is BYOK?`)
  - hard-binding explainer copy (`What is hard binding?`)
  - content-row fallback guidance: `No verification link yet. Sign this post first.`
  - added `rel="noopener noreferrer"` for Verify external link
- [x] Validation:
  - `uv run pytest enterprise_api/tests/test_wordpress_provenance_plugin_contract.py -k 'optional_polish_includes_accessibility_live_regions or optional_polish_includes_explanatory_help_copy' -q` ✅
  - `uv run pytest enterprise_api/tests/test_wordpress_provenance_plugin_contract.py -q` ✅ (27 passed)
  - `uv run ruff check enterprise_api/tests/test_wordpress_provenance_plugin_contract.py` ✅
  - Puppeteer:
    - content page shows fallback no-verification guidance and status labels
    - settings page exposes live-region attrs and helper copy (BYOK/hard binding)

### Comprehensive Commit Message Suggestion (WordPress Optional Polish Session End)
chore(wordpress): polish admin UX accessibility and helper guidance for v1 launch

- add aria live-region status semantics to settings connection feedback containers
- add clear explainer copy for BYOK and hard-binding options in settings
- add content-table fallback guidance when verification URL is not yet available
- harden verify action link with `rel="noopener noreferrer"`
- extend WordPress plugin contract tests for optional polish UX copy/attributes
- verify with focused + full contract test runs and Puppeteer admin validation

## Follow-up Session (Free cap visibility + sidebar branding audit)

- [x] Scope: verify whether free-plan `1,000 sign requests/month` cap is surfaced consistently in plugin UX and tighten Gutenberg sidebar branding around Encypher + C2PA compatibility.
- [x] Test-first contract updates in `enterprise_api/tests/test_wordpress_provenance_plugin_contract.py`:
  - added assertion for settings free-cap language
  - added sidebar contract test for Encypher/C2PA/free-cap/add-on copy
  - added admin-page contract test for free-cap prompts on content/account surfaces
- [x] Product copy + UI updates:
  - `includes/class-encypher-provenance-admin.php`
    - settings tier section now calls out `1,000 sign requests/month` included + usage-based pricing after cap
    - content page now shows free-tier inline notice with cap and billing CTA
    - account page now shows free-tier cap overflow guidance toward billing/add-ons/enterprise
  - `assets/js/editor-sidebar.js`
    - added Encypher/C2PA branding primer block in sidebar panel
    - added free-tier copy for 1,000/month cap, paid-after-cap, and add-on availability
    - updated pre-publish title to `Encypher Content Signing (C2PA-compatible)`
  - `assets/css/editor.css`
    - added styles for brand banner and plan-note content in sidebar
- [x] Validation:
  - `uv run pytest enterprise_api/tests/test_wordpress_provenance_plugin_contract.py -q` ✅ (29 passed)
  - `uv run ruff check enterprise_api/tests/test_wordpress_provenance_plugin_contract.py` ✅
  - `docker exec wordpress-provenance-plugin-wordpress-1 php -l /var/www/html/wp-content/plugins/encypher-provenance/includes/class-encypher-provenance-admin.php` ✅
  - Puppeteer checks ✅:
    - `/wp-admin/post-new.php`: Encypher/C2PA primer + free-cap/add-on copy visible
    - `/wp-admin/post.php?post=112&action=edit`: signed-state sidebar includes branding + free-cap copy + manifest upsell
    - `/wp-admin/admin.php?page=encypher-content`: free-cap + billing CTA visible
    - `/wp-admin/admin.php?page=encypher-account`: free-tier cap overflow guidance visible

### Comprehensive Commit Message Suggestion (Free cap + sidebar branding session end)
feat(wordpress): surface free plan cap messaging and reinforce Encypher/C2PA branding in editor sidebar

- add explicit free-plan cap copy (`1,000 sign requests/month`) and paid-after-cap guidance in settings tier panel
- surface cap + billing CTA on content management and account admin pages for free tier
- enhance Gutenberg sidebar with Encypher-branded C2PA compatibility primer and free-tier cap/add-on messaging
- rename pre-publish panel to `Encypher Content Signing (C2PA-compatible)` for clearer product attribution
- add editor CSS for branded sidebar banner and plan notes
- extend WordPress contract tests to lock in cap visibility and sidebar branding copy
- validate with full contract tests, lint, php syntax check, and Puppeteer admin UX checks

## Follow-up Session (Monthly API usage progress bars across plugin UX)

- [x] Scope: add visible monthly API usage progress (used/limit/remaining/progress) in expected user surfaces: dashboard, settings/tier, content, account, bulk-signing, and Gutenberg sidebars.
- [x] Test-first contract updates in `enterprise_api/tests/test_wordpress_provenance_plugin_contract.py`:
  - added `test_usage_progress_bars_surface_across_plugin_surfaces`
  - assertions cover admin rendering hooks, bulk usage container, and sidebar usage config/copy
- [x] Data flow + SSOT implementation:
  - `includes/class-encypher-provenance-admin.php`
    - settings defaults now include `usage.api_calls` snapshot
    - sanitize flow now persists normalized `usage` from account/quota or fallback
    - added `/account/quota` fetch path and usage normalizer (`fetch_remote_usage_quota`, `normalize_usage_snapshot`, `get_usage_snapshot`)
    - added shared usage renderer `render_usage_progress_bar(...)`
    - surfaced usage bars in dashboard, settings tier, content, and account pages
    - localized usage payload into `EncypherProvenanceConfig.usage` for editor sidebar
  - `includes/class-encypher-provenance-bulk.php`
    - added normalized usage snapshot + usage progress component at top of bulk-sign page
- [x] Sidebar UX updates:
  - `assets/js/editor-sidebar.js`
    - consumes `EncypherProvenanceConfig.usage`
    - renders usage meter with progress bar + remaining calls inside provenance panel
    - adds pre-publish usage summary line
  - `assets/css/editor.css`
    - styles sidebar usage meter and pre-publish usage summary
- [x] Admin styling:
  - `assets/css/settings-page.css`
    - shared usage progress styles for settings/content/account render targets
  - `assets/css/bulk-mark.css`
    - bulk-specific usage progress styling
- [x] Validation:
  - `uv run pytest enterprise_api/tests/test_wordpress_provenance_plugin_contract.py -q` ✅ (30 passed)
  - `uv run ruff check enterprise_api/tests/test_wordpress_provenance_plugin_contract.py` ✅
  - `docker exec wordpress-provenance-plugin-wordpress-1 sh -lc 'php -l ...class-encypher-provenance-admin.php && php -l ...class-encypher-provenance-bulk.php'` ✅
  - Puppeteer checks ✅:
    - `/wp-admin/admin.php?page=encypher` (dashboard usage bar)
    - `/wp-admin/admin.php?page=encypher-settings` (settings usage bar)
    - `/wp-admin/admin.php?page=encypher-content` (content usage bar)
    - `/wp-admin/admin.php?page=encypher-account` (account usage bar)
    - `/wp-admin/admin.php?page=encypher-bulk-mark` (bulk usage bar)
    - `/wp-admin/post-new.php` + `/wp-admin/post.php?post=112&action=edit` (sidebar usage meter in create/edit signed flow)

### Comprehensive Commit Message Suggestion (Monthly usage bars session end)
feat(wordpress): add monthly API usage progress bars across dashboard, bulk, settings, account, content, and editor sidebar

- persist normalized usage snapshot (`used/limit/remaining/percentage/reset`) in plugin settings
- fetch quota from `/account/quota` and gracefully fall back to last-known usage when remote lookup fails
- introduce shared admin usage renderer and show progress bars where users make signing/billing decisions
- add bulk page usage panel for monthly calls alongside bulk operation constraints
- localize usage into Gutenberg sidebar config and render usage meter in create/edit signed post flows
- style usage progress components for admin pages, bulk page, and editor sidebar
- extend WordPress contract tests to lock in usage bar presence across key plugin surfaces
- validate with pytest, ruff, php lint, and Puppeteer admin/editor checks

## Follow-up Session (Free tier API policy alignment: 1,000 + $0.02 overage + verification soft cap)

- [x] Policy alignment implemented in backend SSOT and auth/quota surfaces:
  - `enterprise_api/app/core/tier_config.py`
    - set free-tier `api_calls` limit to `1000` (from `10000`)
  - `enterprise_api/app/services/organization_bootstrap.py`
    - default `monthly_api_limit` now derived from tier SSOT via `get_tier_limits(...)` instead of hardcoded `10000`
  - `enterprise_api/app/routers/account.py`
    - `/account/quota` now clamps free-tier API limit to SSOT cap (`min(row.monthly_api_limit, 1000)`) to neutralize stale org rows
  - `enterprise_api/app/routers/usage.py`
    - usage response now clamps free-tier API call limits to SSOT cap
    - user-level usage response now uses tier API limit (not unlimited)
  - `enterprise_api/app/middleware/api_key_auth.py`
    - added `_effective_monthly_quota(...)`
    - clamps free-tier quotas to 1,000 for both key-service and local-DB auth paths

- [x] WordPress messaging updated to reflect product policy:
  - `includes/class-encypher-provenance-admin.php`
    - free-tier settings copy now: `1,000 sign requests/month included; $0.02/sign request after the monthly cap.`
    - added: `Verification requests remain available with a soft cap of 10,000/month.`
    - content/account notices updated with explicit overage messaging
  - `assets/js/editor-sidebar.js`
    - free-tier sidebar messaging now includes:
      - `$0.02/sign request after the monthly cap.`
      - `Verification stays available with a soft cap of 10,000 requests/month.`

- [x] Tests updated first (TDD) and verified:
  - `enterprise_api/tests/test_account.py`
    - enforce free-tier api limit expectations = 1000
    - add regression: stale DB limit `10000` still reports `1000` via quota endpoint
  - `enterprise_api/tests/test_usage_api.py`
    - enforce free-tier api limit expectations = 1000
  - `enterprise_api/tests/test_api_key_auth.py`
    - key-service free/starter payload with 10,000 now clamps to `monthly_quota == 1000`
  - `enterprise_api/tests/test_wordpress_provenance_plugin_contract.py`
    - assert explicit `$0.02/sign request...` copy and verification soft-cap copy in admin/sidebar

- [x] Validation executed:
  - `uv run pytest ...` targeted suite ✅ (6 passed)
  - `uv run ruff check ...` ✅
  - `php -l includes/class-encypher-provenance-admin.php` ✅
  - Puppeteer UI spot checks ✅
    - settings/content pages include new pricing + verification soft-cap copy
    - editor sidebar includes new overage + verification soft-cap copy

### Comprehensive Commit Message Suggestion (Free-tier policy alignment session end)
fix(tiers): enforce free-tier 1,000 monthly signing API cap and align UX copy with overage + verification soft cap

- set free-tier `api_calls` SSOT limit to 1,000/month in tier config
- remove hardcoded 10,000 bootstrap default by deriving org monthly limits from tier SSOT
- clamp free-tier API limits in `/account/quota`, `/usage`, and API-key auth paths to prevent stale DB values from showing/enforcing 10,000
- ensure user-level usage responses honor tier API limits instead of reporting unlimited
- update WordPress admin and editor sidebar copy to explicit pricing policy:
  - `$0.02/sign request after monthly cap`
  - `verification available with soft cap of 10,000/month`
- add regression tests for clamped free-tier limits and updated copy contracts
- validate with targeted pytest, ruff, php lint, and Puppeteer checks
