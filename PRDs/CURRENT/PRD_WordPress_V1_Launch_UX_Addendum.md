# PRD Addendum: WordPress Plugin v1 Launch UX Hardening

## Status
Complete

## Current Goal
Harden first-run setup, connection clarity, post-state visibility, and recovery UX so editors can self-serve common failures without support intervention before v1 launch.

## Overview
This addendum builds on the completed v1 UX checklist by closing launch-critical operational UX gaps. It focuses on clear setup progress, visible backend health, actionable remediation paths, and explicit provenance state messaging in admin views. The result is a publish-ready plugin that reduces confusion, avoids silent failure modes, and improves operator confidence.

## Objectives
- Provide first-run setup progress and one-click next actions.
- Surface connection/auth health as a stable status card with meaningful states.
- Make content-level provenance states explicit (unsigned, signed, modified, failed).
- Add clear remediation CTAs from the exact surfaces where issues are seen.
- Preserve current sign/verify behavior while adding UX guardrails.

## Tasks

### 1.0 Addendum Definition
- [x] 1.1 Create launch UX addendum PRD in `PRDs/CURRENT`.
- [x] 1.2 Define launch-critical acceptance criteria and validation gates.

### 2.0 Setup and Connection UX
- [x] 2.1 Add first-run setup checklist panel in Settings with step progress.
- [x] 2.2 Add connection health card with state labels (connected, auth required, disconnected), API URL, org/tier, and last check timestamp.
- [x] 2.3 Add explicit remediation CTAs (Get API key, open settings links, run test connection).

### 3.0 Content State and Recovery UX
- [x] 3.1 Expand content status UI to show provenance states: signed, modified since signing, verification failed, unsigned.
- [x] 3.2 Add row-level recovery guidance and CTA copy in content list.
- [x] 3.3 Preserve existing verify and edit actions.

### 4.0 Automated Validation (TDD)
- [x] 4.1 Add/adjust contract tests for setup checklist, health card labels, and content-state labels.
- [x] 4.2 Task — ✅ pytest (`enterprise_api/tests/test_wordpress_provenance_plugin_contract.py`).

### 5.0 Manual + UI Validation
- [x] 5.1 Confirm Settings page shows setup checklist and health card state changes after test connection.
- [x] 5.2 Confirm Content page shows distinct statuses and guidance for signed/modified/unsigned states.
- [x] 5.3 Confirm existing verify/edit actions still work from content table.
- [x] 5.4 Task — ✅ Puppeteer localhost checks for settings + content pages.

## Success Criteria
- A first-time admin can complete setup from a guided checklist without reading docs.
- Connection/auth state is visible and understandable without opening browser console or logs.
- Content table clearly distinguishes signed vs modified vs unsigned states.
- Recovery actions are discoverable from the same surface where errors/states appear.
- Contract tests and manual/Puppeteer checks pass with evidence.

## Completion Notes
- Implemented launch UX checklist and connection health card in settings page with dynamic state updates and persisted hidden fields.
- Added content-table provenance states and recovery guidance copy:
  - `Unsigned (needs signing)`
  - `Modified since signing`
  - `Verification failed`
- Preserved existing row actions (`Verify`, `Edit`) while adding remediation guidance text.
- Added contract tests for launch readiness checklist/health card presence and expanded content-state guidance.
- Automated validation:
  - ✅ `uv run pytest enterprise_api/tests/test_wordpress_provenance_plugin_contract.py -q` (25 passed)
  - ✅ `uv run ruff check enterprise_api/tests/test_wordpress_provenance_plugin_contract.py`
- Manual + Puppeteer validation:
  - ✅ Settings page (`/wp-admin/admin.php?page=encypher-settings`) shows checklist and health card (`3 of 3 launch steps complete`, `Connected and ready`).
  - ✅ Content page (`/wp-admin/admin.php?page=encypher-content`) shows modified/failed/unsigned labels and guidance copy.
  - ✅ Verify/Edit actions remain available from content table rows.
- Optional polish pass completed:
  - ✅ Added accessibility live regions for connection status and test result surfaces.
  - ✅ Added explanatory helper copy for `BYOK` and `hard binding` settings.
  - ✅ Added content-table fallback guidance when verification link is not yet available.
  - ✅ Contract + lint validation: `uv run pytest enterprise_api/tests/test_wordpress_provenance_plugin_contract.py -q` (27 passed), `uv run ruff check enterprise_api/tests/test_wordpress_provenance_plugin_contract.py`.
