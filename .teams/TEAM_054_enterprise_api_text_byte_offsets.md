# TEAM_054 — Enterprise API Text Byte Offsets

## Session Goal
Align `enterprise_api` /sign, /sign/advanced, and /verify behavior with `docs/c2pa/Manifests_Text.txt` requirements for **byte-based offsets** (NFC-normalized UTF-8), across `c2pa-text` and `encypher-ai` dependencies.

## Status Log
- Started: 2026-01-12
- Baseline: `uv run pytest` (enterprise_api) => 564 passed, 62 skipped, 1 failed (`enterprise_api/tests/test_multi_embedding_segmentation_alignment.py::test_multi_embedding_verification_matches_sentence_segmentation`)
- Fix: Updated `c2pa-text` Python `find_wrapper_info` to return UTF-8 byte offsets (start + length) and adjusted wrapper removal. This aligned with `encypher-ai` expectations.
- Verification: `uv run ruff check .` (enterprise_api) => OK
- Verification: `uv run pytest` (enterprise_api) => 566 passed, 62 skipped
