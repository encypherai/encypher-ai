# Enterprise API Reliability & Resilience

**Status**: Drafted for production readiness review
**Scope**: Database HA, idempotency, retry/backoff, rate limiting, failover
**Owners**: Platform + API Engineering

## 1. Overview
This document captures the current reliability posture of the Enterprise API and defines the required steps for production readiness across database availability, idempotency, retries, and failover.

## 2. Database HA Strategy (PRD 2.1)
### Current State
- Primary Postgres instance with connection health checks and retry on startup.
- Migrations are idempotent and run on startup using `app/utils/db_startup.py`.

### Target State
- **Primary + replica** with streaming replication.
- **PITR** enabled via WAL archiving (daily backups, 15-minute recovery point).
- **Restore drills** executed quarterly with documented runbook.

### Open Gaps
- Automated backup verification pipeline.
- Runbook for failover promotion and DNS/connection switch.

## 3. Idempotency Guarantees (PRD 2.2)
### Current State
- Batch signing/verification uses Redis-backed idempotency keys (`idempotency_service`).
- Requests are rejected on payload mismatch, returning `E_IDEMPOTENCY_MISMATCH`.
- Batch records include expiry timestamps with a 30‑day retention window.

### Target State
- Extend idempotency coverage to **single sign/verify endpoints** where possible.
- Ensure idempotency keys are persisted in Redis with TTL aligned to retention policy.

### Open Gaps
- Idempotency headers + docs for non-batch endpoints.
- Structured tests for idempotency across sign/verify endpoints.

## 4. Retry/Backoff Strategy (PRD 2.3)
### Current State
- Database startup retry logic with backoff.
- Webhook dispatcher uses exponential backoff (1m/5m/15m) with capped attempts.
- Some microservices have retry helpers (auth-service `resilience.py`).

### Target State
- Standardized retry helper for external service calls (Key Service, Coalition Service).
- Circuit breaker and timeout defaults for outbound HTTP.
- Retry budget limits to avoid thundering herds.

### Open Gaps
- Shared retry middleware for all outbound requests.
- Documented retry policy for async workers and batch jobs.

## 5. Rate Limiting & Abuse Prevention (PRD 2.4)
### Current State
- Tier-aware per-organization rate limiting (`api_rate_limiter`).
- Public endpoints protected by IP-based rate limiting with trusted proxy allowlist.
- Response headers include limit/remaining/reset/Retry-After.

### Target State
- Redis-backed rate limiter for horizontally scaled deployments.
- Abuse detection signals feeding alerting.

### Open Gaps
- Replace in-memory rate limiter for public endpoints in production.
- Document API gateway/DDoS protections.

## 6. Multi-Region / Failover (PRD 2.5)
### Current State
- Single-region deployment assumptions.

### Target State
- Multi-region active/passive with DNS failover.
- Read replicas for verification-heavy workloads.
- Latency-aware routing for public verification.

### Open Gaps
- Documented failover plan and recovery targets (RTO/RPO).

## 7. Validation & Evidence
- `uv run pytest` baseline must pass.
- Load tests (opt-in) for rate limiting and batch throughput.
- Manual restore drill runbook and evidence.

## 8. References
- `enterprise_api/app/utils/db_startup.py`
- `enterprise_api/app/services/idempotency_service.py`
- `enterprise_api/app/services/batch_service.py`
- `enterprise_api/app/middleware/api_rate_limiter.py`
- `enterprise_api/app/middleware/public_rate_limiter.py`
- `enterprise_api/app/services/webhook_dispatcher.py`
