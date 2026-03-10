# PRD: D2 Documentation Adoption

**Status:** ✅ Complete (source-first rollout)
**Team:** TEAM_252
**Current Goal:** Establish D2 as the repo-standard diagram source format and land the first high-value workflow and architecture diagrams across core READMEs and integration docs.

## Overview
This initiative adds a maintainable, source-controlled diagram layer to the repository so workflows, system boundaries, and integrations are easier to understand than with prose or ASCII diagrams alone. The rollout standardizes where D2 source files live, how they are rendered, which READMEs must reference them, and how motion should be used without sacrificing maintainability.

## Objectives
- Standardize D2 as the canonical source format for architecture and workflow diagrams.
- Add diagram source files for the highest-value repo, API, extension, SDK, services, and WordPress integration flows.
- Wire those diagrams into the most important README and docs entry points.
- Provide a repo-native render/check workflow that works even before D2 is installed locally.
- Define style, animation, and maintenance rules so diagrams stay useful and visually consistent.

## Tasks

### 1.0 Standards and Source of Truth
- [x] 1.1 Create a canonical D2 documentation PRD in `PRDs/CURRENT/`.
- [x] 1.2 Define repo-wide D2 directory structure and naming conventions.
- [x] 1.3 Define rendering rules, output expectations, and animation guidance.
- [x] 1.4 Define README integration rules for diagrams near the sections they explain.

### 2.0 Repo-Wide Diagram Infrastructure
- [x] 2.1 Create `docs/diagrams/README.md` with structure, style rules, and maintenance guidance.
- [x] 2.2 Add a render/check script for D2 source files.
- [x] 2.3 Add core architecture diagrams for repo-wide system context and backend boundaries.
- [x] 2.4 Add cross-product workflow diagrams for API sign/verify, SDK generation, and auth handoff.

### 3.0 Integration and README Rollout
- [x] 3.1 Update root `README.md` to reference D2-backed system and architecture diagrams.
- [x] 3.2 Update `enterprise_api/README.md` to reference sign/verify and dependency flow diagrams.
- [x] 3.3 Update `services/README.md` to replace or augment ASCII topology with D2 references.
- [x] 3.4 Update `sdk/README.md` to reference the SDK generation pipeline diagram.
- [x] 3.5 Update `integrations/chrome-extension/README.md` to reference signing and verification workflow diagrams.
- [x] 3.6 Update `integrations/wordpress-provenance-plugin/README.md` to reference publish, onboarding, and WordPress/ai workflow diagrams.

### 4.0 Content Accuracy Cleanup
- [x] 4.1 Align the Chrome extension README with current shortcut and signing defaults.
- [x] 4.2 Ensure diagram references do not duplicate SSOT tier definitions.
- [x] 4.3 Keep integration docs focused on flow ownership, dependencies, and failure boundaries.

### 5.0 Validation and Handoff
- [x] 5.1 Run D2 source layout validation via the repo render/check script. — ✅ `bash scripts/render-d2-diagrams.sh --check`
- [x] 5.2 Re-read all touched READMEs/docs for broken links and consistency.
- [x] 5.3 Update this PRD with completion notes and validation evidence.

## Success Criteria
- The repo contains a single obvious home for D2 standards and shared diagrams.
- At least the root README, Enterprise API README, services README, SDK README, Chrome extension README, and WordPress plugin README reference D2 artifacts relevant to their sections.
- The first diagram set covers architecture, signing, verification, onboarding, SDK generation, and integration flows.
- A contributor can discover diagram sources, validate the layout, and render outputs using repo-native instructions.
- Animation guidance is documented as optional and purpose-driven, not the default requirement.

## Completion Notes
- Added `docs/diagrams/README.md` as the canonical D2 standards and maintenance guide.
- Added 6 repo-wide D2 source files covering system context, microservices topology, enterprise-vs-core architecture, Enterprise API sign/verify, dashboard-extension auth handoff, and SDK generation.
- Added 5 integration-local D2 source files covering Chrome extension verification/signing and WordPress plugin publish, onboarding, and WordPress/ai flows.
- Wired the new D2 source set into the root README, Enterprise API README, services README, SDK README, Chrome extension README, and WordPress plugin README.
- Corrected the Chrome extension README to match the current shortcut (`Alt+Shift+S`), default embedding mode (`micro_no_embed_c2pa`), default segmentation (`document`), and build flow (`npm run build`).
- Validation completed with `bash scripts/render-d2-diagrams.sh --check`, which discovered 11 D2 source files successfully.
- Follow-up: render `.svg` outputs once the local `d2` CLI is installed; the repo now has a render/check script and source layout ready for that step.
