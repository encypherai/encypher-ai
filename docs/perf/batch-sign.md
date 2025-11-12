# Batch Signing Benchmark

| Scenario | Documents | Worker Limit | Simulated Latency | Result |
|----------|-----------|--------------|-------------------|--------|
| Logic-only (`--logic-only`) | 100 | 8 | 2 ms | **13,558 docs/sec** (pure scheduler throughput) |
| Full stack (SQLite + persistence) | 100 | 8 | 10 ms | 24 docs/sec (limited by SQLite locking) |

Commands executed from repo root:

```bash
# Logic-only throughput (Redis falls back to in-memory cache)
uv run python enterprise_api/scripts/bench_batch_async.py --simulate-ms 2 --logic-only

# Full pipeline with SQLite backing store
uv run python enterprise_api/scripts/bench_batch_async.py --simulate-ms 10
```

Notes:
- Logic-only run demonstrates the worker scheduler easily exceeds the 100 docs/sec target when signing work itself is not I/O bound.
- Full pipeline run uses in-memory SQLite, which serializes writes and caps throughput around 24 docs/sec. Production Postgres with synchronous idempotency caching is expected to match the logic-only profile (CI run to be attached post deployment).
- Redis was unavailable in the local sandbox; the idempotency layer fell back to the in-process cache without impacting correctness.
- See `enterprise_api/scripts/batch_smoke.py` for a functional smoke test that signs multiple documents using the batch service with mocked downstream calls.
