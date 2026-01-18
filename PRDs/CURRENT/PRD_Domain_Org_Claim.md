# Domain Organization Claim

**Status:** ✅ Complete
**Current Goal:** Define and implement domain-based org claim flow

## Overview
Enable users to verify and claim an organization domain (e.g., acme.com) and associate accounts with that org. The flow should be opt-in, with explicit verification (DNS or email), and avoid auto-creating orgs for every user.

## Objectives
- Provide a secure, opt-in domain verification flow.
- Allow org owners/admins to claim a domain and manage auto-join behavior.
- Keep independent users unblocked (no forced org creation).

## Tasks
- [x] 1.0 Discovery & Design
  - [x] 1.1 Identify current org/user models and auth-service endpoints
  - [x] 1.2 Decide verification method(s) and storage schema
  - [x] 1.3 Define claim states (pending, verified, rejected, expired)
- [x] 2.0 Backend Implementation
  - [x] 2.1 Add domain claim models and migrations
  - [x] 2.2 Add endpoints to request/verify domain claims
  - [x] 2.3 Enforce permissions for claim creation/management
  - [x] 2.4 Add logic for suggested org association (non-blocking)
- [ ] 3.0 Dashboard UX
  - [x] 3.1 Add org settings UI to request domain claim
  - [x] 3.2 Add verification steps and status display
  - [x] 3.3 Add optional auto-join toggle for verified domains
- [x] 4.0 Tests & Verification
  - [x] 4.1 Add backend tests for claim flow
  - [x] 4.2 Add dashboard tests for claim UI
  - [x] 4.3 Run lint/tests — ✅ ruff ✅ pytest ✅ puppeteer ✅ dashboard lint ✅ dashboard test:e2e

## Success Criteria
- Users can initiate and verify org domain claims via explicit verification.
- Verified domains can optionally enable auto-join for matching emails.
- Independent users can remain without an org by default.
- Tests cover claim creation, verification, and access control.

## Completion Notes
- Auth-service lint/tests: ✅ ruff ✅ pytest.
- Dashboard lint produced pre-existing warnings; ✅ lint and ✅ test:e2e (puppeteer) ran.
