# Encypher Enterprise SDK - Work Breakdown Structure

Updated: 2025-10-27
Owner: Enterprise SDK squad

## Purpose
- Deliver a production-ready Python SDK that wraps the Enterprise API (`enterprise_api`) while reusing signing primitives from the core package (`encypher-ai/encypher`).
- Mirror the integration patterns used in `encypher-ai/docs/package/integration/anthropic.md` so third-party developers can adopt the SDK with minimal friction.
- Keep Enterprise API documentation aligned so customers can discover the SDK from `enterprise_api/README.md` and `enterprise_api/docs/API.md`.

## Reference Assets
- Core signing primitives: `encypher-ai/encypher/core`
- Existing API contract: `enterprise_api/docs/API.md`
- Integration examples (style reference): `encypher-ai/docs/package/integration/`
- Current SDK code: `enterprise_sdk/encypher_enterprise/`

## Phase Summary
| Phase | Focus | Status | Key Refs |
|-------|-------|--------|----------|
| 1 | Project foundation & packaging | Done | `enterprise_sdk/pyproject.toml`, `encypher_enterprise/config.py` |
| 2 | HTTP clients & models | Done | `encypher_enterprise/client.py`, `encypher_enterprise/async_client.py`, `encypher_enterprise/models.py` |
| 3 | Streaming pipeline | Done | `encypher_enterprise/streaming.py`, `examples/streaming_chat.py` |
| 4 | Framework integrations | Done | `encypher_enterprise/integrations/*`, `examples/` |
| 5 | CLI tooling | Done | `encypher_enterprise/cli/main.py` |
| 6 | QA, testing, and release readiness | In Progress | (tests package to add), `.pre-commit-config.yaml` |
| 7 | Documentation & launch readiness | In Progress | This WBS, SDK README, Enterprise API docs |

Status legend: Done | In Progress | Todo | Blocked

## Detailed Tasks

### Phase 1 - Foundation (Done)
- [Done] Scaffold SDK package and uv project metadata (`enterprise_sdk/pyproject.toml`).
- [Done] Establish configuration helpers for API URLs, retries, and headers (`encypher_enterprise/config.py`).
- [Done] Sync licensing and versioning with commercial policy (`enterprise_sdk/README.md`, `LICENSE`).

### Phase 2 - HTTP Clients (Done)
- [Done] Build synchronous client covering sign, verify, lookup, stats (`encypher_enterprise/client.py`).
- [Done] Add asynchronous parity client with shared error handling (`encypher_enterprise/async_client.py`).
- [Done] Normalise response parsing through Pydantic models (`encypher_enterprise/models.py`).

### Phase 3 - Streaming (Done)
- [Done] Implement buffered streaming signer utilities (`encypher_enterprise/streaming.py`).
- [Done] Document streaming usage in examples (`enterprise_sdk/examples/streaming_chat.py`).
- [Done] Verify compatibility with base encypher streaming helpers (`encypher-ai/encypher/streaming`).

### Phase 4 - Framework Integrations (Done)
- [Done] Implement LangChain callback/tool that signs outputs before returning (`encypher_enterprise/integrations/langchain.py`).
- [Done] Provide OpenAI client wrapper that decorates streamed and non-streamed responses (`encypher_enterprise/integrations/openai.py`).
- [Done] Add LiteLLM provider adapter mirroring Anthropic integration style (`encypher_enterprise/integrations/litellm.py`).
- [Done] Ship runnable examples for each integration (`enterprise_sdk/examples/`).

### Phase 5 - CLI Tooling (Done)
- [Done] Build Typer or Click CLI that supports sign/verify/lookup/stats flows (`encypher_enterprise/cli/main.py`).
- [Done] Support API key discovery via environment variables and `.env` files for parity with Enterprise API onboarding.
- [Done] Document CLI usage in SDK README and Enterprise API docs.

### Phase 6 - Quality & Release (In Progress)
- [Done] Stand up `enterprise_sdk/tests/` with unit coverage for client, async, and streaming flows.
- [Done] Add integration smoke tests that target a local Enterprise API fixture (reuse `enterprise_api/tests` utilities).
- [In Progress] Configure linting, typing, and coverage thresholds in CI (re-use repo `.pre-commit-config.yaml` patterns).
- [Blocked] Publish preview build to private package index (pending commercial approval).

### Phase 7 - Documentation & Launch (In Progress)
- [Done] Replace legacy WBS with actionable breakdown aligned to current code base (this document).
- [Done] Refresh `enterprise_sdk/README.md` to remove non-ASCII bullets and highlight integrations.
- [Done] Surface SDK availability in `enterprise_api/README.md` (Quick Start + discovery links).
- [Done] Highlight SDK usage in `enterprise_api/docs/API.md` (authentication and getting-started sections).
- [Todo] Create dedicated SDK section within the public docs site (link from `encypher-ai/docs/index.md`).

## Cross-Team Dependencies
- **Enterprise API:** Ensure `/api/v1/sign` streaming contract stays compatible with SDK stream signer. Owners: API squad.
- **Core Package (`encypher-ai`):** Coordinate version bumps when signing primitives change.
- **Documentation:** Align shared docs team on release notes, migration steps, and site navigation.

## Milestones
- **M1 - Developer Preview (Nov 2025):** Core clients, streaming, README refresh, minimal tests. Requires Phase 1-3 completion plus initial docs.
- **M2 - Integration Pack (Dec 2025):** Framework adapters, CLI, published examples. Requires Phase 4-5 completion.
- **M3 - GA Launch (Jan 2026):** Full test suite, CI, documentation site updates, published package. Requires Phase 6-7 closure and commercial approval.

## Risks & Mitigations
- **Risk:** Enterprise API schema changes could break SDK models.  
  **Mitigation:** Track `enterprise_api/docs/API.md` updates and add contract tests once tests/ is in place.
- **Risk:** Streaming performance regressions on large payloads.  
  **Mitigation:** Benchmark signer behaviour against Anthropic/OpenAI streaming mocks before GA.
- **Risk:** Configuration drift between SDK and API onboarding docs.  
  **Mitigation:** Centralise environment variable names in `encypher_enterprise/config.py` and cross-link from docs.

## Action Items (Next Sprint)
1. Ensure integration smoke tests run in CI by provisioning the Enterprise API fixture and required env vars.
2. Wire lint/type-check enforcement into CI for the SDK package.
3. Coordinate public documentation publishing for the SDK navigation entry.

---
Document maintained in `enterprise_sdk/SDK_WBS.md`. Update statuses at the start of each sprint or when major deliverables land.
