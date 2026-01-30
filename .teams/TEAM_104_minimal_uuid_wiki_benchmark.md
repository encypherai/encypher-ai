# TEAM_104: Minimal UUID Wiki Benchmark

## Summary
- Ran 500-article minimal_uuid + C2PA batch signing with extract-and-verify sampling.
- Confirmed outputs persisted and validation stats captured.
- Fixed extract-and-verify signer_id resolution + manifest UUID lookup to pass sampling.

## Notes
- Commands:
  - `ENCYPHER_API_KEY=demo-api-key-for-testing uv run python tools/large_dataset_sign_verify.py --mode minimal_uuid --limit 500 --concurrency 8 --verify-sample 50 --base-url http://localhost:9000`
  - `uv run pytest`
  - `uv run ruff check tools/large_dataset_sign_verify.py`
- Verification sampling (post-fix): 50/50 valid via `http://localhost:9000/api/v1/public/extract-and-verify`.
- Batch stats: 500 files, 331.03s total, avg 662.07 ms, p50 297.18 ms, p95 2404.21 ms.
- Extract-and-verify sample: 50 files, 0.47s total, avg 9.30 ms, p50 5.52 ms, p95 27.20 ms.
