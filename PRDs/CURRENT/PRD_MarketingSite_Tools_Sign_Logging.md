# PRD: Marketing Site Tools Sign Logging

**Status:** 🔄 In Progress
**Current Goal:** Add production-grade logging for the marketing-site `/api/tools/sign` proxy to surface 500s.

## Overview
The marketing site sign tool currently returns 500s in production without actionable logs. This PRD adds structured logging to the `/api/tools/sign` proxy (and related tooling) so we can trace failures, validate upstream responses, and pinpoint configuration errors.

## Objectives
- Capture request context (request id, environment, payload metadata) for sign proxy calls.
- Log upstream response status/body details without leaking secrets.
- Ensure error paths surface in logs and responses consistently.

## Tasks
### 1.0 Investigation
- [x] 1.1 Review `/api/tools/sign` proxy flow and upstream Enterprise API call.
- [x] 1.2 Identify missing validation and error logging gaps.

### 2.0 Tests
- [x] 2.1 Add unit coverage for sign request builder/validation helpers. — ✅ npm test

### 3.0 Implementation
- [x] 3.1 Add structured logging for sign proxy request/response paths.
- [x] 3.2 Add request validation and consistent error responses.

### 4.0 Verification
- [x] 4.1 Run marketing-site unit tests — ✅ npm test
- [ ] 4.2 Manual verification against `/api/tools/sign` in production.

## Success Criteria
- Logs capture sign request metadata and upstream failure details in production.
- Missing env vars or invalid payloads emit explicit errors and logs.
- Unit tests cover helper logic used by the sign proxy.

## Completion Notes
- Updated sign payload defaults and provenance-only assertions for marketing-site tools.
- Enabled base /sign custom assertions with starter-tier limit to embed provenance in manifests.
