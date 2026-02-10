# TEAM_155 — Rebuild .next Cache Clearing

## Summary
Fixed `start-dev.sh --rebuild` to clear stale `.next` cache Docker volumes (`marketing_next_cache`, `dashboard_next_cache`) before rebuilding frontend services.

## Problem
After code changes, `--rebuild` would rebuild Docker images but reuse stale Webpack chunks from named `.next` cache volumes. This caused runtime errors like:
```
Cannot read properties of undefined (reading 'call')
```
at `next/dynamic` call sites (e.g., `FileInspectorClientWrapper` on `/tools/inspect`).

## Root Cause
Docker Compose persists `.next` caches in named volumes (`marketing_next_cache`, `dashboard_next_cache`). When `--rebuild` rebuilds images without clearing these volumes, the old Webpack module registry references chunks that no longer exist, causing `undefined.call()` errors.

## Fix
- **`start-dev.sh`**: Added volume removal for `marketing_next_cache` and `dashboard_next_cache` in the `--rebuild` block, before `docker compose build`.
- Updated `--rebuild` help text to document cache clearing.

## Files Changed
- `start-dev.sh` — Added .next cache volume clearing to `--rebuild` flow

## Verification
- Cleared `encypherai-commercial_marketing_next_cache` volume
- Restarted marketing-site container
- Confirmed `/tools/inspect` page loads without error (Puppeteer screenshot)

## Status
✅ Complete
