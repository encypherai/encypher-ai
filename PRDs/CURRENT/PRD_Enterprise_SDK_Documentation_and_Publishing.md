# PRD: Enterprise SDK Documentation & Publishing Strategy

## Status: IN_PROGRESS
## Current Goal: Consolidate SDKs under /sdk with unified versioning, always in sync with API

---

## Overview

Encypher has **three distinct documentation domains** that need clear separation and cross-referencing:

1. **Open-Source Package** (`encypher-ai`) - AGPL v3, hosted at docs.encypherai.com
2. **Enterprise REST API** - Commercial, interactive docs at api.encypherai.com/docs
3. **Enterprise SDKs** - Commercial, multi-language SDKs (Python/Go/Rust/TypeScript)

This PRD defines how to host, publish, and cross-reference these documentation sites.

---

## Current State

### 1. docs.encypherai.com (Open-Source)
- **Source**: `encypher-ai/` (MkDocs)
- **Content**: `encypher-ai` Python package documentation
- **License**: AGPL v3
- **Hosting**: GitHub Pages via CNAME
- **Audience**: Open-source developers, researchers

### 2. api.encypherai.com/docs (Enterprise API)
- **Source**: `enterprise_api/app/main.py` (FastAPI + Swagger UI)
- **Content**: REST API reference with embedded Swagger UI
- **License**: Proprietary
- **Hosting**: Served by enterprise_api FastAPI app
- **Audience**: Enterprise API consumers

### 3. Enterprise SDKs (Not Yet Published)

#### 3a. `enterprise_sdk/` (DEPRECATED - To Be Merged)
- **Package**: `encypher-enterprise`
- **Status**: Feature-complete, but DUPLICATES sdk/python/
- **Features**: High-level client, CI/CD templates, LangChain/OpenAI integrations
- **Action**: Merge valuable features into sdk/python/, then archive

#### 3b. `sdk/` (CANONICAL - Auto-generated Multi-language SDKs)
- **Languages**: Python, TypeScript, Go, Rust
- **Source**: OpenAPI spec from enterprise_api (always in sync)
- **Status**: Generated, needs metadata cleanup
- **Targets**: PyPI, npm, GitHub (Go), crates.io
- **Versioning**: All SDKs share version from API (e.g., 1.0.0-alpha.1)

---

## Proposed Architecture

### Documentation Domains

| Domain | Content | Audience | Hosting |
|--------|---------|----------|---------|
| `docs.encypherai.com` | Open-source `encypher-ai` package | OSS developers | GitHub Pages |
| `api.encypherai.com/docs` | Enterprise REST API (Swagger UI) | API consumers | FastAPI (self-hosted) |
| `docs.encypherai.com/enterprise/` | Enterprise SDK documentation | Enterprise customers | GitHub Pages (new section) |

### SDK Package Names

| Language | Package Name | Registry | Repository |
|----------|--------------|----------|------------|
| Python | `encypher-enterprise` | PyPI | encypherai/enterprise-sdk |
| TypeScript | `@encypher/sdk` | npm | encypherai/sdk-typescript |
| Go | `github.com/encypherai/sdk-go` | Go Modules | encypherai/sdk-go |
| Rust | `encypher` | crates.io | encypherai/sdk-rust |

---

## Decision: SDK Strategy

### DECISION: Single `sdk/` Directory (Auto-Generated, Always In Sync)

**Rationale**: SDKs MUST stay 100% in sync with the API. Auto-generation from OpenAPI guarantees this.

**Action Plan**:
1. `sdk/` is the SINGLE source of truth for all SDKs
2. All languages (Python/TS/Go/Rust) share the same version number
3. Version derived from API version in `openapi.json`
4. High-level features from `enterprise_sdk/` to be:
   - Merged into `sdk/python/` as optional extensions, OR
   - Published as separate `encypher-enterprise-extras` package that depends on `encypher`
5. Archive `enterprise_sdk/` after migration

**Benefits**:
- ✅ SDKs always match API (no drift)
- ✅ Single version number across all languages
- ✅ Automated regeneration on API changes
- ✅ Consistent developer experience across languages

---

## Tasks (WBS)

### 1.0 SDK Documentation Hosting

- [ ] 1.1 Add `/enterprise/` section to docs.encypherai.com (MkDocs)
  - [ ] 1.1.1 Create `encypher-ai/docs/enterprise/` directory structure
  - [ ] 1.1.2 Add SDK quickstart guide
  - [ ] 1.1.3 Add SDK API reference (auto-generated from docstrings)
  - [ ] 1.1.4 Add integration guides (LangChain, OpenAI, CI/CD)
  - [ ] 1.1.5 Update mkdocs.yml navigation

- [ ] 1.2 Alternative: Create separate sdk.encypherai.com
  - [ ] 1.2.1 Set up new MkDocs site in `enterprise_sdk/docs/`
  - [ ] 1.2.2 Configure GitHub Pages with CNAME
  - [ ] 1.2.3 Add DNS record for sdk.encypherai.com

### 2.0 SDK Publishing

- [ ] 2.1 Python SDK (`encypher-enterprise`)
  - [ ] 2.1.1 Update `enterprise_sdk/pyproject.toml` metadata
  - [ ] 2.1.2 Set up PyPI account and API token
  - [ ] 2.1.3 Create GitHub Actions workflow for publishing
  - [ ] 2.1.4 Publish v1.0.0 to PyPI

- [ ] 2.2 TypeScript SDK (`@encypher/sdk`)
  - [ ] 2.2.1 Update `sdk/typescript/package.json` metadata
  - [ ] 2.2.2 Set up npm organization (@encypher)
  - [ ] 2.2.3 Create GitHub Actions workflow for publishing
  - [ ] 2.2.4 Publish v1.0.0-alpha.1 to npm

- [ ] 2.3 Go SDK
  - [ ] 2.3.1 Create `encypherai/sdk-go` repository
  - [ ] 2.3.2 Set up Go module with proper versioning
  - [ ] 2.3.3 Tag v1.0.0-alpha.1

- [ ] 2.4 Rust SDK
  - [ ] 2.4.1 Update `sdk/rust/Cargo.toml` metadata
  - [ ] 2.4.2 Set up crates.io account
  - [ ] 2.4.3 Publish v1.0.0-alpha.1 to crates.io

### 3.0 Cross-Referencing

- [x] 3.1 Update api.encypherai.com/docs
  - [x] 3.1.1 Add "Client SDKs" intro card linking to SDK docs
  - [x] 3.1.2 Add "Open-Source Package" link to docs.encypherai.com

- [ ] 3.2 Update docs.encypherai.com
  - [ ] 3.2.1 Add "Enterprise API" link in navigation
  - [ ] 3.2.2 Add "Enterprise SDKs" section in navigation
  - [ ] 3.2.3 Update homepage to show product ecosystem

- [ ] 3.3 Update marketing site (encypherai.com)
  - [ ] 3.3.1 Update footer "Documentation" link strategy
  - [ ] 3.3.2 Update pricing page API docs link to api.encypherai.com/docs
  - [ ] 3.3.3 Add SDK download links on relevant pages

- [ ] 3.4 Update dashboard (dashboard.encypherai.com)
  - [ ] 3.4.1 Update "Documentation" links to be contextual
  - [ ] 3.4.2 Add SDK quickstart in onboarding flow
  - [ ] 3.4.3 Update support page resource links

### 4.0 Cleanup

- [x] 4.1 Consolidate SDK directories
  - [x] 4.1.1 DECISION: `sdk/` is canonical, `enterprise_sdk/` to be archived
  - [x] 4.1.2 Update sdk/ README files with clear purpose statements
  - [x] 4.1.3 Remove placeholder GIT_USER_ID/GIT_REPO_ID from generated SDKs
  - [x] 4.1.4 Update sdk/ package metadata (author, URLs, license)
  - [ ] 4.1.5 Move enterprise_sdk/ to archive/ or delete after extracting reusable code

- [ ] 4.2 Update internal documentation
  - [ ] 4.2.1 Update root README.md with SDK information
  - [ ] 4.2.2 Update DOCUMENTATION_INDEX.md

---

## Success Criteria

1. ✅ Enterprise SDK published to PyPI as `encypher-enterprise`
2. ✅ SDK documentation accessible at docs.encypherai.com/enterprise/
3. ✅ api.encypherai.com/docs links to SDK documentation
4. ✅ Marketing/dashboard sites link to appropriate docs contextually
5. ✅ Clear separation between open-source and enterprise documentation

---

## Open Questions

1. **SDK docs hosting**: Should enterprise SDK docs live under docs.encypherai.com/enterprise/ or a separate sdk.encypherai.com?
2. **SDK consolidation**: Should `enterprise_sdk/` (hand-crafted) and `sdk/` (auto-generated) be merged or kept separate?
3. **Multi-language priority**: Which languages should be published first after Python?

---

## Appendix: Current Link Audit

### Files referencing docs.encypherai.com (45+ files)
- Marketing site footer, pricing page
- Dashboard navigation, support page, onboarding
- Enterprise SDK README, API README
- Various internal docs

### Recommended Link Updates

| Context | Current | Proposed |
|---------|---------|----------|
| Generic "Documentation" | docs.encypherai.com | docs.encypherai.com (keep) |
| "API Documentation" | docs.encypherai.com | api.encypherai.com/docs |
| "SDK Documentation" | docs.encypherai.com/sdk | docs.encypherai.com/enterprise/ |
| "Python Package" | docs.encypherai.com | docs.encypherai.com (keep) |
