# TEAM_224 - Magic Link Team Invite + Org-Level 2FA Enforcement

## Session Info
- Date: 2026-02-22
- Branch: feature/rights-management-system
- Focus: Magic link team invite page + org-level 2FA enforcement

## Work Log

### Key Findings
- `organization_invites` table exists in enterprise_api DB (raw SQL, no ORM model)
  - Columns: id, organization_id, email, role, invited_by, token, status, expires_at, created_at, accepted_at
  - No org_name column -- use JOIN with organizations table (name column exists)
- `organization_members` table exists in enterprise_api DB
  - Columns: id, organization_id, user_id, role, joined_at (ONLY -- no status/invited_at/accepted_at)
  - FK: user_id -> users(id) (requires user to exist in enterprise_api users table)
  - accept-new endpoint upserts into enterprise_api users first (ON CONFLICT DO NOTHING)
- `org.features["enforce_mfa"]` -- existing JSON column on Organization model in auth-service
- `_has_permission` helper in OrganizationService for admin/owner check
- Dashboard calls both auth-service and enterprise_api via same API gateway at `NEXT_PUBLIC_API_URL`
  - Auth-service: /auth/* and /organizations/*
  - Enterprise API: /org/*
- Existing `/invite/[token]/page.tsx` handles auth-service invitations system (different from team.py invites)
- Auth-service already has `accept_invitation_new_user` endpoint with full org invite flow

### Task Status
- [x] T1 -- Public invite lookup (enterprise_api/app/routers/team.py)
- [x] T2 -- Internal user creation (services/auth-service/app/api/v1/endpoints.py)
- [x] T3 -- accept-new endpoint (enterprise_api/app/routers/team.py)
- [x] auth_service_client.create_user_internal() method
- [x] T4 -- Dashboard invite page (apps/dashboard/src/app/invite/team/[token]/page.tsx)
- [x] M1 -- Login MFA enforcement (services/auth-service/app/api/v1/endpoints.py)
- [x] M2 -- Org security settings GET/PATCH (services/auth-service/app/api/v1/organizations.py)
- [x] M3 -- Dashboard settings org security toggle
- [x] T5 -- Tests (enterprise_api + auth-service) -- pytest green
- [x] README updated with new public invite endpoints
- [x] SDK openapi.public.json updated with 4 missing paths (2 invite + 2 pre-existing)
- [x] enterprise_api: 1234 passed, 58 skipped -- pytest green
- [x] auth-service: 230 passed -- pytest green

## Test Results
- enterprise_api: `uv run pytest -q` -> 1234 passed, 58 skipped, 17 deselected
- auth-service: `uv run pytest -q` -> 230 passed, 21 deselected
- Linters: ruff clean on all modified files

## Suggested Commit Message
```
feat(security): magic link team invite + org-level 2FA enforcement (TEAM_224)

Team Invite (Feature 1):
- GET /org/invites/public/{token}: unauthenticated invite lookup joins
  organization_invites with organizations to return org_name, email, role
- POST /org/invites/public/{token}/accept-new: create user via
  auth-service internal endpoint + create org member record in one step
- POST /internal/users/create in auth-service: creates auto-verified user
  account from invite flow, returns access + refresh tokens
- add create_user_internal() to AuthServiceClient
- New dashboard page apps/dashboard/src/app/invite/team/[token]/page.tsx
  mirrors auth-service invite page with 4 cases (logged-in match, wrong
  email, existing user sign-in, new user registration)

2FA Enforcement (Feature 2):
- Login enforcement: if org.features["enforce_mfa"]=True and
  user.totp_enabled=False, return mfa_setup_required response (no token
  issued) with clear error message
- GET/PATCH /{org_id}/security endpoints on auth-service organizations
  router to read/write enforce_mfa feature flag
- Dashboard settings Organization tab: enforce MFA toggle (admin only)
- Tests: test_team_invite.py, test_mfa_enforcement.py, test_internal_user_create.py
- SDK openapi.public.json: add 4 missing route definitions
- enterprise_api README.md: document new public invite endpoints

Bug fixes during green phase:
- ON CONFLICT upsert in test fixtures (token regenerated each run)
- Use get_password_hash() from security.py (not passlib CryptContext)
- organization_members INSERT uses joined_at not status/invited_at
- Upsert user into enterprise_api users table before org_members insert (FK)
- Login enforcement uses getattr() for SimpleNamespace compatibility
- _make_user() created_at fixed to valid datetime for UserResponse.model_validate
```
