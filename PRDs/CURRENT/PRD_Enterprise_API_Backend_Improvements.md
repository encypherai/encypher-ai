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

- [ ] 1.0 Verification Endpoint Fix (cert lookup, structured verdicts)
  - [ ] 1.1 Model & repo changes for `organizations` (cert chain, status)
  - [ ] 1.2 Service: certificate resolution by signer_id
  - [ ] 1.3 Controller: error mapping, size/time limits
  - [ ] 1.4 Tests: valid, tampered, no-cert, malformed

- [ ] 2.0 Batch Endpoints
  - [ ] 2.1 `POST /batch/sign` (idempotency, concurrency, limits)
  - [ ] 2.2 `POST /batch/verify` (partial failures)
  - [ ] 2.3 DB: `batch_requests` table + indexes
  - [ ] 2.4 Tests: mixed outcomes, idempotency, limits

- [ ] 3.0 Streaming Signing (SSE)
  - [ ] 3.1 Controller emitting events: start/progress/final/error
  - [ ] 3.2 Idempotency via `run_id`; heartbeat; retry support
  - [ ] 3.3 Tests: long content, disconnects, retries

- [ ] 4.0 OpenAPI & Postman
  - [ ] 4.1 Complete spec with schemas/examples
  - [ ] 4.2 Publish Swagger UI + JSON
  - [ ] 4.3 Postman collection + environments

- [ ] 5.0 Error Model & Rate Limiting
  - [ ] 5.1 Standardized error codes & mapping
  - [ ] 5.2 Rate limits + quotas + headers
  - [ ] 5.3 Correlation IDs in responses/logs

- [ ] 6.0 Observability & Ops
  - [ ] 6.1 Metrics and health endpoints
  - [ ] 6.2 Dashboards and alerts
  - [ ] 6.3 Log redaction and sampling

- [ ] 7.0 Performance & Security
  - [ ] 7.1 Benchmarks (C2PA 10K; embeddings 5K rerun)
  - [ ] 7.2 Load tests: 1k concurrent; soak 24h
  - [ ] 7.3 Security tests: OWASP Top 10; dependency scan

- [ ] 8.0 Docs & Handoffs
  - [ ] 8.1 README, examples (curl, Python, JS)
  - [ ] 8.2 Error & rate limit reference
  - [ ] 8.3 SDK/WordPress handoff notes

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
