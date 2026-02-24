# TEAM_229 — Traefik Rights/Analytics Routing Update

## Context
Production dashboard analytics calls to `/api/v1/rights/*` were failing CORS preflight because OPTIONS requests returned `404`.

## Root Cause
`config/traefik/dynamic.yml` did not include explicit routers for several dashboard-used Enterprise API path groups (notably `/api/v1/rights/*`).
Requests fell through to the low-priority catch-all `api-auth` router and hit auth-service, which does not own those endpoints.

## Changes Made
- Updated `config/traefik/dynamic.yml` with explicit routers (all with `cors-api` middleware, priority `100`) for:
  - `/api/v1/rights`
  - `/api/v1/rights-licensing`
  - `/api/v1/notices`
  - `/api/v1/integrations`
  - `/api/v1/cdn`
  - `/api/v1/admin`

## Validation
- Verified new route rules exist via grep checks.
- Parsed YAML successfully:
  - `uv run python -c "import yaml; yaml.safe_load(open('/home/developer/code/encypherai-commercial/config/traefik/dynamic.yml')); print('dynamic.yml OK')"`

## Rollout Notes
- Redeploy API gateway/Traefik so new dynamic routes are loaded.
- Re-test dashboard page `/ai-crawlers` and inspect preflight OPTIONS for `/api/v1/rights/analytics/*`.

## Suggested Commit Message
fix(api-gateway): route rights and related dashboard APIs to enterprise-api

- add Traefik routers for /api/v1/rights, /rights-licensing, /notices
- add routers for /integrations, /cdn, and /admin dashboard paths
- ensure these paths no longer fall through to auth-service catch-all
- preserve cors-api middleware and priority routing behavior
