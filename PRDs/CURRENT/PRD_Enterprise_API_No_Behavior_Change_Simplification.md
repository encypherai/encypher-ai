# PRD: Enterprise API No-Behavior-Change Simplification

## Status: COMPLETED
## Current Goal: Completed the no-behavior-change simplification of application composition and authentication wiring while preserving test-visible module surfaces.
## Related Docs: `enterprise_api/app/main.py`, `enterprise_api/app/dependencies.py`, `enterprise_api/app/api/v1/api.py`, `enterprise_api/tests/test_docs_visibility.py`, `enterprise_api/tests/test_transport_protections.py`, `enterprise_api/tests/test_demo_key_gating.py`

---

## Overview

The `enterprise_api` codebase is functionally rich and increasingly security-sensitive, but some of its complexity is structural rather than essential. In particular, `app/main.py` currently combines startup orchestration, middleware registration, probe routes, public/internal docs handling, router registration, and exception handlers in one file. `app/dependencies.py` similarly combines authentication resolution, org-context normalization, demo key fallback, request-state mutation, and permission enforcement.

This PRD defines a no-behavior-change simplification pass that improves maintainability and auditability while preserving:

- request/response behavior
- route paths and registration
- authentication semantics
- public module exports relied upon by tests and downstream code
- existing security controls and defaults

The goal is to reduce cognitive load and change risk without re-architecting the platform.

---

## Problem Statement

### Current Pain Points

| Area | Current Reality | Cost |
|------|-----------------|------|
| Application composition | `app/main.py` is a large, multi-responsibility module | Higher onboarding cost, harder code review, riskier edits |
| Auth dependencies | `app/dependencies.py` mixes policy, fallback logic, compatibility shaping, and repeated permission enforcement | Harder to audit and extend safely |
| Router wiring | Router registration is explicit but scattered in a long block | Surface-area auditing is slower than necessary |
| Docs/probes wiring | Docs filtering, docs assets, health, readiness, metrics, and root routes live alongside unrelated startup code | Cross-cutting concerns are not isolated |
| Permission helpers | Multiple very similar permission dependencies repeat the same enforcement pattern | Repeated logic, small drift risk |

### Why Simplification Matters

- Security-sensitive code is safer when responsibilities are narrow and explicit.
- Large composition files create avoidable merge conflicts and regression risk.
- Preserving stable public module surfaces allows internal cleanup without breaking tests or downstream imports.

---

## Objectives

- Split application composition into focused modules while preserving runtime behavior.
- Keep `app.main` as the stable import surface for `app` and existing helper functions.
- Simplify auth/dependency logic by extracting repeated patterns and reducing inline branching complexity.
- Preserve all route paths, middleware order, startup/shutdown behavior, and exception behavior.
- Validate the refactor with focused regression tests.

---

## Non-Goals

- Changing API contracts or response payloads.
- Replacing FastAPI or restructuring the entire monorepo.
- Removing backward-compatibility fields from org context.
- Changing authentication providers or permission semantics.
- Performing speculative domain refactors in routers or services outside the composition/auth seams.

---

## Requirements

### Functional Requirements

- `app.main` must still export `app`.
- `app.main` must still export `build_cors_settings`, `build_trusted_hosts`, `build_public_openapi`, and `build_public_docs_html`.
- All existing routes, middleware, startup tasks, and exception handlers must behave the same as before.
- `app.dependencies` must still export the currently used public dependency symbols and `DEMO_KEYS`.
- Permission enforcement behavior must remain unchanged.

### Non-Functional Requirements

- Refactor must be no-behavior-change from the perspective of existing tests.
- Composition concerns must be isolated into smaller, focused modules.
- Auth/dependency code must be easier to audit and reason about.
- Changes must be covered by focused regression tests already in the suite or added as needed.

---

## Work Breakdown Structure

### 1.0 Application Composition Simplification

- [x] 1.1 Extract startup/lifespan orchestration from `app/main.py`
  - [x] 1.1.1 Move startup config validation and lifespan workflow into a focused bootstrap module
  - [x] 1.1.2 Preserve startup/shutdown ordering and failure behavior
- [x] 1.2 Extract middleware composition from `app/main.py`
  - [x] 1.2.1 Move trusted-host and CORS helpers into a focused bootstrap module
  - [x] 1.2.2 Preserve middleware ordering and request logging behavior
- [x] 1.3 Extract probe/docs/exception route registration from `app/main.py`
  - [x] 1.3.1 Move health, readiness, metrics, and root routes into focused modules
  - [x] 1.3.2 Move public/internal docs helpers and routes into focused modules
  - [x] 1.3.3 Move exception handler registration into a focused module
- [x] 1.4 Extract router registration into a focused registry/module
  - [x] 1.4.1 Preserve all current route mounts and tags
  - [x] 1.4.2 Keep `app.main` as the stable top-level app entry point

### 2.0 Authentication & Dependency Simplification

- [x] 2.1 Reduce branching complexity in `app/dependencies.py`
  - [x] 2.1.1 Extract helper functions for unauthorized responses, request-state mutation, and org-context resolution
  - [x] 2.1.2 Preserve demo-key, JWT fallback, and key-service behavior
- [x] 2.2 Reduce permission-helper duplication
  - [x] 2.2.1 Introduce a shared permission dependency builder where safe
  - [x] 2.2.2 Preserve exported dependency names and error messages
- [x] 2.3 Preserve compatibility surfaces
  - [x] 2.3.1 Keep test-patched names in `app.dependencies` valid
  - [x] 2.3.2 Keep org-context normalization behavior unchanged

### 3.0 Validation & Rollout

- [x] 3.1 Run focused regression coverage for docs, transport protections, demo-key gating, and auth-dependent flows
- [x] 3.2 Run compile/syntax validation on touched modules
- [x] 3.3 Update PRD status to reflect completed simplification work

---

## Acceptance Criteria

- `app/main.py` is materially smaller and primarily acts as a stable composition surface.
- Composition concerns are split into focused modules under `app/bootstrap/`.
- `app/dependencies.py` is materially easier to follow, with repeated permission logic consolidated.
- Existing tests covering docs visibility, transport protections, demo-key gating, and representative app imports pass.
- No user-visible API behavior changes are introduced.

---

## Risks & Mitigations

- **Risk: import-surface regressions for tests that patch `app.main` or `app.dependencies` directly**
  - Mitigation: preserve exported symbols and keep `app.main` / `app.dependencies` as stable facades.
- **Risk: middleware or route registration order changes behavior subtly**
  - Mitigation: preserve exact registration order and validate with focused tests.
- **Risk: auth fallback behavior changes during cleanup**
  - Mitigation: keep the same branch order and validate with demo-key/JWT tests.

---

## Success Criteria

- The codebase retains full existing functionality.
- Core composition and auth wiring are significantly easier to navigate.
- Future changes to probes, docs, routers, middleware, and auth dependencies can be made with less regression risk.
