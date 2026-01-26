# Enterprise API Performance & Scale Targets

**Status**: Drafted for production readiness review
**Scope**: Load targets, capacity planning, latency SLOs, batch throughput
**Owners**: Platform + API Engineering

## 1. Overview
Performance targets ensure the Enterprise API can support archive-scale workloads (10k+ documents) with predictable latency and throughput.

## 2. Load-Test Targets (PRD 3.1)
### Baseline Targets
- **Sign (C2PA)**: 250+ req/s sustained
- **Verify**: 400+ req/s sustained
- **Batch sign**: 10k documents within 20 minutes
- **Batch verify**: 10k documents within 15 minutes

### Evidence
- `enterprise_api/docs/BENCHMARK_BASELINE.md` contains November 2025 baseline.

## 3. Capacity Planning (PRD 3.2)
### Storage
- Content references and proofs scale with document count.
- Plan for database growth at **N documents/day** (customer-specific) with 2x headroom.

### Indexing
- Required indexes for hot paths: `content_references`, `merkle_nodes`, `audit_logs`.
- Validate query plans for sign/verify by document ID + org ID.

### Throughput
- Scale API workers horizontally with CPU-bound signing paths.
- Cache Key Service validation results in Redis.

## 4. Latency SLOs (PRD 3.3)
| Endpoint | p50 | p95 | p99 |
| --- | --- | --- | --- |
| `POST /api/v1/sign` | 50ms | 200ms | 500ms |
| `POST /api/v1/verify` | 40ms | 150ms | 400ms |
| `POST /api/v1/sign/advanced` | 150ms | 400ms | 800ms |
| `POST /api/v1/verify/advanced` | 120ms | 350ms | 700ms |

## 5. Batch Throughput (PRD 3.4)
- Target 10k documents per batch with < 20 min end-to-end.
- Batch request retention defaults to 30 days.
- Idempotency keys required per batch request.

## 6. Open Gaps
- Load-test harness for 10k+ document batches.
- Capacity plan with storage + index sizing.
- SLO monitoring dashboards and alerts.

## 7. References
- `enterprise_api/docs/BENCHMARK_BASELINE.md`
- `enterprise_api/app/services/batch_service.py`
- `enterprise_api/app/services/idempotency_service.py`
