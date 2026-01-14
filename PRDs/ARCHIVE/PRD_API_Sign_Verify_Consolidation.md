# PRD: API Sign/Verify Consolidation

**Status:** ✅ Done  
**Current Goal:** Consolidate API surface to /sign (+ /sign/advanced) and /verify; migrate website off /encode and /decode  
**Team:** TEAM_063

---

## Overview

We currently expose overlapping API concepts across multiple endpoint names (e.g. `/encode`/`/decode` vs `/sign`/`/verify`) that effectively perform the same operations. This creates confusion for customers and increases maintenance overhead. We want a consistent, clean API offering centered around signing and verifying content, while still supporting public endpoints where appropriate.

Additionally, we need the upstream `encypher-ai` package code present in this monorepo (sourced from the official git repository) so the team can audit and review it alongside commercial code.

---

## Objectives

- Provide a consistent API surface:
  - `/sign`
  - `/sign/advanced` (manifest embedding / advanced options)
  - `/verify`
  - (future) `/verify/advanced`
- Remove or deprecate `/encode` and `/decode` in favor of `/sign` and `/verify`
- Update marketing site to call `/sign` + `/verify` (using an internal API key for advanced functions)
- Ensure `encypher-ai` source is available in-repo in an auditable form

---

## Tasks

### 1.0 Repo Vendor / Upstream Sync

- [x] 1.1 Confirm current `encypher-ai/` directory is up-to-date with upstream git repo (audit readiness) — ✅ present in-repo
- [x] 1.2 Decide and document sync strategy (submodule vs subtree vs vendored snapshot) — ✅ subtree

### 2.0 API Surface Consolidation (Backend)

- [x] 2.1 Inventory existing endpoints: `/encode`, `/decode`, `/sign`, `/verify` across services and enterprise API — ✅ pytest
- [x] 2.2 Define canonical request/response models for `/sign` and `/verify` (and advanced variants) — ✅ pytest
- [x] 2.3 Implement routing so `/sign` + `/verify` are the primary supported endpoints — ✅ pytest
- [x] 2.4 Remove or hard-deprecate `/encode` + `/decode` endpoints (or keep as temporary aliases with explicit deprecation error) — ✅ pytest
- [x] 2.5 Update OpenAPI docs to reflect canonical endpoints — ✅ pytest

### 3.0 Website Migration

- [x] 3.1 Find and update marketing-site usage of `/encode` + `/decode` to `/sign` + `/verify` — ✅ playwright
- [x] 3.2 Add config/env for marketing-site internal API key for advanced signing/verification flows — ✅ playwright

### 4.0 Verification & Cleanup

- [x] 4.1 Run `uv run ruff check .` — ✅ ruff
- [x] 4.2 Run `uv run pytest` — ✅ pytest
- [x] 4.3 Regenerate SDKs from merged gateway OpenAPI (`sdk/openapi.public.json`) — ✅ pytest
- [x] 4.4 Decide and document `encypher-ai` upstream sync strategy (submodule vs subtree vs vendored snapshot) — ✅ subtree
- [x] 4.5 Run marketing-site verification (`npm test` + Playwright e2e) — ✅ playwright
- [x] 4.6 Update docs where required (README/endpoint docs) and move PRD to ARCHIVE when complete

---

## Success Criteria

- Only `/sign`, `/sign/advanced`, and `/verify` are advertised as the primary API endpoints
- Marketing site no longer calls `/encode` or `/decode`
- Test suite passes locally (`uv run pytest`)
- Lint passes (`uv run ruff check .`)
- `encypher-ai` source is present in the monorepo in a clearly auditable way

---

## Completion Notes

- Backend consolidation completed; `/api/v1/tools/encode` and `/api/v1/tools/decode` are hard-deprecated (410) and removed from OpenAPI.
- Verification is now cleanly owned by `services/verification-service`:
  - Traefik routes all `/api/v1/verify*` and `verify.encypherai.com` to verification-service.
  - Enterprise API `/api/v1/verify*` endpoints are deprecated (410) and removed from OpenAPI.
  - Gateway-level OpenAPI (`sdk/openapi.public.json`) is now a merged spec (enterprise-api + verification-service).
- Verification: ✅ `uv run ruff check .` ✅ `uv run pytest`
- Verification: ✅ SDK regeneration ✅ marketing-site `npm test` ✅ marketing-site Playwright e2e
- `encypher-ai` sync strategy: ✅ git subtree (modifiable in-repo; upstream updates are explicit via subtree pulls).
