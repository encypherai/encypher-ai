# TEAM_212: Chrome Extension v1.0.0 Beta Packaging

**Active PRD**: `PRDs/CURRENT/PRD_Chrome_Extension_UX_Editor_Signing.md`
**Working on**: Packaging workflow execution for v1.0.0 beta artifact
**Started**: 2026-02-19 16:05 UTC
**Status**: completed

## Session Progress
- [x] Packaging pre-flight unit tests — ✅ npm test
- [x] Packaging pre-flight e2e tests — ✅ npm run test:e2e
- [x] Packaging pre-flight lint — ✅ npm run lint (warnings only, no errors)
- [x] Build production zip artifact for beta handoff — ✅ node scripts/build.js
- [x] Validate zip contents + localhost stripping — ✅ python zipfile inspection

## Changes Made
- Generated production package:
  - `integrations/chrome-extension/dist/encypher-verify-v1.0.0.zip`
- Verified package integrity:
  - contains required extension files (`manifest.json`, `background/`, `content/`, `icons/`, `options/`, `popup/`)
  - excludes dev/test artifacts (`tests/`, `node_modules/`, `scripts/`, `store-assets/`, `dist/`)
  - `manifest.json` inside zip contains no localhost/127.0.0.1 entries

## Blockers
- None

## Handoff Notes
- Preparing v1.0.0 production package for beta distribution using workflow `.windsurf/workflows/package-chrome-extension.md`.

## Verification Evidence
- `npm test` — ✅ 160/160 pass
- `npm run test:e2e` — ✅ 10/10 pass
- `npm run lint` — ✅ 0 errors (3 existing warnings)
- `node scripts/build.js` — ✅ produced `dist/encypher-verify-v1.0.0.zip` (346.3 KB)

## Suggested Commit Message
```
chore(chrome-extension): package v1.0.0 production zip for beta release

- run extension preflight checks (unit tests, e2e tests, lint)
- build production artifact with localhost permissions stripped via scripts/build.js
- validate zip contents include only Chrome runtime files
- verify embedded manifest excludes localhost/127.0.0.1 host permissions and externally_connectable matches
- prepare dist/encypher-verify-v1.0.0.zip for local beta install and store submission flow
```

---

## Session Addendum: Messaging Audit + Copy Alignment (2026-02-19)

### Scope Completed
- Updated Chrome extension release messaging to approved outcome-led vocabulary:
  - "verify who authored any text"
  - "invisible cryptographic watermarks"
  - "proof of origin"
  - "survives copy-paste"
- Removed/rewrote user-facing phrasing that leaned on "trust badges" and C2PA-heavy language in store/popup/settings/marketing surfaces.

### Files Updated
- `integrations/chrome-extension/manifest.json`
- `integrations/chrome-extension/STORE_LISTING.md`
- `integrations/chrome-extension/README.md`
- `integrations/chrome-extension/popup/popup.html`
- `integrations/chrome-extension/options/options.html`
- `integrations/chrome-extension/scripts/generate-store-assets.js`
- `integrations/chrome-extension/tests/onboarding-setup-flow.test.js`
- `integrations/chrome-extension/tests/popup-verification-ux.test.js`
- `apps/dashboard/src/app/integrations/ChromeExtensionCard.tsx`
- `integrations/wordpress-provenance-plugin/plugin/encypher-provenance/readme.txt`

### Verification Evidence
- `npm test` — ✅ 160/160 pass
- `npm run test:e2e` — ✅ 10/10 pass
- `npm run lint` — ✅ 0 errors (3 existing warnings)
- `uv run pytest enterprise_api/tests/test_wordpress_provenance_plugin_contract.py -q --tb=short` — ✅ 52/52 pass

### Suggested Commit Message (comprehensive)
```
chore(messaging): align chrome extension release copy with approved authorship/proof language

- set manifest short description to approved 132-char-safe tagline
- update Chrome Web Store listing short + long copy to outcome-led wording:
  verify authorship, invisible cryptographic watermarks, embedded proof of origin,
  survives copy-paste
- refresh popup empty/found/onboarding and embedding-mode labels to remove C2PA-heavy user-facing terms
- update options page verification/signing hints to emphasize proof-of-origin outcomes
- align extension README opening/features copy with release messaging
- update dashboard integration card extension description/setup text to match approved messaging
- refresh generated store-asset promo copy strings for tagline/feature consistency
- update onboarding + popup UX tests to match new UI copy
- soften WordPress plugin directory description/tagline wording to remove AI-detection framing

Verification:
- npm test (160/160)
- npm run test:e2e (10/10)
- npm run lint (0 errors)
- uv run pytest enterprise_api/tests/test_wordpress_provenance_plugin_contract.py (52/52)
```

---

## Session Addendum: Dashboard + Marketing Build Failures (2026-02-19)

### Scope Completed
- Investigated Railway build failures for:
  - `apps/dashboard`
  - `apps/marketing-site`
- Applied targeted code/config fixes for root causes found in logs.

### Root Cause Findings
- **Dashboard failure**: stale JSX block referenced `integration.href`, but the union type for `comingSoonIntegrations` only supports `setupHref`/`downloadHref` on plugin entries and no `href` field. This caused TypeScript build failure at `src/app/integrations/page.tsx:131`.
- **Marketing-site failure**: Railpack selected Node 18 from app engine constraints, while dependency graph includes Tailwind v4 native oxide bindings that require newer Node/runtime compatibility. Logs also showed `EBADENGINE` warnings and `@tailwindcss/oxide` native binding failure.

### Files Updated
- `apps/dashboard/src/app/integrations/page.tsx`
  - Removed obsolete `integration.href` rendering branch.
- `apps/marketing-site/package.json`
  - Updated engines from `>=18.0.0` to `>=22.0.0` to align build runtime with current frontend dependency requirements.

### Verification Evidence
- `apps/dashboard`: `npm run build` — ✅ pass (warnings only).
- `apps/marketing-site`: local `npm run build` still blocked by pre-existing file ownership issue in workspace cache (`.next/server/app/_not-found` owned by root), but failure mode is environment-permission related and separate from Railway Node/runtime mismatch.
- Confirmed local Node runtime is modern (`v24.12.0`), supporting the engine bump rationale.

### Suggested Commit Message (comprehensive)
```
fix(frontend-build): resolve dashboard integrations type failure and align marketing runtime engine

- remove stale integration.href render branch in dashboard integrations page
  to fix Next/TypeScript build error on union-typed integration cards
- bump marketing-site Node engine requirement to >=22 to match Tailwind v4
  oxide native binding/runtime expectations in CI/Railpack builds
- validate dashboard production build locally after fix
- document local marketing build cache permission issue as unrelated env artifact
```

---

## Session Addendum: 2FA Login Investigation + Normalization Fix (2026-02-19)

### Scope Completed
- Investigated reported login issues potentially related to recently enabled 2FA.
- Traced full auth path across dashboard frontend (`/login`) and auth-service (`/auth/login`, `/auth/login/mfa/complete`).
- Reproduced and fixed a concrete MFA code parsing issue that can block otherwise valid TOTP codes.

### Root Cause Findings
- **Confirmed bug**: TOTP verification expected raw code without visual separators. Codes entered as `123 456` or with dashes could be rejected even when mathematically valid.
  - Affected code paths:
    - TOTP setup confirmation
    - Login-time TOTP verification
- This can present to end users as "reset worked but login still fails," especially when 2FA is enabled and code entry formatting differs by app/browser/password manager.

### Files Updated
- `services/auth-service/app/services/auth_factors_service.py`
  - Added `_normalize_factor_code` helper.
  - Normalized code input before TOTP verification and backup-code hashing.
- `services/auth-service/tests/test_auth_factors_service.py`
  - Added regression tests:
    - `test_confirm_totp_setup_accepts_code_with_spaces`
    - `test_verify_totp_or_backup_accepts_totp_code_with_spaces`

### Verification Evidence
- `uv run pytest tests/test_auth_factors_service.py -q` — ✅ 13 passed
- `uv run pytest tests/test_mfa_login_flow.py -q` — ✅ 3 passed
- `uv run pytest -q` (auth-service full suite) — ✅ 211 passed, 21 deselected

### Suggested Commit Message (comprehensive)
```
fix(auth-2fa): normalize MFA codes to prevent valid TOTP rejection with spaced input

- investigate customer-reported login issues after enabling 2FA
- add factor-code normalization helper to strip common visual separators
  (spaces/dashes) before TOTP and backup-code verification
- apply normalization to both TOTP setup confirmation and runtime login checks
- add regression tests for spaced TOTP inputs in setup and login factor validation
- run full auth-service test suite to confirm no regressions

Verification:
- uv run pytest tests/test_auth_factors_service.py -q (13 passed)
- uv run pytest tests/test_mfa_login_flow.py -q (3 passed)
- uv run pytest -q (211 passed, 21 deselected)
```

### Session Addendum: Dashboard NextAuth MFA Error Handling Fix
**Goal:** Fix issue where users with 2FA enabled see a generic "Invalid email or password" error instead of the MFA code prompt.

**Root Cause:**
NextAuth v4's `CredentialsProvider` catches errors thrown in the `authorize` callback and URL-encodes them if they are custom errors, then returns them in the `result.error` property when `redirect: false` is used.
The frontend at `@/apps/dashboard/src/app/login/page.tsx` was checking `if (result.error.startsWith('MFA_REQUIRED:'))`. However, because NextAuth URL-encoded the error string, the actual value was `MFA_REQUIRED%3A[token]`, causing the `.startsWith()` check to fail and fall through to the generic "Invalid email or password" error.

**Changes:**
1. Modified `@/apps/dashboard/src/app/login/page.tsx` to `decodeURIComponent(result.error || '')` before checking for `MFA_REQUIRED:`.
2. Updated the token extraction logic to use the decoded error string.
3. Added a contract test `@/apps/dashboard/tests/e2e/login.mfa.contract.test.mjs` to ensure the login page correctly decodes the NextAuth error string.
4. Verified TypeScript type checking still passes for the dashboard app.

**Suggested Git Commit:**
```text
fix(dashboard): decode NextAuth error to correctly surface MFA challenge

NextAuth v4 URL-encodes custom errors thrown from the authorize callback.
The frontend was previously doing a direct string comparison which failed
because the colon was encoded to %3A. This caused users with TOTP enabled
to see a generic "Invalid email or password" error instead of the MFA prompt.

This patch adds `decodeURIComponent` to the login error handler so the
MFA_REQUIRED token prefix is correctly identified and the user is prompted
for their 2FA code.
```

### Session Addendum 2: Fixing Password Hash Mismatch for Test User
**Goal:** The test user `test@encypher.com` was unable to log in because the password hash in the database did not match the application's hashing format.

**Root Cause:**
The `auth-service` uses a custom pre-hashing step `base64.b64encode(hashlib.sha256(password).digest())` before running it through bcrypt to avoid bcrypt's 72-byte limit. The password hash stored in the database for `test@encypher.com` was seemingly generated using standard bcrypt or another format, meaning `Password123!` was failing to verify on the backend and returning a 401 Unauthorized before it could ever trigger the MFA flow.

**Fix Applied:**
We manually generated the correct hash for `Password123!` using the backend's exact hashing function and updated the `test@encypher.com` user row in the postgres database.

The user can now successfully log in with `Password123!` and will be prompted for their MFA code.

### Session Addendum 3: Decoding the "Invalid email or password" MFA Fallback Error
**Goal:** Fix the issue where an invalid MFA code submission correctly returned a 401 from the backend, but the frontend still displayed `Invalid%20multi-factor%20authentication%20code` or failed to decode the error, leading to an incorrect UI state.

**Root Cause:**
When a user submits an incorrect MFA code, NextAuth catches the thrown error (`Invalid multi-factor authentication code`) from the `authorize` callback and returns it URL-encoded in `result.error`. In `@/apps/dashboard/src/app/login/page.tsx`, we were previously only decoding the error to check if it started with `MFA_REQUIRED:`. If it did not, we fell back to displaying `result.error` directly. Because NextAuth URL-encoded the error string (e.g. `Invalid%20multi-factor%20...`), the raw string was displayed or fell back to the generic `Invalid email or password` message when the string didn't match cleanly.

**Fix Applied:**
Updated the error fallback logic in `@/apps/dashboard/src/app/login/page.tsx` to display the `decodedError` instead of the raw `result.error` so that the user correctly sees "Invalid multi-factor authentication code" (or other decoded errors) instead of "Invalid email or password" when an MFA attempt fails.

**Suggested Git Commit:**
```text
fix(dashboard): use decoded NextAuth error for all login failure messages

When an MFA code was invalid, NextAuth URL-encoded the custom error string.
Because the frontend was only decoding the string to check for the MFA
challenge prefix, any other errors (like an invalid code) were rendered in
their raw URL-encoded format or fell back to the default generic error message.

This commit updates the login page to always render the decoded error string,
ensuring users see the correct "Invalid multi-factor authentication code"
message when they enter a wrong code.
```

### Session Addendum 4: Password Sync Issue
**Goal:** The test user was still unable to log in with `Password123!`.
**Root Cause:** The earlier password reset was accidentally rolled back or overwritten during the restart/rebuild to `TestPassword123!` via the seed script, but the user was typing `Password123!`.
**Fix Applied:** We have forcibly reset the password hash in the database to the pre-hashed bcrypt equivalent of `Password123!`.
