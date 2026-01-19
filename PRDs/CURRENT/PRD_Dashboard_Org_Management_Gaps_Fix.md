# Dashboard Org Management Gaps Fix

**Status:** 🔄 In Progress
**Current Goal:** Task 5.1 — Run linters and relevant tests

## Overview

Implement fixes for the identified organization management gaps across the dashboard, auth-service, and key-service. This includes org-scoped API key management, using active organization context in audit logs, a working create-organization flow, and sending invitation emails via the notification service.

## Objectives

- Enable org-scoped API key creation/listing with proper permission checks.
- Ensure dashboard org management flows respect active organization context.
- Implement create-organization UX and backend wiring.
- Dispatch invitation emails via notification service with proper templates.
- Add regression tests and verification coverage.

## Tasks

### 1.0 Baseline & Test Plan
- [x] 1.1 Run baseline tests (auth-service, key-service) — ✅ pytest
- [x] 1.2 Run dashboard baseline checks (lint/test) — ✅ npm test

### 2.0 Key Service Org-Scoped API Keys
- [x] 2.1 Update key-service schemas to accept optional organization_id
- [x] 2.2 Add org-scoped key listing/creation logic with permission checks
- [x] 2.3 Add tests for org-scoped key flows and access control — ✅ pytest ✅ ruff

### 3.0 Auth Service Invitation Email Delivery
- [x] 3.1 Add invitation email template and helper
- [x] 3.2 Send invitation emails via notification service in org endpoints
- [x] 3.3 Add tests for invitation email dispatch behavior

### 4.0 Dashboard Org Management UX Updates
- [x] 4.1 Update dashboard API client for org-scoped key requests
- [x] 4.2 Fix audit logs to use active organization context
- [x] 4.3 Implement create organization flow on Team page
- [x] 4.4 Update API keys page to use active org context
- [x] 4.5 Add dashboard regression coverage (unit/e2e)

### 5.0 Verification & Documentation
- [x] 5.1 Run linters and relevant tests — ✅ ruff ✅ pytest ✅ puppeteer
- [ ] 5.2 Update docs/README where behavior changes

## Success Criteria

- Org-scoped API key management works end-to-end with permissions enforced.
- Audit logs reflect the active organization selection.
- Create-organization flow works from the dashboard and persists correctly.
- Invitation emails send successfully via notification service.
- Tests and verification steps complete with documented evidence.

## Completion Notes

- Baseline tests: auth-service + key-service pytest complete.
- Dashboard lint runs with existing warnings; type-check passes; no npm test script available.
- Key-service org-scoped keys: schemas/endpoints/tests updated; pytest + ruff passed.
- Dashboard: org-scoped API key requests, audit log org context, team create-org flow; `npm run lint` (warnings), `npm run type-check`, `npm run test:e2e`.
