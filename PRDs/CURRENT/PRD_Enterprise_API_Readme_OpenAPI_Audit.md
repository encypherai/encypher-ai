# PRD: Enterprise API README/OpenAPI Audit

**Status:** 🟢 Complete  
**Current Goal:** Ensure `enterprise_api/README.md` matches the authoritative OpenAPI schema used for SDK generation and prevent future drift via contract tests.

---

## Overview

The Enterprise API uses auto-generated SDKs (Python/TypeScript/Go/Rust) derived from its OpenAPI schema. To ensure consistent integrations and reduce customer confusion, the `enterprise_api/README.md` endpoint reference must accurately reflect the implemented FastAPI routes and the OpenAPI schema used for SDK generation.

---

## Objectives

- Ensure `enterprise_api/README.md` endpoint tables are accurate (paths + methods).
- Identify and resolve drift between implemented routes, generated OpenAPI, and README.
- Add automated contract tests that fail on future documentation/API drift.
- Confirm which OpenAPI schema is used for SDK generation (public filtered vs internal full) and document it.

---

## Tasks

### 1.0 Audit Ground Truth (OpenAPI)

- [x] 1.1 Confirm which schema is used for SDK generation (likely `enterprise_api/docs/openapi.json` vs `/docs/openapi.json` filtered)
- [x] 1.2 Generate/inspect OpenAPI schema and extract path+method inventory

### 2.0 README Accuracy

- [x] 2.1 Parse endpoint tables in `enterprise_api/README.md`
- [x] 2.2 Compare README endpoints to OpenAPI inventory
- [x] 2.3 Update `enterprise_api/README.md` to eliminate mismatches and omissions

### 3.0 Contract Tests (TDD)

- [x] 3.1 Add/extend OpenAPI contract tests to ensure README endpoint reference matches OpenAPI
- [x] 3.2 Ensure test suite runs without requiring production infrastructure

### 4.0 Verification

- [x] 4.1 `uv run ruff check .`
- [x] 4.2 `uv run pytest`

---

## Success Criteria

- [x] README endpoint reference matches OpenAPI schema for path+method pairs.
- [x] Contract tests fail on drift and pass on current main.
- [x] `uv run pytest`
- [x] `uv run ruff check .`

---

## Completion Notes

- Fixed `enterprise_api` test suite blockers (documents schema mismatch, idempotent licensing test setup).
- Added missing SQL migration for status list tables required by documents endpoints.
- Added contract test: `enterprise_api/tests/test_readme_openapi_contract.py` (now passing against the public OpenAPI schema).
- Implemented Option C (split specs):
  - `sdk/openapi.public.json` (filtered public schema)
  - `sdk/openapi.internal.json` (full internal schema)
- Updated `enterprise_api/README.md` endpoint tables to match the public schema and removed internal-only endpoints from Markdown tables.
