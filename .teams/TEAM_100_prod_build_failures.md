# TEAM_100 — Resolve Prod Build Failures

## Status: COMPLETE

## Scope
Fix two production build failures:
1. **verification-service**: `Dockerfile.railway` not found
2. **web-service**: Database connection refused on startup

## Changes Made

### 1. verification-service/railway.json
- Changed `dockerfilePath` from `"Dockerfile.railway"` to `"services/verification-service/Dockerfile.railway"`
- Railway resolves `dockerfilePath` relative to the repo root, not the service root directory

### 2. shared_commercial_libs/db/startup.py (+ all service copies)
- Increased `check_database_connection` defaults: `max_retries` 5→15, `retry_delay` 2.0→3.0
- Increased `ensure_database_ready` defaults to match: 15 retries, 3s delay (~45s total)
- Synced updated startup.py to all 10 service `shared_libs` copies

## Notes
- The web-service DB error (`Connection refused` to `postgres-a67472f8.railway.internal:5432`) indicates Postgres is down or the hostname is stale — this is an infrastructure issue on Railway, not a code bug
- Increased retries help with race conditions during cold starts but won't fix a dead Postgres instance
- User should verify Postgres service is running on Railway

## Handoff
- Verify Postgres service status on Railway dashboard
- Redeploy verification-service and web-service after merge

## Suggested Git Commit Message
```
fix: resolve prod build failures for verification-service and web-service

- verification-service: fix railway.json dockerfilePath to use full
  repo-root-relative path (services/verification-service/Dockerfile.railway)
  since Railway resolves paths from repo root, not service root dir
- web-service (all services): increase DB connection retry defaults from
  5 retries/2s delay (~10s) to 15 retries/3s delay (~45s) to handle
  Railway cold starts where Postgres may take longer to become reachable
- Synced updated startup.py to all 10 service shared_libs copies

Note: web-service "Connection refused" error to postgres-a67472f8.railway.internal
may also indicate Postgres service is down on Railway — verify on dashboard.
```
