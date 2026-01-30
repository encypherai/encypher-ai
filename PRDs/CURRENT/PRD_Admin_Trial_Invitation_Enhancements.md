# Admin Trial Invitation Enhancements

**Status:** ✅ Complete
**Current Goal:** Require recipient names for trial invites and auto-create orgs when none exist.

## Overview
Trial invitations should capture recipient first/last names for personalized emails and account creation. Admins should be able to create trials for new organizations by creating a fresh org when no existing org is selected.

## Objectives
- Enforce first/last name capture for trial invitations.
- Allow admins to create a new organization during trial invite flow.
- Update admin UI to collect required details and pass them to the API.
- Add regression coverage for trial invite validation and org creation.

## Tasks

### 1.0 Baseline & Tests
- [x] 1.1 Add backend test for trial invites requiring first/last name. ✅ pytest
- [x] 1.2 Update admin invite e2e to include name fields and org creation flow. ✅ puppeteer

### 2.0 Backend Updates
- [x] 2.1 Enforce first/last name requirement for trial invitations in organization service. ✅ pytest
- [x] 2.2 Include recipient name data in invitation email payload. ✅ pytest

### 3.0 Dashboard Updates
- [x] 3.1 Add first/last name inputs and optional org creation fields to admin invite form. ✅ puppeteer
- [x] 3.2 Trigger org creation when no existing org is selected. ✅ puppeteer

### 4.0 Verification
- [x] 4.1 Run auth-service lint/tests and dashboard e2e. ✅ pytest ✅ puppeteer
- [x] 4.2 Update PRD + team log with outcomes.

## Success Criteria
- Trial invites reject missing first/last names.
- Admins can send trial invites without selecting an existing org, and a new org is created.
- Invitation email payload includes recipient name metadata.
- Tests cover new validation and admin invite flow.

## Completion Notes
- ✅ `uv run ruff check .` (auth-service)
- ✅ `uv run pytest` (auth-service)
- ✅ `npm run lint` (dashboard - existing warnings only)
- ✅ `npm run test:e2e -- tests/e2e/team.upgrade-prompt.test.mjs tests/e2e/team.invite-trial.test.mjs tests/e2e/signup.validation.test.mjs`
- Fixed signup validation e2e timing by waiting for React hydration before typing.
