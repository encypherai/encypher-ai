# Dashboard Org Management Audit

**Status:** 🔄 In Progress
**Current Goal:** Task 4.1 — Baseline tests (if applicable)

## Overview

Assess whether the dashboard supports organization management and user-level permissions for business/enterprise accounts, including org invitations, role levels, and org-level vs user-level API keys. Produce an evidence-based audit of current functionality and gaps.

## Objectives

- Identify existing org management UX and user role flows in the dashboard app.
- Verify backend services/models support orgs, invitations, roles, and key scoping.
- Confirm how org-level vs user-level keys are modeled and enforced.

## Tasks

### 1.0 Discovery & Requirements

- [x] 1.1 Review docs/PRDs for org management expectations
- [x] 1.2 Identify dashboard UI entry points for org management, invites, roles

### 2.0 Backend Capability Audit

- [x] 2.1 Review user/org models and role definitions in services
- [x] 2.2 Review key service for org-level vs user-level key scoping
- [x] 2.3 Verify API endpoints for org invites and membership management

### 3.0 Validation

- [x] 3.1 Trace dashboard UI → API wiring for org management flows
- [x] 3.2 Summarize functional gaps vs requirements

### 4.0 Testing & Verification

- [ ] 4.1 Baseline tests (if applicable) — ✅ pytest
- [ ] 4.2 Frontend verification — ✅ puppeteer

## Success Criteria

- Audit summarizes where org management/user roles/keys are implemented (or missing) with file references.
- Clear statement whether features exist and work as intended, with documented gaps.
- Any required follow-up tasks captured in PRD or questions log.

## Completion Notes

Audit findings (in progress):
- Dashboard UI includes Team Management page with seat counts, member list, role updates, invites, and invitation cancellation, gated to Business/Enterprise tier.
- Organization context + switcher are implemented to select active org, but audit logs still read orgId from session instead of active org.
- Auth service models and OrganizationService cover orgs, members, invitations, audit logs, and RBAC helpers.
- Key service models allow org_id, but key creation/listing is user-scoped and does not enforce org-level ownership from the dashboard.

Gaps/risks:
- Org-level key management is not wired in dashboard or key-service endpoints (user_id-only filtering).
- Audit logs page ignores active organization selection (uses session orgId).
- Create org flow appears linked but not implemented on Team page.

Verification: tests not run yet (pending 4.1/4.2).
