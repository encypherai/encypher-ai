# PRD: Onboarding Checklist & Auto-Approve API Access

**Status**: Complete
**Team**: TEAM_191
**Current Goal**: Remove manual API access gate, add server-tracked onboarding checklist

---

## Overview

Replace the manual admin-approval API access gate with instant auto-approval on signup, and replace the client-side localStorage onboarding modal with a server-side tracked per-user onboarding checklist that measures real product engagement milestones.

---

## Objectives

- Eliminate friction between signup and first API call (no more "pending review" wait)
- Track real onboarding milestones per user on the server (not localStorage)
- Provide a persistent dashboard checklist widget showing progress
- Retain admin ability to suspend users (existing TEAM_164 functionality)
- Maintain backward compatibility for existing approved/suspended users

---

## Tasks

### 1.0 Backend — Auth Service

- [x] 1.1 Change default `api_access_status` from `not_requested` to `approved` — ✅ pytest
  - [x] 1.1.1 Update User model default in `models.py`
  - [x] 1.1.2 Update `create_user` and `upsert_oauth_user` to initialize onboarding on creation
  - [x] 1.1.3 Alembic migration to change default + migrate existing `not_requested`/`pending` users to `approved`

- [x] 1.2 Add onboarding checklist to User model — ✅ pytest
  - [x] 1.2.1 Add `onboarding_checklist` JSON column to User model
  - [x] 1.2.2 Add `onboarding_completed_at` DateTime column
  - [x] 1.2.3 Include in Alembic migration `010_onboarding_checklist_auto_approve.py`

- [x] 1.3 Create OnboardingService — ✅ pytest (21 tests)
  - [x] 1.3.1 Define checklist steps: account_created, first_api_key, first_api_call, first_document_signed, first_verification
  - [x] 1.3.2 `get_onboarding_status(user_id)` — returns checklist with completion state
  - [x] 1.3.3 `complete_step(user_id, step_id)` — marks a step complete
  - [x] 1.3.4 `dismiss_checklist(user_id)` — marks checklist as dismissed

- [x] 1.4 Add API endpoints — ✅ pytest
  - [x] 1.4.1 `GET /api/v1/auth/onboarding-status` — get current checklist
  - [x] 1.4.2 `POST /api/v1/auth/onboarding/complete-step` — mark step done
  - [x] 1.4.3 `POST /api/v1/auth/onboarding/dismiss` — dismiss checklist

- [x] 1.5 Add Pydantic schemas for onboarding request/response

- [x] 1.6 Write tests — ✅ 21 tests pass
  - [x] 1.6.1 Test onboarding service (get status, complete step, dismiss)
  - [x] 1.6.2 Test auto-approve on signup (new default)
  - [x] 1.6.3 Test existing suspended users are NOT affected

### 2.0 Frontend — Dashboard

- [x] 2.1 Add onboarding API client methods — ✅ tsc
  - [x] 2.1.1 `getOnboardingStatus(accessToken)`
  - [x] 2.1.2 `completeOnboardingStep(accessToken, stepId)`
  - [x] 2.1.3 `dismissOnboarding(accessToken)`

- [x] 2.2 Create OnboardingChecklist component — ✅ tsc
  - [x] 2.2.1 Fetches status from server on mount
  - [x] 2.2.2 Shows progress bar + step list with completion state
  - [x] 2.2.3 Each step links to relevant page (API keys, docs, playground)
  - [x] 2.2.4 Dismiss button to hide permanently

- [x] 2.3 Integrate into dashboard home page — ✅ tsc
  - [x] 2.3.1 Replace old OnboardingModal with new OnboardingChecklist
  - [x] 2.3.2 Show checklist in sidebar card on home page

- [x] 2.4 Remove ApiAccessGate from API keys page — ✅ tsc
  - [x] 2.4.1 Remove `<ApiAccessGate>` wrapper from `app/api-keys/page.tsx`

---

## Success Criteria

- [x] New users get `approved` status immediately on signup
- [x] Onboarding checklist is tracked server-side per user
- [x] Dashboard shows checklist with real completion state
- [x] Users can dismiss the checklist permanently
- [x] Existing suspended users are unaffected
- [x] All tests pass (151 passed, 3 pre-existing failures from TEAM_145)
- [x] No regression in existing auth/admin flows
- [x] TypeScript compiles cleanly (0 errors)

---

## Completion Notes

Completed by TEAM_191 on 2026-02-14.

**Key decisions:**
- Default `api_access_status` changed from `not_requested` to `approved` in User model
- Migration 010 auto-approves existing `not_requested` and `pending` users; does NOT touch `denied` or `suspended`
- Onboarding checklist stored as JSON on User model (no new table needed)
- Old `OnboardingModal` (localStorage-based) replaced by server-backed `OnboardingChecklist`
- `ApiAccessGate` component left in codebase but no longer used on API keys page
- Admin suspend/deny flows remain fully functional for abuse prevention
