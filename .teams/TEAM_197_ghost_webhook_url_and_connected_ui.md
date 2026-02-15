# TEAM_197: Ghost webhook URL and connected UI

**Active PRD**: `PRDs/CURRENT/PRD_Hosted_Ghost_Webhook_Endpoint.md`
**Working on**: Return live Ghost webhook URL from backend, clarify webhook event mapping, improve connected-state dashboard UX
**Started**: 2026-02-15 16:15 UTC
**Status**: completed

## Session Progress
- [x] 1.1 — baseline verification — ✅ pytest
- [x] 1.2 — tests first for live webhook URL behavior (red -> green) — ✅ pytest
- [x] 2.1 — backend implementation
- [x] 2.2 — dashboard connected-state UX improvements
- [x] 2.3 — dashboard feature-gating hotfix
- [x] 3.1 — verification (pytest/lint + UI check) — ✅ pytest ✅ ruff ✅ npm lint ✅ npm type-check ✅ puppeteer(login-gate)
- [x] 3.2 — targeted test verification for dashboard feature-gating hotfix

## Changes Made
- `enterprise_api/app/routers/integrations.py`
  - `_build_webhook_url(...)` now returns absolute/live URL using request base URL fallback to `settings.api_base_url`.
  - Create/get/regenerate endpoints now pass `request` through response/url builders.
  - Masked webhook URL in GET response is now absolute as well.
- `enterprise_api/tests/test_ghost_integration.py`
  - Added TDD coverage for webhook URL generation with configured `api_base_url`.
  - Updated response schema fixture URLs to absolute webhook URL examples.
- `apps/dashboard/src/app/integrations/GhostIntegrationCard.tsx`
  - Clarified event labels: "Published post/page updated" with fallback note for Ghost versions showing "Post/Page updated".
  - Redesigned connected state to include dedicated webhook URL block + copy action.
  - Fixed overflow/readability issues for long masked API key and long webhook URLs.
  - Improved action layout wrapping for regenerate/disconnect confirms.
- `apps/dashboard/src/app/billing/page.tsx`: Fixed current-plan price label rendering so enterprise orgs without a fixed recurring amount render `Custom` instead of `Free`.
- `apps/dashboard/src/app/billing/page.tsx`: Removed eager `apiClient.getSubscription(...)` call from billing page load path to avoid expected/noisy `GET /api/v1/billing/subscription` 404s for orgs without Stripe-managed subscriptions.
- `apps/dashboard/src/app/audit-logs/page.tsx`: Expanded audit-log gate to allow super-admin access (`enterprise || isSuperAdmin`), reusing `apiClient.isSuperAdmin`.
- `apps/dashboard/src/components/layout/DashboardLayout.tsx`: Fixed enterprise nav filtering to keep enterprise-only items visible for super admins.
- `apps/dashboard/tests/e2e/feature-gating.super-admin-and-billing.test.mjs`: Added targeted regression coverage for billing label behavior, audit-log super-admin gating, and nav visibility.
- `apps/dashboard/tests/e2e/billing.subscription-intent.test.mjs`: Added targeted regression test to enforce billing page intent (tier sourced from org/session, no eager legacy subscription endpoint fetch).

## Blockers
- Could not fully validate connected-state UI via puppeteer because localhost session routes to sign-in page without authenticated test credentials.
- `npm run test:e2e` currently fails on pre-existing playground contract tests unrelated to Ghost integration changes.

## Handoff Notes
- Ghost webhook URL now copies as absolute/live URL from backend (`https://.../api/v1/integrations/ghost/webhook?token=...`) instead of relative path.
- Ghost event guidance now explicitly handles both naming variants for updated events.
- Connected card UX no longer overflows on long values and surfaces webhook URL as a first-class field.
- Targeted verification run only (per request):
  - `node --test tests/e2e/feature-gating.super-admin-and-billing.test.mjs tests/e2e/billing.enterprise-revshare.test.mjs` 
- Additional targeted verification for billing 404 fix:
  - `node --test tests/e2e/billing.subscription-intent.test.mjs tests/e2e/feature-gating.super-admin-and-billing.test.mjs` ✅
- Full `npm run test:e2e` was intentionally not re-run because it contains unrelated pre-existing failures.

## Suggested Commit Message
```
fix(ghost): return absolute webhook URLs and improve connected integration UX

Backend:
- Build Ghost webhook URLs as absolute/live URLs using request base URL,
  with api_base_url fallback for non-request contexts.
- Pass request through Ghost integration create/get/regenerate response builders
  so dashboard receives copy-ready target URLs for Ghost Admin.
- Add/adjust tests for webhook URL generation against configured api_base_url.

Dashboard:
- Clarify Ghost webhook event labels for version differences
  (Published post/page updated vs Post/Page updated).
- Redesign connected Ghost card to show configured webhook URL with copy action.
- Fix overflow/readability issues for long API key masks and long URLs.
- Improve action button wrapping/confirm states for regenerate/disconnect.

Verification:
- uv run pytest enterprise_api/tests/test_ghost_integration.py
- uv run ruff check enterprise_api/app/routers/integrations.py enterprise_api/tests/test_ghost_integration.py
- npm run lint (apps/dashboard)
- npm run type-check (apps/dashboard)
```
