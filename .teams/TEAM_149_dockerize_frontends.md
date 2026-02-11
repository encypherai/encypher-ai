# TEAM_149 — Dockerize Frontend Applications

## Objective
Move marketing-site and dashboard from bare `npm run dev` processes in `start-dev.sh` into Docker containers managed by `docker-compose.full-stack.yml`, unifying all services under one orchestration layer.

## Status: COMPLETE ✅

## Changes Made

### New Files
- `apps/marketing-site/Dockerfile.dev` — Alpine + node-gyp build deps + npm install
- `apps/dashboard/Dockerfile.dev` — Same pattern
- `apps/marketing-site/.dockerignore` — Excludes node_modules, .next, logs
- `apps/dashboard/.dockerignore` — Same

### Modified Files
- **`docker-compose.full-stack.yml`** — Added `marketing-site` and `dashboard` services with:
  - Bind-mount source for hot reload
  - Named volumes for `node_modules`, `design-system/node_modules`, `.next` cache
  - `env_file` pointing to each app's `.env` / `.env.local`
  - `WATCHPACK_POLLING=true` for file watching inside containers
  - Health checks and `depends_on: auth-service`
- **`start-dev.sh`** — Removed bare `npm run dev` subshells, PID tracking, log tailing for frontends. Frontends now managed entirely by Docker Compose. Added `--scale` flags for `--skip-frontend`. Added frontend health checks. Added color codes for frontend log lines. Removed dead `install_node_deps_if_needed` function.

### Key Design Decisions
- **Named volumes for node_modules** — Prevents host bind-mount from overwriting container's installed deps
- **`npm install` over `npm ci`** — More resilient to lock file drift in dev
- **`.npmrc` copied into container** — Both apps require `legacy-peer-deps=true`
- **Alpine + native build deps** — `canvas` package needs python3, make, g++, cairo-dev, etc.
- **`--skip-frontend` uses `--scale=0`** — Cleanly excludes frontend containers without separate compose files

## Verification
- `./start-dev.sh --skip-stripe-listen --skip-docker-logs` exits 0
- All backend services healthy (auth, key, enterprise-api, etc.)
- Marketing site responds at http://localhost:3000 — Puppeteer verified
- Dashboard responds at http://localhost:3001 — Puppeteer verified
- Both containers show `Up` in `docker ps`
