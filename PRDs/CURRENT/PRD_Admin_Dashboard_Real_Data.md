# Admin Dashboard Real Data

**Status:** 🔄 In Progress
**Current Goal:** Surface real users and stats in the admin dashboard

## Overview
The admin dashboard currently shows seeded placeholder data and omits real auth-service users (e.g., test@encypherai.com). We need to wire the admin stats and user directory to live auth-service data so super admins see accurate user and organization metrics.

## Objectives
- Provide admin endpoints that return real users and organization stats from auth-service.
- Update dashboard admin API client to use the new real-data endpoints.
- Add regression tests for admin stats and user listing.
- Verify results in the dashboard UI.

## Tasks

### 1.0 Baseline & Test Plan
- [x] 1.1 Add tests for auth-service admin stats endpoint (red). — ✅ pytest
- [x] 1.2 Add tests for auth-service admin user list endpoint (red). — ✅ pytest

### 2.0 Auth-Service Admin Data Endpoints
- [x] 2.1 Implement AdminService for stats + user listing.
- [x] 2.2 Add /api/v1/auth/admin/stats and /api/v1/auth/admin/users routes.
- [x] 2.3 Ensure super-admin gating using existing JWT verification.

### 3.0 Dashboard Integration
- [x] 3.1 Update dashboard API client to call auth-service admin endpoints.
- [x] 3.2 Validate user list and stats show live auth-service data.

### 4.0 Verification
- [x] 4.1 Run linters and relevant tests — ✅ pytest, ✅ ruff check (auth-service), ⚠️ dashboard lint warnings, ✅ dashboard e2e (admin invite flow)
- [x] 4.2 Manual admin dashboard verification.

## Success Criteria
- Admin stats show live counts derived from auth-service organizations.
- Admin user directory includes test@encypherai.com and other auth users.
- Tests cover admin stats and user list endpoints.
- Dashboard UI displays real data with no stubs.

## Completion Notes
- Added auth-service admin tier/status update endpoints and wired dashboard admin client to route through Traefik.
- Added admin org lookup endpoint + typeahead for trial invites; removed team trial invite controls.
- Tests: ✅ `uv run ruff check app/` (auth-service), ✅ `uv run pytest tests/test_admin_dashboard_data.py`, ✅ `npm run test:e2e -- tests/e2e/team.invite-trial.test.mjs`.
- Manual verification: created local super admin and verified admin stats + trial invite org lookup in `/admin`.
- Dashboard lint still reports existing warnings.
- Enforced super admin flag for `erik.svilich@encypherai.com` at auth-service startup with ✅ `uv run pytest tests/test_super_admin_startup.py`.
