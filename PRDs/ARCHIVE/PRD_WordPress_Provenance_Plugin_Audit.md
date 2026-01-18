## Status
Completed

## Current Goal
Audit and align the WordPress provenance plugin workflows with Enterprise API sign/verify (standard + advanced) endpoints, including verification coverage and testing guidance.

## Overview
This PRD captures the audit and remediation work needed to ensure the WordPress provenance plugin integrates the Enterprise API signing and verification endpoints correctly for all tiers. It focuses on sign/sign-advanced usage, verify/verify-advanced usage where tier-appropriate, and validation via automated and dockerized workflows.

## Objectives
- Confirm current plugin workflows and docs match the Enterprise API sign/verify surface area.
- Add or adjust verification flows to include verify/advanced where tier-appropriate.
- Add automated contract coverage and document dockerized verification steps.
- Produce an audit summary with evidence of tests and manual verification.

## Tasks
- [x] 1.0 Audit existing WordPress plugin endpoint usage
  - [x] 1.1 Review plugin sign/sign-advanced integration paths
  - [x] 1.2 Review plugin verify/verify-advanced integration paths
  - [x] 1.3 Cross-check documentation and docker compose instructions
- [x] 2.0 Implement missing endpoint integration
  - [x] 2.1 Add verify/advanced workflow for eligible tiers (fallback to verify)
  - [x] 2.2 Store/report advanced verification metadata where needed
  - [x] 2.3 Update documentation to reflect advanced verification usage
- [x] 3.0 Verification & testing
  - [x] 3.1 Add/adjust contract tests for sign/verify endpoint usage
  - [x] 3.2 Run pytest for WordPress plugin contract coverage
  - [x] 3.3 (If needed) Run dockerized WordPress + Enterprise API flow and record results

## Success Criteria
- WordPress plugin uses `/sign`, `/sign/advanced`, `/verify`, and `/verify/advanced` appropriately per tier.
- Contract tests cover endpoint usage and pass (`uv run pytest enterprise_api/tests/test_wordpress_provenance_plugin_contract.py`).
- Documentation and local testing guidance reflect the verified endpoint workflows.

## Completion Notes
- Dockerized WordPress + Enterprise API flow validated on 2026-01-17.
- WordPress installed and plugin configured with `api_base_url=http://enterprise-api:8000/api/v1`, `api_key=demo-local-key`, tier=professional.
- Created post ID 4 and verified via REST with timeout-protected curl:
  - `curl --connect-timeout 5 --max-time 20 -sS -i -X POST "http://localhost:8080/index.php?rest_route=/encypher-provenance/v1/verify" -H "Content-Type: application/json" -d '{"post_id":4}'`
  - Response: `verification_mode=advanced`, `valid=true`, `correlation_id=req-efc6b83800f147e1a378dd992d747127`.
