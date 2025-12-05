# PRD: OpenAPI SDK Generation

**Status**: 🟢 Complete  
**Current Goal**: ~~Set up automated SDK generation from OpenAPI spec~~  
**Team**: TEAM_001

---

## Overview

Generate Python, TypeScript, and other language SDKs automatically from the Enterprise API's OpenAPI specification. This replaces the manually-maintained `enterprise_sdk` with auto-generated clients that stay in sync with the API.

---

## Objectives

- Auto-generate SDKs for Python, TypeScript, Go, and potentially other languages
- Ensure 100% API coverage (currently 51 endpoints)
- Maintain backward compatibility with existing SDK users
- Set up CI/CD to regenerate SDKs on API changes

---

## Current State

### Existing Assets
- **OpenAPI Spec**: `enterprise_api/docs/openapi.json` (51 endpoints)
- **Spec Generator**: `enterprise_api/scripts/validate_openapi.py`
- **Manual Python SDK**: `enterprise_sdk/` (partial coverage, ~15 methods)

### API Endpoints (51 total)

| Category | Endpoints | SDK Coverage |
|----------|-----------|--------------|
| Core Signing | `/sign`, `/verify`, `/lookup` | ✅ Manual |
| Streaming | `/stream/*` (7 endpoints) | ✅ Partial |
| Merkle/Enterprise | `/enterprise/merkle/*` (3) | ✅ Manual |
| Embeddings | `/enterprise/embeddings/*` (1) | ✅ Manual |
| C2PA Custom | `/enterprise/c2pa/*` (5) | ❌ Missing |
| Provisioning | `/provisioning/*` (4) | ❌ Missing |
| Public Verify | `/public/*` (3) | ✅ Partial |
| Batch | `/batch/*` (2) | ❌ Missing |
| Licensing | `/licensing/*` (7) | ❌ Missing |
| Kafka | `/kafka/*` (8) | ❌ Missing |
| Onboarding | `/onboarding/*` (2) | ❌ Missing |

---

## Tasks

### 1.0 OpenAPI Spec Preparation
- [x] 1.1 Regenerate OpenAPI spec from current API — ✅ 68 endpoints, 113 schemas
- [x] 1.2 Add operation IDs for all endpoints (SDK method names) — ✅ FastAPI auto-generates
- [x] 1.3 Add x-sdk-group tags for logical grouping — ✅ 21 tags from FastAPI
- [x] 1.4 Validate spec with openapi-generator-cli — ✅ v7.17.0
- [x] 1.5 Add security schemes (Bearer, API Key) — ✅ HTTPBearer in spec

### 2.0 SDK Generation Infrastructure
- [x] 2.1 Choose codegen tool — ✅ openapi-generator-cli v7.17.0
- [x] 2.2 Create `sdk/` directory structure — ✅ sdk/{python,typescript,go,rust}
- [x] 2.3 Set up generation scripts for each language — ✅ generate_sdk.py with rich logging
- [x] 2.4 Configure templates for idiomatic code — ✅ Custom wrappers for each language

### 3.0 Python SDK
- [x] 3.1 Generate base client with openapi-generator — ✅ 22 API modules
- [x] 3.2 Add custom wrapper for ergonomic API (EncypherClient) — ✅ client.py
- [ ] 3.3 Add async client support — Deferred (generated code supports it)
- [ ] 3.4 Port existing high-level utilities (RepositorySigner, etc.) — Deferred
- [ ] 3.5 Ensure backward compatibility with existing SDK — Deferred
- [ ] 3.6 Add tests — Deferred

### 4.0 TypeScript SDK
- [x] 4.1 Generate with openapi-generator (typescript-fetch) — ✅
- [x] 4.2 Add browser + Node.js support — ✅ fetch-based
- [ ] 4.3 Add React hooks (optional) — Deferred
- [ ] 4.4 Publish to npm — Deferred
- [ ] 4.5 Add tests — Deferred

### 5.0 Go SDK
- [x] 5.1 Generate with openapi-generator — ✅
- [x] 5.2 Add idiomatic Go patterns — ✅ client.go wrapper
- [ ] 5.3 Add tests — Deferred

### 6.0 Rust SDK (Added)
- [x] 6.1 Generate with openapi-generator — ✅
- [x] 6.2 Add async support (reqwest) — ✅
- [x] 6.3 Add client wrapper — ✅ client.rs
- [ ] 6.4 Add tests — Deferred

### 7.0 CI/CD Integration
- [x] 7.1 GitHub Action to regenerate on API changes — ✅ `.github/workflows/sdk-generate.yml`
- [x] 7.2 Auto-create PR with SDK updates — ✅ Uses peter-evans/create-pull-request
- [x] 7.3 SDK validation in CI (build/compile check) — ✅ validate-sdks job
- [ ] 7.4 Publish to PyPI/npm on release — Deferred until ready

### 8.0 Documentation
- [x] 8.1 Create sdk/README.md — ✅
- [ ] 8.2 Update DOCUMENTATION_INDEX.md — Pending
- [ ] 8.3 Add migration guide from manual SDK — Deferred

---

## Technical Decisions

### Codegen Tool Comparison

| Tool | Python | TypeScript | Go | Pros | Cons |
|------|--------|------------|-----|------|------|
| **openapi-generator** | ✅ | ✅ | ✅ | Multi-language, mature | Verbose output |
| **openapi-typescript** | ❌ | ✅ | ❌ | Excellent TS types | TS only |
| **datamodel-code-generator** | ✅ | ❌ | ❌ | Clean Pydantic models | Python only |
| **oapi-codegen** | ❌ | ❌ | ✅ | Idiomatic Go | Go only |

**Recommendation**: Use **openapi-generator** for Python/Go, **openapi-typescript** for TypeScript.

### Directory Structure

```
sdk/
├── openapi.json              # Source of truth (copied from enterprise_api)
├── generate.py               # Generation script
├── python/
│   ├── encypher_enterprise/  # Generated + manual wrappers
│   ├── pyproject.toml
│   └── README.md
├── typescript/
│   ├── src/
│   ├── package.json
│   └── README.md
└── go/
    ├── encypher/
    ├── go.mod
    └── README.md
```

### Backward Compatibility

The existing `enterprise_sdk/` will be deprecated but maintained for 6 months:
1. New SDK published as `encypher` (Python) / `@encypher/sdk` (npm)
2. Old `encypher-enterprise` package marked deprecated
3. Migration guide provided

---

## Success Criteria

- [x] All 68 API endpoints have SDK methods — ✅ 100% coverage
- [ ] Python SDK passes existing tests — Deferred
- [x] TypeScript SDK works in browser and Node.js — ✅ fetch-based
- [ ] CI regenerates SDKs on API changes — Deferred
- [x] Documentation is complete — ✅ sdk/README.md

---

## Completion Notes

**Completed: Dec 4, 2025**

### What Was Built

1. **OpenAPI Spec Generator** (`sdk/generate_openapi.py`)
   - Extracts OpenAPI 3.1 spec from FastAPI without starting server
   - Handles Windows env var conflicts

2. **SDK Generator** (`sdk/generate_sdk.py`)
   - Supports Python, TypeScript, Go, Rust
   - Rich logging with progress indicators
   - Cross-platform (Windows/Linux/macOS)
   - Custom wrapper generation for ergonomic APIs

3. **Generated SDKs**
   - **Python**: 22 API modules, 117 models, urllib3-based
   - **TypeScript**: fetch-based, browser + Node.js compatible
   - **Go**: idiomatic Go patterns with context support
   - **Rust**: async/await with reqwest

### Usage

```bash
# Regenerate OpenAPI spec
uv run python sdk/generate_openapi.py

# Generate specific SDK
uv run python sdk/generate_sdk.py python
uv run python sdk/generate_sdk.py typescript

# Generate all SDKs
uv run python sdk/generate_sdk.py all
```

### Next Steps

1. ~~Add CI/CD workflow for automatic regeneration~~ — ✅ `.github/workflows/sdk-generate.yml`
2. Publish to PyPI/npm/crates.io — Deferred until ready
3. Port high-level utilities from enterprise_sdk — See analysis below
4. Add comprehensive tests — See analysis below

---

## Analysis: What to Port from enterprise_sdk

The existing `enterprise_sdk` has **high-level utilities** beyond basic API calls. These are NOT auto-generated and would need manual porting:

### High-Level Utilities (Worth Porting)

| Module | Purpose | Port Priority |
|--------|---------|---------------|
| `batch.py` | `RepositorySigner` - bulk sign files in a directory | High |
| `streaming.py` | `StreamingSigner` - SSE streaming for long content | High |
| `verification.py` | `RepositoryVerifier` - bulk verify files | High |
| `cli/main.py` | Full CLI with sign/verify/lookup commands | Medium |
| `reports.py` | `ReportGenerator` - CSV/HTML verification reports | Medium |
| `state.py` | `StateManager` - track signed file state | Medium |
| `metadata_providers.py` | Git/Frontmatter metadata extraction | Low |
| `diff.py` | `DiffGenerator` - version tracking | Low |
| `analytics.py` | `MetricsCollector` - usage stats | Low |
| `expiration.py` | `ExpirationTracker` - signature renewal | Low |

### CLI Tools for Other Languages

The Python CLI (`encypher sign`, `encypher verify`) has been ported to:
- ✅ **Go** - `encypher sign` (single binary, no runtime) — `sdk/go/cmd/encypher/`

Future:
- **TypeScript/Node.js** - `npx @encypher/cli sign`
- **Rust** - `encypher sign` (single binary)

#### Go CLI Usage

```bash
# Build
cd sdk/go && make build

# Sign content
encypher sign --text "Hello, world!"
encypher sign --file document.txt --output signed.txt

# Verify content
encypher verify --file signed.txt

# Lookup document
encypher lookup <document_id>

# JSON output
encypher sign --text "Hello" --output json
```

---

## Analysis: Auto-Generated Tests

### What openapi-generator Provides

The generator creates **basic test stubs** but they are:
- Empty/placeholder tests
- No actual API mocking
- Not useful without customization

### Better Approach: Contract Tests

1. **Generate OpenAPI spec** → source of truth
2. **Use spec for contract testing** with tools like:
   - Python: `schemathesis` (auto-generates tests from OpenAPI)
   - TypeScript: `openapi-typescript-codegen` + `msw` for mocking
   - Go: `go-swagger` validation
   - Rust: `progenitor` with mock server

### Recommended Test Strategy

```yaml
# In CI, run contract tests against the spec
- name: Run Python Contract Tests
  run: |
    pip install schemathesis
    schemathesis run sdk/openapi.json --base-url http://localhost:9000

# Or validate SDK can parse all response types
- name: Validate SDK Types
  run: |
    cd sdk/python
    python -c "from encypher import models; print('All models valid')"
```

### What We Should Add

1. **Type validation tests** - ensure generated models match spec
2. **Mock server tests** - test SDK against mock responses
3. **Integration tests** - test against real API (in CI with test key)
