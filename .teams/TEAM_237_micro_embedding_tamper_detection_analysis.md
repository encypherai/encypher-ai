# TEAM_237 — Micro Embedding Tamper-Detection Investigation

**Status:** In progress
**Focus:** Analyzing normalization-resilient tamper detection for micro embedding approach

## Session Goal
Investigate whether our ZW/VS256 micro embedding approach provides tamper-detection guarantees that hold regardless of Unicode normalization transforms (NFC/NFD/NFKC/NFKD).

## Key Files
- app/utils/zw_crypto.py
- app/utils/vs256_crypto.py
- app/utils/vs256_rs_crypto.py
- app/utils/multi_embedding.py
- app/utils/merkle/hashing.py
- app/utils/print_stego.py
- tests/test_vs256_crypto.py
- tests/test_zw_crypto.py

## Session Update (Implementation Complete)

### What was implemented
- Added optional sentence-level content binding to VS256 micro signatures using:
  - `HMAC(signing_key, uuid_bytes || SHA256(NFC(sentence_text))[:8])`
  - Backward-compatible verification fallback for existing UUID-only signatures.
- Applied this to both non-ECC and ECC variants:
  - `enterprise_api/app/utils/vs256_crypto.py`
  - `enterprise_api/app/utils/vs256_rs_crypto.py`
- Wired signing path to pass segment text for micro mode:
  - `enterprise_api/app/services/embedding_service.py`
- Wired verification fallback path to extract the containing sentence, strip marker span, and pass `sentence_text` into verify functions:
  - `enterprise_api/app/services/verification_logic.py`

### Tests added/updated
- `enterprise_api/tests/test_vs256_crypto.py`
  - content-binding tamper detection
  - NFC-stability check
  - legacy compatibility (with and without `sentence_text` during verify)
- `enterprise_api/tests/test_vs256_rs_crypto.py`
  - same coverage for RS/ECC signatures
- `enterprise_api/tests/test_verification_logic.py`
  - regression for sentence extraction/marker stripping used by micro fallback verify

### Verification executed
- ✅ `uv run pytest enterprise_api/tests/test_vs256_crypto.py enterprise_api/tests/test_vs256_rs_crypto.py enterprise_api/tests/test_verification_logic.py enterprise_api/tests/test_micro_c2pa_embedding.py -q`
  - Result: `91 passed, 1 skipped`
- ✅ `uv run --offline ruff check app/utils/vs256_crypto.py app/utils/vs256_rs_crypto.py app/services/embedding_service.py app/services/verification_logic.py tests/test_vs256_crypto.py tests/test_vs256_rs_crypto.py tests/test_verification_logic.py`
  - Result: `All checks passed!`

### Status
- Sentence-level tamper detection is now enforced in micro mode signatures while maintaining non-breaking behavior for existing signed content.

### Suggested commit message
```
feat(micro-signatures): add sentence-bound tamper detection with backward-compatible verify

Implement sentence-level content integrity binding for micro mode signatures by
including a normalized text commitment in VS256/VS256-RS HMAC input.

Changes:
- vs256_crypto: add optional sentence_text to create/verify, bind HMAC to
  SHA256(NFC(sentence_text))[:8], preserve legacy UUID-only verification fallback
- vs256_rs_crypto: mirror sentence_text binding + legacy fallback for ECC mode
- embedding_service: pass segment text when creating micro signatures
- verification_logic: extract containing sentence, strip signature span, and pass
  clean sentence_text into micro fallback verification
- tests: add coverage for tamper detection, NFC normalization stability, and
  backward compatibility in both VS256 and VS256-RS; add sentence extraction
  regression test in verification logic

Validation:
- pytest: 91 passed, 1 skipped (targeted micro/vs256/verification suites)
- ruff: all checks passed (offline)
```

## Session Update (Enterprise API Docs Alignment)

### What was updated
- Refreshed core API docs to match current unified sign/verify behavior:
  - `enterprise_api/docs/API.md`
    - `/sign` now documents unified `options` flow and current response envelope shape.
    - Added explicit micro-mode behavior notes (`ecc`, `embed_c2pa`, `store_c2pa_manifest`).
    - Added verification semantics notes for C2PA primary path + micro/ZW fallback behavior.
    - Updated webhooks section from "planned" to currently available endpoints/events and corrected payload examples.
- Updated quickstart examples to use current envelope paths:
  - `enterprise_api/docs/QUICKSTART.md`
    - response access now uses `data.document.signed_text` and `data.document.document_id`.
- Updated stale endpoint references in supporting docs:
  - `enterprise_api/docs/ZW_EMBEDDING_MODE.md` (`/api/v1/sign` + current response shape)
  - `enterprise_api/docs/PERFORMANCE_SCALE.md` (removed `/api/v1/sign/advanced` row)
  - `enterprise_api/docs/THREAT_MODEL.md` (removed `/api/v1/sign/advanced` flow reference)

### Sanity checks executed
- Grep scans confirm no remaining stale references in docs for:
  - `/sign/advanced`
  - `certificate.issued`
  - `verification.tamper_detected`

### Suggested commit message (docs addendum)
```
docs(api): align enterprise docs with unified sign/verify and current webhook taxonomy

Update API and quickstart documentation to reflect the live unified /api/v1/sign
contract (options-based micro configuration, response envelope shape) and current
verification semantics.

Also refresh stale docs that referenced removed endpoints or outdated event names:
- replace /sign/advanced references with /sign
- update webhook availability and supported event taxonomy
- align zw_embedding examples with current request/response shapes

Files:
- enterprise_api/docs/API.md
- enterprise_api/docs/QUICKSTART.md
- enterprise_api/docs/ZW_EMBEDDING_MODE.md
- enterprise_api/docs/PERFORMANCE_SCALE.md
- enterprise_api/docs/THREAT_MODEL.md
```

## Session Update (Remaining Gaps Closed)

### Implemented
- Added formal Merkle assertion contract document:
  - `enterprise_api/docs/MERKLE_ASSERTION_SCHEMA.md`
  - Defines `com.encypher.merkle.v1`, required/optional fields, versioning and verification guidance.
- Added explicit verification trust model documentation:
  - `enterprise_api/docs/VERIFICATION_TRUST_MODEL.md`
  - Covers C2PA primary path, micro/ZW fallback behavior, and reason code semantics.
- Added automated docs-drift guard test suite:
  - `enterprise_api/tests/test_docs_contract_integrity.py`
  - Enforces presence/content of contract docs and blocks stale references (`/sign/advanced`, old webhook events).

### Validation executed
- ✅ `uv run pytest enterprise_api/tests/test_docs_contract_integrity.py -q`
- ✅ `uv run pytest enterprise_api/tests/test_docs_contract_integrity.py enterprise_api/tests/test_customer_docs_contract.py -q`
  - Result: `6 passed`
- ✅ `uv run --offline ruff check tests/test_docs_contract_integrity.py`
  - Result: `All checks passed!`

### Suggested commit message (final)
```
docs(contract): add merkle assertion + verification trust model and enforce docs drift checks

Close remaining API-contract gaps by introducing formal documentation for
Merkle linkage assertions and verification trust semantics, plus automated tests
that prevent stale endpoint/event references from re-entering customer docs.

Includes:
- docs/MERKLE_ASSERTION_SCHEMA.md for com.encypher.merkle.v1
- docs/VERIFICATION_TRUST_MODEL.md for primary/fallback verify behavior and reason_code usage
- tests/test_docs_contract_integrity.py for contract doc existence/content and stale reference guardrails
- aligned docs updates across API.md, QUICKSTART.md, ZW_EMBEDDING_MODE.md,
  PERFORMANCE_SCALE.md, THREAT_MODEL.md
```

## Session Update (Streaming Doc Normalization)

### Implemented
- Normalized `enterprise_api/docs/STREAMING_API.md` to current implementation contract:
  - Canonical run-based SSE flow (`POST /api/v1/sign/stream`) with explicit event sequence.
  - Added run-state recovery endpoint docs (`GET /api/v1/sign/stream/runs/{run_id}`).
  - Corrected session-based WebSocket + session SSE semantics.
  - Updated chat streaming section (`POST /api/v1/chat/completions`, `WS /api/v1/chat/stream`).
  - Removed stale phased/preview framing and outdated examples.

### TDD / Guardrails
- Extended docs contract test suite:
  - `enterprise_api/tests/test_docs_contract_integrity.py`
  - Added streaming contract assertions for required stream-sign SSE tokens and run-state endpoint references.

### Validation executed
- ✅ `uv run pytest enterprise_api/tests/test_docs_contract_integrity.py enterprise_api/tests/test_customer_docs_contract.py -q`
  - Result: `7 passed`
- ✅ `uv run --offline ruff check tests/test_docs_contract_integrity.py`
  - Result: `All checks passed!`

### Suggested commit message (streaming addendum)
```
docs(streaming): normalize STREAMING_API contract and enforce SSE/run-state doc coverage

Align streaming documentation with live implementation by documenting the canonical
run-based SSE signing flow, session-based WS/SSE patterns, and run-state lookup.

Also extend docs contract tests to prevent regressions in streaming contract docs.

Files:
- enterprise_api/docs/STREAMING_API.md
- enterprise_api/tests/test_docs_contract_integrity.py
```

## Session Update (Hybrid Merkle Linkage)

### What was implemented
- Added a hybrid Merkle linkage layer that complements micro sentence-bound signatures:
  - Persist Merkle linkage metadata on `content_references.embedding_metadata` for all embedding modes.
  - Attach Merkle linkage assertion into C2PA manifests when a Merkle root hash is available.
- Extended embedding service inputs to accept:
  - `merkle_root_hash`
  - `merkle_segmentation_level`
- Wired call sites to pass Merkle linkage context:
  - `enterprise_api/app/services/embedding_executor.py`
  - `enterprise_api/app/services/streaming_merkle_service.py`

### Files changed
- `enterprise_api/app/services/embedding_service.py`
- `enterprise_api/app/services/embedding_executor.py`
- `enterprise_api/app/services/streaming_merkle_service.py`
- `enterprise_api/tests/test_micro_c2pa_embedding.py`
- `enterprise_api/tests/test_embedding_service_invisible.py`

### Tests added/updated
- `test_sign_micro_hybrid_merkle_metadata_in_manifest_and_db`
  - verifies micro + C2PA embeds `com.encypher.merkle.v1`
  - verifies DB metadata includes `merkle_root_id`, `merkle_root_hash`, `merkle_segmentation_level`
- `test_create_embeddings_persists_merkle_linkage_metadata`
  - verifies non-micro/general embedding flow persists Merkle linkage metadata

### Verification executed
- ✅ `uv run pytest enterprise_api/tests/test_embedding_service_invisible.py -k test_create_embeddings_persists_merkle_linkage_metadata -q`
- ✅ `uv run pytest enterprise_api/tests/test_micro_c2pa_embedding.py -k test_sign_micro_hybrid_merkle_metadata_in_manifest_and_db -q`
- ✅ `uv run pytest enterprise_api/tests/test_vs256_crypto.py enterprise_api/tests/test_vs256_rs_crypto.py enterprise_api/tests/test_verification_logic.py enterprise_api/tests/test_micro_c2pa_embedding.py enterprise_api/tests/test_embedding_service_invisible.py enterprise_api/tests/test_document_level_c2pa_placement.py enterprise_api/tests/test_sign_advanced_content_db_routing.py -q`
  - Result: `107 passed, 1 skipped`
- ✅ `uv run --offline ruff check app/services/embedding_service.py app/services/embedding_executor.py app/services/streaming_merkle_service.py tests/test_micro_c2pa_embedding.py tests/test_embedding_service_invisible.py`
  - Result: `All checks passed!`

### Suggested commit message (updated)
```
feat(hybrid-integrity): add Merkle linkage metadata/assertions across micro and embedding modes

Add a hybrid integrity layer that combines sentence-bound micro signatures with
document-level Merkle linkage persisted in DB and embedded in C2PA manifests.

Changes:
- embedding_service:
  - accept merkle_root_hash + merkle_segmentation_level
  - persist merkle_root_id/root_hash/segmentation metadata in content_references.embedding_metadata
  - add com.encypher.merkle.v1 assertion (root_hash/root_id/segmentation_level/total_segments)
    to C2PA embedding paths when Merkle context exists
- embedding_executor: pass selected Merkle root hash/level into create_embeddings
- streaming_merkle_service: pass computed streaming root hash/segmentation into create_embeddings
- tests:
  - micro integration test for Merkle assertion + DB metadata persistence
  - embedding service unit test for Merkle linkage metadata persistence in general flow

Validation:
- pytest: 107 passed, 1 skipped (targeted integrity + embedding suites)
- ruff: all checks passed (offline)
```
