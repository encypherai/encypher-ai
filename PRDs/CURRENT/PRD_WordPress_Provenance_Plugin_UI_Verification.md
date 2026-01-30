
# PRD: WordPress Provenance Plugin CMS Workflow Audit

**Status:** In Progress  
**Current Goal:** Audit WordPress plugin signing and verification flows against Enterprise API `/sign`, `/sign/advanced`, `/verify`, `/verify/advanced` and document compatibility gaps.
**Team:** TEAM_136

## Overview
Review the WordPress provenance plugin's CMS workflows for signing and verification to ensure compatibility with the updated Enterprise API. Focus on request/response schema alignment, fallback behaviors, and local-dev routing so both starter and paid tiers validate content correctly.

## Objectives
- Validate WordPress plugin request payloads match current Enterprise API schemas.
- Confirm verification workflows align with verification-service / enterprise-api routing and response shapes.
- Identify gaps that could break signing/verification, especially in local Docker setup.
- Document fixes and test plan for any required remediation.

## Tasks
### 1.0 Signing Workflow Audit
- [x] 1.1 Review `/sign` payload/response mapping (starter tier)
- [x] 1.2 Review `/sign/advanced` payload/response mapping (pro+ tiers)
- [x] 1.3 Verify provenance chain handling (`previous_instance_id`, instance storage)
- [x] 1.4 Validate auto-signing on publish/update and content stripping behavior

### 2.0 Verification Workflow Audit
- [x] 2.1 Review `/verify` request/response mapping (public)
- [x] 2.2 Review `/verify/advanced` request/response mapping (auth)
- [x] 2.3 Validate fallback/caching logic and status updates
- [x] 2.4 Validate frontend verification badge/modal integration

### 3.0 Environment & Routing Checks
- [x] 3.1 Confirm local Docker routing supports `/verify` for starter tier
- [x] 3.2 Confirm production gateway routing for `/verify` + `/verify/advanced`

### 4.0 Remediation Plan
- [ ] 4.1 Route starter-tier verification to verification-service or API gateway in local docker compose
- [ ] 4.2 Align legacy verification fields (`append_verification_badge`) with normalized response or remove unused method
- [ ] 4.3 Decide whether to surface `metadata_format` + `add_hard_binding` settings in sign payload
- [ ] 4.4 Add tests/manual verification steps for fixes
- [ ] 4.5 Update plugin documentation and team log

## Success Criteria
- WordPress plugin requests match Enterprise API schemas for signing and verification.
- Verification flows return expected normalized fields (`valid`, `tampered`, manifest metadata).
- Local Docker setup supports starter-tier verification without 410 errors.
- Gaps and fixes are documented with clear test steps.

## Completion Notes
- **Findings (draft):**
  - WordPress `handle_verify_request` normalizes `success/data` responses correctly, but local Docker points `api_base_url` to the enterprise-api container (port 8001) where `/verify` is deprecated (410). Starter-tier verification will fail locally unless routed through the verification-service or API gateway.
  - The front-end badge modal reads `data.valid` + `data.metadata` (normalized in REST handler), while `Verification::append_verification_badge` still expects legacy fields (`is_valid`, `signature_timestamp`, `organization_name`). This method is currently disabled but needs alignment if re-enabled.
  - Signing payloads match current `/sign` + `/sign/advanced` schemas, but WordPress settings `metadata_format` and `add_hard_binding` are unused in the current API request shape.
  - `previous_instance_id` and instance_id storage align with advanced signing flow (instance ID is extracted from response metadata).
  - Verification fallback to `/verify` on auth failures is correct for pro+ tiers.
