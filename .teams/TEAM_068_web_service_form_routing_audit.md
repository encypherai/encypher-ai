# TEAM_068: Web Service Form Routing Audit

**Active PRD**: `PRDs/CURRENT/PRD_Web_Service_Form_Routing_Audit.md`
**Working on**: Task 3.2
**Started**: 2026-01-15 19:34 UTC
**Status**: complete

## Session Progress
- [x] 1.1 — ✅ npm test
- [x] 1.2 — ✅ npm test
- [x] 1.3 — ✅ npm test
- [x] 3.2 — ✅ playwright

## Changes Made
- `apps/marketing-site/src/app/api/demo-request/route.ts`: rerouted demo-request proxy to web-service endpoints (pending full audit).
- `apps/marketing-site/src/app/ai-demo/components/ui/DemoRequestModal.tsx`: route AI demo form through /api/demo-request.
- `apps/marketing-site/src/app/publisher-demo/components/ui/DemoRequestModal.tsx`: route publisher demo form through /api/demo-request.
- `apps/marketing-site/src/app/demo/page.tsx`: route demo page through /api/demo-request.
- `apps/marketing-site/src/lib/demoRequestRouting.ts`: add routing helper for demo requests.
- `apps/marketing-site/src/lib/demoRequestRouting.test.ts`: add routing unit tests.
- `config/traefik/dynamic.yml`: add web-service routing/service entries.
- `services/api-gateway/dynamic.yml`: add web-service routing/service entries.
- `infrastructure/traefik/routes-local.yml`: add web-service routing/service entries.
- `apps/marketing-site/.env.example`: document WEB_SERVICE_URL.
- `services/web-service/.env.example`: clarify EMAIL_FROM_NAME usage.
- `services/README.md`: add web-service to microservices list.
- `apps/marketing-site/src/lib/api.ts`: route analytics events to analytics-service pageview endpoint.
- `apps/marketing-site/.env.example`: document NEXT_PUBLIC_ANALYTICS_SERVICE_URL.
- `apps/marketing-site/playwright.config.ts`: set 1920x1080 viewport for e2e.

## Blockers
- None.

## Handoff Notes
- Add Traefik routing for web-service and update marketing-site/web-service paths to /api/v1/web.
