# PRD: Microservice Ownership — Verify + Coalition

**Status**: In Progress  
**Current Goal**: Move `/api/v1/verify` + `/api/v1/coalition` to secure, scalable microservice ownership and align Traefik routing (prod + local).

---

## Overview

We currently have overlapping ownership for verification and coalition APIs between `enterprise_api` and dedicated microservices. This PRD migrates the Enterprise SDK-compatible `POST /api/v1/verify` contract into `services/verification-service`, hardens `services/coalition-service` authentication/authorization, and updates Traefik routing so these paths are served by microservices in production and local development.

---

## Objectives

- Establish a single authoritative owner for `/api/v1/verify*` (verification-service).
- Establish a single authoritative owner for `/api/v1/coalition*` (coalition-service) with proper auth.
- Preserve Enterprise SDK compatibility for `POST /api/v1/verify` response envelope.
- Route traffic consistently in both production and local Traefik configurations.

---

## Tasks

### 1.0 Verification Service — Enterprise-compatible `POST /api/v1/verify`

- [x] 1.1 Add request/response schemas matching Enterprise API envelope (VerifyRequest/VerifyResponse)
- [x] 1.2 Implement API key auth via Key Service `/api/v1/keys/validate`
- [ ] 1.3 Implement C2PA verification using `encypher-ai` `UnicodeMetadata.verify_metadata`
- [ ] 1.4 Add tests for:
  - [x] 1.4.1 Missing/invalid API key → 401 — ✅ pytest
  - [ ] 1.4.2 Payload too large → 413
  - [ ] 1.4.3 Valid signed text → 200 with structured verdict

### 2.0 Coalition Service — Auth hardening

- [ ] 2.1 Add API key auth via Key Service `/api/v1/keys/validate`
- [ ] 2.2 Update member-scoped endpoints to derive identity from token (no trusting `user_id` from request alone)
- [ ] 2.3 Add tests for:
  - [ ] 2.3.1 Unauthorized access → 401
  - [ ] 2.3.2 Cross-user access attempts → 403

### 3.0 Traefik routing alignment

- [ ] 3.1 Production: route `/api/v1/verify*` → `verification-service`
- [ ] 3.2 Production: route `/api/v1/coalition*` → `coalition-service`
- [ ] 3.3 Local: update `config/traefik/dynamic.yml` to match production routing
- [ ] 3.4 Local: update `infrastructure/traefik/routes-local.yml` to match production routing

### 4.0 Verification Protocol

- [x] 4.1 `uv run ruff check .` (service-level) — ✅ ruff
- [x] 4.2 `uv run pytest` (service-level) — ✅ required
- [ ] 4.3 Manual smoke verification (curl) against gateway routes

---

## Success Criteria

- [ ] `POST /api/v1/verify` is served by `verification-service` and matches Enterprise SDK expectations.
- [ ] `coalition-service` endpoints enforce authentication and prevent cross-tenant access.
- [ ] Traefik routes for verify/coalition are consistent across prod + local configs.
- [ ] All relevant tests pass.

---

## Completion Notes

(To be filled upon completion)
