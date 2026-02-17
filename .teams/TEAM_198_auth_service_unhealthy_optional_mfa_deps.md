# TEAM_198 - Auth Service Unhealthy (Optional MFA Dependencies)

## Status: COMPLETE

## Summary
Resolved full-stack startup failure where `encypher-auth-service` was marked unhealthy and blocked dependent containers. The service crashed during import when optional MFA dependencies (`pyotp`, then `webauthn`) were absent in the running image.

## Root Cause
- `auth-service` imports `AuthFactorsService` at module import time via API endpoints.
- `AuthFactorsService` imported `pyotp` and `webauthn` unconditionally.
- In the affected container image, those packages were not installed, causing startup-time `ModuleNotFoundError` before health endpoint initialization.
- Container healthcheck failed repeatedly (`/health` connection refused), resulting in dependency startup failure.

## Fix Applied
1. Added defensive optional imports and explicit runtime guards in:
   - `services/auth-service/app/services/auth_factors_service.py`
2. Added TDD regression coverage in:
   - `services/auth-service/tests/test_auth_factors_service.py`
   - Verifies graceful `ValueError` when `pyotp` is unavailable.
   - Verifies backup-code path remains usable when `pyotp` is unavailable.
   - Verifies graceful `ValueError` when `webauthn` is unavailable.
3. Validated:
   - `uv run pytest tests/test_auth_factors_service.py -q` (11 passed)
   - `uv run ruff check app/services/auth_factors_service.py tests/test_auth_factors_service.py` (passed)
   - Container health endpoint responds and Docker marks service healthy.

## Verification Notes
- `docker inspect --format='{{.State.Health.Status}}' encypher-auth-service` => `healthy`
- `docker exec encypher-auth-service python -c "import urllib.request; print(urllib.request.urlopen('http://localhost:8001/health').read().decode())"` => healthy payload

## Suggested Commit Message
fix(auth-service): prevent startup crash when optional MFA deps are missing

- guard pyotp import in AuthFactorsService and raise explicit ValueError for TOTP setup/confirm when unavailable
- guard webauthn import in AuthFactorsService and raise explicit ValueError for passkey operations when unavailable
- keep backup code verification path functional when pyotp is absent
- add regression tests for missing pyotp/webauthn dependency behavior
- verify auth-service healthcheck recovers and container reports healthy

---

## Session Update - start-dev rebuild Docker build failures

### Status: COMPLETE

### Summary
Investigated `./start-dev.sh --rebuild` failures caused by Docker BuildKit instability (`open /proc/stat: transport endpoint is not connected` / HTTP2 frame errors), then implemented a minimal script-level fallback to legacy builder mode for rebuilds.

### Root Cause
- BuildKit path was intermittently failing at daemon/host level during image builds.
- The same Dockerfiles successfully built with legacy builder mode (`DOCKER_BUILDKIT=0`, `COMPOSE_DOCKER_CLI_BUILD=0`), indicating infra-layer BuildKit instability rather than app Dockerfile defects.

### Fix Applied
1. Added `compose_build_with_fallback()` in `start-dev.sh`:
   - First attempts normal `docker compose build`.
   - On failure, retries build with legacy builder env vars.
2. Switched `--rebuild` path to call fallback helper.
3. Added regression test asserting fallback env vars are present in `start-dev.sh`.

### Validation
- `DOCKER_BUILDKIT=0 docker build -f apps/dashboard/Dockerfile.dev ...` => success.
- `DOCKER_BUILDKIT=0 COMPOSE_DOCKER_CLI_BUILD=0 docker compose -f docker-compose.full-stack.yml build dashboard coalition-service` => success.
- `uv run pytest enterprise_api/tests/test_start_dev_sh.py -q` => pass (2 tests).
- `bash -n start-dev.sh` => pass.
- `./start-dev.sh --rebuild --skip-stripe-listen --skip-docker-logs` => command completed successfully; services built and started.

### Follow-up Note
- Enterprise API readiness probe timed out during this run while build/start orchestration still completed; if needed, investigate Enterprise API startup separately.

### Comprehensive Suggested Commit Message
fix(start-dev): add rebuild fallback to legacy Docker builder when BuildKit fails

- add compose_build_with_fallback helper to retry docker compose builds with
  DOCKER_BUILDKIT=0 and COMPOSE_DOCKER_CLI_BUILD=0 after initial failure
- route --rebuild service build path through fallback helper to mitigate
  intermittent daemon-level BuildKit errors (e.g. /proc/stat transport endpoint)
- add regression test in enterprise_api/tests/test_start_dev_sh.py to assert
  fallback env markers are present in start-dev.sh
- verify shell syntax, targeted pytest coverage, and end-to-end
  ./start-dev.sh --rebuild execution
