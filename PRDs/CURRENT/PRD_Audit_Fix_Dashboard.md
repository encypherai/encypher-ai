# PRD: Dashboard App Audit Fixes

**Status:** COMPLETE
**Current Goal:** All tasks implemented
**Branch:** feat/codebase-audit-fixes

## Overview
The audit agent already removed dead code (createAuthErrorHandler, 4 unused HTTP methods). This PRD covers remaining gaps: break up authorize function, clean up phantom URL aliases, add timing metadata.

## Objectives
- Break up monolithic authorize function
- Clean up phantom microservice URL aliases
- Add response timing metadata

## Tasks

### 1.0 Two-Layer Separation
- [x] 1.1 Break up `authorize` function in `route.ts:110-257` (~150 lines) into separate handlers for credential validation, MFA, token-based login, and error shaping -- extracted `authorizeWithToken`, `authorizeWithMfa`, `authorizeWithCredentials`, `buildAuthorizedUser` -- tsc clean
- [x] 1.2 Consolidate the 4 URL alias constants (`AUTH_SERVICE_URL`, etc. at `api.ts:24-27`) that all equal `API_BASE_URL` -- removed all 4 aliases, replaced every usage with `API_BASE_URL` directly -- tsc clean

### 2.0 Metadata Footer
- [x] 2.1 Add timing/status metadata to API responses where applicable -- health route adds `meta.ts` ISO timestamp; `fetchWithAuth` logs `OK/ERROR <status> <url> (<ms>ms)` in development

### 3.0 Stderr/Error Handling
- [x] 3.1 Fix `refreshBackendToken` to surface error cause instead of returning `null` silently -- changed return type to `RefreshResult = { ok: true; data } | { ok: false; reason: string }` -- tsc clean
- [x] 3.2 Make JWT callback error (`'RefreshAccessTokenError'`) carry underlying cause info -- silent refresh failure now sets `error: 'RefreshAccessTokenError: <reason>'` -- tsc clean

### 4.0 Linting
- [x] 4.1 Run eslint on changed files -- zero errors (pre-existing warnings in unrelated files only)
- [x] 4.2 Verify `tsc --noEmit` passes -- confirmed zero errors

## Success Criteria
- All tasks checked off -- YES
- `tsc --noEmit` passes -- YES
- Lint passes (no errors) -- YES

## Completion Notes
All changes confined to `apps/dashboard/src/`. No new files created. Key files changed:
- `src/app/api/auth/[...nextauth]/route.ts` -- authorize split + refreshBackendToken typed result union
- `src/lib/api.ts` -- 4 URL aliases removed, timing logging added to fetchWithAuth
- `src/app/api/health/route.ts` -- meta.ts timestamp added
