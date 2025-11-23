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

## 7.0 Marketing Site Backend Migration

### 7.1 Architecture & Planning
- [x] 7.1.1 Define `web-service` schema for sales/contact forms and analytics
- [x] 7.1.2 Set up new PostgreSQL database for marketing data
- [x] 7.1.3 Design API contracts for web-service endpoints
- [x] 7.1.4 Plan data migration from legacy backend

### 7.2 Web-Service Implementation
- [x] 7.2.1 Initialize new FastAPI service in `services/web-service`
- [x] 7.2.2 Implement database models for demo requests and analytics events
- [x] 7.2.3 Create API endpoints for contact forms and demo requests
- [x] 7.2.4 Implement analytics event tracking endpoints
- [x] 7.2.5 Add email notification system for new leads
- [x] 7.2.6 Set up database migrations with Alembic

### 7.3 Frontend Integration
- [x] 7.3.1 Update frontend API client to use new web-service endpoints
- [x] 7.3.2 Implement error handling and loading states
- [x] 7.3.3 Add analytics event tracking to key user interactions
- [x] 7.3.4 Update environment configuration

### 7.4 Testing & Deployment
- [x] 7.4.1 Write unit and integration tests
- [x] 7.4.2 Set up Local Development Environment (Docker + Scripts)
- [x] 7.4.3 Verify Encode/Decode Tool functionality (Local + Enterprise API)
- [ ] 7.4.4 Set up CI/CD pipeline for web-service
- [ ] 7.4.5 Deploy to staging environment
- [ ] 7.4.6 Perform end-to-end testing (Automated)
- [ ] 7.4.7 Deploy to production with feature flags

### 7.5 Post-Migration
- [ ] 7.5.1 Monitor system performance
- [ ] 7.5.2 Verify data consistency
- [ ] 7.5.3 Update documentation
- [ ] 7.5.4 Decommission legacy backend endpoints

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
    - **Marketing Site Backend Migration (7.0)**:
        - Architecture & Planning (7.1)
        - Web-Service Implementation (7.2)
        - Frontend Integration (7.3)
        - Local Dev Environment Setup (7.4.2)
        - **Encode/Decode Tool Integration (Enterprise API Proxy)**
        - **Tamper Detection UI Features**
        - **Analytics Integration Fix (Shared DB Migration)**
    - **C2PA Standard Strategy (8.0)**:
        - Audited `encypher-ai` for C2PA Compliance.
        - Created `c2pa-text` Monorepo (MIT License).
        - Implemented Python, TypeScript, Rust, and Go packages.
        - Polished Docs with Encypher Branding & Enterprise Upsell.
        - Added Security & Contribution guidelines.
- **In Progress**:
    - Marketing Site CI/CD & Deployment (7.4.4+)
- **Pending**:
    - Production Deployment


## 8.0 C2PA Standard Strategy (Commoditize the Complement)

### 8.1 Core Infrastructure
- [x] 8.1.1 Audit `encypher-ai` package for C2PA Compliance (Magic bytes, VS encoding)
- [x] 8.1.2 Create `c2pa-text` Monorepo (Permissive License strategy)
- [x] 8.1.3 Implement Python Reference Package (`c2pa-text/python`)
- [x] 8.1.4 Implement TypeScript Reference Package (`c2pa-text/typescript`)
- [x] 8.1.5 Implement Rust Reference Crate (`c2pa-text/rust`)
- [x] 8.1.6 Implement Go Reference Module (`c2pa-text/go`)

### 8.2 Documentation & Trust
- [x] 8.2.1 Polish Documentation (Badges, Logo, Attribution, Upsell)
- [x] 8.2.2 Add Enterprise Trust Docs (SECURITY.md, CONTRIBUTING.md)
- [x] 8.2.3 Verify Marketing Asset Links

