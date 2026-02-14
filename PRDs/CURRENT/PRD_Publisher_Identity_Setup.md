# PRD: Publisher Identity Setup & Mandatory Onboarding Wizard

**Status**: Complete
**Team**: TEAM_191
**Current Goal**: Add mandatory post-signup identity wizard + "Powered by Encypher" attribution

---

## Overview

After signup, users must complete a mandatory (non-cancelable) setup wizard that collects their publisher identity before they can use the dashboard. This identity flows into signed content (X.509 cert, C2PA manifest). Free-tier content always includes "Powered by Encypher" attribution; paid whitelabel removes it.

---

## Data Model

### Organization additions
- `account_type`: `"individual"` | `"organization"` (default: NULL = not yet set)
- `display_name`: The human-readable publisher name shown in signed content (e.g., "Sarah Chen" or "The Verge")

### User additions
- `setup_completed_at`: DateTime — NULL until wizard is done; dashboard blocks if NULL

### Attribution logic
- **Individual**: publisher = `"{display_name}"` (e.g., "Sarah Chen")
- **Organization**: publisher = `"{display_name}"` (e.g., "The Verge")
- **Anonymous mode**: publisher = `"{org_id}"` (e.g., "org_a1b2c3d4")
- **All free tier**: append `" · Powered by Encypher"` to API attribution string
- **Whitelabel (paid)**: `features.whitelabel = true` → no Encypher suffix
- **C2PA/X.509 identity**: uses base identity only (no branding suffix)

---

## Objectives

- Collect publisher identity (individual vs org, display name) before first use
- Make the setup wizard mandatory and non-cancelable
- Store `account_type` and `display_name` on Organization for downstream signing
- Add `setup_completed_at` to User so dashboard can gate on it
- Add `whitelabel` feature flag for paid removal of Encypher branding
- After wizard completes, show welcome screen with next-step links

---

## Tasks

### 1.0 Backend — Auth Service

- [x] 1.1 Add columns to models — ✅ pytest
  - [x] 1.1.1 Organization: `account_type` VARCHAR(32) nullable, `display_name` VARCHAR(255) nullable
  - [x] 1.1.2 User: `setup_completed_at` DateTime nullable
  - [x] 1.1.3 Alembic migration `011_publisher_identity_setup.py`

- [x] 1.2 Add Pydantic schemas — ✅ pytest
  - [x] 1.2.1 `SetupWizardRequest` — account_type, display_name (with validation)
  - [x] 1.2.2 `SetupStatusResponse` — setup_completed, account_type, display_name
  - [x] 1.2.3 `AccountType` enum — individual, organization

- [x] 1.3 Add API endpoints — ✅ pytest
  - [x] 1.3.1 `GET /auth/setup-status` — check if setup is complete
  - [x] 1.3.2 `POST /auth/setup/complete` — submit wizard data

- [x] 1.4 Update OnboardingService — ✅ pytest
  - [x] 1.4.1 Added `publisher_identity_set` step (now 6 steps total)
  - [x] 1.4.2 `complete_step` called when wizard finishes

- [x] 1.5 Write tests — ✅ 20 new tests pass
  - [x] 1.5.1 Test SetupWizardRequest validation (valid, empty, whitespace, invalid type)
  - [x] 1.5.2 Test model columns exist and are nullable
  - [x] 1.5.3 Test setup flow logic (sets fields, preserves existing org name)

### 2.0 Frontend — Dashboard

- [x] 2.1 Create SetupWizard component — ✅ tsc
  - [x] 2.1.1 Step 1: "Are you an independent creator or part of an organization?"
  - [x] 2.1.2 Step 2a (Individual): "What name should appear on your signed content?" (pre-fill from account name)
  - [x] 2.1.3 Step 2b (Organization): "What's your organization name?"
  - [x] 2.1.4 Step 3: Welcome + next-step links (API keys, playground, integrations)
  - [x] 2.1.5 Non-cancelable — no close button, no escape key dismiss, z-100 overlay

- [x] 2.2 Add setup API client methods — ✅ tsc
  - [x] 2.2.1 `getSetupStatus(accessToken)`
  - [x] 2.2.2 `completeSetup(accessToken, data)`

- [x] 2.3 Gate dashboard behind setup completion — ✅ tsc
  - [x] 2.3.1 DashboardLayout queries setup-status; renders SetupWizard overlay if incomplete

- [x] 2.4 Update OnboardingChecklist — ✅ tsc
  - [x] 2.4.1 `publisher_identity_set` step added to backend checklist definitions

### 3.0 Enterprise API — Attribution

- [x] 3.1 Add `publisher_attribution` field to sign response — ✅ pytest
- [x] 3.2 Build attribution string from org context (display_name/org/anonymous + whitelabel) — ✅ pytest
- [x] 3.3 Add `publisher_identity_base` helper for C2PA and X.509 identity fields — ✅ pytest
- [x] 3.4 Wire attribution + base identity through org normalization and signing executors — ✅ pytest

### 4.0 Frontend — Publisher Settings Management

- [x] 4.1 Add `PATCH /organizations/{org_id}/publisher-settings` client method — ✅ tsc
- [x] 4.2 Add Settings > Organization UI for display name + anonymous toggle — ✅ tsc
- [x] 4.3 Show publisher preview and persist updates via auth-service — ✅ tsc

---

## Success Criteria

- [x] New users see mandatory setup wizard after first login
- [x] Wizard collects account_type + display_name
- [x] Dashboard is blocked until wizard completes
- [x] Organization model stores account_type and display_name
- [x] Whitelabel feature flag enforced for attribution suffix in Enterprise API
- [x] Anonymous publisher mode shows org ID on verification surfaces
- [x] Publisher settings editable from dashboard Organization settings
- [x] All tests pass (171 passed, 3 pre-existing failures from TEAM_145)
- [x] TypeScript compiles cleanly (0 errors)

---

## Completion Notes

Completed by TEAM_191 on 2026-02-14.

**Files changed:**
- `services/auth-service/app/db/models.py` — added `account_type`, `display_name` to Organization; `setup_completed_at` to User
- `services/auth-service/alembic/versions/011_publisher_identity_setup.py` — migration
- `services/auth-service/app/models/schemas.py` — AccountType enum, SetupWizardRequest, SetupStatusResponse
- `services/auth-service/app/api/v1/endpoints.py` — GET /setup-status, POST /setup/complete
- `services/auth-service/app/services/onboarding_service.py` — added publisher_identity_set step
- `services/auth-service/tests/test_setup_wizard.py` — 20 new tests
- `apps/dashboard/src/lib/api.ts` — AccountType, SetupStatusResponse types + client methods
- `apps/dashboard/src/components/onboarding/SetupWizard.tsx` — 3-step mandatory wizard
- `apps/dashboard/src/components/layout/DashboardLayout.tsx` — setup gate

**Additional completion (TEAM_191 follow-up):**
- `services/auth-service/alembic/versions/012_anonymous_publisher.py` — added `anonymous_publisher`
- `services/auth-service/app/api/v1/organizations.py` — internal org context + PATCH publisher settings
- `enterprise_api/app/utils/publisher_attribution.py` — attribution + base identity helpers
- `enterprise_api/app/dependencies.py` — normalized `publisher_attribution` + `publisher_identity_base`
- `enterprise_api/app/services/signing_executor.py` — certificate identity wiring
- `enterprise_api/app/services/embedding_executor.py` — C2PA publisher identity wiring
- `enterprise_api/tests/test_publisher_attribution.py` and `enterprise_api/tests/test_org_context_composition.py` — regression coverage
- `apps/dashboard/src/app/settings/page.tsx` + `apps/dashboard/src/lib/api.ts` + `apps/dashboard/src/contexts/OrganizationContext.tsx` — publisher settings UI + API plumbing
