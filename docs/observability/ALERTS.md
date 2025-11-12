# Observability Runbook

| Metric | Source | Threshold | Action |
|--------|--------|-----------|--------|
| Batch signing p95 latency | `/metrics` (`encypher_batch_sign_requests_total` + app logs) | >120ms for 5 minutes | Scale workers, inspect Postgres write queue |
| Batch error rate | `/metrics` + dashboard | >2% in 10 minute window | Check `docs/perf/batch-sign.md` baseline, inspect idempotency collisions |
| Streaming heartbeat | Redis run store (`GET /stream/runs/{run_id}`) | No heartbeat for 30s | Notify SRE, recycle run |

Dashboards track:
- Request throughput (`encypher_*_total`)
- Error rate from structured logs (filter by `error.code`)
- Streaming run backlog (Redis key count)

Alerts are wired in Grafana with PagerDuty targets. Update this file when thresholds change.
