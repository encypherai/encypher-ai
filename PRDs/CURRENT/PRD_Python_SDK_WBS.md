# PRD: Python SDK Production Readiness WBS

**Status:** Draft  
**Owner:** Enterprise SDK Team  
**Last Updated:** November 12, 2025  
**Target Release:** December 15, 2025  
**Related Docs:** `PRD_Production_Readiness_Checklist.md`, `enterprise_api/README.md`, `enterprise_sdk/SDK_WBS.md`

---

## Executive Summary

The Enterprise Python SDK (`enterprise_sdk/`) must reach feature parity with the Enterprise API before we ship the broader production readiness program. Today the API exposes enhanced embeddings, Merkle-tree introspection, public extraction/verification, and SSE streaming endpoints (`enterprise_api/README.md`). The SDK client (`encypher_enterprise/client.py`) exposes only basic signing/verification and Merkle encoders, leaving tier-exclusive functionality inaccessible to customers and integration partners. This WBS turns the gap list from the production readiness checklist (#2) into actionable work packages with clear sequencing, dependencies, and exit criteria so that we can cut a v2.0.0 release with confidence.

---

## Current State Assessment

| Concern | API Reality | SDK Reality | Impact |
|---------|-------------|-------------|--------|
| Enhanced embeddings (`POST /api/v1/enterprise/embeddings/encode-with-embeddings`) | Live endpoint with Merkle metadata and invisible embeddings (`enterprise_api/app/api/v1/endpoints/embeddings.py`) | No `sign_with_embeddings` method or models (`encypher_enterprise/client.py`) | Cannot access marquee enterprise feature |
| Merkle tree retrieval & proofs | API stores trees (`app/services/merkle_service.py`) and tooling expects `GET /enterprise/merkle/tree/{root_id}` | SDK lacks `get_merkle_tree` / proof helpers | WordPress + dashboard integrations blocked |
| Sentence verification | API design includes `extract-and-verify` & Merkle attribution responses (`app/api/v1/public/verify.py`) | SDK only exposes coarse `verify` & `lookup` | No way to validate single sentences or embeddings |
| Streaming SSE | API offers `/stream/sign` and run recovery (`app/routers/streaming.py`) | SDK “streaming” module re-signs chunks locally instead of hitting SSE API | Partners cannot rely on API-backed progress |
| Tests & docs | API contract documented, but SDK tests only cover basic HTTP flows; README lacks enterprise workflows | Hard to guarantee 90% coverage or provide migration plan |

---

## Goals & Success Criteria

- Ship `encypher-enterprise` v2.0.0 with feature parity for enterprise endpoints.
- Maintain ≥90% unit test coverage for new surfaces; add integration smoke tests against staging API.
- Provide complete docs: README API reference, migration guide, examples, changelog.
- Ensure DX parity across sync + async clients and CLI wrappers.

---

## Scope

### In Scope
- New request/response models for embeddings, Merkle trees, and sentence verification.
- Sync/async client methods plus CLI/utility plumbing where applicable.
- Test harness updates, fixtures, contract tests, and coverage gate updates.
- Documentation, changelog, version bump, and PyPI/GitHub release prep.

### Out of Scope
- Core Enterprise API changes (handled by backend squad).
- Non-Python SDKs (tracked in separate PRDs).
- Dashboard UI work beyond updated examples/snippets.

---

## Dependencies

- Stable API contracts from `enterprise_api`: embeddings, Merkle retrieval, public extract-and-verify, streaming SSE.
- UV-managed environment with httpx, pydantic, and pytest.
- Access to staging API keys for integration tests.
- Coordination with docs team for README + QUICK_START updates.

---

## Work Breakdown Structure

### Phase 0 – Contract Validation & Planning (2 days)
- Confirm request/response schemas for embeddings, Merkle trees, extract-and-verify, and streaming runs.
- Capture acceptance tests + fixtures (mock responses + golden payloads).
- Update SDK decision log + align with backend owners on any open API gaps (e.g., `/enterprise/merkle/tree/{root_id}` response shape).
- Deliverable: API contract checklist, fixture catalog, refined stories.

### Phase 1 – Embeddings & Metadata Surfaces (4 days)
- [x] Implement `EncodeWithEmbeddingsRequest/Response`, `EmbeddingOptions`, `LicenseInfo`, etc. in `encypher_enterprise/models.py`.
- [x] Add `sign_with_embeddings` (sync + async) with ergonomic parameter builders.
- [x] Extend CLI/examples to showcase invisible embedding flows.
- [x] Unit tests: request serialization, response parsing, error handling (mock transport).
- [x] Exit criteria: tests passing, README section + example snippet committed.

### Phase 2 – Merkle Retrieval & Sentence Verification (4 days)
- [x] Implement `get_merkle_tree`, `get_merkle_proof`, and helper types once API path confirmed.
- [x] Add `verify_sentence` (likely wrapping `POST /api/v1/public/extract-and-verify` + attribution metadata).
- [x] Provide convenience utilities for highlighting verified segments (reusing `verification.py` structures).
- [x] Add mock + integration tests (flagged to run only when API key available).
- [x] Update docs + repo examples (WordPress plugin + dashboard references).

### Phase 3 – Streaming & Batch Parity (5 days)
- [x] Build SSE client that calls `/api/v1/stream/sign` and exposes async iterator plus backoff/resume via `/api/v1/stream/runs/{run_id}`.
- [x] Align CLI + streaming utilities to use API-backed signing instead of local chunk re-signing.
- [x] Ensure batch helper can optionally proxy to `/api/v1/batch/sign|verify` (idempotency key plumbing).
- [x] Verify rate-limit + retry strategy via integration smoke tests.

### Phase 4 – Quality, Release, and Documentation (3 days)
- Raise test coverage gates, add new Ruff/Black targets, ensure mypy/multi-version test matrix.
- Author migration guide (v1.x → v2.0.0) plus changelog + version bump.
- Publish release candidate to internal index, gather QA sign-off, then push to PyPI and tag GitHub release with binaries.
- Update root docs (`README.md`, `DOCUMENTATION_INDEX.md`, QUICK_START) referencing new capabilities.

---

## Milestones & Timeline

| Milestone | Target Date | Dependencies | Exit Criteria |
|-----------|-------------|--------------|---------------|
| M0 – Contracts locked | Nov 15 | Backend schema clarity | Fixture catalog + API checklist |
| M1 – Embeddings GA | Nov 22 | M0 | `sign_with_embeddings` shipped + docs/tests |
| M2 – Provenance parity | Nov 29 | M1 + Merkle endpoint availability | `get_merkle_tree`, `verify_sentence` ready |
| M3 – Streaming/batch parity | Dec 6 | M2 + SSE stability | Streaming client + CLI wiring |
| M4 – Release & docs | Dec 15 | M3 | v2.0.0 published, docs updated |

---

## Risks & Mitigations

- **API drift** – Backend changes could break SDK models. Mitigation: add schema snapshot tests and coordinate via shared fixtures.
- **SSE complexity** – SSE client reliability may lag if Redis/session service is unstable. Mitigation: implement exponential backoff + resumable runs early in Phase 3.
- **Timeline pressure** – Parallel work on JS SDK + WordPress plugin may compete for reviewers. Mitigation: dedicate rotating reviewer for SDK PRs and align on sprint goals.
- **Docs debt** – Multiple doc touchpoints increase merge conflicts. Mitigation: maintain single-source doc plan (section in README + root index) and update checklists per PR.

---

## Acceptance Checklist

- [ ] Feature parity with enterprise API (embeddings, Merkle retrieval, sentence verification, streaming, batch proxy)
- [ ] 90%+ unit coverage and smoke tests against staging API
- [ ] README + QUICK_START + DOCUMENTATION_INDEX updated
- [ ] Changelog + version bump + signed tag ready
- [ ] Migration guide published
- [ ] All items validated against `PRD_Production_Readiness_Checklist.md` item #2

---

## Open Questions

1. When will `/api/v1/enterprise/merkle/tree/{root_id}` ship? SDK method depends on it.
2. Should sentence verification reuse Merkle attribution or public extract-and-verify responses?
3. Do we expose streaming utilities as high-level async generators or low-level SSE hooks?
4. How do we version CLI vs library features (single version or create subcommands per tier)?

Document owner: Enterprise SDK Team (engineering@encypherai.com). Update weekly or whenever scope changes.
