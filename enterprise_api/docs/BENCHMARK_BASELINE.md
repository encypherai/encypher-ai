# Benchmark Baseline (November 2025)

## Test Environment
- **Hardware**: Docker Desktop on Windows (10 cores allocated)
- **Stack**: 
  - API: Python 3.11 (FastAPI + Uvicorn w/ uvloop)
  - Database: PostgreSQL 15 (Alpine)
  - Dependencies: Managed via `uv`
- **Dataset**: 5,000 Wikipedia articles (Simple English)
- **Concurrency**: 20 workers

## Results

| Metric      | C2PA Sign (CPU Bound) | Merkle Encode (I/O Bound) |
|-------------|-----------------------|---------------------------|
| **Total Time**  | 18.05s                | 541.20s                   |
| **Throughput**  | **276.96 docs/s**     | **9.24 docs/s**           |
| **Avg Latency** | 3.61 ms               | 108.24 ms                 |

## Analysis

### 1. C2PA Signing (277 req/s)
- **Performance**: Excellent.
- **Bottleneck**: CPU (hashing and cryptographic signing).
- **Conclusion**: The current Python implementation (likely leveraging C-extensions for crypto) is highly efficient. Moving to Rust would offer minimal gains here as the overhead is already low (3.6ms).

### 2. Merkle Encoding (9.2 req/s)
- **Performance**: Moderate/Slow.
- **Bottleneck**: **Database I/O**.
    - Merkle encoding requires segmentation (sentence splitting) and inserting *every node* (leaves and parents) into the database for provenance tracking.
    - For 5,000 docs with ~20 sentences each, that's 100,000+ database inserts.
- **Optimization Strategy**: 
    - **Do not rewrite in Rust yet.** The constraint is PostgreSQL write latency.
    - **Action Items**: 
        1. Use **bulk inserts** (`COPY`) instead of individual row inserts.
        2. Tune PostgreSQL `wal_level` and `commit_delay` for write-heavy workloads.
        3. Consider caching Merkle trees in Redis and persisting to Postgres asynchronously.
