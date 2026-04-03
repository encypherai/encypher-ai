# TEAM_062 — Dashboard Dev .env.local + NextAuth Login

## Status
In Progress

## Goal
Fix local dashboard credential login by ensuring NextAuth points at the local API gateway instead of production.

## Work Completed
- Added `apps/dashboard/.env.local` with local `NEXT_PUBLIC_API_URL` and `NEXTAUTH_*` values suitable for local development.

- Playground UX follow-ups:
  - Fixed playground auth header behavior so selected API keys are sent even for endpoints marked public (e.g. `/verify`).
  - Replaced category tabs with a grouped vertical endpoint menu (Signing/Verification) while preserving search.
  - Implemented a hybrid request builder for `sign`/`verify`/`lookup`: Guided Form + Advanced JSON toggle.
  - Added a request-builder contract test suite.

## Notes
- Symptom: NextAuth credentials provider attempted login to `https://api.encypher.com/api/v1/auth/login` causing 401 for local-only test credentials.

## Verification
- ✅ `npm run type-check` (apps/dashboard)
- ✅ `npm run lint` (apps/dashboard) (warnings pre-existing)
- ✅ `npm run test:e2e` (apps/dashboard)
