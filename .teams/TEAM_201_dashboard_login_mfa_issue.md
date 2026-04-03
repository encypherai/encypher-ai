# TEAM_201 — Dashboard Login MFA Issue

## Session Summary
- Investigating localhost dashboard login failure with "Invalid or expired MFA challenge" error.
- Verified local auth DB record for `test@encypher.com` has MFA disabled (`totp_enabled = false`).
- Implemented dashboard NextAuth fallback so stale MFA challenges do not block credential login.

## Files Changed
- `apps/dashboard/src/app/api/auth/[...nextauth]/route.ts`

## Verification
- `docker exec encypher-postgres psql -U encypher -d encypher_auth -c "SELECT email, totp_enabled, (totp_secret_encrypted IS NOT NULL) AS has_totp_secret, totp_enabled_at, totp_backup_code_hashes FROM users WHERE email = 'test@encypher.com';"` ✅
- `npx eslint src/app/api/auth/[...nextauth]/route.ts` ✅ (existing `no-explicit-any` warnings only)
- `npm run type-check` ✅

## Handoff Notes
- Root cause in the observed loop is stale/expired MFA challenge handling in dashboard auth flow, not local DB MFA flags.
- New behavior: if `/auth/login/mfa/complete` returns `Invalid or expired MFA challenge`, NextAuth now logs a warning and continues to the primary `/auth/login` call instead of hard-failing.

## Suggested Commit Message
fix(dashboard-auth): recover from stale MFA challenge during login

- handle `/auth/login/mfa/complete` stale challenge responses without aborting auth flow
- if response detail is `Invalid or expired MFA challenge`, fall back to primary `/auth/login`
- preserve strict error handling for other MFA failures (invalid code, server errors)
- verify local test user MFA flags are disabled in `encypher_auth.users`
- run dashboard type-check and targeted lint on NextAuth route
