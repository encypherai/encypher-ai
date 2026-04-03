# Enterprise 1.0 Launch — Comprehensive Feature PRD

**Status:** 📋 Planning
**Current Goal:** Define all features required for enterprise publisher launch targeting AP, BBC, Springer, Taylor & Francis, and AI industry partners.

## Overview

This PRD consolidates all features required for Encypher's Enterprise 1.0 launch, addressing the publisher and AI licensing ecosystem. It covers infrastructure gaps, CMS integrations, consumer-facing tools, and enterprise compliance requirements.

## Objectives

- Enable enterprise publishers to integrate C2PA signing into their existing workflows
- Provide consumer-facing verification tools (browser extension, verification badges)
- Support enterprise authentication and compliance requirements (SAML, data residency)
- Expand platform reach through CMS plugins and integrations
- Create async bulk processing for archive signing workflows

---

## Feature Categories

1. [Enterprise Authentication & Compliance](#10-enterprise-authentication--compliance)
2. [CMS Integrations](#20-cms-integrations)
3. [Consumer-Facing Tools](#30-consumer-facing-tools)
4. [Bulk Processing & Jobs API](#40-bulk-processing--jobs-api)
5. [C2PA Rights & Licensing Metadata](#50-c2pa-rights--licensing-metadata)
6. [Documentation & SLA](#60-documentation--sla)
7. [Publisher Dashboard](#70-publisher-dashboard)

## Sprint PRD Breakdown (Parallel Workstreams)

Each sprint PRD below is intended to be worked in parallel by a dedicated team. This epic PRD is the index/rollup; sprint PRDs are the SSOT for implementation details.

- **Identity (SAML + SCIM)**: `PRD_Enterprise_Identity_SAML_SCIM.md`
- **CMS (Drupal)**: `PRD_Enterprise_Drupal_Module.md`
- **CMS (AEM)**: `PRD_Enterprise_AEM_Integration.md`
- **CMS (Contentful)**: `PRD_Enterprise_Contentful_Integration.md`
- **CMS (Ghost)**: `PRD_Enterprise_Ghost_Integration.md`
- **Browser Tools (Chrome + Substack workflow)**: `PRD_Enterprise_Chrome_Extension_Substack.md`
- **Bulk Jobs API**: `PRD_Enterprise_Bulk_Jobs_API.md`
- **Rights + AI Licensing Signals**: `PRD_Enterprise_Rights_Metadata_AI_Licensing.md`
- **Verification Widget + Portal**: `PRD_Enterprise_Verification_Widget_Portal.md`
- **Publisher Dashboard + Analytics**: `PRD_Enterprise_Publisher_Dashboard_Analytics.md`
- **Enterprise Readiness (SLA/Security/Data Residency)**: `PRD_Enterprise_SLA_Security_Data_Residency.md`

### Suggested Parallel Teams

This is the recommended parallelization model for 1.0 (teams can run concurrently with minimal overlap).

| Team | Owns PRDs | Primary code surfaces |
|------|----------|------------------------|
| Identity | Identity (SAML/SCIM) | `services/auth-service`, `services/user-service`, dashboard SSO UI |
| CMS Integrations | Drupal, AEM, Contentful, Ghost | `integrations/*`, publisher onboarding docs |
| Browser Tools | Chrome + Substack workflow | new `integrations/chrome-extension/*`, Enterprise API verify endpoints |
| Platform Jobs | Bulk Jobs API | Enterprise API + worker/queue service + object storage |
| Rights & Licensing | Rights + AI licensing signals | Enterprise API signing payload + coalition/licensing services |
| Trust UX | Widget + Portal + verification UX | marketing site/dashboard + public endpoints |
| Enterprise Readiness | SLA/Security/Data Residency | docs + ops tooling + legal templates |

---

## 1.0 Enterprise Authentication & Compliance

### 1.1 SAML 2.0 SSO Integration

Enterprise publishers (BBC, Springer, Condé Nast) require SAML-based SSO with identity providers like Okta, Azure AD, and OneLogin.

**Tasks:**

- [ ] 1.1.1 Research SAML 2.0 libraries for Python/FastAPI (python-saml, pysaml2)
- [ ] 1.1.2 Design SAML metadata exchange flow (SP-initiated and IdP-initiated)
- [ ] 1.1.3 Add SAML configuration to Organization model
  - [ ] `saml_enabled: bool`
  - [ ] `saml_metadata_url: str`
  - [ ] `saml_entity_id: str`
  - [ ] `saml_acs_url: str`
  - [ ] `saml_certificate: text`
- [ ] 1.1.4 Implement `/api/v1/auth/saml/metadata` endpoint (SP metadata XML)
- [ ] 1.1.5 Implement `/api/v1/auth/saml/login` endpoint (redirect to IdP)
- [ ] 1.1.6 Implement `/api/v1/auth/saml/acs` endpoint (Assertion Consumer Service)
- [ ] 1.1.7 Map SAML attributes to Encypher user fields (email, name, roles)
- [ ] 1.1.8 Add SAML configuration UI to dashboard
- [ ] 1.1.9 Write integration tests with mock IdP
- [ ] 1.1.10 Document SAML setup for common IdPs (Okta, Azure AD, Google Workspace)

### 1.2 SCIM User Provisioning

Automated user lifecycle management for enterprise orgs.

**Tasks:**

- [ ] 1.2.1 Research SCIM 2.0 spec requirements
- [ ] 1.2.2 Implement `/scim/v2/Users` CRUD endpoints
- [ ] 1.2.3 Implement `/scim/v2/Groups` CRUD endpoints
- [ ] 1.2.4 Add SCIM bearer token authentication
- [ ] 1.2.5 Sync SCIM groups to Encypher teams/roles
- [ ] 1.2.6 Add SCIM configuration to Organization settings
- [ ] 1.2.7 Write integration tests with Okta SCIM simulator
- [ ] 1.2.8 Document SCIM provisioning setup

### 1.3 Data Residency Documentation

GDPR compliance requires clarity on data processing locations.

**Tasks:**

- [ ] 1.3.1 Document current deployment region(s)
- [ ] 1.3.2 Create data processing addendum (DPA) template
- [ ] 1.3.3 Document data flow diagram (API → DB → Storage)
- [ ] 1.3.4 Add region selection to Organization settings (future multi-region)
- [ ] 1.3.5 Create GDPR compliance page for marketing site
- [ ] 1.3.6 Document data retention policies
- [ ] 1.3.7 Implement data export endpoint for GDPR subject access requests

---

## 2.0 CMS Integrations

### 2.1 Drupal Module

Drupal powers ~20% of enterprise news and academic publishing (Springer, Nature, university presses).

**Tasks:**

- [ ] 2.1.1 Research Drupal module development best practices
- [ ] 2.1.2 Create Drupal module scaffolding (encypher_provenance)
- [ ] 2.1.3 Implement API key configuration in Drupal admin
- [ ] 2.1.4 Add hook_node_presave for auto-signing on publish
- [ ] 2.1.5 Add hook_node_update for re-signing on content update
- [ ] 2.1.6 Create verification block for content display
- [ ] 2.1.7 Add bulk signing UI for existing content
- [ ] 2.1.8 Implement Drupal entity reference for signed content metadata
- [ ] 2.1.9 Add Drupal Views integration for signed content queries
- [ ] 2.1.10 Create Drupal.org module page and documentation
- [ ] 2.1.11 Write automated tests (PHPUnit)
- [ ] 2.1.12 Test with Drupal 9.x and 10.x

### 2.2 Adobe Experience Manager (AEM) Integration

BBC, Condé Nast, and major media companies use AEM.

**Tasks:**

- [ ] 2.2.1 Research AEM Cloud Service integration patterns
- [ ] 2.2.2 Create AEM package structure
- [ ] 2.2.3 Implement Sling model for C2PA metadata
- [ ] 2.2.4 Add workflow step for auto-signing on activation
- [ ] 2.2.5 Create AEM component for verification badge
- [ ] 2.2.6 Implement OSGi configuration for API credentials
- [ ] 2.2.7 Add content fragment support for structured content
- [ ] 2.2.8 Create AEM dispatcher cache rules for verification
- [ ] 2.2.9 Write integration tests
- [ ] 2.2.10 Document AEM integration guide

### 2.3 Contentful Integration

Growing API-first CMS used by modern publishers.

**Tasks:**

- [ ] 2.3.1 Create Contentful App (React-based)
- [ ] 2.3.2 Implement Contentful webhook receiver for publish events
- [ ] 2.3.3 Add custom field type for C2PA manifest metadata
- [ ] 2.3.4 Create sidebar extension for manual signing
- [ ] 2.3.5 Implement entry transformation for signed content
- [ ] 2.3.6 Add Contentful Marketplace listing
- [ ] 2.3.7 Document Contentful integration

### 2.4 Substack Integration

Substack is a major platform for independent journalists and newsletters.

**Architecture Analysis:**
- Substack does NOT have a traditional plugin system
- Options: (a) Browser extension approach, (b) Substack API integration if available, (c) Email/RSS post-processing
- Most viable: Chrome extension that authors can use to sign before pasting into Substack

**Tasks:**

- [ ] 2.4.1 Research Substack API availability and limitations
- [ ] 2.4.2 Evaluate Substack custom domain embedding options
- [ ] 2.4.3 Design "Sign before paste" workflow via Chrome extension
- [ ] 2.4.4 Create Substack-specific documentation for authors
- [ ] 2.4.5 Explore Substack partnership for native integration
- [ ] 2.4.6 Build verification widget for Substack custom domains
- [ ] 2.4.7 Create Substack author onboarding guide

### 2.5 Ghost CMS Plugin

Growing open-source alternative for publishers.

**Tasks:**

- [ ] 2.5.1 Research Ghost integration API
- [ ] 2.5.2 Create Ghost custom integration (webhook-based)
- [ ] 2.5.3 Implement post.published webhook handler
- [ ] 2.5.4 Add Ghost Admin API integration for content update
- [ ] 2.5.5 Create Ghost theme helper for verification badges
- [ ] 2.5.6 Document Ghost integration

---

## 3.0 Consumer-Facing Tools

### 3.1 Chrome Extension — C2PA Content Verifier

A browser extension that scans web pages for C2PA embeddings and displays verification status inline.

**Value Proposition:**
- Readers can verify content authenticity on any website
- Publishers with signed content get visual trust indicators
- Builds consumer awareness of content provenance
- Competitive differentiator vs. other C2PA implementations

**Tasks:**

- [ ] 3.1.1 Create Chrome extension scaffolding (Manifest V3)
- [ ] 3.1.2 Implement content script to scan page text for C2PA wrappers
- [ ] 3.1.3 Extract C2PATextManifestWrapper from page content
- [ ] 3.1.4 Call Encypher public verification API
- [ ] 3.1.5 Design verification badge overlay UI
  - [ ] Green checkmark for verified content
  - [ ] Organization name and signing date
  - [ ] Click to see full manifest details
- [ ] 3.1.6 Implement popup showing page verification summary
- [ ] 3.1.7 Add options page for user preferences
- [ ] 3.1.8 Handle multiple signed sections per page
- [ ] 3.1.9 Cache verification results for performance
- [ ] 3.1.10 Create Chrome Web Store listing
- [ ] 3.1.11 Create Firefox extension (WebExtension API compatible)
- [ ] 3.1.12 Create Edge extension (Chromium-based, should work with Chrome version)
- [ ] 3.1.13 Write automated tests (Puppeteer)
- [ ] 3.1.14 Design marketing page for extension

**Extension Features (Phase 2):**

- [ ] 3.1.15 Add right-click context menu "Verify selected text"
- [ ] 3.1.16 Integrate with trust anchor lookup API
- [ ] 3.1.17 Show revocation status (retracted content warning)
- [ ] 3.1.18 Add notification for newly signed content on followed sites
- [ ] 3.1.19 Publisher verification history/statistics

### 3.2 Verification Badge Embed Widget

JavaScript widget publishers can embed to show verification status.

**Tasks:**

- [ ] 3.2.1 Create lightweight JS widget (<10KB)
- [ ] 3.2.2 Implement auto-detect signed content on page
- [ ] 3.2.3 Design badge variants (minimal, detailed, floating)
- [ ] 3.2.4 Add click-to-verify modal with full details
- [ ] 3.2.5 Create CDN distribution for widget script
- [ ] 3.2.6 Add customization options (colors, position)
- [ ] 3.2.7 Implement lazy loading for performance
- [ ] 3.2.8 Create embed code generator in dashboard
- [ ] 3.2.9 Document widget integration

### 3.3 Public Verification Portal

Web-based tool for anyone to paste text and verify C2PA signatures.

**Tasks:**

- [ ] 3.3.1 Design verification portal UI/UX
- [ ] 3.3.2 Implement paste/upload text interface
- [ ] 3.3.3 Display verification results with manifest details
- [ ] 3.3.4 Show signer information and trust anchor
- [ ] 3.3.5 Add share verification results feature
- [ ] 3.3.6 Create SEO-optimized verification result pages
- [ ] 3.3.7 Implement rate limiting for anonymous users
- [ ] 3.3.8 Add verification history for logged-in users

---

## 4.0 Bulk Processing & Jobs API

### 4.1 Async Bulk Signing Jobs

For archive signing (millions of articles), publishers need async job processing.

**Tasks:**

- [ ] 4.1.1 Design job queue architecture (Redis/Celery or similar)
- [ ] 4.1.2 Create Job model
  - [ ] `id`, `organization_id`, `job_type`
  - [ ] `status` (pending, processing, completed, failed)
  - [ ] `total_items`, `processed_items`, `failed_items`
  - [ ] `created_at`, `started_at`, `completed_at`
  - [ ] `error_log`, `webhook_url`
- [ ] 4.1.3 Implement `POST /api/v1/jobs/bulk-sign` endpoint
  - Accept: JSONL file upload or S3 URL
  - Return: job_id for tracking
- [ ] 4.1.4 Implement `GET /api/v1/jobs/{job_id}` status endpoint
- [ ] 4.1.5 Implement `GET /api/v1/jobs/{job_id}/results` for output retrieval
- [ ] 4.1.6 Implement `DELETE /api/v1/jobs/{job_id}` to cancel
- [ ] 4.1.7 Add webhook notification on job completion
- [ ] 4.1.8 Implement progress streaming via SSE
- [ ] 4.1.9 Add retry logic for failed items
- [ ] 4.1.10 Create job management UI in dashboard
- [ ] 4.1.11 Set configurable concurrency limits per tier
- [ ] 4.1.12 Write integration tests

### 4.2 Bulk Import Formats

Support various input formats for bulk operations.

**Tasks:**

- [ ] 4.2.1 Support JSONL input (one document per line)
- [ ] 4.2.2 Support CSV input (text, title, metadata columns)
- [ ] 4.2.3 Support ZIP archive with text files
- [ ] 4.2.4 Support S3 bucket URL input
- [ ] 4.2.5 Validate input format before job creation
- [ ] 4.2.6 Document supported formats and limits

### 4.3 Bulk Export

Export signed content and metadata.

**Tasks:**

- [ ] 4.3.1 Implement `POST /api/v1/jobs/bulk-export` endpoint
- [ ] 4.3.2 Support date range filters
- [ ] 4.3.3 Support output format selection (JSONL, CSV)
- [ ] 4.3.4 Generate signed URL for download
- [ ] 4.3.5 Include manifest metadata in export
- [ ] 4.3.6 Add GDPR data export support (all org data)

---

## 5.0 C2PA Rights & Licensing Metadata

### 5.1 Rights Assertion Support

Implement `c2pa.rights` assertion for licensing metadata.

**Tasks:**

- [ ] 5.1.1 Research C2PA rights assertion schema
- [ ] 5.1.2 Define Encypher rights metadata schema
  - [ ] `usage_terms`: string (CC license, custom terms)
  - [ ] `copyright_holder`: string
  - [ ] `contact_email`: string
  - [ ] `syndication_allowed`: bool
  - [ ] `ai_training_allowed`: bool
  - [ ] `embargo_until`: datetime (optional)
  - [ ] `license_url`: string
- [ ] 5.1.3 Add rights fields to SignRequest model
- [ ] 5.1.4 Embed rights assertion in C2PA manifest
- [ ] 5.1.5 Display rights info in verification response
- [ ] 5.1.6 Add rights template management in dashboard
- [ ] 5.1.7 Create pre-built rights templates
  - [ ] Creative Commons (CC-BY, CC-BY-NC, etc.)
  - [ ] All Rights Reserved
  - [ ] News Wire (AP style)
  - [ ] Academic/Open Access
- [ ] 5.1.8 Document rights metadata usage

### 5.2 Licensing Signal for AI Companies

Explicit signals for AI training opt-in/opt-out.

**Tasks:**

- [ ] 5.2.1 Extend `c2pa.training-mining.v1` assertion
- [ ] 5.2.2 Add granular AI usage permissions
  - [ ] `ai_training`: bool
  - [ ] `ai_inference`: bool
  - [ ] `ai_fine_tuning`: bool
  - [ ] `commercial_ai_use`: bool
- [ ] 5.2.3 Create robots.txt-style machine-readable format
- [ ] 5.2.4 Integrate with Coalition licensing API
- [ ] 5.2.5 Document AI licensing signals for AI companies

---

## 6.0 Documentation & SLA

### 6.1 API Versioning Policy

**Tasks:**

- [ ] 6.1.1 Create `API_VERSIONING.md` document
- [ ] 6.1.2 Define deprecation policy (12-month minimum notice)
- [ ] 6.1.3 Document version header support (`X-API-Version`)
- [ ] 6.1.4 Plan `/api/v2` migration path
- [ ] 6.1.5 Add deprecation warning headers for sunset endpoints

### 6.2 SLA Documentation

Enterprise contracts require documented SLAs.

**Tasks:**

- [ ] 6.2.1 Create `SLA.md` document
- [ ] 6.2.2 Define uptime commitment (99.9% target)
- [ ] 6.2.3 Define latency SLOs
  - [ ] Sign: p50 < 100ms, p99 < 500ms
  - [ ] Verify: p50 < 50ms, p99 < 200ms
- [ ] 6.2.4 Define support response times by tier
- [ ] 6.2.5 Document incident communication process
- [ ] 6.2.6 Create status page (verify.encypher.com/status)
- [ ] 6.2.7 Set up uptime monitoring (Pingdom, Better Uptime)
- [ ] 6.2.8 Create incident post-mortem template

### 6.3 Security Documentation

**Tasks:**

- [ ] 6.3.1 Create security whitepaper
- [ ] 6.3.2 Document encryption at rest and in transit
- [ ] 6.3.3 Document key management practices
- [ ] 6.3.4 Create penetration test summary (redacted)
- [ ] 6.3.5 Document SOC 2 compliance status/roadmap
- [ ] 6.3.6 Create security contact and disclosure policy

---

## 7.0 Publisher Dashboard

### 7.1 Content Portfolio Overview

Publishers need visibility into their signed content.

**Tasks:**

- [ ] 7.1.1 Design dashboard home with key metrics
  - [ ] Total signed documents
  - [ ] Verification rate (last 30 days)
  - [ ] Revocations
  - [ ] API usage
- [ ] 7.1.2 Implement signed content list view
- [ ] 7.1.3 Add search/filter for signed documents
- [ ] 7.1.4 Show per-document verification count
- [ ] 7.1.5 Add content health indicators (valid, revoked, expired)
- [ ] 7.1.6 Create exportable reports (CSV, PDF)

### 7.2 Verification Analytics

**Tasks:**

- [ ] 7.2.1 Track verification requests by document
- [ ] 7.2.2 Show verification geography (country breakdown)
- [ ] 7.2.3 Show verification sources (direct API, widget, extension)
- [ ] 7.2.4 Create verification trend charts
- [ ] 7.2.5 Add alerts for unusual verification patterns

### 7.3 Team Management Enhancements

**Tasks:**

- [ ] 7.3.1 Add role-based permissions (admin, editor, viewer)
- [ ] 7.3.2 Implement department/team hierarchy
- [ ] 7.3.3 Add API key scoping by team
- [ ] 7.3.4 Create activity log per team member
- [ ] 7.3.5 Add invitation workflow with role assignment

---

## 8.0 Testing & Quality Assurance

### 8.1 End-to-End Testing

**Tasks:**

- [ ] 8.1.1 Create E2E test suite for signing → verification flow
- [ ] 8.1.2 Test bulk signing with 10K+ documents
- [ ] 8.1.3 Test SAML SSO flow with mock IdP
- [ ] 8.1.4 Test CMS plugin integrations
- [ ] 8.1.5 Test Chrome extension on major news sites
- [ ] 8.1.6 Load test async job processing
- [ ] 8.1.7 Test revocation propagation timing

### 8.2 Security Testing

**Tasks:**

- [ ] 8.2.1 Run OWASP ZAP scan
- [ ] 8.2.2 Test API rate limiting under load
- [ ] 8.2.3 Test authentication bypass attempts
- [ ] 8.2.4 Test SAML signature validation
- [ ] 8.2.5 Review dependency vulnerabilities (pip-audit, npm audit)

---

## Success Criteria

- [ ] SAML SSO functional with Okta and Azure AD
- [ ] Drupal module published on Drupal.org
- [ ] Chrome extension published on Chrome Web Store
- [ ] Bulk signing tested with 100K+ documents
- [ ] SLA and security documentation complete
- [ ] All P0 and P1 features implemented and tested

## Dependencies

- **Auth Service**: SAML integration will be added here
- **Key Service**: API key scoping enhancements
- **Analytics Service**: Verification tracking
- **Coalition Service**: Rights metadata integration

## Open Questions

1. Should Chrome extension require Encypher account for premium features?
2. What is the archive signing throughput requirement for enterprise publishers?
3. Should we prioritize Substack partnership outreach over technical workaround?
4. AEM integration target: AEM Cloud Service first (AEM 6.5 deferred post-1.0) — resolved

---

## Completion Notes

(Filled when PRD is complete.)
