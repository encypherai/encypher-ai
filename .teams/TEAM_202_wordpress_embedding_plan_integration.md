# TEAM_202: WordPress Embedding Plan Integration

**Active PRD**: `PRDs/CURRENT/PRD_WordPress_Provenance_Plugin_UI_Verification.md`
**Working on**: Task 4.4 (tests/manual verification) + sign response compatibility follow-up
**Started**: 2026-02-16 18:50 UTC
**Status**: in_progress

## Session Progress
- [x] 4.4 — completed (contract + local e2e)

## Changes Made
- Updated WordPress REST signing flow to request and consume `embedding_plan` from `/sign` with fallback to `signed_text`/`embedded_content`.
- Added plugin-side helpers for embedding-plan application in `class-encypher-provenance-rest.php`.
- Updated contract coverage in `enterprise_api/tests/test_wordpress_provenance_plugin_contract.py` for embedding-plan usage and canonical tier IDs.
- Migrated local E2E tests from deprecated `/api/v1/sign/advanced` to `/api/v1/sign` + `options` payload:
  - `enterprise_api/tests/e2e_local/test_local_sign_verify.py`
  - `enterprise_api/tests/e2e_local/test_local_zw_embedding.py`
- Normalized local E2E assertions for unified response envelopes (`data.document`) and sign status codes (`200/201`).
- Switched WordPress plugin verification flow from `/api/v1/verify/advanced` to `/api/v1/verify` in `handle_verify_request` (public verify path, no auth).
- Removed advanced-only verify payload fields from plugin verify requests and set verification mode to `standard`.
- Strengthened contract test to enforce `'/verify/advanced'` is not present in plugin REST implementation.
- Fixed false tamper verification in WordPress parser by removing unconditional inter-fragment spaces in `extract_text_for_verify` and adding block-aware gap handling (`gap_requires_space`).
- Added contract regression test to guard verify text extraction behavior:
  - `test_verify_text_extraction_preserves_inline_boundaries_without_forced_spaces`.
- Updated verify response normalization to:
  - prefer `signing_identity` for `signer_name` (with C2PA metadata assertion fallback), and
  - expose full C2PA assertion payload in `metadata` when available (instead of only `details.manifest`).
- Updated frontend modal summary to prioritize `data.signing_identity` over `data.signer_name`/`data.signer_id`.
- Added contract regression test:
  - `test_verify_response_prefers_signing_identity_and_full_manifest_payload`.

## Blockers
- Local stack mismatch observed: plugin now correctly calls `/api/v1/verify`, but local `enterprise-api` container returns `404` for that route. Upstream API/router alignment needed if local environment must support this endpoint.

## Handoff Notes
- Verification completed:
  - `uv run pytest enterprise_api/tests/test_wordpress_provenance_plugin_contract.py` -> 17 passed.
  - `LOCAL_API_TESTS=true uv run pytest enterprise_api/tests/e2e_local -m e2e -v` -> 7 passed.
- Local unblock outcome: compose services were healthy; perceived hangs were from attached compose commands and missing bounded log invocations.
- UI/manual E2E (WordPress admin):
  - Logged into `http://localhost:8888/wp-admin` as `admin`.
  - Created and published new post ID `87`: `Embedding Plan UI E2E 2026-02-16T19:33:39.110Z`.
  - Screenshot captured: `wp-ui-e2e-published-post-87`.
  - Enterprise API logs show plugin-originated sign call around publish time:
    - `POST /api/v1/sign - Status: 201` at `19:33:57` from Docker client `172.18.0.22`.
  - Public post payload confirms embedded marker codepoints present in content (`\U000e....` escapes), indicating signed-marker insertion was applied.
- Verify endpoint migration validation:
  - `uv run pytest enterprise_api/tests/test_wordpress_provenance_plugin_contract.py -q` -> 17 passed.
  - Runtime probe after patch: `POST /api/v1/verify` observed in enterprise-api logs from WordPress client (`172.18.0.22`), confirming plugin no longer calls `/verify/advanced`.
  - Current local API response for `/api/v1/verify`: `404 Not Found` (backend route availability issue, not plugin endpoint selection).
- Verification parity fix validation:
  - `uv run pytest enterprise_api/tests/test_wordpress_provenance_plugin_contract.py -q` -> 18 passed.
  - Runtime verify checks after parser patch:
    - Post `89`: `valid=true`, `tampered=false`, `reason_code=OK`, `verification_mode=standard`.
    - Post `87`: `valid=true`, `tampered=false`, `reason_code=OK`, `verification_mode=standard`.
- Manifest + signer identity display validation:
  - `uv run pytest enterprise_api/tests/test_wordpress_provenance_plugin_contract.py -q` -> 19 passed.
  - Runtime verify (`post_id=89`) now returns:
    - `signing_identity = "Test User at Encypher"`
    - `signer_name = "Test User at Encypher"`
    - `metadata.assertions` populated (`count=5`) plus sentence summary fields (`total_signatures`).

## Suggested Commit Message
- `fix(wordpress-plugin): prefer signing identity and surface full db-backed C2PA manifest in verify modal`
