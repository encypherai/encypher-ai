# Enterprise API Observability & Incident Response

**Status**: Drafted for production readiness review
**Scope**: Logging, metrics, alerts, runbooks
**Owners**: Platform + SRE

## 1. Overview
Observability ensures production reliability and rapid incident response through structured logging, metrics, alerts, and runbooks.

## 2. Structured Logging (PRD 4.1)
### Current State
- Standard logging configured in `app/main.py`.
- Request logging middleware captures status + latency.
- All tier-enforcement rejections (proxy signing, batch limit) and quota enforcement (feature gating, quota exceeded) emit `logger.warning()` before returning 403/429 responses, enabling monitoring via log-based alerting.

### Target State
- JSON structured logging with correlation IDs.
- Unified log schema for sign/verify/batch operations.

### Open Gaps
- Standardize log fields across routers.

### Correlation ID Propagation
The `[req-xxxx]` correlation ID is forwarded as the `x-request-id` header on all outbound calls to key-service and auth-service, enabling end-to-end trace correlation across service boundaries.

## 2.1. Distributed Tracing (OpenTelemetry)
Distributed tracing is available via OpenTelemetry. Set `OTEL_EXPORTER_OTLP_ENDPOINT` to enable export (e.g., to Jaeger, Grafana Tempo, or Datadog). FastAPI endpoints and httpx calls are auto-instrumented. Tracing is a safe no-op when the env var is unset.

Service name defaults to `enterprise-api` and can be overridden with `OTEL_SERVICE_NAME`.

## 2.2. Audit Log Events
Core signing/verification operations write audit log entries to the `audit_logs` table. The following events are emitted:

| Event | Source |
|-------|--------|
| `document.signed` (`DOCUMENT_SIGNED`) | Single-document signing endpoint |
| `batch.sign.started` (`BATCH_SIGN_COMPLETED`) | Batch signing completion |
| `document.verified` (`DOCUMENT_VERIFIED`) | Document verification endpoint |

These writes are performed asynchronously (best-effort, fire-and-forget via `asyncio.create_task`) and do not block the API response.

## 3. Metrics & Dashboards (PRD 4.2)
### Current State
- Metrics service initialized in `app/main.py`.
- Prometheus exporter via `app/observability/metrics`.

### Target State
- Dashboards for throughput, latency, error rates, queue depth.
- Business KPIs (usage by tier, quota warnings).

### Open Gaps
- Metrics coverage for batch worker durations and verification failures.

## 4. Alert Thresholds & Runbooks (PRD 4.3)
### Alert Signals
- Error rate > 2% over 5 minutes.
- Latency p95 > 500ms for sign/verify.
- Database connection failures.
- Key Service validation failures.

### Runbooks
- Incident runbook for API downtime.
- Database failover runbook.
- Key compromise response runbook.

## 5. Incident Response Drill (PRD 4.4)
- Quarterly incident drill with postmortem template.
- Root cause analysis and corrective action tracking.

## 6. References
- `enterprise_api/app/main.py`
- `enterprise_api/app/observability/metrics.py`
- `enterprise_api/app/middleware/metrics_middleware.py`
