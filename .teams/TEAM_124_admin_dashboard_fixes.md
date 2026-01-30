# TEAM_124: Admin dashboard fixes

**Active PRD**: `PRDs/CURRENT/PRD_Admin_Dashboard_Real_Data.md`
**Working on**: Billing page fixes, admin role select
**Started**: 2026-01-21 20:58
**Status**: in_progress

## Session Progress
- [x] 3.2 — ✅ pytest ✅ ruff check
- [x] 4.1 — dashboard lint warnings pre-existing (not blocking)
- [x] 4.3 — ✅ pytest (super admin startup enforcement)
- [x] Billing page tier display fix — ✅ org tier fallback works
- [x] Infinite /organizations loop fix — ✅ useCallback + ref guard
- [x] Admin role select fix — ✅ backend endpoint + frontend API
- [x] Pricing sync — ✅ "Similarity detection" matches marketing site
- [x] Coalition revenue language — ✅ matches marketing (no percentages)
- [x] Popular badge suppression — ✅ hide when current tier > Professional
- [x] Starter signing limit — ✅ 1K/mo across pricing configs + billing service
- [x] Removed unlimited starter signing claims — ✅ marketing copy + docs + coalition value props
- [x] c2pa-text dependency — ✅ installed to unblock billing-service tests

## Changes Made (Session 2)
- `apps/dashboard/src/app/billing/page.tsx`: use org tier as fallback, remove infinite loop useEffect, align coalition revenue wording, suppress popular badge for higher tiers.
- `apps/dashboard/src/contexts/OrganizationContext.tsx`: fix infinite fetch loop with useCallback + hasFetchedRef.
- `apps/dashboard/src/lib/api.ts`: add updateUserRole API method.
- `apps/dashboard/src/lib/pricing-config/tiers.ts`: sync "Similarity detection", revenue share wording, and starter signing limit (1K/mo).
- `services/auth-service/app/models/schemas.py`: add RoleUpdateRequest/Response schemas.
- `services/auth-service/app/services/admin_service.py`: add update_user_role method.
- `services/auth-service/app/api/v1/endpoints.py`: add /admin/users/update-role endpoint.
 - `packages/pricing-config/src/tiers.ts`: starter signing limit now 1K/mo.
 - `services/billing-service/app/services/billing_service.py`: starter signing limit now 1K/mo.
 - `services/billing-service/app/api/v1/endpoints.py`: fallback starter signing limit now 1K/mo.
 - `apps/marketing-site/src/components/pricing/FeatureComparisonTable.tsx`: starter signing limit 1K/mo.
 - `apps/marketing-site/src/app/pricing/page.tsx`: starter signing limit 1K/mo.
 - `apps/marketing-site/src/lib/pricing-config/tiers.ts`: starter signing limit 1K/mo.
- `packages/pricing-config/src/coalition.ts`: starter coalition copy now 1K/mo.
- `apps/marketing-site/src/lib/pricing-config/coalition.ts`: starter coalition copy now 1K/mo.
- `apps/dashboard/src/lib/pricing-config/coalition.ts`: starter coalition copy now 1K/mo.
- `apps/marketing-site/src/components/pricing/pricing-table.tsx`: starter description now 1K/mo (no unlimited).
- `apps/marketing-site/src/app/solutions/publishers/page.tsx`: starter list item now 1K/mo.
- `enterprise_api/app/utils/quota.py`: starter C2PA quota now 1K/mo (no unlimited comment).
- `docs/pricing/PRICING_STRATEGY.md`: removed unlimited starter claims and updated tables/value prop.
- `enterprise_api/README.md`: starter monthly quota updated to 1,000.
- `services/billing-service/shared_libs/pyproject.toml`: added c2pa-text dependency.
 - `docs/pricing/PRICING_STRATEGY.md`: starter soft cap updated to 1K/mo.
 - `docs/guides/publisher-integration-guide.md`: starter signing limit updated to 1K/mo.

## Changes Made (Session 1)
- `apps/dashboard/src/components/UserActivityModal.tsx`: force opaque modal background for activity log viewer.
- `apps/dashboard/src/lib/api.ts`: route admin tier/status updates through auth-service Traefik paths.
- `services/auth-service/app/models/schemas.py`: add admin tier/status update schemas.
- `services/auth-service/app/services/admin_service.py`: implement tier/status update logic (including user->org lookup).
- `services/auth-service/app/api/v1/endpoints.py`: add admin update-tier/update-status endpoints.
- `services/auth-service/tests/test_admin_dashboard_data.py`: add tests for tier/status updates.
- `services/auth-service/app/services/super_admin_service.py`: enforce super admin flag on startup.
- `services/auth-service/app/main.py`: call super admin enforcement during lifespan startup.
- `services/auth-service/tests/test_super_admin_startup.py`: add startup enforcement tests.
- `PRDs/CURRENT/PRD_Admin_Dashboard_Real_Data.md`: add completion notes.

## Blockers
- None.

## Handoff Notes
- Rebuild auth-service container to pick up role update endpoint.
- Test role select on admin page after rebuild.
- Dashboard lint warnings are pre-existing, not from these changes.
