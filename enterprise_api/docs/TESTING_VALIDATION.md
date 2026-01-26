# Enterprise API Testing & Validation

**Status**: Drafted for production readiness review
**Scope**: Unit, integration, load/perf, security testing
**Owners**: QA + API Engineering

## 1. Unit Tests (PRD 8.1)
- Run: `uv run pytest`
- Covers core signing, verification, auth, and utility functions.

## 2. Integration Tests (PRD 8.2)
- Requires full microservices stack.
- Run with Docker stack: `docker-compose.full-stack.yml`.
- Enable integration suites via environment variables:
  - `DEMO_KEY_TESTS=true`
  - `STREAMING_E2E_TESTS=true`

## 3. Load/Performance Tests (PRD 8.3)
- Load tests are opt-in:
  - `LOAD_TESTS=true`
  - `REAL_LOAD_TESTS=true`
- Targets defined in `docs/PERFORMANCE_SCALE.md`.

## 4. Security Tests (PRD 8.4)
- Security regression tests in `enterprise_api/tests/*`.
- Dependency audit: `uv run pip-audit`.
- Manual pen-test evidence required for production launch.

## 5. Disaster Recovery Tests (PRD 8.5)
- See `enterprise_api/docs/DISASTER_RECOVERY_RUNBOOK.md`.

## 6. References
- `enterprise_api/tests/`
- `enterprise_api/docs/TESTING_GUIDE.md`
