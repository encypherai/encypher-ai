# Signup Password Length and Request Size Limits

**Status:** 🔄 In Progress
**Current Goal:** Task 1.1 — Confirm current signup validation and request size handling

## Overview
Auth endpoints currently enforce a minimum password length but do not cap password size or request body size. Large payloads can increase CPU/memory usage before validation, risking availability on the signup flow. We will add explicit password max-length validation and request body size limits to mitigate application-layer DoS.

## Objectives
- Add server-side max-length validation for passwords across auth endpoints.
- Enforce request body size limits on sensitive auth endpoints to avoid oversized payloads.
- Add tests and documentation for the new limits.

## Tasks

### 1.0 Discovery
- [ ] 1.1 Confirm current signup/login/password reset validation and hashing behavior
- [ ] 1.2 Identify where to enforce request body size limits in auth service

### 2.0 Remediation
- [ ] 2.1 Add max-length validation to auth schemas for passwords
- [ ] 2.2 Add request body size limit middleware for auth endpoints
- [ ] 2.3 Add configuration/env docs for request size limits

### 3.0 Testing & Validation
- [ ] 3.1 Unit tests passing — ✅ pytest
- [ ] 3.2 Integration tests passing — ✅ pytest
- [ ] 3.3 Frontend verification — ✅ puppeteer (if applicable)

## Success Criteria
- Auth endpoints reject oversized passwords with 4xx responses before hashing.
- Auth endpoints reject request bodies above the configured limit with 413.
- Tests and docs updated with verification markers.

## Completion Notes

(Filled when PRD is complete. Summarize what was accomplished.)
