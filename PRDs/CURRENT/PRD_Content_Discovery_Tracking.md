# PRD: Content Discovery Tracking

## Status: COMPLETE
## Current Goal: All tasks complete

## Overview
Enhance the existing content discovery analytics to give organizations real-time visibility into where their signed content appears across the web. When a Chrome extension user verifies content on a page, the discovery event (URL, domain, signer info) is reported to our analytics service. If the content is found on a domain different from the signer's known domain, the owning organization is alerted. Reporter identity is anonymized (ephemeral session IDs, no PII). Discovery reporting is non-optional to ensure comprehensive coverage.

## Objectives
- Provide organizations with a "where is my content?" dashboard view
- Detect and alert when signed content appears on unexpected domains (copy-paste detection)
- Anonymize the discovering user completely (no browser history, no PII, ephemeral session IDs)
- Make discovery reporting mandatory (not toggleable by end users)
- Store discovery events in a dedicated, efficiently queryable table

## Tasks

### 1.0 Server-Side: Analytics Service
- [x] 1.1 Audit existing discovery infrastructure (schemas, endpoints, DB)
- [x] 1.2 Create dedicated `ContentDiscovery` + `DiscoveryDomainSummary` DB models -- pytest
- [x] 1.3 Create Alembic migration `002_content_discoveries.py` -- pytest
- [x] 1.4 Implement `DiscoveryService` with domain-mismatch detection logic -- pytest (23 tests)
- [x] 1.5 Update `POST /discovery` endpoint to use dedicated table -- pytest
- [x] 1.6 Add `GET /discovery/domains` endpoint -- pytest
- [x] 1.7 Add `GET /discovery/alerts` + `POST /discovery/alerts/{id}/ack` + `GET /discovery/events` endpoints -- pytest
- [x] 1.8 Write tests for discovery service (23 pass) and existing endpoint tests (12 pass)

### 2.0 Chrome Extension: Non-Optional Reporting
- [x] 2.1 Remove `ANALYTICS_CONFIG.enabled` toggle — discovery always reports -- node --test (42 pass)
- [x] 2.2 Ensure `pageUrl` is always included (already done in detector.js) -- node --test
- [x] 2.3 Extension tests pass (42/42) -- node --test

### 4.0 Owned Domain Allowlist (API-configurable source domains)
- [x] 4.1 Add `OwnedDomain` DB model with wildcard pattern support -- pytest
- [x] 4.2 Add Alembic migration `003_owned_domains.py` -- pytest
- [x] 4.3 Add Pydantic schemas for CRUD (OwnedDomainCreate/Update/Item/ListResponse) -- pytest
- [x] 4.4 Add CRUD endpoints: GET/POST/PATCH/DELETE `/discovery/owned-domains` -- pytest
- [x] 4.5 Implement `domain_matches_pattern()` with wildcard support (fnmatch) -- pytest (13 tests)
- [x] 4.6 Update `_is_external_domain()` priority: allowlist → originalDomain → heuristic -- pytest (10 tests)
- [x] 4.7 Owned domain CRUD tests (13 tests) -- pytest
- [x] 4.8 All tests pass: 62 discovery service + 12 schema = 74 total -- pytest

### 3.0 Documentation
- [x] 3.1 Update Chrome extension PRIVACY.md with discovery tracking disclosure
- [x] 3.2 Update summary section in PRIVACY.md

## Success Criteria
- Discovery events stored in dedicated table with proper indexes
- Domain-mismatch detection identifies content on non-signer domains
- Organizations can query where their content was found via API
- Reporter identity is fully anonymized (session-scoped, no PII)
- Discovery reporting cannot be disabled by extension users
- All new code has passing tests

## Completion Notes
- All server-side and extension-side changes implemented and tested
- 62 discovery service tests + 12 schema tests + 42 extension tests = 116 total, all pass
- Privacy policy updated with full disclosure of discovery tracking
- Discovery reporting is non-optional (cannot be disabled by users)
- Reporter identity fully anonymized via ephemeral session IDs
- Orgs can configure owned domains via API with wildcard support (*.example.com)
- Domain-mismatch detection priority: allowlist → originalDomain → heuristic
