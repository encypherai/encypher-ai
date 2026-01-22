# PRD: Marketing Site Tools API Host Fix

**Status:** In Progress  
**Current Goal:** Ensure the marketing-site encode/decode tools default to the production Enterprise API host (`api.encypherai.com`) when environment variables are missing, while keeping local development safe.

## Overview
The marketing site proxies encode/decode requests through Next.js API routes. The sign route currently defaults to a staging host, causing production requests to hit the wrong backend. We will standardize Enterprise API URL resolution for tools routes, add unit coverage for fallback behavior, and verify the corrected routing.

## Objectives
- Route `/api/tools/sign` and `/api/tools/verify` to the production Enterprise API host by default in production.
- Preserve local development defaults when environment variables are not set.
- Add unit tests that validate the Enterprise API URL resolution logic.

## Tasks
- [x] 1.0 Investigation
  - [x] 1.0.1 Review marketing-site tools proxy routes
  - [x] 1.0.2 Confirm current Enterprise API environment defaults
- [x] 2.0 Tests
  - [x] 2.0.1 Add unit coverage for Enterprise API URL resolution
- [x] 3.0 Implementation
  - [x] 3.0.1 Create shared Enterprise API URL resolver
  - [x] 3.0.2 Update tools proxy routes to use shared resolver
- [ ] 4.0 Verification
  - [x] 4.0.1 Run marketing-site unit tests
  - [x] 4.0.2 Run marketing-site linting
  - [x] 4.0.3 Manual encode/decode verification (✅ puppeteer)

## Success Criteria
- The sign/verify proxy routes default to `https://api.encypherai.com` in production when env vars are unset.
- Local development defaults remain `http://localhost:9000` when env vars are unset.
- Unit tests for URL resolution pass.

## Completion Notes
- _TBD_
