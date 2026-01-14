# PRD — Enterprise API Integrity Hashing SSOT

## Status
Completed

## Current Goal
Unify `enterprise_api` integrity hashing across signing and verification: **NFC-normalized UTF-8 bytes, case-sensitive**.

## Overview
`enterprise_api` previously used multiple hashing semantics (including lowercasing for Merkle leaf hashes and raw hashing for `/sign`). This PRD defines and implements a single source of truth for integrity hashing to keep tamper detection deterministic and consistent with NFC normalization expectations.

## Objectives
- Ensure Merkle `leaf_hash` is computed from NFC-normalized text without case folding.
- Ensure `/sign` `text_hash` and `sentence_hash` are computed from NFC-normalized text without case folding.
- Lock these semantics with tests.

## Tasks
- [x] 1.0 Tests (TDD)
- [x] 1.1 Add tests asserting NFC equivalence and case sensitivity for integrity hashes
- [x] 2.0 Implementation
- [x] 2.1 Update Merkle `compute_leaf_hash` to NFC-only (no lowercasing)
- [x] 2.2 Update `/sign` hashing (`compute_text_hash`, `compute_sentence_hash`) to NFC-only (no lowercasing)
- [x] 3.0 Verification
- [x] 3.1 Task — ✅ pytest ✅ ruff (enterprise_api)

## Success Criteria
- Merkle leaf hashes differ for `"Hello"` vs `"hello"`.
- Merkle leaf hashes match for NFC-equivalent forms (`"café"` vs `"cafe\u0301"`).
- `/sign` `text_hash` and `sentence_hash` match for NFC-equivalent forms and differ by case.
- ✅ `uv run ruff check .` (enterprise_api)
- ✅ `uv run pytest` (enterprise_api)

## Completion Notes
- Updated `enterprise_api/app/utils/merkle/hashing.py::compute_leaf_hash` to hash `unicodedata.normalize("NFC", text)`.
- Updated `enterprise_api/app/utils/sentence_parser.py` to NFC-normalize before hashing.
- Added `enterprise_api/tests/test_integrity_hashing.py` to lock semantics.
