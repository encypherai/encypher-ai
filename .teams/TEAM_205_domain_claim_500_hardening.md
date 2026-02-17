# TEAM_205: Domain Claim 500 Hardening

**Active PRD**: `PRDs/CURRENT/PRD_Domain_Org_Claim.md`
**Working on**: Post-release hardening for domain claims + publisher identity trust enforcement
**Started**: 2026-02-16 22:34 UTC
**Status**: in_progress

## Session Progress
- [x] 1.0 Investigate production `POST /organizations/{org_id}/domain-claims` 500 root cause — ✅ pytest
- [x] 2.0 Implement backend hardening for domain claim creation and email dispatch resilience — ✅ pytest ✅ ruff
- [x] 3.0 Enforce verified-domain requirement before organization publisher display-name changes — ✅ pytest
- [x] 4.0 Add regression tests for domain claim + publisher settings guardrails — ✅ pytest
- [x] 5.0 Implement controlled signing identity modes + entitlement gate for custom mode — ✅ pytest ✅ ruff
- [x] 6.0 Update dashboard Organization settings UX to controlled identity mode selector — ✅ tsc
- [x] 7.0 Update pricing SSOT for Custom Signing Identity add-on to $9/mo and sync generated pricing config copies — ✅ sync scripts
- [ ] 8.0 Final end-to-end validation and docs closeout — blocked on unrelated pre-existing dashboard e2e failures

## Changes Made
- `services/auth-service/app/api/v1/organizations.py`
  - Fixed logging calls in invitation/domain-claim email notification helpers to avoid runtime `TypeError` on structured keyword args.
  - Wrapped domain-claim notification dispatch in endpoint-level guard so claim creation remains successful even if notification send fails.
  - Added publisher identity policy enforcement: org accounts must have at least one verified domain claim before setting `display_name`.
  - Added controlled signing identity modes (`organization_name`, `organization_and_author`, `custom`) and enforced custom mode entitlement via `custom-signing-identity` add-on (or enterprise tier).
  - Extended publisher settings response to include `signing_identity_mode`, `signing_identity_custom_label`, and `custom_signing_identity_enabled`.
- `services/auth-service/app/db/models.py`
  - Added `Organization.signing_identity_mode` and `Organization.signing_identity_custom_label`.
- `services/auth-service/alembic/versions/014_signing_identity_modes.py`
  - Added migration for controlled signing identity fields on `organizations`.
- `services/auth-service/tests/test_organization_invitation_emails.py`
  - Added regression test: domain claim creation succeeds even when domain claim email dispatch throws.
  - Added policy tests for publisher-settings endpoint requiring verified domain for organization accounts.
  - Added tests for custom signing identity add-on requirement and returning signing identity mode fields.
- `apps/dashboard/src/app/settings/page.tsx`
  - Replaced raw free-text org identity editing with controlled mode selector UI.
  - Added custom mode gating text tied to add-on entitlement and updated preview behavior.
- `apps/dashboard/src/lib/api.ts`
  - Added `signing_identity_mode`/`signing_identity_custom_label`/`add_ons` typing and updated publisher settings payload.
- `apps/dashboard/src/contexts/OrganizationContext.tsx`
  - Added organization context fields for signing identity mode/custom label and add-ons.
- `packages/pricing-config/src/tiers.ts`
  - Updated `custom-signing-identity` add-on price to `$9/mo` and adjusted Publisher Identity bundle value labels/pricing.
- `apps/dashboard/src/lib/pricing-config/*` and `apps/marketing-site/src/lib/pricing-config/*`
  - Synced generated pricing config copies from SSOT package via sync scripts.
- `apps/dashboard/src/lib/playgroundEndpoints.mjs`
  - Corrected invalid playground endpoint tier gates from `professional` to `enterprise` (actual supported tier model is Free + Enterprise).
- `apps/dashboard/tests/e2e/playground.endpoints.contract.test.mjs`
  - Updated contract expectations to assert `enterprise` tier metadata for gated endpoints.
- `apps/dashboard/src/lib/playgroundRequestBuilder.mjs`
  - Kept sign request parser contract-compatible by returning advanced sign option fields only when present in parsed JSON.

## Validation
- ✅ `uv run pytest services/auth-service/tests/test_organization_invitation_emails.py services/auth-service/tests/test_organization_service.py -q`
- ✅ `uv run ruff check services/auth-service/app/api/v1/organizations.py services/auth-service/app/db/models.py services/auth-service/tests/test_organization_invitation_emails.py`
- ✅ `uv run ruff check services/auth-service/alembic/versions/014_signing_identity_modes.py`
- ✅ `npm run type-check` (apps/dashboard)
- ✅ `npm run lint` (apps/dashboard) — passes with pre-existing warnings unrelated to this work
- ✅ `node --test tests/e2e/playground.endpoints.contract.test.mjs tests/e2e/playground.request-builder.contract.test.mjs` (apps/dashboard)
- ⚠️ `npm run test:e2e` (apps/dashboard) still includes additional suite failures outside this targeted contract fix scope
- ✅ Puppeteer manual smoke captured login flow render (`dashboard_current` screenshot)

## Blockers
- Dashboard e2e suite still has failures outside the now-fixed playground endpoint/request-builder contract tests.
- Running dashboard manual verification for settings requires authenticated session in local environment.

## Handoff Notes
- Primary production issue addressed in route + helper behavior.
- Policy now enforces domain authority for organization display identity updates.
- If desired, next hardening step is adding DB-level uniqueness constraints for active domain claims and domain-token expirations.

## Suggested Commit Message
feat(identity): enforce verified-domain signing modes and add $9 custom signing identity add-on

- harden auth-service publisher settings with controlled signing identity modes and add-on entitlement checks
- add organization schema + migration fields for signing_identity_mode and signing_identity_custom_label
- keep domain claim creation resilient when email dispatch fails and preserve verified-domain guardrails
- add regression coverage for custom mode entitlement and signing identity response fields
- replace dashboard org publisher free-text workflow with controlled mode selector + custom add-on gating UX
- update pricing SSOT custom-signing-identity to $9/mo and sync dashboard/marketing generated pricing config
- validate with targeted auth pytest + ruff, dashboard type-check/lint, and manual puppeteer smoke capture
