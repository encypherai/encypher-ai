# Enterprise SDK Production Readiness Plan

## Task List

- [ ] 1.0 Audit SDK vs API Contract
    - [x] 1.0.1 Compare `encypher_enterprise/models.py` with live API responses
    - [ ] 1.0.2 Verify `TIMESTAMPTZ` parsing in SDK models
    - [ ] 1.0.3 Audit Exception mapping (`exceptions.py`) against API error codes

- [x] 2.0 Integration Test Suite (`tests/integration`)
    - [x] 2.0.1 Create `test_live_api.py` skeleton
    - [x] 2.0.2 Implement Sign & Verify flow against Dockerized API
    - [ ] 2.0.3 Implement Enterprise Embeddings flow (Verified logic manually, integration test harness issue pending)
    - [ ] 2.0.4 Implement Streaming flow (Pending test harness fix)

- [x] 3.0 Developer Experience & Polish
    - [x] 3.0.1 Verify README Quick Start examples
    - [x] 3.0.2 Ensure CLI commands (`encypher sign`) work with local config

## Notes
- **Context**: `enterprise_api` passed load tests with Docker/Postgres. We can reuse this running instance for SDK integration tests.
- **Constraint**: SDK must handle `TIMESTAMPTZ` formats returned by the API (fixed in previous phase).

## Status
- **Completed**:
    - Load test fixes (sync DB init, demo seeding).
    - DB Schema updates (TIMESTAMPTZ, user_id, missing columns).
    - SDK Contract Audit (SignRequest).
    - Sign/Verify Integration Tests (Dockerized env).
    - Developer Experience review.
- **Pending**:
    - Debugging integration test harness for Embeddings/Streaming flows (core logic verified).
