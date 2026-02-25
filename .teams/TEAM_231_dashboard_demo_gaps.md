# TEAM_231 — Dashboard Demo Gaps

## Status: COMPLETE (with session management addendum -- see C1-C4 below)

## Objective
Close 5 UI display bugs and 2 prefilled-data disconnects for Valnet-style demo with times@encypherai.com.

## Tasks
- [x] A1. rights/page.tsx: use licensee_name not licensee_org_id -- verified "Nexus AI Corp", "Meridian AI (Coalition Member)" in table
- [x] A2. TemplateSelector.tsx: neutral error state -- verified "No rights templates configured" in Playground
- [x] A3. DashboardLayout.tsx: rename "Provenance Activity" -> "AI Crawlers" -- verified in sidebar
- [x] A4. ai-crawlers/page.tsx: add CRAWLER_NAME_TO_COMPANY fallback -- fixed at service level too (see below)
- [x] A5. billing/page.tsx: bulk archive backfill callout -- verified callout appears above Add-Ons section
- [x] B1. Discover service databases -- all on same postgres instance (encypher_keys, encypher_coalition, encypher_content, etc.)
- [x] B2. Seed api_keys into key-service DB -- 3 keys seeded, fingerprint fixed (LEFT(id,8)), verified on API Keys page
- [x] B3. Seed coalition_earnings: billing service now queries encypher_content.coalition_earnings directly (fallback) -- verified $2,130.00
- [x] B4. Verify AI Company names via Puppeteer -- OpenAI (56), Google (28), Perplexity AI (27), Anthropic (15) now showing
- [x] Lint check -- warnings only, no errors, all pre-existing
- [x] Puppeteer verification -- all 5 UI fixes confirmed via screenshots

## Root Causes Fixed

### A4 / B4 Company Name Fix (service-level)
The service was grouping by `user_agent_category` ("ai_crawler") and looking up `known_crawlers` by
`crawler_type` ("ai_training", "ai_search"). These keys never matched, so `company` was always null.
Fix: changed `get_crawler_summary()` to group by `requester_user_agent` and match against
`known_crawlers.user_agent_pattern` via case-insensitive substring search.
File: `enterprise_api/app/services/rights_service.py` lines ~1041-1112.

### B3 Coalition Earnings
Billing service had `COALITION_SERVICE_URL` defaulting to `http://localhost:8009` (unreachable from
container). JWT vs API key auth mismatch, plus non-UUID user_id. Fix: added
`_query_content_coalition_earnings()` helper in billing service that queries
`encypher_content.coalition_earnings` directly via SQLAlchemy.
File: `services/billing-service/app/api/v1/endpoints.py`

### B2 API Keys
`encypher_keys` DB had no org or keys for times@encypherai.com. Seeded org and 3 keys.
NULL fingerprint caused 500 error -- fixed with `UPDATE api_keys SET fingerprint = LEFT(id, 8)`.

## Files Modified
- `apps/dashboard/src/app/rights/page.tsx`
- `apps/dashboard/src/components/TemplateSelector.tsx`
- `apps/dashboard/src/components/layout/DashboardLayout.tsx`
- `apps/dashboard/src/app/ai-crawlers/page.tsx`
- `apps/dashboard/src/app/billing/page.tsx`
- `enterprise_api/app/services/rights_service.py`
- `services/billing-service/app/api/v1/endpoints.py`
- `encypher_keys` DB (seeded via psql -- not in code)

## Session Management Addendum (C1-C4)

### C1. Silent token refresh (route.ts)
Added `refreshBackendToken()` helper + refresh logic in JWT callback. When the stored
`accessTokenExpires` timestamp passes, the server-side JWT callback calls `POST /auth/refresh`
with the stored `refreshToken`. On success, the new access token replaces the old one transparently.
On failure (revoked/expired refresh token), sets `error: 'RefreshAccessTokenError'` on the token.

### C2. Capture refresh token on login (route.ts)
Credentials `authorize()` now returns `refreshToken: data.data.refresh_token` and
`accessTokenExpires: Date.now() + 8h - 5m`. JWT callback stores these in the signed cookie.
Both Credentials and MFA-complete paths updated.

### C3. Session maxAge extended to 30 days (route.ts)
Was: 1 hour. Now: 30 days (matching refresh token lifetime). With rolling `updateAge: 24h`,
active users stay logged in indefinitely. Inactive users are logged out after 30 days.

### C4. DashboardLayout session guard (DashboardLayout.tsx)
Added `useEffect` that watches `status` (unauthenticated -> redirect) and `sessionError`
(RefreshAccessTokenError -> force signOut). This runs on every page that uses DashboardLayout,
not just user settings.

### C5. providers.tsx updates
- SessionProvider `refetchInterval` changed from 5min to 4min (triggers JWT callback more often,
  catches expiry earlier)
- `isSessionExpiredError`: bare 401 with no message body now returns `true` (was `false`)

### Files Modified (session management)
- `apps/dashboard/src/app/api/auth/[...nextauth]/route.ts`
- `apps/dashboard/src/components/layout/DashboardLayout.tsx`
- `apps/dashboard/src/components/providers.tsx`

## Suggested Git Commit Message

```
fix(dashboard): close demo gaps for times@encypherai.com

UI fixes:
- rights/page: show licensee_name instead of truncated org_id in Licensing table
- TemplateSelector: neutral "No rights templates configured" error state instead of
  "Enterprise tier required" (which fires on any error, not just tier blocks)
- DashboardLayout: rename "Provenance Activity" nav label to "AI Crawlers"
- ai-crawlers: add CRAWLER_NAME_TO_COMPANY fallback map for company attribution
- billing: add bulk archive backfill callout when documents_signed == 0

Service fixes:
- rights_service: group crawler analytics by requester_user_agent (not user_agent_category)
  and match against known_crawlers.user_agent_pattern -- fixes "Unknown" company breakdown
- billing-service: add _query_content_coalition_earnings() fallback that queries
  encypher_content directly when coalition-service is unreachable (JWT/URL mismatch)

Seed fixes (applied to encypher_keys DB directly):
- seeded org_encypher_times + 3 api_keys into encypher_keys; set fingerprint = LEFT(id,8)

Verified via Puppeteer:
- Licensing tab: "Nexus AI Corp", "Meridian AI (Coalition Member)"
- Playground: "No rights templates configured"
- Sidebar: "AI Crawlers"
- AI Crawlers: OpenAI (56), Google (28), Perplexity AI (27), Anthropic (15)
- Billing: Coalition Earnings $2,130.00, bulk archive callout visible
- Overview: 3 API keys displayed
```
