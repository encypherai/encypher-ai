# PRD: WordPress Provenance Plugin UI + Verification

**Status:** Complete  
**Current Goal:** Complete menu consolidation + branding, then validate bulk signing + verification end-to-end against Enterprise API  
**Team:** TEAM_054

## Overview
Refine the Encypher WordPress Provenance Plugin admin experience to use a single top-level Encypher menu with exact brand SVG assets, and ensure the signing/verification workflow matches Enterprise API behavior (hybrid embeddings: one C2PA wrapper plus per-sentence embeddings). Validate with contract tests plus an end-to-end WP UI flow.

## Objectives
- Use exact Encypher brand SVG asset for WP admin menu icon and dashboard header.
- Consolidate all plugin admin screens under a single top-level **Encypher** menu.
- Align plugin signing + verification logic with Enterprise API embedding/verification expectations.
- Prevent regression via contract tests.
- Validate end-to-end via UI automation (Puppeteer) for bulk sign + verify.

## Tasks

### 1.0 UI / Menu Consolidation
- [x] 1.1 Replace emoji/placeholder icons with exact Encypher brand SVG
- [x] 1.2 Move Bulk Sign under Encypher menu
- [x] 1.3 Move Coalition under Encypher menu
- [x] 1.4 Remove legacy Settings/Tools menu artifacts

### 2.0 Verification + Embedding Correctness
- [x] 2.1 Align wrapper detection to count only true C2PA wrappers (FEFF + magic)
- [x] 2.2 Ensure verification URL uses `instance_id` when available
- [x] 2.3 Allow re-signing already marked posts (bulk re-mark)

### 3.0 Tests
- [x] 3.1 Contract tests: no legacy menu artifacts
- [x] 3.2 Contract tests: no resign-block guard / no delete-meta bypass
- [x] 3.3 Task — ✅ pytest ✅ ruff (`enterprise_api/tests/test_wordpress_provenance_plugin_contract.py`)

### 4.0 End-to-End Verification (WP UI)
- [x] 4.1 Bring up WP test stack (`docker-compose.test.yml`) and confirm plugin active
- [x] 4.2 Create/publish a post in WP admin
- [x] 4.3 Run Bulk Sign for all posts (re-mark path)
- [x] 4.4 Verify post (UI) and confirm verification result + verification URL
- [x] 4.5 Task — ✅ puppeteer

### 5.0 Finalization
- [x] 5.1 Update docs referencing legacy menu locations (Tools/Settings)
- [x] 5.2 Commit changes — ✅ pytest ✅ ruff

## Success Criteria
- All WP plugin admin pages exist only under top-level **Encypher** menu.
- Encypher brand SVG is used for menu icon and dashboard header.
- Signing works for both first-time signing and re-signing (bulk re-mark).
- Verification works and links use correct `instance_id`.
- ✅ Contract tests pass (`uv run pytest enterprise_api/tests/test_wordpress_provenance_plugin_contract.py`).
- ✅ Full test suite passes (`uv run pytest`).
- ✅ E2E flow validated with Puppeteer.

## Completion Notes
- Updated WordPress provenance plugin documentation to reference current Enterprise API endpoints (`/sign`, `/sign/advanced`, `/verify`, `/public/extract-and-verify`) and removed references to the removed legacy embeddings endpoint.
- Added contract test to prevent doc regressions (`enterprise_api/tests/test_wordpress_provenance_plugin_contract.py`).
- ✅ `uv run ruff check .`
- ✅ `uv run pytest`
