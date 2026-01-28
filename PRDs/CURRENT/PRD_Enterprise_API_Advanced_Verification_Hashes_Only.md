# Enterprise API Advanced Verification (Hashes-Only)

**Status:** 🔄 In Progress
**Current Goal:** Task 6.6 — Frontend verification (puppeteer, if applicable)

## Overview

Enterprise API verification must support advanced tamper detection without storing or returning DB-backed text. Public/basic verification should only validate signer + manifest integrity, while advanced verification performs strict Merkle-based tamper detection, localization, and soft-match similarity based solely on user-submitted text.

## Objectives

- Enforce hashes-only storage and response policy across verification workflows.
- Implement strict tamper detection using canonicalization, segmentation, and Merkle root comparison.
- Provide tamper localization and soft-match scoring using request-derived snippets only.
- Update tests, logging, and documentation to reflect new behavior.

## Tasks

### 1.0 PRD & API Design

- [x] 1.1 Define public/basic verification response policy (no DB text; signer + manifest integrity only).
- [x] 1.2 Specify advanced verification request/response payloads.
- [x] 1.3 Define canonicalization/segmentation versioning (NFC + newline/whitespace policy; C2PA alignment).
- [x] 1.4 Define PII/access-control policy for snippets (request-derived only) and logging redaction rules.

### 2.0 Data Model & Storage Policy

- [x] 2.1 Stop persisting `content_references.text_content`, `content_references.text_preview`, `content_references.manifest_data`.
- [x] 2.2 Stop persisting `merkle_subhashes.text_content`.
- [x] 2.3 Stop persisting `fuzzy_fingerprints.text_preview` (replace with request-derived previews).
- [x] 2.4 Create migration plan for removing legacy text columns once safe.

### 3.0 Public/Basic Verification Behavior

- [x] 3.1 `GET /api/v1/public/verify/{ref_id}`: signer + manifest integrity only (no text preview).
- [x] 3.2 `POST /api/v1/public/verify/batch`: signer + manifest integrity only (no text preview).
- [x] 3.3 `POST /api/v1/public/extract-and-verify`: compute preview only from request text; remove request-preview logging.

### 4.0 Advanced Verification (Strict Tamper Detection)

- [x] 4.1 Canonicalize and segment request text using NFC normalization.
- [x] 4.2 Compute Merkle root and compare with stored root for strict tamper detection.
- [x] 4.3 Persist version metadata for canonicalization/segmentation used at sign time.

### 5.0 Advanced Verification (Localization + Soft Match)

- [x] 5.1 Tamper localization: diff segment hashes, report changed/inserted/deleted segments (request-derived snippets only).
- [x] 5.2 Soft-match: similarity scoring using SimHash (request text only).
- [x] 5.3 Return structured evidence with indices and optional request-derived snippets.

### 6.0 Testing & Validation

- [x] 6.1 Unit tests for public verification endpoints (no DB text).
- [x] 6.2 Unit tests for strict tamper detection + localization.
- [x] 6.3 Unit tests for soft-match scoring.
- [x] 6.4 Linting + typing — ✅ ruff ✅ mypy
- [x] 6.5 Integration tests — ✅ pytest
- [ ] 6.6 Frontend verification — ✅ puppeteer (if applicable)

## Success Criteria

- Public/basic verification never returns DB-stored text and only validates signer + manifest integrity.
- Advanced verification performs strict tamper detection using canonicalization + Merkle root equality.
- Localization identifies changed/inserted/deleted segments with request-derived snippets only.
- Soft-match provides similarity score resilient to copy/paste changes.
- Hashes-only storage policy enforced across data models and logs.
- All tests passing with verification markers.

## Completion Notes

### Advanced Verification Payload (1.2)
- Request: `text`, `segmentation_level`, `search_scope`, `include_attribution`, `detect_plagiarism`, `include_heat_map`, `min_match_percentage`, `fuzzy_search`.
- Response: `data` (verdict), `tamper_detection` (root match status), `tamper_localization` (events + counts + request-derived previews), `attribution`, `plagiarism`, `fuzzy_search`, `soft_match`.

### Canonicalization/Segmentation Versioning (1.3, 4.3)
- Canonicalization version `v1` stored in Merkle root metadata + embedding metadata.
- NFC normalization enforced before hashing; boundary detection uses spaCy default when available else regex fallback.
- Metadata includes hashing algorithm (SHA-256), segmentation levels, primary level, and word inclusion flag.

### PII/Access Control Policy (1.4)
- Never return DB-stored text or previews.
- Snippets/previews only derived from request text.
- Logs omit request text content (no previews).

### Migration Plan (2.4)
1. Add migration to drop legacy text columns (`content_references.text_content`, `text_preview`, `manifest_data`, `merkle_subhashes.text_content`, `fuzzy_fingerprints.text_preview`).
2. Backfill/validate that no code paths depend on dropped columns; run verification tests.
3. Roll out with feature flag in staging, then production, and monitor error rates.

### Dev Environment Validation
- `uv run python scripts/test_full_stack.py` (full-stack integration smoke test)
