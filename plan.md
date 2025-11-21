# Enterprise API Production Readiness Plan

## Task List

- [x] 1.0 Audit `enterprise_api` for performance and security
    - [x] 1.0.1 Review `README.md` and `MICROSERVICES_FEATURES.md`
    - [x] 1.0.2 Analyze code structure (`app/dependencies.py`, `app/utils`, etc.)
    - [x] 1.0.3 Identify performance bottlenecks (Sync DB writes, Spacy loading)
    - [x] 1.0.4 Identify architectural mismatches (Auth integration)
- [x] 1.1 Create WBS PRD
    - [x] 1.1.1 Document findings and action plan in `PRDs/enterprise_api_launch_audit.md`
- [ ] 2.0 Phase 1: Critical Performance Fixes
    - [x] 2.1 Optimize Auth Stats Update (TDD)
        - [x] 2.1.1 Create test to reproduce sync update behavior/verify background task need
        - [x] 2.1.2 Refactor `get_current_organization` to use background tasks
        - [x] 2.1.3 Implement `StatService` for safe background execution
    - [x] 2.2 Fix Spacy Model Loading (TDD)
        - [x] 2.2.1 Create test to verify model reloading issue
        - [x] 2.2.2 Implement Singleton/Cache for Spacy model

- [ ] 3.0 Phase 2: Architectural Alignment (Option B: Service Call + Redis)
    - [x] 3.1 Unify Authentication Logic (TDD)
        - [x] 3.1.1 Update `config.py` with `key_service_url`
        - [x] 3.1.2 Create `KeyServiceClient` with Redis caching support
        - [x] 3.1.3 Create tests for `KeyServiceClient` (mocking HTTP and Redis)
        - [x] 3.1.4 Refactor `get_current_organization` to use `KeyServiceClient`
    - [x] 3.2 Cleanup Dependencies
        - [x] 3.2.1 Remove unused dependencies (e.g. kafka-python)

- [ ] 4.0 Phase 3: Final Polish & Verification
    - [x] 4.1 Update Documentation
        - [x] 4.1.1 Update `README.md` with new architecture (Key Service)
        - [x] 4.1.2 Update `docs/API.md` if necessary
    - [x] 4.2 Load Testing (Docker-based)
        - [x] 4.2.1 Create load test script (`scripts/run_load_test.py`)
        - [x] 4.2.2 Implement Docker container fixture (Postgres)
        - [x] 4.2.3 Verify load test success (p95 < 100ms target)
            - Result: Avg 42.21ms, P95 58.05ms (Pass)

## Notes
- **Critical Finding**: `app/dependencies.py` performs a synchronous DB `UPDATE` on every request. This will kill performance.
- **Critical Finding**: `app/utils/segmentation/advanced.py` reloads the Spacy model on every call.
- **Architecture**: `enterprise_api` implements its own API key validation against a local table, ignoring the `Key Service`.
- **Fix**: Updated DB schema to use `TIMESTAMPTZ` for timezone-aware consistency.
- **Fix**: Added missing `user_id` column to `organizations` table for Coalition integration.

## Current Goal
- Audit complete. Ready to implement fixes upon user request.
