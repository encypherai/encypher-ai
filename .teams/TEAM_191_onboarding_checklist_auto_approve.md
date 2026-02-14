# TEAM_191 — Remove API Access Gate + Server-Tracked Onboarding Checklist

**Status**: Complete
**Date**: 2026-02-14

## Summary
Removed the manual API access approval gate (auto-approve on signup) and replaced the client-side localStorage onboarding modal with a server-side tracked onboarding checklist per user.

## Changes Made

### Backend (auth-service)
1. Changed default `api_access_status` from `not_requested` to `approved` in User model
2. Added `onboarding_checklist` (JSON) and `onboarding_completed_at` (DateTime) columns to User model
3. Alembic migration `010_onboarding_checklist_auto_approve.py` — migrates existing not_requested/pending users to approved
4. New service: `OnboardingService` — get status, complete step, dismiss, initialize for new user
5. New endpoints: `GET /auth/onboarding-status`, `POST /auth/onboarding/complete-step`, `POST /auth/onboarding/dismiss`
6. Both `create_user` and `upsert_oauth_user` now initialize onboarding (mark `account_created`)
7. 21 new tests in `test_onboarding_service.py` — all pass

### Frontend (dashboard)
1. New `OnboardingChecklist` component (server-backed, replaces localStorage modal)
2. API client methods: `getOnboardingStatus`, `completeOnboardingStep`, `dismissOnboarding`
3. Removed `ApiAccessGate` wrapper from `app/api-keys/page.tsx`
4. Replaced `OnboardingModal` with `OnboardingChecklist` on dashboard home page
5. TypeScript compiles cleanly (0 errors)

### Session 2: Publisher Identity Setup Wizard

#### Backend (auth-service)
1. Added `account_type` (individual/organization) and `display_name` to Organization model
2. Added `setup_completed_at` to User model (NULL = wizard not done, dashboard blocks)
3. Alembic migration `011_publisher_identity_setup.py` — adds columns, backfills existing users as setup-complete
4. New Pydantic schemas: `AccountType` enum, `SetupWizardRequest`, `SetupStatusResponse`
5. New endpoints: `GET /auth/setup-status`, `POST /auth/setup/complete`
6. Added `publisher_identity_set` step to onboarding checklist (now 6 steps)
7. 20 new tests in `test_setup_wizard.py` — all pass

#### Frontend (dashboard)
1. New `SetupWizard` component — mandatory 3-step wizard (account type → display name → welcome)
2. Non-cancelable: no close button, no escape key, z-100 overlay
3. API client methods: `getSetupStatus`, `completeSetup`
4. `DashboardLayout` gates on setup-status — shows wizard overlay if incomplete
5. Welcome step links to API keys, playground, integrations

## Test Results
- **Backend**: 171 passed, 3 pre-existing failures (TEAM_145 tier consolidation), 0 new regressions
- **Frontend**: `tsc --noEmit` passes with 0 errors

## Blockers
None

## Handoff Notes
- The old `ApiAccessGate` component and `OnboardingModal` component still exist in the codebase but are no longer imported/used. A future cleanup PR can delete them.
- The onboarding steps are defined in `onboarding_service.py::ONBOARDING_STEPS`. To add new steps, add to that list and the frontend will auto-render them.
- Steps are completed by calling `POST /auth/onboarding/complete-step` with a `step_id`. The dashboard or other services should call this when the user performs the relevant action (e.g., key-service calls it when first API key is created).
- The 3 pre-existing test failures in `test_organization_invitation_emails.py` reference `UserTier.BUSINESS` which was removed in TEAM_145.
- **Future work**: Enterprise API needs to build the publisher attribution string from org context (`"{user.name} at {org.display_name} · Powered by Encypher"` for free tier, without suffix for whitelabel). The `account_type` and `display_name` fields are ready in the DB.

## Suggested Git Commit Message
```
feat(TEAM_191): onboarding overhaul — auto-approve, checklist, publisher identity wizard

Session 1: Remove manual API access gate, add server-tracked onboarding
Session 2: Add mandatory publisher identity setup wizard

Backend (auth-service):
- Change default api_access_status from 'not_requested' to 'approved'
- Add onboarding_checklist (JSON) and onboarding_completed_at columns
- Alembic migration 010: auto-approve existing not_requested/pending users
- New OnboardingService with get/complete/dismiss/initialize methods
- Onboarding endpoints: GET /onboarding-status, POST /complete-step, POST /dismiss
- Add account_type, display_name to Organization model
- Add setup_completed_at to User model (gates dashboard access)
- Alembic migration 011: publisher identity columns
- Setup endpoints: GET /setup-status, POST /setup/complete
- 6 onboarding steps: account_created, publisher_identity_set, first_api_key,
  first_api_call, first_document_signed, first_verification
- 41 new tests (all pass)

Frontend (dashboard):
- New OnboardingChecklist component (server-backed, progress bar, dismiss)
- New SetupWizard component (mandatory 3-step: account type → name → welcome)
- DashboardLayout gates on setup completion
- Remove ApiAccessGate wrapper from API keys page
- Replace OnboardingModal with OnboardingChecklist on dashboard home
- API client methods for onboarding + setup endpoints

Existing suspended/denied users are NOT affected by migrations.
Admin suspend/deny flows remain fully functional.
```

---

## Session 3: Publisher Attribution + Anonymous Verification Mode (Follow-up)

### Backend (auth-service)
1. Added `anonymous_publisher` to organization API shape for dashboard org context/list responses.
2. Added hard validation for publisher settings update: blank/whitespace `display_name` now rejected with 400.
3. Added `whitelabel` defaults in org tier feature config (`free=false`, `enterprise=true`, `strategic_partner=true`) for attribution suffix control.
4. Migration `012_anonymous_publisher.py` updated to use explicit SQL boolean default (`sa.text("false")`).
5. Extended setup wizard test coverage for `anonymous_publisher` Organization column.

### Backend (enterprise_api)
1. Refactored attribution utility into:
   - `build_publisher_identity_base(...)` for C2PA/X.509 identity fields.
   - `build_publisher_attribution(...)` for API-facing verification strings.
2. Enforced anonymous mode as org-id only (no branding suffix) in attribution builder.
3. Added `publisher_identity_base` to normalized org context in `dependencies.py`.
4. Wired `publisher_identity_base` into:
   - certificate provisioning path (`signing_executor.py`),
   - C2PA publisher identity field (`embedding_executor.py`).
5. Kept `publisher_attribution` in sign responses for verification-facing UX.
6. Extended tests:
   - updated anonymous attribution assertions,
   - added base identity helper tests,
   - added composed org context assertions for account/display/anonymous + identity fields.

### Frontend (dashboard)
1. Added Publisher Settings API method: `updatePublisherSettings(accessToken, orgId, { display_name, anonymous_publisher })`.
2. Extended organization types/context with `account_type`, `display_name`, `anonymous_publisher`.
3. Added Settings → Organization UI card:
   - editable display name,
   - anonymous publisher toggle,
   - identity preview,
   - save mutation + success/error toasts.

### Verification (Session 3)
- `services/auth-service`: `uv run pytest tests/test_setup_wizard.py -q` ✅
- `enterprise_api`: `uv run pytest tests/test_publisher_attribution.py tests/test_org_context_composition.py -q` ✅ (19 passed)
- `apps/dashboard`: `npx tsc --noEmit` ✅

### Blockers
1. Full browser-level Puppeteer verification for dashboard settings flow not executed in this session (requires running dashboard app and interactive verification path).

### Handoff Notes
1. Anonymous mode now intentionally returns only `org_id` in API attribution and base identity outputs.
2. C2PA/X.509 identity now uses `publisher_identity_base` (no "Powered by Encypher" suffix).
3. API response-facing attribution remains in `publisher_attribution`.
4. If product wants individual attribution to include user name (e.g., "User at Org") for shared org keys, that requires key-service/auth-service user-name propagation not currently present in composed org context.

### Suggested Git Commit Message (Session 3)
```
feat(TEAM_191): add anonymous publisher settings and wire publisher identity across API/C2PA/certs

Auth-service:
- include account_type/display_name/anonymous_publisher in Organization API response model
- hard-validate blank display_name in PATCH /organizations/{org_id}/publisher-settings
- add whitelabel feature defaults by tier (free=false, enterprise/strategic_partner=true)
- normalize anonymous_publisher migration default to SQL boolean literal
- extend setup wizard tests for anonymous_publisher column

Enterprise API:
- refactor publisher attribution utility into base identity + API attribution helpers
- enforce anonymous mode as org_id-only attribution
- expose publisher_identity_base in normalized org context
- use publisher_identity_base for certificate org name provisioning
- use publisher_identity_base for C2PA publisher field
- keep publisher_attribution in sign responses
- expand attribution and org-context regression tests

Dashboard:
- add updatePublisherSettings API client method
- extend organization context typings with publisher identity fields
- add Settings > Organization publisher identity management card
  (display name edit, anonymous toggle, preview, save flow)

Validation:
- uv run pytest services/auth-service/tests/test_setup_wizard.py -q
- uv run pytest enterprise_api/tests/test_publisher_attribution.py tests/test_org_context_composition.py -q
- npx tsc --noEmit (apps/dashboard)
```

---

## Session 4: Phase 2 + 3 Completion (TOTP + Passkeys)

### Backend (auth-service)
1. Added auth-factor service `app/services/auth_factors_service.py`:
   - TOTP provisioning + verification + backup code consumption
   - Passkey registration/authentication challenge + verification flow
   - Passkey list/delete lifecycle helpers
2. Added MFA/Passkey config in `app/core/config.py`:
   - `MFA_ISSUER`, `MFA_BACKUP_CODES_COUNT`, `MFA_CHALLENGE_EXPIRE_MINUTES`
   - `PASSKEY_ENABLED`, `PASSKEY_RP_ID`, `PASSKEY_RP_NAME`, `PASSKEY_EXPECTED_ORIGIN`
3. Added User columns in `app/db/models.py`:
   - `totp_enabled`, `totp_secret_encrypted`, `totp_enabled_at`, `totp_backup_code_hashes`
   - `passkey_credentials`, `passkey_challenge`, `passkey_challenge_expires_at`
4. Added migration `013_mfa_and_passkeys.py` for new user security columns.
5. Extended auth schemas in `app/models/schemas.py`:
   - login payload accepts `mfa_code`/`mfaCode`
   - TOTP + passkey request schemas
   - MFA challenge completion schema
6. Updated auth login behavior in `app/api/v1/endpoints.py`:
   - TOTP-enabled users receive `mfa_required` + short-lived `mfa_token` unless code provided
   - New endpoint: `POST /auth/login/mfa/complete`
   - New status/setup endpoints for TOTP and passkeys
   - New passkey auth endpoints for passwordless flow
7. Updated `AuthService.authenticate_user` to avoid marking `last_login_at` before MFA succeeds; moved to `mark_login_success(...)` after all factors pass.

### Frontend (dashboard)
1. Extended API client (`src/lib/api.ts`) with MFA/passkey methods:
   - `getMfaStatus`, `beginTotpSetup`, `confirmTotpSetup`, `disableTotp`
   - `completeMfaLogin`, `startPasskeyRegistration`, `completePasskeyRegistration`
   - `startPasskeyAuthentication`, `completePasskeyAuthentication`, `deletePasskey`
2. Updated NextAuth credentials flow (`src/app/api/auth/[...nextauth]/route.ts`):
   - handles MFA_REQUIRED challenge path
   - supports completing MFA challenge token flow
   - forwards optional MFA + Turnstile fields on login
3. Updated login page (`src/app/login/page.tsx`):
   - passkey sign-in button + browser credential assertion flow
   - MFA challenge UX (`mfa_token` + code submit)
4. Updated settings security tab (`src/app/settings/page.tsx`):
   - TOTP enrollment/confirmation/disable controls
   - backup-code display at setup time
   - passkey registration and removal UI

### Verification (Session 4)
- `uv run pytest tests/test_mfa_login_flow.py tests/test_auth_factors_service.py tests/test_signup_input_validation.py tests/test_turnstile_security.py -q` ✅
- `uv run ruff check app tests` (services/auth-service) ✅
- `npx tsc --noEmit` (apps/dashboard) ✅
- Puppeteer manual verification:
  - login shows passkey sign-in CTA
  - settings security tab renders TOTP/passkey controls
  - screenshot: `settings-security-phase2-phase3` ✅

### Known Existing Failures (Not Introduced Here)
Running full `uv run pytest -q` in `services/auth-service` still reports unrelated pre-existing failures:
- `tests/test_internal_org_context.py` (mock fixture mismatch)
- `tests/test_organization_invitation_emails.py` (`UserTier.BUSINESS` legacy reference)

### Suggested Git Commit Message (Session 4)
```
feat(TEAM_191): complete Phase 2/3 onboarding security with TOTP MFA and passkeys

Auth-service:
- add AuthFactorsService for TOTP + backup code + passkey orchestration
- add MFA/passkey config flags and defaults
- add user security columns and migration 013_mfa_and_passkeys
- add MFA-aware login challenge flow and /auth/login/mfa/complete
- add TOTP setup/confirm/disable endpoints
- add passkey register/authenticate/delete endpoints
- ensure last_login_at updates only after all auth factors pass

Dashboard:
- add MFA/passkey API client methods
- extend NextAuth credentials flow for MFA challenge completion
- add passkey sign-in on login page
- add security settings UI for TOTP and passkey management

Validation:
- uv run pytest tests/test_mfa_login_flow.py tests/test_auth_factors_service.py tests/test_signup_input_validation.py tests/test_turnstile_security.py -q
- uv run ruff check app tests (auth-service)
- npx tsc --noEmit (apps/dashboard)
- Puppeteer manual verification screenshot: settings-security-phase2-phase3
```
