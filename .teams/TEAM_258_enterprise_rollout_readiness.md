# TEAM_258 -- Enterprise Rollout Readiness

**Created:** 2026-03-18
**Status:** Complete
**Focus:** P0 blockers for enterprise pilot sales + P1 expected features

## Scope
Implement enterprise rollout gaps identified in gap analysis:
- P0.1: BYOK Certificate Management UI
- P0.2: Stripe Connect Payout Wiring
- P0.3: API Key IP Allowlisting
- P1.1: Organization Administration Page
- P1.2: Image Signing Dashboard UI
- P1.3: Print Leak Detection Workflow UI
- P1.4: GDPR Data Deletion Workflow
- P1.5: Seat Management Upgrade Flow

## Session Log
- 2026-03-18: All 8 tasks completed using 4 parallel agents
  - byok-agent: P0.1 (BYOK UI)
  - stripe-agent: P0.2 (Stripe Connect), P1.5 (Seat Management)
  - ip-allowlist-agent: P0.3 (IP Allowlisting), P1.3 (Print Detection)
  - org-admin-agent: P1.1 (Org Admin), P1.2 (Image Signing), P1.4 (GDPR Deletion)

## Files Changed

### Modified
- apps/dashboard/src/app/api-keys/page.tsx (IP allowlist UI)
- apps/dashboard/src/app/billing/page.tsx (Stripe Connect + seat upgrade)
- apps/dashboard/src/app/settings/page.tsx (BYOK card + account deletion)
- apps/dashboard/src/app/team/page.tsx (seat upgrade CTA)
- apps/dashboard/src/components/layout/DashboardLayout.tsx (nav items)
- apps/dashboard/src/lib/api.ts (all new API methods)
- enterprise_api/app/bootstrap/routers.py (data_management router)
- enterprise_api/app/dependencies.py (IP allowlist check)
- services/billing-service/app/api/v1/endpoints.py (Connect onboarding)

### Created
- apps/dashboard/src/app/image-signing/page.tsx
- apps/dashboard/src/app/print-detection/page.tsx
- apps/dashboard/src/app/settings/organization/page.tsx
- enterprise_api/app/routers/data_management.py
- enterprise_api/tests/test_data_management.py (22 tests)
- enterprise_api/tests/test_ip_allowlist.py (12 tests)

## Verification
- next build: passes clean
- pytest: 34/34 new tests pass
- ruff: clean

## Suggested Commit Message

```
feat: enterprise rollout readiness -- P0 blockers and P1 features

BYOK certificate management UI in settings (register, list, revoke keys,
view trusted CAs). Stripe Connect payout wiring end-to-end (billing-service
endpoint, dashboard button, return/refresh handling). API key IP allowlisting
with IPv4/IPv6 CIDR support in auth middleware and dashboard UI.

Organization admin page with security policies, signing config, and feature
overview. Image signing dashboard with drag-drop upload, C2PA/watermark
options, and download. Print leak detection workflow with scan upload and
fingerprint matching. GDPR data deletion workflow with request/approval
lifecycle, 90-day purge window, and compliance receipts. Seat management
upgrade flow linking team page to billing.

New pages: /settings/organization, /image-signing, /print-detection
New backend: data_management.py (6 GDPR endpoints), IP allowlist middleware
Tests: 34 new (12 IP allowlist + 22 data management)
```
