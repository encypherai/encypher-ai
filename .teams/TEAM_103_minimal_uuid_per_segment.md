# TEAM_103: Minimal UUID Per-Segment

## Summary
- Implemented per-segment minimal_uuid pointers with optional document-level C2PA manifest.
- Updated extract-and-verify lookup to resolve manifest_uuid pointers.
- Added tests for minimal_uuid per-segment payloads and disable_c2pa behavior.

## Notes
- Verification: `uv run ruff check .`, `uv run pytest enterprise_api/tests/test_sign_advanced_minimal_uuid.py enterprise_api/tests/test_embedding_service_invisible.py`.
