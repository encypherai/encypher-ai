# PRD: Enterprise API – Backend Improvements (Production Readiness)

Status: Draft  
Priority: P0 (Critical)  
Owner: Backend Agent (Assignee: TBD)  
Created: 2025-11-11  
Target Completion: 2025-12-01

---

## Overview

This PRD defines the backend work required to take the Enterprise API to full production readiness. It covers endpoint completeness (verification, batch, streaming), performance and reliability improvements, documentation, testing, security, and operational readiness. It also specifies acceptance criteria, WBS tasks, and handoff requirements for SDKs and WordPress.

---

## Objectives

- Provide complete, reliable endpoints for document and sentence-level provenance.  
- Fix verification correctness (certificate resolution) with deterministic results.  
- Add batch and streaming APIs for high-throughput ingestion.  
- Standardize error model, observability, rate limiting, and quotas.  
- Deliver OpenAPI specification, Postman collection, and examples.  
- Achieve production performance targets and test coverage thresholds.  

---

## Non-Goals

- Frontend/UI work (handled by Dashboard/WordPress teams).  
- New AI features beyond signing/verification scope.  
- Changes to pricing/billing (business-owned).  

---

## Current State (Summary)

- C2PA signing endpoint operational.  
- Enhanced embeddings endpoint operational with improved sentence segmentation (Wiki/Markdown aware); benchmarked on 5K docs.  
- Verification endpoint returns invalid due to missing certificate lookup for signer_id (`org_demo`).  
- No batch/streaming endpoints yet.  
- OpenAPI not complete; Postman collection missing.  
- Observability, rate limits, and security hardening are partial.  

---

## Requirements & Specifications

### 1. Verification Endpoint (Fix and Harden)
- Route: `POST /api/v1/verify`
- Purpose: Validate C2PA signatures and minimal embeddings; return validity, tamper status, signer, and metadata.
- Issues to fix:
  - Resolve signer certificate by `signer_id` (e.g., `org_demo`) from `organizations` table.
  - Support PEM chain: leaf + intermediate (optional) + root (configurable trust store).
  - Return structured verdict: `valid`, `tampered`, `reason`, `signer_id`, `signer_name`, `timestamp`.
  - Add size/time limits and robust error handling.
- Data sources:
  - `organizations(organization_id, organization_name, certificate_pem)`; may add `cert_chain_pem`, `status`, `rotated_at`.
- Response (example):
```json
{
  "success": true,
  "data": {
    "valid": true,
    "tampered": false,
    "signer_id": "org_demo",
    "signer_name": "Demo Org",
    "timestamp": "2025-11-11T22:11:12Z",
    "details": {
      "c2pa": { "alg": "ed25519" },
      "document_id": "article_0000001",
      "mode": "c2pa|embeddings"
    }
  },
  "error": null
}
```
- Acceptance Criteria:
  - Certificate lookup works for existing orgs; returns `valid=true` for signed sample; `tampered=true` when mutated.
  - Handles missing/invalid cert with `400` and structured error.
  - p95 latency < 100 ms for 10KB payloads.

### 2. Batch Endpoints
- Routes:
  - `POST /api/v1/batch/sign` – signs multiple documents (C2PA or embeddings based on `mode`).
  - `POST /api/v1/batch/verify` – verifies multiple documents.
- Request (sign):
```json
{
  "mode": "c2pa|embeddings",
  "segmentation_level": "sentence|paragraph|document",
  "items": [
    { "document_id": "doc-1", "text": "..." },
    { "document_id": "doc-2", "text": "..." }
  ],
  "idempotency_key": "uuid-..."
}
```
- Response (sign):
```json
{
  "success": true,
  "data": {
    "results": [
      { "document_id": "doc-1", "status": "ok", "embedded_content": "...", "statistics": {"ms": 87} },
      { "document_id": "doc-2", "status": "ok", "embedded_content": "...", "statistics": {"ms": 92} }
    ]
  },
  "error": null
}
```
- Limits & Behavior:
  - Max items per request: 100 (configurable).
  - Enforce idempotency (store `idempotency_key` + hash(items)).
  - Parallelize per-item work with bounded concurrency.
- Acceptance Criteria:
  - Correctness on success/tampered cases; partial-failure reporting.
  - Throughput target: >= 100 docs/sec (C2PA mode) with 8 workers.

### 3. Streaming Signing Endpoint
- Route: `POST /api/v1/stream/sign` (SSE preferred; WebSocket optional future).
- Purpose: Stream signing progress for large inputs or long pipelines.
- Protocol: Server-Sent Events with events: `start`, `progress`, `partial`, `final`, `error`.
- Example events:
```
event: start
data: {"document_id":"doc-1"}

event: progress
data: {"document_id":"doc-1","pct":35}

event: final
data: {"document_id":"doc-1","embedded_content":"...","statistics":{"ms":1240}}
```
- Acceptance Criteria:
  - Works for 1–10MB content; client receives `final` within SLA.
  - Handles disconnect/retry; idempotent by `document_id` + `run_id`.

### 4. OpenAPI & Postman
- Complete OpenAPI 3.1 spec including all endpoints, schemas, examples.
- Publish Swagger UI at `/docs`; JSON at `/openapi.json`.
- Provide Postman collection with environment templates.
- Acceptance: Spec lint passes; examples executable.

### 5. Error Model & Status Codes
- Standard response format used everywhere.
- Error codes namespace: `E_AUTH_*`, `E_RATE_*`, `E_INPUT_*`, `E_VERIFY_*`, `E_INT_*`.
- Map to HTTP status (400/401/403/404/409/413/429/500).
- Include `correlation_id` in responses and logs.

### 6. Rate Limiting & Quotas
- Per-API-key and per-IP limits (e.g., 60 rps burst, 100k/day default).
- 429 responses include `Retry-After` and current quota in headers.
- Admin overrides via config.

### 7. Observability & Ops
- Structured JSON logging; log levels; redact secrets.
- Metrics: request count/latency (p50/p95), error rate, queue depth.
- Health: `/health` returns version and subsystem status.
- Tracing: propagation via `X-Request-ID`/`traceparent`.

### 8. Performance Targets
- C2PA sign p95 < 100 ms for 10KB docs (single).  
- Embeddings sign p95 < 600 ms for median doc (sentence-level).  
- Batch: 100 docs/sec (C2PA) with 8 workers.  

### 9. Security
- API key Bearer auth; key scope + rotation policy.
- Input size limits (e.g., 2 MB default; configurable).
- SQL injection prevention (parameterized queries).
- CORS production policy; allowlist origins.
- Certificate store management (org lifecycle).

### 10. Data & Storage
- DB indices for hot paths (content refs, merkle nodes, orgs).
- Connection pooling tuned for concurrency.
- Optional Redis cache for Merkle trees and idempotency keys (TTL 24h).
- Migrations versioned and reversible.

---

## Data Models (Additions/Changes)

- `organizations`
  - Add columns (if missing): `cert_chain_pem TEXT NULL`, `status VARCHAR(16) DEFAULT 'active'`, `rotated_at TIMESTAMPTZ NULL`.
- `batch_requests`
  - New table for idempotency and audit (id, idempotency_key, api_key_id, hash, created_at, status).

---

## Testing Plan

- Unit Tests: 90%+ coverage for verification, batch, streaming controllers and services.
- Integration Tests: Against running API; golden samples for signed/tampered.
- Load Tests: k6/Gatling scenarios for single, batch, streaming; 1k concurrent users.
- Fault Injection: Simulate DB down, Redis miss, partial failures.
- Security Tests: AuthZ/AuthN, rate limit bypass attempts, payload fuzzing.
- Benchmarks: Re-run 5K embeddings; add 10K C2PA batch.

---

## Documentation Deliverables

- OpenAPI 3.1 complete; Swagger UI enabled.
- Postman collection and environment templates.
- README updates with examples (curl, Python, JS).
- Error code reference; rate limiting guide.

---

## Rollout & Ops

- Feature flags for batch/streaming endpoints.
- Staging environment soak test (24–48h) with synthetic load.
- Monitoring dashboards and alert thresholds defined.
- Rollback procedure documented (config flag + deploy rollback).

---

## Risks & Mitigations

- Cert discovery complexity → Preload trusted orgs; admin tooling.  
- Batch overload → Strict limits; backpressure; per-key quotas.  
- Streaming instability → SSE with heartbeat; retry strategy; idempotency.  
- Spec drift with SDKs → Contract tests and CI schema checks.

---

## Acceptance Criteria

- Verification returns correct results for valid/tampered samples; cert lookup fixed.  
- Batch and streaming endpoints pass integration and load tests.  
- OpenAPI + Postman delivered; examples executable.  
- p95 latencies meet targets; 0 critical security findings.  
- 90%+ unit test coverage in modified modules.  

---

## Dependencies

- DB migration tooling ready.  
- Redis (optional) available for caching/idempotency.  
- CI runners for tests and benchmarks.  

---

## Handoff Notes for SDK & WordPress Teams

- Publish updated OpenAPI; notify SDKs for regeneration.
- Python SDK to add: `sign_with_embeddings`, `get_merkle_tree`, `verify_sentence`, batch & streaming clients.  
- JS SDK to mirror Python API surface.  
- WordPress to consume embeddings mode and verification once verification is fixed.

---

## Task List

### 1.0 Verification Endpoint Fix (Week 1)
- [x] **1.1 Extend `organizations` model**  
  - **Description**: Add `cert_chain_pem`, `status`, `rotated_at` columns plus Alembic migration + seed updates. Document new fields in component README and agents.md.  
  - **Owner**: Backend API + Database  
  - **Dependencies**: Access to prod/staging DBs; seed scripts (`seed_c2pa_data.py`).  
  - **Acceptance**: Migration applies cleanly; sample orgs show populated chains; rollback script validated.
- [x] **1.2 Certificate resolution service**  
  - **Description**: Implement caching layer (Redis-backed) that resolves signer_id → certificate chain with rotation awareness and trust anchor validation.  
  - **Owner**: Backend API Services  
  - **Acceptance**: Cache hit rate telemetry emitted; stale certificates evicted; unit tests cover active/revoked states.
- [x] **1.3 Controller hardening**  
  - **Description**: Update `/verify` controller for structured verdicts, body size enforcement (2 MB), timeout guard, correlation IDs, and rate limiting middleware hook.  
  - **Owner**: Backend API Controllers  
  - **Acceptance**: Endpoint returns new schema; 400/422/429 handling confirmed via integration tests.
- [x] **1.4 Verification test suite**  
  - **Description**: Add golden sample tests (valid/tampered/missing signer/malformed) plus fuzz harness; integrate into CI.  
  - **Owner**: QA + Backend  
  - **Acceptance**: `uv run pytest tests/test_c2pa_api.py -m verify` passes locally and in CI with ≥90% coverage for module.

### 2.0 Batch Endpoints (Week 2)
- [x] **2.1 `POST /batch/sign` implementation**  
  - **Description**: Shared request schema, bounded concurrency worker pool, idempotency (Redis + `batch_requests`), per-item metrics.  
  - **Acceptance**: Handles up to 100 docs, enforces payload limits, stores runs for 30 days.
- [x] **2.2 `POST /batch/verify` implementation**  
  - **Description**: Reuse batch infrastructure for verification; support partial successes and consolidated failure summary.  
  - **Acceptance**: Mixed payload test returns accurate statuses; tampered docs flagged without aborting batch.
- [x] **2.3 Persistence layer**  
  - **Description**: Create `batch_requests` + `batch_items` tables, indexes, ORM models, admin cleanup job.  
  - **Acceptance**: Alembic migration + rollback succeed; retention job documented.
- [x] **2.4 Batch testing & benchmarks**  
  - **Description**: Add pytest coverage for idempotency/limits; run k6 benchmark to verify ≥100 docs/sec throughput with 8 workers.  
  - **Acceptance**: Benchmark report stored in `docs/perf/batch-sign.md`; throttling proves stable under load.

### 3.0 Streaming Signing (SSE) (Week 3)
- [x] **3.1 SSE controller**  
  - **Description**: Implement `/stream/sign` SSE endpoint with events (`start`, `progress`, `partial`, `final`, `error`) and JSON schema validation.  
  - **Acceptance**: Reference client receives ordered events; connection upgrade documented.
- [x] **3.2 Run state + recovery**  
  - **Description**: Persist run state in Redis with `run_id`, heartbeat, reconnect instructions, and expiration policy.  
  - **Acceptance**: Disconnect/reconnect test resumes progress; heartbeat missed alerts emitted.
- [x] **3.3 Streaming QA**  
  - **Description**: Automated tests for long content, simulated network drops, retry semantics; soak test 2h.  
  - **Acceptance**: Failures captured with actionable logs; soak metrics appended to release artifacts.

### 4.0 OpenAPI & Postman (Weeks 1-2)
- [x] **4.1 Complete OpenAPI 3.1 spec**  
  - **Description**: Document new schemas, error objects, SSE endpoint notes; add CI check to fail on drift.  
  - **Acceptance**: `uv run scripts/validate_openapi.py` passes; spec published at `/docs/openapi.json`.
- [x] **4.2 Swagger UI + JSON publishing**  
  - **Description**: Enable Swagger UI in staging, protect prod with basic auth; ensure versioned spec downloadable.  
  - **Acceptance**: QA confirms accessibility; cache headers set.
- [x] **4.3 Postman assets**  
  - **Description**: Create Postman collection/env templates with working examples; include batch + streaming flows.  
  - **Acceptance**: Collection imported in QA workspace and succeeds against staging.

### 5.0 Error Model & Rate Limiting (Weeks 1-2)
- [x] **5.1 Canonical error catalog**  
  - **Description**: Define error codes/messages/hints; update middleware to return structured responses.  
  - **Acceptance**: Error reference doc merged; endpoints emit codes in logs + responses.
- [x] **5.2 Rate limiting + quotas**  
  - **Description**: Implement Redis sliding window per plan, expose headers (`x-ratelimit-*`), add admin overrides.  
  - **Acceptance**: Load tests trigger 429 with Retry-After; metrics show per-plan usage.
- [x] **5.3 Correlation IDs & logging**  
  - **Description**: Generate/request `x-request-id`, propagate through logs/traces, ensure sampling & PII redaction.  
  - **Acceptance**: Log audit verifies fields present; tracing UI links request to downstream spans.

### 6.0 Observability & Ops (Weeks 2-3)
- [x] **6.1 Metrics + health checks**  
  - **Description**: Add Prometheus metrics (duration, batch size, verdict counts) and `/healthz` `/readyz` endpoints.  
  - **Acceptance**: Metrics scraped in staging; health checks wired into Kubernetes probes.
- [x] **6.2 Dashboards & alerts**  
  - **Description**: Grafana dashboards for latency, error %, queue depth; alerts for p95>120ms, error>2%, heartbeat loss.  
  - **Acceptance**: Dashboards reviewed with SRE; alert runbooks documented.
- [x] **6.3 Log governance**  
  - **Description**: Ensure log redaction, sampling for verbose endpoints, and retention compliance (90 days).  
  - **Acceptance**: Security review sign-off; log pipeline tests confirm redaction rules.

### 7.0 Performance & Security (Weeks 3-4)
- [x] **7.1 Benchmarks**  
  - **Description**: Re-run 5K embeddings benchmark + new 10K C2PA batch; compare to targets and archive results.  
  - **Acceptance**: Report shows throughput/latency meeting KPIs; regressions flagged/resolved.
- [x] **7.2 Load + soak tests**  
  - **Description**: k6 scenarios for single, batch, streaming with 1k concurrent users; 24h soak on staging.  
  - **Acceptance**: No critical errors during soak; resource utilization within plan.
- [x] **7.3 Security validation**  
  - **Description**: OWASP Top 10 testing, dependency scans (`uv pip audit`), auth/rate-limit bypass attempts, secrets review.  
  - **Acceptance**: 0 critical findings; medium issues remediated or waived with approval.

### 8.0 Documentation & Handoffs (Week 4)
- [x] **8.1 Developer docs & examples**  
  - **Description**: Update Enterprise API README, QUICK_START, MICROSERVICES_FEATURES, component agents; add curl, Python (uv), JS samples.  
  - **Acceptance**: Docs PR approved by DevRel; links verified.
- [x] **8.2 Error & rate limit reference**  
  - **Description**: Publish dedicated doc section + Postman markdown summarizing error codes and headers.  
  - **Acceptance**: Reference linked from README + SDK docs.
- [x] **8.3 SDK/WordPress handoff**  
  - **Description**: Conduct walkthrough, deliver OpenAPI + changelog + sample scripts; capture integration feedback.  
  - **Acceptance**: SDK + WordPress teams acknowledge receipt; follow-up issues logged if any.

---

## Timeline & Milestones

- Week 1: Items 1.0, 4.0, 5.0 foundations  
- Week 2: Items 2.0 complete; begin 6.0  
- Week 3: Item 3.0 complete; performance/security 7.0  
- Week 4: Docs & handoffs 8.0; freeze & release  

---

## Communication & Reporting

- Daily async update in project channel with WBS progress.  
- Weekly milestone review; risks/blocks surfaced early.  
- All test and benchmark artefacts attached to releases.  
