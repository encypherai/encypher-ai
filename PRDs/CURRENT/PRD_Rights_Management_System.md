# PRD: Rights Management System

**Status**: IN PROGRESS
**Team**: TEAM_215
**Spec**: `docs/prds/Encypher_Rights_Management_Architecture.md`
**Branch**: `feature/rights-management-system`

## Current Goal

Implement the complete publisher-controlled rights management system as specified in the Encypher Rights Management Architecture Specification. This extends the existing enterprise_api and coalition-service microservices architecture to provide cryptographically-bound licensing terms, formal notice infrastructure, and machine-readable rights discovery.

## Overview

Build a **machine-readable deed system** where publishers define licensing terms across three tiers (Bronze/Scraping, Silver/RAG, Gold/Training), embed pointers to those terms in signed content via existing Unicode variation selectors, and provide public API endpoints for rights resolution. The system eliminates the "innocent infringement" defense by serving formal notice through the content itself. Built on top of the existing enterprise_api (port 9000, core DB) and coalition-service (port 8009) architecture.

## Objectives

- Publishers can set default rights profiles in under 5 minutes using templates
- Any party encountering signed content can discover rights via a single public API call
- Formal notices are cryptographically provable and independently verifiable
- Evidence packages are court-ready with complete chain-of-custody documentation
- Platform partners can onboard publishers with rights profiles in a single API call
- RSL 1.0 interoperability — import existing RSL terms and export to RSL XML format
- Phone-home analytics reveal exactly where content appears and who is accessing rights info
- Publisher dashboard surfaces actionable rights intelligence in real-time

## Architecture Decisions

- **Rights tables** → enterprise_api Core DB (PostgreSQL, encypher_core): orgs, licensing, and all rights data live here for consistency
- **Coalition analytics** → coalition-service DB remains for member content indexing and revenue distribution
- **Public rights API** → enterprise_api (has document signing context, ContentReference data)
- **Enhanced sign endpoint** → enterprise_api `/api/v1/sign` extended with `rights` param
- **Cross-service calls** → enterprise_api calls coalition-service for aggregate licensing stats

## Tasks (WBS)

### 1.0 Foundation — Database Schema

- [ ] 1.1 Create git branch `feature/rights-management-system`
- [ ] 1.2 Write Alembic migration: `publisher_rights_profiles` table
  - organization_id (FK → organizations), profile_version (auto-increment), effective_date, created_at, updated_by
  - IDENTITY: publisher_name, publisher_url, contact_email, contact_url, legal_entity, jurisdiction
  - DEFAULT RIGHTS: default_license_type (enum)
  - TIER TERMS: bronze_tier (JSONB), silver_tier (JSONB), gold_tier (JSONB)
  - FORMAL NOTICE: notice_status, notice_effective_date, notice_text, notice_hash
  - COALITION: coalition_member, coalition_joined_at, licensing_track
  - UNIQUE(organization_id, profile_version)
- [ ] 1.3 Write Alembic migration: `document_rights_overrides` table
  - document_id (UUID FK → content_references), organization_id, override_version, override_type
  - Collection/content-type/date-range selectors
  - bronze_tier_override, silver_tier_override, gold_tier_override (JSONB, nullable)
  - Special flags: do_not_license, premium_content, embargo_until, syndication_rights
- [ ] 1.4 Write Alembic migration: `formal_notices` table
  - Target entity info (name, domain, contact, type)
  - Scope (all_content, specific_documents, date_range)
  - Notice type, notice_text, notice_hash (SHA-256)
  - Demands (JSONB), status, delivery info, acknowledgment
  - Immutability constraint: once delivered, content cannot change
- [ ] 1.5 Write Alembic migration: `notice_evidence_chain` table
  - Append-only linked list: event_type, event_data (JSONB), event_hash, previous_hash
  - DB trigger to prevent UPDATE/DELETE
- [ ] 1.6 Write Alembic migration: `licensing_requests` table (new, distinct from existing agreements)
  - publisher_org_id, requester_org_id, tier, scope (JSONB), proposed_terms (JSONB)
  - requester_info (JSONB), status, response, responded_at
- [ ] 1.7 Write Alembic migration: `rights_audit_log` table
  - BIGSERIAL, organization_id, action, resource_type, resource_id, old_value, new_value
  - performed_by, performed_at, ip_address
  - Append-only (no UPDATE/DELETE)
- [ ] 1.8 Write Alembic migration: `content_detection_events` table (partitioned by month)
  - document_id, organization_id, detection_source, detected_on_url, detected_on_domain
  - requester_ip, requester_org_id, requester_user_agent, user_agent_category
  - segments_found, integrity_status, rights_served, rights_acknowledged
  - Partition by RANGE(created_at)
- [ ] 1.9 Write Alembic migration: `known_crawlers` table
  - user_agent_pattern, crawler_name, operator_org, crawler_type
  - respects_robots_txt, respects_rsl, known_ip_ranges
- [ ] 1.10 Create all required DB indexes as specified
- [ ] 1.11 Run migrations locally, verify schema in DB

### 2.0 Foundation — Models & Schemas

- [ ] 2.1 Create `enterprise_api/app/models/rights.py`
  - SQLAlchemy ORM models for all new tables
  - PublisherRightsProfile, DocumentRightsOverride, FormalNotice, NoticeEvidenceChain
  - LicensingRequest, RightsAuditLog, ContentDetectionEvent, KnownCrawler
- [ ] 2.2 Create `enterprise_api/app/schemas/rights_schemas.py`
  - Pydantic schemas for all request/response bodies
  - TierPermissions, TierPricing, TierAttribution models (Bronze/Silver/Gold)
  - PublisherRightsProfileCreate, PublisherRightsProfileResponse
  - DocumentRightsOverrideCreate, PublicRightsResponse
  - FormalNoticeCreate, LicensingRequestCreate, etc.
- [ ] 2.3 Create rights template definitions in `enterprise_api/app/core/rights_templates.py`
  - Built-in templates: "news_publisher_default", "blog_independent", "academic_open_access", "all_rights_reserved", "premium_paywalled"
  - Each template fully populates bronze/silver/gold tiers with sensible defaults

### 3.0 Foundation — Rights Profile API (Publisher-Facing)

- [ ] 3.1 Create `enterprise_api/app/routers/rights.py` router
- [ ] 3.2 Implement `PUT /api/v1/rights/profile` — Set/update default rights profile for org
  - Auth: org admin required
  - Versioning: new version created on each update (immutable history)
  - Returns: profile with version number
- [ ] 3.3 Implement `GET /api/v1/rights/profile` — Get current rights profile
  - Auth: org member
  - Returns: current active profile (latest version)
- [ ] 3.4 Implement `GET /api/v1/rights/profile/history` — Version history
  - Auth: org admin
  - Returns: array of profile versions with timestamps
- [ ] 3.5 Implement `PUT /api/v1/rights/documents/{document_id}` — Document override
  - Auth: org member, must own document
- [ ] 3.6 Implement `PUT /api/v1/rights/collections/{collection_id}` — Collection override
- [ ] 3.7 Implement `PUT /api/v1/rights/content-types/{content_type}` — Content-type override
- [ ] 3.8 Implement `POST /api/v1/rights/bulk-update` — Bulk rights update
  - Returns: applied count, skipped count, errors
- [ ] 3.9 Implement `GET /api/v1/rights/templates` — Public templates list (no auth)
- [ ] 3.10 Implement `POST /api/v1/rights/profile/from-template/{template_id}` — Init from template
- [ ] 3.11 Create `enterprise_api/app/services/rights_service.py`
  - Rights resolution logic: document → collection → content-type → publisher default (COALESCE query)
  - Profile CRUD with versioning
  - Audit log on every change
- [ ] 3.12 Register rights router in `enterprise_api/app/main.py`

### 4.0 Foundation — Public Rights Resolution (Consumer-Facing)

- [ ] 4.1 Create `enterprise_api/app/api/v1/public/rights.py` router (no auth required)
- [ ] 4.2 Implement `GET /api/v1/public/rights/{document_id}` — Full rights resolution
  - Rate limited: 10,000 requests/hour per IP
  - Returns: publisher identity, full tier objects, formal notice status, licensing contact, verification
  - Logs to content_detection_events (detection_source='rights_api_lookup')
- [ ] 4.3 Implement `POST /api/v1/public/rights/resolve` — Resolve rights from raw text
  - Extracts Unicode variation selectors, resolves to document_ids, returns rights per segment
- [ ] 4.4 Implement `GET /api/v1/public/rights/organization/{org_id}` — Org default profile
  - Returns: publisher profile with tier terms (no document-specific overrides)
- [ ] 4.5 Implement `GET /api/v1/public/rights/{document_id}/json-ld` — JSON-LD output
  - Schema.org compatible machine-readable rights
- [ ] 4.6 Implement `GET /api/v1/public/rights/{document_id}/odrl` — ODRL output (W3C standard)
- [ ] 4.7 Implement `GET /api/v1/public/rights/organization/{org_id}/robots-meta` — robots.txt additions
- [ ] 4.8 Register public rights router in `enterprise_api/app/api/v1/api.py`

### 5.0 Foundation — Enhanced Sign Endpoint

- [ ] 5.1 Extend `SignRequest` schema in `enterprise_api/app/schemas/sign_schemas.py`
  - Add `rights` field: `{ use_profile_defaults: bool, overrides: { bronze_tier, silver_tier, gold_tier }, custom_notice: str | null }`
- [ ] 5.2 Extend sign endpoint handler to:
  - When `use_profile_defaults: true`: fetch publisher's rights profile, apply overrides
  - Merge resulting rights into the C2PA manifest (rights_resolution_url, notice_status)
  - Store rights snapshot in ContentReference (rights_snapshot JSONB column — add migration)
  - Add `rights_resolution_url` to C2PA manifest pointing to `/api/v1/public/rights/{document_id}`
- [ ] 5.3 Add `rights_snapshot` column to `content_references` via migration
- [ ] 5.4 Validate that rights work for platform partner `on_behalf_of` signing

### 6.0 Enforcement — Formal Notice API

- [ ] 6.1 Create `enterprise_api/app/routers/notices.py` router
- [ ] 6.2 Implement `POST /api/v1/notices/create` — Create formal notice
  - Auth: org admin
  - Generates SHA-256 hash of notice content
  - Creates initial evidence chain entry
- [ ] 6.3 Implement `GET /api/v1/notices/{notice_id}` — Get notice with evidence chain
  - Returns: notice with cryptographic proof, delivery confirmations, response history
- [ ] 6.4 Implement `POST /api/v1/notices/{notice_id}/deliver` — Deliver notice
  - Channels: email (via notification-service), API callback, returns delivery receipt
  - Creates evidence chain entry with delivery hash
  - Once delivered, notice content is locked (immutable)
- [ ] 6.5 Implement `GET /api/v1/notices/{notice_id}/evidence` — Evidence package
  - Returns: court-ready bundle (signed content proofs, notice, delivery confirmation, usage evidence)
  - Bundle includes Merkle proofs, C2PA validation, rights terms at time of signing
- [ ] 6.6 Create `enterprise_api/app/services/notice_service.py`
  - Notice CRUD, hash generation (SHA-256), evidence chain management
  - Evidence package assembly (structured JSON + cryptographic proofs)
- [ ] 6.7 Register notices router in `enterprise_api/app/main.py`

### 7.0 Licensing Transactions

- [ ] 7.1 Create `enterprise_api/app/routers/licensing_requests.py` (new — separate from existing licensing.py)
- [ ] 7.2 Implement `POST /api/v1/licensing/request` — Submit licensing request
  - Auth: consumer API key
  - Body: organization_id, tier, scope, proposed_terms, requester info
  - Returns: request ID, status, estimated response time
  - Notifies publisher via notification-service
- [ ] 7.3 Implement `GET /api/v1/licensing/requests` — List requests
  - Publisher view: incoming requests with status
  - Consumer view: outgoing requests with status
- [ ] 7.4 Implement `PUT /api/v1/licensing/requests/{request_id}/respond` — Publisher respond
  - Auth: publisher org admin
  - Actions: approve, counter, reject
  - On approve: creates licensing_agreement record
- [ ] 7.5 Implement `GET /api/v1/licensing/agreements` — List active agreements
  - Auth: party to agreement
  - Returns: agreements with terms, status, usage metrics
- [ ] 7.6 Implement `GET /api/v1/licensing/agreements/{agreement_id}/usage` — Usage metrics
  - Returns: articles accessed, retrievals, ingestion events, compliance status

### 8.0 Standards Interoperability — RSL

- [ ] 8.1 Implement `GET /api/v1/public/rights/organization/{org_id}/rsl` — RSL 1.0 XML generation
  - Map bronze/silver/gold tiers to RSL `<license>` elements
  - No auth, public endpoint
- [ ] 8.2 Implement `GET /api/v1/public/rights/organization/{org_id}/robots-txt` — robots.txt additions
  - Returns text block to append to publisher's robots.txt
  - Includes RSL `License:` directive, User-agent rules for AI crawlers
- [ ] 8.3 Implement `POST /api/v1/rights/rsl/import` — Import existing RSL document
  - Auth: org admin
  - Parse RSL XML, map to bronze/silver/gold tiers
  - Creates rights profile from RSL terms
- [ ] 8.4 Implement `POST /api/v1/rsl/olp/token` — RSL Open License Protocol token endpoint
  - OLP (OAuth 2.0 extension) for crawler license acquisition
  - Validates crawler, checks bronze tier terms, issues/denies token
  - Logs to content_detection_events
- [ ] 8.5 Implement `GET /api/v1/rsl/olp/validate/{token}` — Validate OLP token
  - Auth: publisher API key
  - Returns: token validity, scope, requester identity

### 9.0 Analytics — Phone-Home

- [ ] 9.1 Enhance `/api/v1/public/c2pa/zw/resolve` endpoint to log detection events
  - When segment UUID is resolved, log to content_detection_events
  - Capture requester IP, user_agent, detected_on_url (via Referer header), segments_found
- [ ] 9.2 Create `enterprise_api/app/services/detection_service.py`
  - Classify user agents against known_crawlers registry
  - Async detection event logging (non-blocking)
- [ ] 9.3 Create `GET /api/v1/analytics/rights/detections` — Publisher detection analytics
  - Auth: org member
  - Returns: detection events grouped by source, domain, date
  - Uses materialized view or aggregated query
- [ ] 9.4 Create `GET /api/v1/analytics/rights/crawlers` — AI crawler activity for org
  - Returns: crawler visits, rights lookup rate, licensed vs unlicensed
- [ ] 9.5 Populate `known_crawlers` table with seed data:
  - GPTBot (OpenAI), ClaudeBot (Anthropic), Google-Extended, PerplexityBot, Common Crawl, etc.

### 10.0 Platform Partner Integration

- [ ] 10.1 Implement `POST /api/v1/rights/profile/delegated-setup` — Platform partner onboards publisher
  - Auth: strategic_partner tier API key
  - Creates publisher org + rights profile in one call
  - Sets delegation flags (partner_can_sign, partner_can_modify_rights, publisher_can_override)
- [ ] 10.2 Validate delegated signing respects publisher's rights profile (not partner's)
- [ ] 10.3 Validate platform partner cannot override individual publisher terms after setup

### 11.0 Testing

- [ ] 11.1 Write unit tests for rights resolution logic (priority cascade: document → collection → content-type → default)
- [ ] 11.2 Write unit tests for formal notice hash generation and immutability
- [ ] 11.3 Write unit tests for RSL XML generation from profile
- [ ] 11.4 Write integration tests for full sign-with-rights → public-rights-lookup flow
- [ ] 11.5 Write integration tests for formal notice create → deliver → evidence-package flow
- [ ] 11.6 Write integration tests for licensing request → respond → agreement flow
- [ ] 11.7 Write integration tests for platform partner delegated setup flow
- [ ] 11.8 Verify all existing tests still pass (no regression)
- [ ] 11.9 End-to-end test with local test user:
  - Create test org/publisher
  - Set up rights profile using template
  - Sign content with rights
  - Call public rights API, verify response
  - Create formal notice, deliver, generate evidence package
  - Submit licensing request, respond, verify agreement created

### 12.0 Documentation & Cleanup

- [ ] 12.1 Update OpenAPI docs (auto-generated from FastAPI schemas)
- [ ] 12.2 Add rights endpoints to `enterprise_api/docs/` if applicable
- [ ] 12.3 Update `services/ENV_VARS_MAPPING.md` for any new config vars
- [ ] 12.4 Move PRD to ARCHIVE when complete

## Success Criteria

- [ ] `uv run pytest` passes in enterprise_api (all existing + new tests)
- [ ] Publisher can set rights profile via PUT, retrieve via GET, with version history
- [ ] GET `/api/v1/public/rights/{document_id}` returns full tier terms for signed document
- [ ] Signed documents include `rights_resolution_url` in C2PA manifest
- [ ] Formal notice create + deliver + evidence package flow works end-to-end
- [ ] RSL 1.0 XML generated correctly from bronze/silver/gold profile
- [ ] Local test user can complete full publisher onboarding → sign → rights discovery flow

## Completion Notes

(To be filled when implementation is complete)
