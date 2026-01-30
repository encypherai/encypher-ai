# TEAM_135 — Advanced Verification Hashes-Only

## Status
- **In Progress**

## Goal
Implement advanced verification for Enterprise API with hashes-only storage, ensuring public/basic verification never returns DB-stored text and advanced verification provides strict tamper detection, localization, and soft-match based solely on user-submitted text.

## Scope
- PRD creation for advanced verification workflow and API changes.
- Public/basic verification responses: signer + manifest integrity only (no DB text).
- Advanced verification: canonicalization/segmentation + Merkle root checks, tamper localization, soft-match similarity scoring.
- Hashes-only storage policy enforcement across content references, Merkle subhashes, and fuzzy fingerprints.

## Verification Plan
- `uv run ruff check .`
- `uv run mypy .`
- `uv run pytest` (targeted tests for public verify, advanced verification)
- Puppeteer verification for website tool (if applicable)

## Notes
- Snippets returned must be derived only from user-submitted text.
- Follow C2PA NFC normalization rules where applicable.
- Added tamper detection/localization + soft-match assertions in advanced verification tests.
- Implemented canonicalization/segmentation version metadata persisted in Merkle root + embedding metadata.
- Updated full-stack smoke script to align with verification-service endpoint + DB email verify checks.
- Latest checks: `uv run ruff check .`, `uv run mypy .`, `uv run pytest`, `uv run pytest tests/test_sign_advanced_merkle_options.py`, `uv run python scripts/test_full_stack.py`.
- Remaining: Puppeteer verification (if applicable).
