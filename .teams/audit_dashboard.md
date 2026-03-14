# Dashboard Audit: apps/dashboard/src/

**Date:** 2026-03-14
**Scope:** apps/dashboard/src/ (excluding node_modules/, .next/, dist/)
**Skills run:** unix-agent-design, simplify, security-review

---

## 1. Unix Agent Design Audit

### Auditable Surfaces

The dashboard exposes two Next.js HTTP route handlers and a rich API client library:

| Surface | File |
|---|---|
| GET /api/health | src/app/api/health/route.ts |
| POST /api/auth/[...nextauth] | src/app/api/auth/[...nextauth]/route.ts |
| fetchWithAuth / apiClient | src/lib/api.ts |

No MCP servers, CLI tools, or agent tool handlers exist. Criteria designed for agent interfaces (overflow, binary guard, progressive help L0/L1, chain composition) are not applicable. The 10 criteria are assessed for the HTTP/client surfaces only.

### Scorecard

| Surface | Nav Errors | Overflow | Binary Guard | Footer | Help L1 | Help L0 | Stderr | Two-Layer | Surface Area | Chains |
|---|---|---|---|---|---|---|---|---|---|---|
| GET /api/health | N/A | N/A | N/A | FAIL | N/A | N/A | N/A | N/A | PASS | N/A |
| POST /api/auth | PARTIAL | N/A | N/A | FAIL | N/A | N/A | PARTIAL | PARTIAL | PASS | N/A |
| fetchWithAuth | PARTIAL | N/A | N/A | FAIL | N/A | N/A | N/A | PARTIAL | PASS | N/A |

### Key Findings

**Criterion 1 - Navigation errors: PARTIAL**
- `route.ts:113`: `throw new Error('Please enter both email and password')` gives no next-step action.
- `route.ts:151,215`: Session expiry and OAuth error paths throw bare strings with no navigation hint.
- `api.ts:483-502`: `ApiError` carries `nextAction` and `docsUrl` -- good. But methods returning `unknown` (e.g., `getProfile`, `getAdminStats`) lose this context at the call site.

**Criterion 4 - Metadata footer: FAIL (all paths)**
- No response path adds a timing/status token (`[OK|ERROR | Xms]`). All JSON responses are plain data with no metadata footer. Low priority for a browser dashboard (not an agent tool), but noted.

**Criterion 7 - Stderr attachment: PARTIAL**
- `route.ts:52-54`: `refreshBackendToken` logs refresh failures to console but returns `null`. The JWT callback converts `null` into the generic string `'RefreshAccessTokenError'` with no underlying detail. Callers cannot distinguish network error from token revocation.
- Fix: change `refreshBackendToken` to return `{ ok: true; data: ... } | { ok: false; reason: string }` and propagate the reason into the error token.

**Criterion 8 - Two-layer separation: PARTIAL**
- `mapBackendUser`, `refreshBackendToken`, `verifyBackendAccessToken` are correctly isolated.
- The `authorize` function (`route.ts:110-257`, ~150 lines) mixes credential validation, HTTP calls, MFA logic, token-based login, and error shaping. It should be split into `authorizeWithToken`, `authorizeWithMfa`, `authorizeWithCredentials`.
- Four dead URL alias constants (`AUTH_SERVICE_URL`, `KEY_SERVICE_URL`, `ANALYTICS_SERVICE_URL`, `BILLING_SERVICE_URL`) all equal `API_BASE_URL` at `api.ts:24-27`, implying microservice separation that does not exist.

**Criterion 9 - Tool surface area: PASS**
All surfaces are focused and minimal.

**Applicable Production Patterns:**
- Story 2 (stderr attachment): `refreshBackendToken` returns `null` silently on failure, matching the "stderr silently dropped" anti-pattern. The client sees `'RefreshAccessTokenError'` with no cause, forcing blind retries or confusing UX.

---

## 2. Simplify Review

### Changes Reviewed (from git diff)

Three files were changed by the preceding work:
- `apps/dashboard/src/components/providers.tsx` -- deduplicated `isSessionExpiredError`, added `ApiError` toast handling
- `apps/dashboard/src/hooks/useAuthErrorHandler.ts` -- removed local `isSessionExpiredError`, now imports from SSOT
- `apps/dashboard/src/lib/api.ts` -- extended `ApiError` with `nextAction`, `docsUrl`, `fieldErrors`; enriched error envelope parsing in `fetchWithAuth`
- `apps/dashboard/src/lib/session-errors.ts` -- new SSOT file (untracked)

### Issues Found and Fixed

**Fix 1: Dead function `createAuthErrorHandler` removed**
- File: `apps/dashboard/src/hooks/useAuthErrorHandler.ts`
- The function was defined but never imported or called anywhere in the codebase. It duplicated the same toast+signOut logic already present in `providers.tsx::handleAuthError`. Removed per Rule 13.

**Fix 2: Dead generic HTTP methods removed from `apiClient`**
- File: `apps/dashboard/src/lib/api.ts` (lines 1511-1599 before removal)
- Four methods (`get`, `post`, `patch`, `delete`) duplicated header construction and error handling already provided by `fetchWithAuth`. None were called anywhere in the codebase. They also bypassed the new error-envelope parsing (`nextAction`, `docsUrl`, `fieldErrors`), meaning any caller would receive impoverished `ApiError` objects. Removed per Rules 13 and 12.

**TypeScript check:** `npx tsc --noEmit` passes with zero errors after both removals.

### Findings Not Fixed (Pre-existing / Out of Diff Scope)

- Dead URL alias constants (`AUTH_SERVICE_URL` etc.) at `api.ts:24-27` -- pre-existing, not in the diff. Recommended future cleanup.
- `authorize` function at `route.ts:110-257` is too large and mixes concerns -- pre-existing structure, out of scope.

---

## 3. Security Review

### Scope

Only security implications **newly introduced** by the diff were assessed. Pre-existing concerns are excluded.

### Findings

**No HIGH or MEDIUM confidence vulnerabilities were found** in the `apps/dashboard/src/` changes.

The following patterns were investigated and cleared:

**Investigated: `nextAction` rendered in Sonner toast (providers.tsx:58,64)**
- `api.ts:533`: `nextAction = err.next_action` is taken from the API error response (attacker-observable but backend-controlled in normal operation).
- `providers.tsx:58,64`: Rendered as `toast.error(error.message, { description: error.nextAction })`.
- Cleared: Sonner renders toast content as plain text, not HTML. No `dangerouslySetInnerHTML` in the changed files. React's XSS protections apply. No exploit path.

**Investigated: Keyword-based session-expiry detection (session-errors.ts:29-46)**
- Error messages are matched against keyword lists to decide whether a 401 triggers logout.
- A 401 whose backend message happens to contain a tier keyword (e.g., "Your enterprise plan session has expired") would NOT trigger logout.
- Cleared: This is client-side behavior only. Server-side auth enforcement is independent. Failing to auto-logout is a UX flaw, not an authentication bypass -- the next request will still be rejected by the backend.

**Investigated: `isLoggingOut` module-level flag (providers.tsx:19)**
- Set to `true` on first logout trigger, never reset.
- If `signOut()` fails, subsequent 401s are silently swallowed.
- Cleared: Module-level flag is a reliability issue, not a security vulnerability. No attacker can exploit this to gain access; it only prevents repeated logout toasts.

### Summary

The changes are security-neutral. They consolidate duplicated session-expiry detection into a single canonical function (`session-errors.ts`) and enrich `ApiError` objects with backend-provided metadata that is rendered as plain text. No new attack surfaces are introduced.

---

## Priority Recommendations (Combined)

| Priority | Finding | File | Action |
|---|---|---|---|
| P1 | `refreshBackendToken` returns `null` silently; JWT callback loses error detail | `route.ts:44-68` | Return typed result union; propagate reason into token error field |
| P2 | `authorize` function is 150 lines mixing MFA, token login, credential login, error shaping | `route.ts:110-257` | Extract into `authorizeWithToken`, `authorizeWithMfa`, `authorizeWithCredentials` |
| P3 | Dead URL alias constants (`AUTH_SERVICE_URL` etc.) suggest non-existent microservice split | `api.ts:24-27` | Remove aliases, use `API_BASE_URL` directly throughout |
| P4 | Admin/profile methods return `unknown`, losing `nextAction` context for callers | `api.ts:811,1004` | Type return values concretely |

---

## Changes Made During This Audit

1. **Removed** `createAuthErrorHandler` dead function from `src/hooks/useAuthErrorHandler.ts`
2. **Removed** four dead generic HTTP methods (`get`, `post`, `patch`, `delete`) from `apiClient` in `src/lib/api.ts`
3. TypeScript: zero errors confirmed after changes

No commits were made.
