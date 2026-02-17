# TEAM_206: WordPress signer identity mismatch

**Active PRD**: `PRDs/CURRENT/PRD_WordPress_Provenance_Plugin_UI_Verification.md`
**Working on**: Task 4.2
**Started**: 2026-02-17 13:58 UTC-05:00
**Status**: in_progress

## Session Progress
- [x] 4.2.1 — Investigate signer identity source
- [x] 4.2.2 — Add regression tests for signing identity priority (pending runtime execution)
- [x] 4.2.3 — Implement minimal identity-priority fix in REST normalization path
- [x] 4.2.4 — Trace browser extension identity/rendering path and patch opaque ID handling
- [x] 4.2.5 — Add extension regression tests and run targeted unit tests
- [x] 4.2.6 — Patch tooltip hover layering (badge/tooltip stacking context + z-index)
- [x] 4.2.7 — Implement hover/click UX refinement (shared header tooltip + manifest disclosure)
- [x] 4.2.8 — Fix duplicate badge/pending race via per-element detection dedupe
- [ ] 4.2.9 — Manual extension verification on affected page

## Changes Made
- `integrations/wordpress-provenance-plugin/plugin/encypher-provenance/includes/class-encypher-provenance-rest.php`: Reordered signing identity candidates to prefer publisher name before publisher identifier.
- `integrations/wordpress-provenance-plugin/plugin/encypher-provenance/tests/test-html-text-extraction.php`: Added reflection hook + two regression tests for identity preference/fallback behavior.
- `integrations/chrome-extension/background/verification-utils.js`: Treat `user_/org_/usr_` IDs (including UUID-style hyphenated IDs) as opaque; avoid using them as display identity and improve signer fallback.
- `integrations/chrome-extension/content/detector.js`: Align opaque ID detection for detail panel + tooltip; avoid rendering raw IDs; add 15s timeout guard around VERIFY_CONTENT messaging so pending badge cannot stay indefinitely.
- `integrations/chrome-extension/tests/verification-utils.test.js`: Added regression tests for opaque explicit `user_*` identities and signer-label fallback behavior.
- `integrations/chrome-extension/content/badge.css`: Increased badge/tooltip stacking behavior (`z-index` + `isolation`) to keep hover tooltip above host-page overlays.
- `integrations/chrome-extension/tests/badge-css.test.js`: Added regression tests asserting tooltip layering CSS contract.
- `integrations/chrome-extension/content/detector.js`: Added compact hover tooltip renderer using same verification header, now showing only Status + Signing Identity; click panel remains expanded with Format/Verification link and now includes optional C2PA manifest disclosure (`<details>`).
- `integrations/chrome-extension/background/service-worker.js`: Passed through `c2pa_manifest` and `c2pa_assertions` so content script can render full-manifest dropdown on click.
- `integrations/chrome-extension/content/badge.css`: Added styles for tooltip card rows and click-panel C2PA manifest disclosure block.
- `integrations/chrome-extension/tests/detector-ui-contract.test.js`: Added UI contract tests for hover tooltip and C2PA manifest disclosure rendering hooks.
- `integrations/chrome-extension/tests/service-worker-contract.test.js`: Added contract test ensuring C2PA assertions are forwarded in verify payload.
- `integrations/chrome-extension/content/detector.js`: Added `_dedupeDetectionsByElement` and queued-element guards inside `_detectEmbeddings` + merged-scan dedupe in `scanPage` to prevent duplicate badges/pending states for the same container.
- `integrations/chrome-extension/tests/detector-ui-contract.test.js`: Added contract assertions that dedupe helper is defined and applied to both uncached/cached detection paths.

## Blockers
- Local runtime missing for test execution:
  - `php` not installed on host shell.
  - Docker daemon not running, so WordPress container test path is unavailable.
- Full chrome-extension `npm test` currently has unrelated pre-existing failures outside verification-utils scope; targeted test suite was executed and passed.

## Handoff Notes
- Root cause identified in plugin identity resolver ordering: `c2pa.metadata.publisher.identifier` was selected before `publisher.name`, causing internal `user_*` IDs to display in verification modal.
- Additional root cause identified in chrome extension: opaque ID regex only matched hex IDs without hyphens, so UUID-style `user_*` IDs leaked into UI as Signing Identity/Signed by.
