# TEAM_166 — Enterprise API README Endpoint Audit

## Status: COMPLETE

## Goal
Audit and update `enterprise_api/README.md` to accurately reflect the current API endpoint structure.

## Key Findings

### Discrepancies Found

1. **`/api/v1/sign/advanced`** — README lists it twice with contradictory info:
   - Line 140: Says "REMOVED - Returns 410 Gone" ✅ (correct per signing.py)
   - Line 177: Lists it under "Enterprise Embeddings Endpoint" as active Professional+ — **WRONG**, it's deprecated/410

2. **`/api/v1/verify`** — README says POST public (line 142) but code returns 410 Gone (verification.py line 373-382). The unified verify is now via verification-service, not enterprise_api directly.

3. **`/api/v1/verify/{document_id}`** — README says GET public (line 143) but code returns 410 Gone (verification.py line 107-119).

4. **`/api/v1/verify/signature`** — Listed in README (line 144) but does NOT exist in codebase.

5. **`/api/v1/verify/document`** — Listed in README (line 145) but does NOT exist in codebase.

6. **`/api/v1/verify/history/{document_id}`** — Listed in README (line 146) but does NOT exist in codebase.

7. **`/api/v1/verify/stats`** — Listed in README (line 147) but does NOT exist in codebase.

8. **`/api/v1/verify/health`** — Listed in README (line 148) but does NOT exist in codebase.

9. **`/api/v1/public/extract-and-verify`** — README lists as active (line 221) but code returns 410 Gone (deprecated).

10. **Missing endpoints not in README:**
    - `/api/v1/usage/reset` (POST, Admin)
    - `/api/v1/usage/history` (GET)
    - `/api/v1/audit-logs` (GET)
    - `/api/v1/audit-logs/export` (GET)
    - `/api/v1/org/members` (team management endpoints)
    - `/api/v1/provisioning/*` (auto-provision, api-keys, users, health)
    - `/api/v1/tools/encode` and `/api/v1/tools/decode` (include_in_schema=False)
    - `/api/v1/admin/*` (admin endpoints)
    - `/api/v1/licensing/*` (internal licensing endpoints — README mentions them as excluded, OK)
    - `/api/v1/organizations/*` (proxy endpoints)
    - `/api/v1/public/c2pa/zw/resolve` (POST bulk resolve)
    - `/api/v1/sign/stream/health` (Admin only)
    - `/api/v1/sign/stream/runs/{run_id}` (GET)

11. **`/api/v1/chat/stream`** — README says WS but code doesn't have a `/chat/stream` route. The WebSocket is at `/api/v1/sign/stream` (websocket upgrade). Chat router only has `/chat/completions` and `/chat/health`.

12. **Onboarding endpoints** — README lists `/api/v1/onboarding/request-certificate` and `/api/v1/onboarding/certificate-status` which match the code ✅

13. **Signing endpoint** — README says `/api/v1/sign/v2` in tier matrix header (line 86) but actual endpoint is `/api/v1/sign`.

## Changes Made

1. Fixed tier matrix header: `/api/v1/sign/v2` → `/api/v1/sign`
2. Rewrote Core Endpoints table:
   - Removed 6 phantom endpoints that never existed (`verify/signature`, `verify/document`, `verify/history/{id}`, `verify/stats`, `verify/health`)
   - Marked `POST /verify` and `GET /verify/{document_id}` as 410 MOVED to verification-service
   - Added explanatory note about verification-service split
3. Removed duplicate "Enterprise Embeddings Endpoint" section that incorrectly listed `/sign/advanced` as active
4. Updated Invisible Signed Embeddings section: endpoint reference changed from `/sign/advanced` to `/sign` (with options)
5. Fixed Public Verification table: marked `extract-and-verify` as deprecated/410
6. Fixed Streaming Endpoints: removed non-existent `/chat/stream` WS route
7. Added bulk ZW resolve endpoint to Public C2PA Utilities table
8. Added 3 new endpoint sections:
   - Team Management (`/org/members/*`)
   - Audit Logs (`/audit-logs`, `/audit-logs/export`)
   - Provisioning (Internal) (`/provisioning/*`)
9. Added `/metrics` to Health & Monitoring table

## Git Commit Suggestion

```
docs(enterprise_api): audit and fix README endpoint reference

- Fix tier matrix header (/sign/v2 → /sign)
- Remove 6 phantom endpoints that never existed in codebase
- Mark /verify and /verify/{document_id} as 410 (moved to verification-service)
- Remove duplicate Enterprise Embeddings section (sign/advanced is 410)
- Mark /public/extract-and-verify as deprecated (410 Gone)
- Remove non-existent /chat/stream WS route from streaming table
- Add missing sections: Team Management, Audit Logs, Provisioning
- Add bulk ZW resolve and /metrics endpoints
- Update Invisible Embeddings section to reference /sign with options

TEAM_166
```

## Session 1
- Date: 2026-02-12
- Scope: Endpoint accuracy audit

## Session 2
- Date: 2026-02-12
- Scope: Pricing restructure (Free + Enterprise) and /verify consolidation

### Session 2 Changes

1. **Tier matrix rewritten** — 2-column (Free / Enterprise), removed Professional/Business columns
2. **`/verify` consolidated** — single endpoint with feature flags (`include_attribution`, `detect_plagiarism`, `fuzzy_search`, `search_scope`), matching `/sign` pattern. Removed `/verify/advanced` from all tables and references.
3. **All endpoint tables updated** — replaced Professional+/Business+ with correct tier (All or Enterprise) per `tier_config.py`
4. **Rate limiting table** — simplified to Free/Enterprise/Strategic Partner
5. **Features by Tier** — Free tier now includes attribution + plagiarism detection; Enterprise list cleaned to only true Enterprise-only features
6. **Stale tier references fixed** — all prose sections updated (Security, Architecture, API examples)
7. **Design note added** — explains the unified endpoint pattern for both `/sign` and `/verify`

### Git Commit Suggestion (Session 2)

```
docs(enterprise_api): restructure README for freemium + enterprise pricing

- Rewrite tier matrix to 2-tier model (Free + Enterprise)
- Consolidate /verify/advanced into /verify with feature flags
  (matching /sign pattern: single endpoint, tier-gated flags)
- Update all endpoint tables: Professional+/Business+ → All or Enterprise
- Simplify rate limiting table to Free/Enterprise/Strategic Partner
- Fix Features by Tier: attribution + plagiarism now free
- Remove all stale Professional/Business/Starter tier references
- Add design note explaining unified endpoint pattern

TEAM_166
```
