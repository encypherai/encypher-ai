# TEAM_174 - Auth Service Docker Rebuild (Stale shared_libs)

## Status: COMPLETE

## Summary
Resolved `start-dev.sh` failure caused by stale Docker images across all microservices. The `encypher_commercial_shared` package installed inside containers was missing the `pricing_constants` module (added by TEAM_173), causing `alembic upgrade head` to fail with `ModuleNotFoundError`.

## Root Cause
- `services/auth-service/app/db/models.py` imports `DEFAULT_COALITION_PUBLISHER_PERCENT` from `encypher_commercial_shared.core.pricing_constants`
- The Docker images were cached from before `pricing_constants.py` was added to `shared_libs/`
- `alembic upgrade head` (run at container startup) imports `app.db.models` which triggers the missing module error
- Auth-service exits(1) -> all dependent services (`key-service`, `user-service`, etc.) fail with "dependency failed to start"

## Fix Applied
Rebuilt all 9 microservice Docker images with `--no-cache` to pick up the current `shared_libs` contents:
1. `docker compose -f docker-compose.full-stack.yml build --no-cache auth-service`
2. `docker compose -f docker-compose.full-stack.yml build --no-cache key-service user-service encoding-service verification-service coalition-service analytics-service billing-service notification-service`
3. `docker compose -f docker-compose.full-stack.yml up -d`

All 17 containers now running and healthy.

## Suggested Git Commit
No code changes were made. This was a Docker image cache issue resolved by rebuilding.
