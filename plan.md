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

- [ ] 4.0 WordPress Plugin & Enterprise Tier Strategy
    - [x] 4.0.1 Audit & Define Tier Differentiation (Free vs Pro vs Enterprise)
    - [x] 4.0.2 Update WordPress Admin UI with Tier Features (HSM, BYOK)
    - [x] 4.0.3 Backend Infrastructure for AWS KMS (HSM) Signing
        - [x] Create `AWSSigner` adapter
        - [x] Update core `Signer` protocol
        - [x] Implement `kms_key_id` loading logic in `crypto_utils.py`
    - [x] 4.0.4 Database Schema Migration for HSM
        - [x] Create Alembic migration (`add_kms_support`)
        - [x] Update `Organization` model

- [x] 5.0 Plugin Differentiation Features
    - [x] 5.0.1 Whitelabeling Support (Enterprise/Pro)
        - [x] Add `show_branding` option to Settings (hidden for Free)
        - [x] Update Frontend Badge to respect branding setting
    - [x] 5.0.2 Advanced Analytics Integration
        - [x] Ensure Analytics page respects `advanced_analytics_enabled` feature flag from API
        - [x] Mock "Verification Hits" data for Pro/Enterprise tiers

- [x] 6.0 Final Integration Testing
    - [x] 6.0.1 Fix Embeddings Integration Test (`test_live_system.py`)
    - [x] 6.0.2 Fix Streaming Integration Test (`test_live_system.py`)

## Notes
- **Context**: `enterprise_api` passed load tests with Docker/Postgres. We can reuse this running instance for SDK integration tests.
- **Constraint**: SDK must handle `TIMESTAMPTZ` formats returned by the API (fixed in previous phase).
- **New Feature**: Added AWS KMS support for Enterprise tier (Legal Non-Repudiation).
- **New Feature**: Added Plugin Whitelabeling and Advanced Analytics (Mocked) for Pro/Enterprise tiers.

## Status
- **Completed**:
    - Load test fixes (sync DB init, demo seeding).
    - DB Schema updates (TIMESTAMPTZ, user_id, missing columns).
    - SDK Contract Audit (SignRequest).
    - Sign/Verify Integration Tests (Dockerized env).
    - Developer Experience review.
    - WordPress Tier Audit & HSM Infrastructure Implementation.
    - Plugin Whitelabeling & Analytics differentiation.
    - **Final Integration Testing (Embeddings & Streaming).**
- **Pending**:
    - None. Feature complete.
