# PRD — EncypherAI C2PA Context Config Release 3.0.3

## Status
In Progress

## Current Goal
Release `encypher-ai==3.0.3` with configurable C2PA `@context` emission and verification allowlisting so production services can control schema compatibility via environment variables.

## Overview
Production verification failures were caused by strict C2PA `@context` validation (v2.2 expected vs v2.3 emitted). This release makes the emitted `@context` and the verifier’s accepted `@context` list configurable via env vars, while preserving safe defaults.

## Objectives
- Provide env-driven configuration for emitted C2PA `@context`.
- Provide env-driven configuration for verifier accepted C2PA `@context` values.
- Publish `encypher-ai==3.0.3` and update production microservices to consume the published artifact.

## Tasks
- [x] 1.0 Add env-configurable C2PA context settings in `encypher-ai` (emit + verify)
  - [x] 1.1 Tests: settings parsing for `ENCYPHER_C2PA_CONTEXT_URL` and `ENCYPHER_C2PA_ACCEPTED_CONTEXTS`
  - [x] 1.2 Tests: verifier respects configured allowlist (accept/reject)
  - [x] 1.3 Impl: signer uses configured context URL
  - [x] 1.4 Impl: verifier uses configured accepted contexts
- [x] 2.0 Bump `encypher-ai` version to `3.0.3` and update changelog
  - [x] 2.1 Task — ✅ pytest ✅ ruff
- [ ] 3.0 Update production microservices to depend on published `encypher-ai==3.0.3`
  - [ ] 3.1 Remove any monorepo path overrides from service `pyproject.toml`
  - [ ] 3.2 Task — ✅ pytest

## Success Criteria
- Signing emits the configured `@context` URL.
- Verification accepts configured `@context` values and rejects non-allowed contexts.
- `encypher-ai` test suite passes (`uv run pytest`) and lint passes (`uv run ruff check .`).
- Microservices install `encypher-ai==3.0.3` from the package registry in production.

## Completion Notes

- [x] 2.1 Task — ✅ pytest ✅ ruff
