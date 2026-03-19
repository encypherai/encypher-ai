# TEAM_257 - Session Persistence Across Deploys

## Status: COMPLETE

## Summary
Users were being logged out on every deploy. Root cause: if `NEXTAUTH_SECRET` is not pinned as a stable Railway env var, each deploy generates a new random secret, invalidating all existing session cookies.

## Changes Made

1. **`apps/dashboard/src/app/api/auth/[...nextauth]/route.ts`** - Added fail-fast guard that crashes the app with a clear error if `NEXTAUTH_SECRET` is missing in production, preventing silent random secret generation.

2. **`apps/dashboard/next.config.js`** - Added `output: 'standalone'` for proper runtime env var inheritance on containerized platforms (Railway/RAILPACK).

3. **`apps/dashboard/src/app/enforcement/[noticeId]/page.tsx`** - Fixed pre-existing type error (`unknown` not assignable to `ReactNode` / `string`) that blocked the build.

## Manual Steps Required
- Verify in Railway dashboard that `NEXTAUTH_SECRET` is set as a stable shared variable on the dashboard service (at least 32 chars)
- Verify `JWT_SECRET_KEY` is set as a stable shared variable on the auth-service
- After deploy: confirm users stay logged in across subsequent deploys

## Suggested Commit Message
```
fix(dashboard): prevent session invalidation on deploy

Add fail-fast NEXTAUTH_SECRET production guard to crash with a clear
error instead of silently generating a random secret per deploy.
Add output: 'standalone' to next.config.js for proper runtime env var
handling on Railway. Fix pre-existing type error in enforcement page.
```
