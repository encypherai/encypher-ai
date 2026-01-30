# TEAM_066 — API Consolidation: Sign/Verify Advanced

## Session Goal
Implement consolidated API surface:
- Enhance `POST /api/v1/sign/advanced` with multi-level Merkle indexing and quota enforcement.
- Add `POST /api/v1/verify/advanced` with attribution + plagiarism options.
- Hard-deprecate standalone Merkle attribution/plagiarism endpoints.
- Update routing + OpenAPI + SDKs + docs + marketing table.

## Working Notes
- Started: 2026-01-15
- Constraints: TDD first; `uv` only for Python deps/commands.

## Verification Checklist
- [x] `uv run ruff check .`
- [x] `uv run pytest` (relevant suites)
- [x] OpenAPI regen + contract tests
- [x] SDK regen (Python/TS/Go/Rust)
- [x] Marketing-site `npm test`
- [ ] e2e (Playwright) if available
