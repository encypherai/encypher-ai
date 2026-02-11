# TEAM_159 — Fix marketing-site /tools/sign "Invalid host header"

## Problem
Marketing-site's `/api/tools/sign` returns `{"detail":"Invalid host header"}` (HTTP 400).

## Root Cause
- Marketing-site runs in Docker with `ENTERPRISE_API_URL=http://traefik:8000`
- Next.js route handler calls `fetch("http://traefik:8000/api/v1/sign")`
- Node's fetch sends `Host: traefik` header
- Traefik forwards to enterprise-api at `host.docker.internal:9000`
- Enterprise-api's `EncypherTrustedHostMiddleware` rejects `traefik` as untrusted host
- TEAM_156 added `enterprise-api` Docker service name but missed `traefik`

## Fix
Add `traefik` to the dev-mode trusted hosts in `enterprise_api/app/main.py:build_trusted_hosts()`.
