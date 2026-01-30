# TEAM_057 — OpenAPI Docs Audit

## Scope
- Audit public OpenAPI documentation for:
  - `/sign`
  - `/sign/advanced`
  - `/verify`
  - `/tools/decode`
- Ensure docs are accurate but do not leak proprietary implementation details.
- Create internal-only SSOT markdown describing normalization, hashing, and byte-offset semantics.

## Session Log
- Started: 2026-01-12

## Work Completed
- Baseline tests were initially blocked by `enterprise_api/test_spacy.py` loading a non-installed spaCy model during collection.
- Updated `enterprise_api/test_spacy.py` to a real pytest test that skips when spaCy or `en_core_web_sm` is unavailable.
- Sanitized public OpenAPI-exposed schema/docstrings to reduce implementation leakage:
  - `enterprise_api/app/schemas/embeddings.py`: removed references to Unicode variation selectors, removed explicit SHA-256 wording, and reduced implementation-specific tier details.
  - `enterprise_api/app/routers/signing.py`: removed explicit ECC mention in `/sign/advanced` OpenAPI description.
  - `enterprise_api/app/routers/verification.py`: removed internal library naming in `/verify` docstring.
  - `enterprise_api/app/routers/tools.py`: removed “proprietary feature” + “trust anchor” wording from `/tools/decode` docstring; clarified `text_span` as UTF-8 byte offsets.
  - `enterprise_api/app/models/response_models.py`: removed NFC wording from public `text_span` description (kept UTF-8 byte offsets).
- Added internal-only SSOT doc:
  - `enterprise_api/docs/INTERNAL_TEXT_NORMALIZATION_HASHING_OFFSETS_SSOT.md`

## Verification
- [x] Baseline: `uv run pytest enterprise_api` (after fixing `test_spacy.py`)
- [x] After changes: `uv run ruff check .`
- [x] After changes: `uv run pytest enterprise_api`
