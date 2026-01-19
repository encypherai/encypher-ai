# Enterprise API Fuzzy Fingerprinting

**Status:** ✅ Completed
**Current Goal:** ✅ Complete — ready to archive.

## Overview

Add locality-sensitive hash (LSH) fingerprinting to the Enterprise API to enable fuzzy attribution of text segments that have been paraphrased, reordered, or lightly edited. The feature will build a fingerprint index for Merkle-encoded content and provide similarity search endpoints that return attribution results with Merkle proofs.

## Objectives

- Implement LSH fingerprint indexing for Merkle-encoded text segments (SimHash first, MinHash optional).
- Expose enterprise-tier API endpoints for fuzzy similarity search with Merkle proofs and similarity scores.
- Ensure persistence, tier gating, OpenAPI docs, and test coverage.

## Tasks

### 1.0 Product & Spec Alignment

- [x] 1.1 Summarize ENC0100 fuzzy fingerprint requirements and map to API endpoints
- [x] 1.2 Define request/response schema fields (fingerprint type, similarity threshold, proof inclusion)

### 2.0 Data Model & Services

- [x] 2.1 Add fuzzy fingerprint index table + SQLAlchemy model
- [x] 2.2 Implement SimHash/MinHash generation utilities (SimHash required)
- [x] 2.3 Implement FuzzyFingerprintService (index segments, query candidates, compute similarity)
- [x] 2.4 Integrate indexing into Merkle document encoding or add explicit indexing endpoint

### 3.0 API Endpoints

- [x] 3.1 Add enterprise fuzzy fingerprint search endpoint
- [x] 3.2 Add enterprise fingerprint indexing endpoint or indexing toggle on /enterprise/merkle/encode
- [x] 3.3 Add tier gating and quota tracking

### 4.0 Tests

- [x] 4.1 Unit tests for fingerprint generation + similarity scoring
- [x] 4.2 API tests for indexing + search
- [x] 4.3 Integration tests for Merkle proof inclusion

### 5.0 Documentation

- [x] 5.1 Update enterprise_api/README.md
- [x] 5.2 Update enterprise_api/docs/openapi.json
- [x] 5.3 Update API sandbox strategy doc with fuzzy fingerprint commercial value

### 6.0 Validation

- [x] 6.1 Linting clean — ✅ ruff
- [x] 6.2 Unit/integration tests passing — ✅ pytest

## Success Criteria

- Fuzzy fingerprint endpoints return candidate matches with similarity scores and optional Merkle proofs.
- Fingerprint index is persisted and supports similarity threshold configuration.
- Enterprise tier gating enforced for all fuzzy fingerprint operations.
- Documentation updated and tests passing with verification markers.

## Completion Notes
- ✅ OpenAPI regenerated with Verify Advanced + fuzzy search fields.
- ✅ Tests: `uv run pytest` (586 passed, 62 skipped); `uv run ruff check .`.
- ✅ PRD ready for archive.
