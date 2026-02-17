# TEAM_166 — Micro Mode Flag-Based Architecture Refactor

## Session: 2026-02-17
## Goal: Collapse micro_ecc/micro_c2pa/micro_ecc_c2pa into single "micro" mode with ecc + embed_c2pa flags

## Status: Complete

## Design Decision
Collapse 4 manifest modes (`micro`, `micro_ecc`, `micro_c2pa`, `micro_ecc_c2pa`) into a single `micro` mode
controlled by two orthogonal boolean flags:

| Flag | Default | Effect |
|------|---------|--------|
| `ecc` | `true` | Use RS error-correcting encoding (44 chars) vs plain HMAC (36 chars) |
| `embed_c2pa` | `true` | Embed full C2PA manifest into the signed content |

A C2PA-compatible manifest is **always** generated for micro mode requests.
- `store_c2pa_manifest` (existing, default true) controls whether it's persisted in DB.
- `embed_c2pa` controls whether it's embedded into the content itself.

Breaking change: old mode names removed immediately (no deprecation aliases).

## Files to Change
- `app/schemas/signing_constants.py` — remove old modes
- `app/schemas/sign_schemas.py` — add ecc + embed_c2pa flags
- `app/schemas/embeddings.py` — add ecc + embed_c2pa flags
- `app/services/unified_signing_service.py` — propagate flags
- `app/services/embedding_executor.py` — propagate flags
- `app/services/embedding_service.py` — collapse 4 branches into 1
- `app/schemas/integration_schemas.py` — update default
- `app/models/ghost_integration.py` — update default
- `app/services/ghost_integration.py` — update default
- `app/services/verification_logic.py` — update mode references
- `app/api/v1/public/verify.py` — update mode checks
- `app/utils/html_text_extractor.py` — update docstrings
- `apps/dashboard/src/app/playground/page.tsx` — update UI
- `apps/dashboard/src/lib/playgroundEndpoints.mjs` — update default
- `tests/test_micro_c2pa_embedding.py` — rewrite for flag API
- `tests/test_ghost_integration.py` — update default mode assertions
- `tests/test_c2pa_conformance_sign_verify.py` — update mode reference
- `tests/test_email_embedding_survivability.py` — update docstrings/names
- `tests/test_html_text_extractor.py` — update docstring
- `tests/e2e_live/test_live_html_cms_signing.py` — rewrite for flag API
- `scripts/sign_html_cms.py` — update CLI choices and defaults
- `apps/dashboard/src/app/playground/page.tsx` — update UI options
- `apps/dashboard/src/lib/playgroundEndpoints.mjs` — update default
- `app/routers/signing.py` — update endpoint docs

## Session Log

### Changes Made
1. **signing_constants.py**: Removed `micro_ecc`, `micro_c2pa`, `micro_ecc_c2pa` from `MANIFEST_MODES`
2. **sign_schemas.py**: Added `ecc` and `embed_c2pa` boolean fields to `SignOptions`
3. **embeddings.py**: Added `ecc` and `embed_c2pa` fields to `EncodeWithEmbeddingsRequest`
4. **unified_signing_service.py**: Propagated `ecc` and `embed_c2pa` from options to legacy request
5. **embedding_executor.py**: Propagated `ecc` and `embed_c2pa` to `create_embeddings` call
6. **embedding_service.py**: Collapsed 4 micro branches (~390 lines) into 1 unified branch (~140 lines) with flag-driven logic. Key design: always generate C2PA manifest via `embed_metadata`, then choose whether to include it in returned content based on `embed_c2pa` flag
7. **integration_schemas.py**: Updated default and validator
8. **ghost_integration.py** (model + service): Updated defaults from `micro_ecc_c2pa` to `micro`
9. **alembic migration**: Updated server_default
10. **verification_logic.py**: Updated fallback mode names and comments
11. **public verify.py**: Updated mode check from `("micro_c2pa", "micro_ecc_c2pa")` to `"micro"`
12. **All test files**: Rewrote to use `micro` with `ecc`/`embed_c2pa` flags
13. **Dashboard playground**: Updated UI options and defaults
14. **Script**: Updated CLI choices and defaults
15. **Router docs**: Added `ecc` and `embed_c2pa` to options reference table

### Test Results
- **1011 passed**, 11 failed (all pre-existing), 39 skipped
- Pre-existing failures: 9× verify 404→410, 1× README/OpenAPI drift, 1× webhook tier gating
- **Zero regressions** from this refactor

### Blockers
None.

## Suggested Commit Message
```
feat(api)!: collapse micro modes into single "micro" with ecc + embed_c2pa flags

BREAKING CHANGE: Remove manifest_mode values micro_ecc, micro_c2pa,
micro_ecc_c2pa. Use manifest_mode="micro" with boolean flags instead:
  - ecc (default: true) — Reed-Solomon error correction (44 vs 36 chars)
  - embed_c2pa (default: true) — embed C2PA manifest in content

A C2PA-compatible manifest is ALWAYS generated for micro mode.
store_c2pa_manifest controls DB persistence; embed_c2pa controls
in-content embedding. Default behaviour (ecc=true, embed_c2pa=true)
is equivalent to the old micro_ecc_c2pa mode.

Files changed:
- app/schemas/signing_constants.py — remove old modes from MANIFEST_MODES
- app/schemas/sign_schemas.py — add ecc + embed_c2pa to SignOptions
- app/schemas/embeddings.py — add ecc + embed_c2pa to request schema
- app/services/embedding_service.py — collapse 4 branches into 1
- app/services/unified_signing_service.py — propagate new flags
- app/services/embedding_executor.py — propagate new flags
- app/schemas/integration_schemas.py — update default + validator
- app/models/ghost_integration.py — update default
- app/services/ghost_integration.py — update default
- app/services/verification_logic.py — update mode references
- app/api/v1/public/verify.py — update mode check
- app/routers/signing.py — update endpoint docs
- app/utils/html_text_extractor.py — update docstrings
- alembic/versions/20260213_190000_add_ghost_integrations.py — update default
- scripts/sign_html_cms.py — update CLI choices
- apps/dashboard/src/app/playground/page.tsx — update UI
- apps/dashboard/src/lib/playgroundEndpoints.mjs — update default
- tests/test_micro_c2pa_embedding.py — rewrite for flag API
- tests/test_ghost_integration.py — update assertions
- tests/test_c2pa_conformance_sign_verify.py — update mode
- tests/test_email_embedding_survivability.py — update names
- tests/test_html_text_extractor.py — update docstring
- tests/e2e_live/test_live_html_cms_signing.py — rewrite for flag API
