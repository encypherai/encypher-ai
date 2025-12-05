# PRD: User Onboarding Flow Fixes

**Status**: Deployed (Pending Verification)  
**Team**: TEAM_005  
**Created**: 2025-12-05  
**Priority**: P0 (Critical - Blocking new user activation)

## Current Goal
Fix the complete user onboarding flow from signup through first API call.

## Overview
New users are experiencing multiple friction points during onboarding:
1. Signup page has poor readability/UX
2. No notification that email verification is required
3. Email verification link doesn't auto-login the user
4. "Go to dashboard" after verification requires cache clear + re-login
5. API keys created via key-service don't work with enterprise-api (returns "Organization not found")

The root cause of issue #5 is a **split-brain architecture**: key-service creates API keys linked to `users`, while enterprise-api expects API keys linked to `organizations` in its own database schema.

## Objectives
- Improve signup page readability and UX
- Clearly communicate email verification requirement
- Auto-login users after email verification
- Fix session/cookie issues after verification
- Resolve the organization lookup failure for new user API keys

## Tasks

### 1.0 Signup Page Improvements
- [ ] 1.1 Audit current signup page styling for readability issues
- [ ] 1.2 Add email verification notice after successful signup
- [ ] 1.3 Improve form validation feedback
- [ ] 1.4 Add success state with clear next steps

### 2.0 Email Verification Flow
- [x] 2.1 Create `/auth/verify-email` page in dashboard
  - [x] 2.1.1 Accept `token` query parameter
  - [x] 2.1.2 Call auth-service `/api/v1/auth/verify-email` endpoint
  - [x] 2.1.3 Handle success: auto-login user with returned tokens
  - [x] 2.1.4 Handle error: show appropriate message
- [x] 2.2 Update auth-service email template URL if needed (already correct)
- [x] 2.3 Implement auto-login after verification
  - [x] 2.3.1 Use NextAuth `signIn('credentials')` with returned tokens
  - [ ] 2.3.2 Or implement custom session creation (not needed)

### 3.0 Session/Cookie Issues
- [ ] 3.1 Investigate why "Go to dashboard" requires cache clear
- [ ] 3.2 Ensure cookies are properly set after verification
- [ ] 3.3 Test cross-subdomain cookie behavior

### 4.0 Organization/API Key Architecture Fix (Critical)
- [x] 4.1 Diagnose the split-brain issue
  - [x] 4.1.1 key-service creates keys in `api_keys` table with `user_id`
  - [x] 4.1.2 enterprise-api expects keys joined to `organizations` table
  - [x] 4.1.3 New users have no organization record in enterprise-api DB
- [x] 4.2 Design solution (choose one):
  - Option A: Auto-create organization when user creates first API key
  - Option B: Sync organizations from auth-service to enterprise-api
  - Option C: Modify enterprise-api to call key-service for validation
  - **Option D (CHOSEN)**: Use key-service's `/validate` endpoint which returns synthetic org context
- [x] 4.3 Implement chosen solution
- [ ] 4.4 Test end-to-end: signup → verify → create key → use in playground

### 5.0 Local Testing
- [ ] 5.1 Set up local Docker environment
- [ ] 5.2 Test complete flow locally
- [ ] 5.3 Document any environment-specific issues

## Technical Analysis

### Current Architecture (Split-Brain Problem)

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Dashboard      │────▶│  Key Service    │────▶│  Auth Service   │
│  (Next.js)      │     │  (FastAPI)      │     │  (FastAPI)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                       │                       │
        │                       ▼                       ▼
        │               ┌─────────────────┐     ┌─────────────────┐
        │               │  Core DB        │     │  Core DB        │
        │               │  - api_keys     │     │  - users        │
        │               │  - (user_id)    │     │  - organizations│
        │               └─────────────────┘     └─────────────────┘
        │
        ▼
┌─────────────────┐
│  Enterprise API │
│  (FastAPI)      │
└─────────────────┘
        │
        ▼
┌─────────────────┐
│  Enterprise DB  │
│  - api_keys     │ ◀── Different schema!
│  - organizations│     Expects organization_id
└─────────────────┘
```

### Key Service's `/validate` Response (for user-level keys)
```json
{
  "key_id": "...",
  "user_id": "...",
  "organization_id": "user_{user_id}",  // Synthetic
  "organization_name": "Personal Account",
  "tier": "starter",
  "is_demo": true,  // Allows demo signing key
  "features": {...},
  "permissions": ["sign", "verify"]
}
```

### Recommended Solution: Option D
Modify enterprise-api to call key-service's `/validate` endpoint for authentication instead of querying its local database. This:
- Leverages existing infrastructure
- Provides synthetic org context for user-level keys
- Sets `is_demo: true` so demo signing keys can be used
- Avoids database sync complexity

## Files to Modify

### Dashboard (apps/dashboard)
- `src/app/signup/page.tsx` - Improve UX, add verification notice
- `src/app/auth/verify-email/page.tsx` - NEW: Handle verification link
- `src/app/api/auth/[...nextauth]/route.ts` - May need session handling updates

### Auth Service (services/auth-service)
- `shared_libs/src/encypher_commercial_shared/email/emails.py` - Verify URL format

### Enterprise API (enterprise_api)
- `app/middleware/api_key_auth.py` - Call key-service instead of local DB

## Success Criteria
- [ ] New user can sign up and see clear "check your email" message
- [ ] Clicking verification link auto-logs user into dashboard
- [ ] User can create API key in dashboard
- [ ] API key works in playground for /sign endpoint
- [ ] No "Organization not found" errors
- [ ] All tests pass

## Completion Notes

### 2025-12-05 - Initial Implementation Deployed

**Changes Made:**
1. Created `/auth/verify-email` page in dashboard that:
   - Accepts token from email link
   - Calls auth-service to verify
   - Attempts auto-login with returned tokens
   - Shows success/error states

2. Updated signup page:
   - Shows clear "Check Your Email" success state after signup
   - Lists next steps for user
   - Improved styling to match login page

3. Updated enterprise-api auth middleware:
   - Now calls key-service `/validate` endpoint first
   - Falls back to local DB for legacy keys
   - User-level keys get `is_demo: true` for demo signing key access

**Railway Environment Variable Required:**
```
KEY_SERVICE_URL=http://key-service.railway.internal:8080
```

**Pending Verification:**
- Test complete flow in production
- Verify auto-login works correctly
- Confirm API keys work in playground
