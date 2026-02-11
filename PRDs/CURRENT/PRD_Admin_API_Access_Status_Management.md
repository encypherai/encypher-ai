# PRD: Admin API Access Status Management

**Status**: ✅ Complete  
**Team**: TEAM_164  
**Current Goal**: Add API access status visibility and toggle controls to admin user directory

## Overview
Super admins need to see and manage the API access status of every user from the admin dashboard. This includes viewing the current status and toggling between active, inactive, and suspended states. Suspended users are blocked from requesting API access and shown a support contact message.

## Objectives
- Display API access status for every user in the admin user directory
- Allow super admins to toggle API access status (active/inactive/suspended)
- Suspended users cannot request API access and see a "contact support" message
- Maintain audit trail of status changes

## Tasks

### 1.0 Backend Changes
- [x] 1.1 Add `suspended` to `ApiAccessStatus` enum in `db/models.py`
- [x] 1.2 Add `suspended` to `ApiAccessStatus` enum in `models/schemas.py`
- [x] 1.3 Add `api_access_status` field to admin `list_users` response in `admin_service.py`
- [x] 1.4 Create new schema `ApiAccessStatusSetRequest` for admin to set status directly
- [x] 1.5 Add `set_api_access_status` method to `ApiAccessService`
- [x] 1.6 Add admin endpoint `POST /admin/set-api-access-status` in `endpoints.py`
- [x] 1.7 Update `request_api_access` to reject suspended users
- [x] 1.8 Update `is_api_access_approved` to return False for suspended users
- [x] 1.9 Update `get_api_access_status` to return suspended message

### 2.0 Frontend Changes
- [x] 2.1 Add `setApiAccessStatus` method to `apiClient` in `lib/api.ts`
- [x] 2.2 Add `api_access_status` to `AdminUser` type and normalizer
- [x] 2.3 Add "API Access" column header to user directory table
- [x] 2.4 Add API access status dropdown per user row
- [x] 2.5 Add mutation for setting API access status
- [x] 2.6 Update user-facing API access status page to handle suspended state

### 3.0 Testing
- [x] 3.1 Backend unit tests for `set_api_access_status` — ✅ pytest (7 tests)
- [x] 3.2 Backend unit tests for suspended user blocking — ✅ pytest (3 tests)
- [x] 3.3 Frontend TypeScript compilation verified — ✅ tsc --noEmit
- [x] 3.4 Backend linting verified — ✅ ruff check

## Completion Notes
- All 27 backend tests pass (10 new TEAM_164 tests)
- TypeScript compiles cleanly with no errors
- Ruff linting passes with no issues
- New endpoint: `POST /api/v1/auth/admin/set-api-access-status`
- New enum value: `suspended` added to `ApiAccessStatus`
- Admin user directory now shows color-coded API Access dropdown per user
- Suspended users see a "Contact Support" page with no reapply option

## Success Criteria
- Admin can see API access status for all users in the user directory
- Admin can change any user's API access status via dropdown
- Suspended users see a "contact support" message when viewing API access
- Suspended users cannot submit new API access requests
- All changes are reflected immediately in the UI
