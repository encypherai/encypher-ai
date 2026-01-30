# TEAM_121: Marketing Site Encode/Decode Endpoints

**Active PRD**: `PRDs/CURRENT/PRD_MarketingSite_Tools_Rebrand_Analytics.md`
**Working on**: Task 4.0.3
**Started**: 2026-01-20 22:20
**Status**: completed

## Session Progress
Reference PRD task numbers. Mark with test verification:
- [x] 4.0.3 — ✅ jest ✅ puppeteer
- [x] 4.0.4 — ✅ jest (CORS verify routing)
- [x] 4.0.5 — ✅ jest (verify proxy uses public URL)
- [x] 4.0.6 — ✅ .env updated to use Traefik port 8000
- [x] 2.0.1 — ✅ jest (tools analytics helper tests)
- [x] 3.0.1 — add tools analytics helper
- [x] 3.0.2 — instrument sign/verify UI analytics
- [x] 3.0.3 — verify route logging
- [x] 3.0.4 — sign/verify rebrand (copy + metadata)
- [x] 3.0.5 — add sign/verify routes + redirects
- [x] 3.0.6 — update sitemap/tool links/tests
- [x] 4.0.1 — ✅ jest
- [x] 4.0.2 — ✅ lint (warnings pre-existing)

## Changes Made
- `apps/marketing-site/src/components/tools/EncodeDecodeTool.tsx`: Route verification to public `/api/v1/verify` via resolved enterprise API URL.
- `apps/marketing-site/src/lib/enterpriseApiUrl.ts`: Add public enterprise API URL resolver.
- `apps/marketing-site/src/lib/enterpriseApiUrl.test.ts`: Add public URL resolution tests.
- `apps/marketing-site/src/components/tools/EncodeDecodeTool.tsx`: Revert verification to `/api/tools/verify` proxy to avoid browser CORS in local dev.
- `apps/marketing-site/src/app/api/tools/verify/route.ts`: Use public Enterprise API URL resolver to avoid deprecated enterprise_api verify endpoint.
- `apps/marketing-site/.env`: Change ENTERPRISE_API_URL from port 9000 (deprecated enterprise-api) to port 8000 (Traefik gateway).
- `apps/marketing-site/.env.example`: Update example to reflect correct Traefik port 8000.
- `apps/marketing-site/src/lib/toolsAnalytics.ts`: Add tools analytics helper and session tracking.
- `apps/marketing-site/src/lib/toolsAnalytics.test.ts`: Add unit tests for tools analytics helper.
- `apps/marketing-site/src/components/tools/EncodeDecodeTool.tsx`: Add sign/verify analytics events and rebrand UI copy.
- `apps/marketing-site/src/app/api/tools/verify/route.ts`: Add structured logging for verify proxy.
- `apps/marketing-site/src/app/tools/sign-verify/*`: Add new sign/verify route and metadata.
- `apps/marketing-site/src/app/tools/sign/*`: Add sign-only route and metadata.
- `apps/marketing-site/src/app/tools/verify/*`: Add verify-only route and metadata.
- `apps/marketing-site/next.config.js`: Add redirects from encode/decode to sign/verify.
- `apps/marketing-site/src/app/sitemap.ts`: Update tool URLs.
- `apps/marketing-site/src/config/tools.ts`: Update tool links and descriptions.
- `apps/marketing-site/e2e/tools.smoke.spec.ts`: Update tool UI assertions.

## Blockers
- None.

## Handoff Notes
- Manual encode/decode UI check performed on http://localhost:3003/tools/encode-decode.
- Lint: `npm run lint` (warnings only). Tests: `npm test`.
- Manual sign/verify flow still needed (update PRD 4.0.3).
