# Testing & Benchmarking Scripts

This directory contains scripts for testing, benchmarking, and maintaining the Encypher Enterprise API.

## Prerequisites

Before running any scripts, ensure you have:

1.  **Python 3.11+** installed.
2.  **Dependencies installed:**
    ```bash
    pip install -r requirements.txt
    pip install -r requirements-dev.txt
    ```
3.  **Database initialized:**
    ```bash
    python scripts/init_db.py
    ```

## Load Testing

Use `run_load_test.py` to simulate traffic and measure system performance.

**Usage:**

```bash
python scripts/run_load_test.py --host http://localhost:8000 --users 10 --duration 30
```

**Arguments:**
*   `--host`: Target API URL (default: `http://localhost:8000`)
*   `--users`: Number of concurrent users (default: 10)
*   `--duration`: Duration of the test in seconds (default: 30)

## Benchmarks

We provide PowerShell scripts for benchmarking specific components.

### C2PA Benchmarks
Measures throughput for C2PA signing and verification.

```powershell
./scripts/bench_c2pa.ps1
```

### Merkle Tree Benchmarks
Measures performance of Merkle tree encoding for large documents.

```powershell
./scripts/bench_merkle.ps1
```

### Embedding Benchmarks
Measures performance of creating and verifying invisible text embeddings.

```powershell
./scripts/bench_embeddings.ps1
```

## Maintenance

*   `init_db.py`: Initializes the database schema.
*   `seed_c2pa_data.py`: Seeds the database with sample C2PA data for testing.
*   `clean_test_artifacts.ps1`: Removes temporary files and artifacts generated during testing.
