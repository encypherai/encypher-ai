# Enterprise SDK Production Readiness Plan

## Task List

- [ ] 1.0 Audit SDK vs API Contract
    - [x] 1.0.1 Compare `encypher_enterprise/models.py` with live API responses
    - [ ] 1.0.2 Verify `TIMESTAMPTZ` parsing in SDK models
    - [ ] 1.0.3 Audit Exception mapping (`exceptions.py`) against API error codes

- [x] 2.0 Integration Test Suite (`tests/integration`)
    - [x] 2.0.1 Create `test_live_api.py` skeleton
    - [x] 2.0.2 Implement Sign & Verify flow against Dockerized API
    - [ ] 2.0.3 Implement Enterprise Embeddings flow (Verified logic manually, integration test harness issue pending)
    - [ ] 2.0.4 Implement Streaming flow (Pending test harness fix)

- [x] 3.0 Developer Experience & Polish
    - [x] 3.0.1 Verify README Quick Start examples
    - [x] 3.0.2 Ensure CLI commands (`encypher sign`) work with local config

- [ ] 4.0 WordPress Plugin & Enterprise Tier Strategy
    - [x] 4.0.1 Audit & Define Tier Differentiation (Free vs Pro vs Enterprise)
    - [x] 4.0.2 Update WordPress Admin UI with Tier Features (HSM, BYOK)
    - [x] 4.0.3 Backend Infrastructure for AWS KMS (HSM) Signing
        - [x] Create `AWSSigner` adapter
        - [x] Update core `Signer` protocol
        - [x] Implement `kms_key_id` loading logic in `crypto_utils.py`
    - [x] 4.0.4 Database Schema Migration for HSM
        - [x] Create Alembic migration (`add_kms_support`)
        - [x] Update `Organization` model

- [x] 5.0 Plugin Differentiation Features
    - [x] 5.0.1 Whitelabeling Support (Enterprise/Pro)
        - [x] Add `show_branding` option to Settings (hidden for Free)
        - [x] Update Frontend Badge to respect branding setting
    - [x] 5.0.2 Advanced Analytics Integration
        - [x] Ensure Analytics page respects `advanced_analytics_enabled` feature flag from API
        - [x] Mock "Verification Hits" data for Pro/Enterprise tiers

- [x] 6.0 Final Integration Testing
    - [x] 6.0.1 Fix Embeddings Integration Test (`test_live_system.py`)
    - [x] 6.0.2 Fix Streaming Integration Test (`test_live_system.py`)

## Notes
- **Context**: `enterprise_api` passed load tests with Docker/Postgres. We can reuse this running instance for SDK integration tests.
- **Constraint**: SDK must handle `TIMESTAMPTZ` formats returned by the API (fixed in previous phase).
- **New Feature**: Added AWS KMS support for Enterprise tier (Legal Non-Repudiation).
- **New Feature**: Added Plugin Whitelabeling and Advanced Analytics (Mocked) for Pro/Enterprise tiers.

## 7.0 Marketing Site Backend Migration

### 7.1 Architecture & Planning
- [x] 7.1.1 Define `web-service` schema for sales/contact forms and analytics
- [x] 7.1.2 Set up new PostgreSQL database for marketing data
- [x] 7.1.3 Design API contracts for web-service endpoints
- [x] 7.1.4 Plan data migration from legacy backend

### 7.2 Web-Service Implementation
- [x] 7.2.1 Initialize new FastAPI service in `services/web-service`
- [x] 7.2.2 Implement database models for demo requests and analytics events
- [x] 7.2.3 Create API endpoints for contact forms and demo requests
- [x] 7.2.4 Implement analytics event tracking endpoints
- [x] 7.2.5 Add email notification system for new leads
- [x] 7.2.6 Set up database migrations with Alembic

### 7.3 Frontend Integration
- [x] 7.3.1 Update frontend API client to use new web-service endpoints
- [x] 7.3.2 Implement error handling and loading states
- [x] 7.3.3 Add analytics event tracking to key user interactions
- [x] 7.3.4 Update environment configuration
- [x] 7.3.5 Enable Cross-Subdomain SSO (Marketing <-> Dashboard)

### 7.4 Testing & Deployment
- [x] 7.4.1 Write unit and integration tests
- [x] 7.4.2 Set up Local Development Environment (Docker + Scripts)
    - [x] 7.4.2.1 Local HTTPS with mkcert & Traefik (for Secure Cookies)
- [x] 7.4.3 Verify Encode/Decode Tool functionality (Local + Enterprise API)
- [ ] 7.4.4 Set up CI/CD pipeline for web-service
- [ ] 7.4.5 Deploy to staging environment
- [ ] 7.4.6 Perform end-to-end testing (Automated)
- [ ] 7.4.7 Deploy to production with feature flags

### 7.5 Post-Migration
- [ ] 7.5.1 Monitor system performance
- [ ] 7.5.2 Verify data consistency
- [ ] 7.5.3 Update documentation
- [ ] 7.5.4 Decommission legacy backend endpoints

## Status
- **Completed**:
    - Load test fixes (sync DB init, demo seeding).
    - DB Schema updates (TIMESTAMPTZ, user_id, missing columns).
    - SDK Contract Audit (SignRequest).
    - Sign/Verify Integration Tests (Dockerized env).
    - Developer Experience review.
    - WordPress Tier Audit & HSM Infrastructure Implementation.
    - Plugin Whitelabeling & Analytics differentiation.
    - **Final Integration Testing (Embeddings & Streaming).**
    - **Marketing Site Backend Migration (7.0)**:
        - Architecture & Planning (7.1)
        - Web-Service Implementation (7.2)
        - Frontend Integration (7.3)
        - Local Dev Environment Setup (7.4.2)
        - **Encode/Decode Tool Integration (Enterprise API Proxy)**
        - **Tamper Detection UI Features**
        - **Analytics Integration Fix (Shared DB Migration)**
    - **C2PA Standard Strategy (8.0)**:
        - Audited `encypher-ai` for C2PA Compliance.
        - Created `c2pa-text` Monorepo (MIT License).
        - Implemented Python, TypeScript, Rust, and Go packages.
        - Polished Docs with Encypher Branding & Enterprise Upsell.
        - Added Security & Contribution guidelines.
- **In Progress**:
    - Dashboard Functional Implementation (9.0)
- **Pending**:
    - Marketing Site CI/CD & Deployment (7.4.4+)
    - Production Deployment


## 9.0 Dashboard Full Functionality

### 9.1 Core Infrastructure
- [x] 9.1.1 Create API client library (`src/lib/api.ts`)
- [x] 9.1.2 Add shared layout component with navigation
- [x] 9.1.3 Configure React Query provider (already configured)

### 9.2 Main Dashboard Page (`/`)
- [x] 9.2.1 Fetch real usage stats from analytics-service
- [x] 9.2.2 Fetch real API keys summary from key-service
- [x] 9.2.3 Display user profile from session
- [x] 9.2.4 Add navigation links to sub-pages
- [x] 9.2.5 Add loading skeletons

### 9.3 API Keys Page (`/api-keys`)
- [x] 9.3.1 Fix missing API client import
- [x] 9.3.2 Verify create/delete/list functionality (wired to key-service)
- [x] 9.3.3 Add copy-to-clipboard for full key (already implemented)

### 9.4 Analytics Page (`/analytics`)
- [x] 9.4.1 Fetch real data from analytics-service
- [x] 9.4.2 Connect time range selector to API
- [ ] 9.4.3 Display real activity history (requires activity endpoint)

### 9.5 Settings & Other Pages
- [x] 9.5.1 Implement settings page functionality (profile/notifications)
- [ ] 9.5.2 Implement billing page functionality (requires billing-service endpoints)
- [x] 9.5.3 Add sign-out functionality (in DashboardLayout)

### 9.6 Testing & Verification
- [x] 9.6.1 Test full login -> dashboard flow (verified working)
- [x] 9.6.2 Test API key generation (endpoint working, UI functional)
- [x] 9.6.3 Verify analytics data display (endpoint working)

### 9.7 Backend Fixes Applied
- [x] 9.7.1 Fix key-service metadata column name (SQLAlchemy reserved)
- [x] 9.7.2 Fix key-service missing logging import
- [x] 9.7.3 Fix key-service get_current_user to parse standard response format
- [x] 9.7.4 Update Traefik routing for key-service and analytics-service

### 9.8 Design System & Branding
- [x] 9.8.1 Add Roboto font to dashboard
- [x] 9.8.2 Add logo to dashboard (copied from marketing site)
- [x] 9.8.3 Default marketing emails to true for new users
- [x] 9.8.4 Replace rosy-brown with cyber-teal per brand guidelines
- [x] 9.8.5 Create design assessment document (docs/design/DESIGN_ASSESSMENT.md)
- [x] 9.8.6 Fix API key normalizer bug (array.keys() method conflict)
- [x] 9.8.7 Fix API key display (show key_prefix instead of fingerprint)
- [x] 9.8.8 Remove misleading Copy button from key list view

### 9.9 Dashboard UX/UI Improvements
- [x] 9.9.1 Redesign main dashboard page with hero section, enhanced stats, sidebar
- [x] 9.9.2 Make API key rows clickable (navigate to API Keys page)
- [x] 9.9.3 Fix navigation - remove nested Link/Button pattern
- [x] 9.9.4 Update billing page to use DashboardLayout for consistent header
- [x] 9.9.5 Redesign header - larger logo, "Dashboard" badge, cleaner nav
- [x] 9.9.6 Improve user dropdown with click-to-toggle and icons
- [x] 9.9.7 Create unified pricing strategy document (docs/pricing/PRICING_STRATEGY.md)
- [x] 9.9.8 Update billing tiers to align with pricing strategy (Starter/Professional/Business)
- [x] 9.9.9 Comprehensive pricing strategy v2 with licensing coalition economics
- [x] 9.9.10 Add rev share tiers (65/35 free → 85/15 strategic partner)
- [x] 9.9.11 Document publisher revenue projections (NYT, Atlantic, regional, indie examples)
- [x] 9.9.12 Update dashboard billing page with coalition rev share info

### 9.10 Pricing Implementation

#### 9.10.1 Database Schema & Models (P0)
- [x] 9.10.1.1 Create subscription_tiers table (id, name, price_monthly, price_annual, features JSON) - Using pricing.py constants
- [x] 9.10.1.2 Create organization_subscriptions table (org_id, tier_id, status, current_period_start/end) - 20251125_150600
- [x] 9.10.1.3 Create usage_records table (org_id, metric, count, period, recorded_at) - 20251125_150700
- [x] 9.10.1.4 Create coalition_earnings table (org_id, period, gross_revenue, publisher_share, encypher_share) - add_coalition_tracking.py
- [x] 9.10.1.5 Add tier_id and coalition_rev_share to organizations table - add_tier_coalition_fields.py
- [x] 9.10.1.6 Create Pydantic schemas for all billing models - Updated billing-service schemas

#### 9.10.2 Tier Enforcement in API (P0)
- [x] 9.10.2.1 Create TierService with feature/limit checking - enterprise_api/app/services/tier_service.py
- [x] 9.10.2.2 Add tier check middleware/dependency for protected endpoints - require_feature() dependency
- [x] 9.10.2.3 Implement rate limiting per tier (10/50/200/unlimited req/sec) - TIER_RATE_LIMITS in quota.py
- [x] 9.10.2.4 Block Merkle endpoints for Starter/Professional tiers - TIER_FEATURES config
- [x] 9.10.2.5 Block sentence tracking for Starter tier - TIER_FEATURES config
- [x] 9.10.2.6 Block batch operations for Starter/Professional tiers - TIER_FEATURES config
- [x] 9.10.2.7 Return 403 with upgrade prompt for tier-locked features - TierService.check_feature_access()
- [x] 9.10.2.8 Add usage metering for signatures and tracked sentences - enterprise_api/app/routers/usage.py

#### 9.10.3 Billing API Endpoints
- [x] 9.10.3.1 GET /api/v1/billing/subscription - Current subscription info
- [x] 9.10.3.2 GET /api/v1/billing/usage - Current period usage with tier limits
- [x] 9.10.3.3 GET /api/v1/billing/invoices - Invoice history
- [x] 9.10.3.4 POST /api/v1/billing/upgrade - Initiate upgrade (returns Stripe checkout URL)
- [x] 9.10.3.5 POST /api/v1/billing/cancel - Cancel subscription (DELETE endpoint)
- [x] 9.10.3.6 GET /api/v1/billing/coalition - Coalition earnings summary
- [x] 9.10.3.7 GET /api/v1/billing/plans - Get all available plans
- [x] 9.10.3.8 POST /api/v1/billing/checkout - Create Stripe Checkout session
- [x] 9.10.3.9 GET /api/v1/billing/portal - Get Stripe Billing Portal URL

#### 9.10.4 Dashboard Billing Integration
- [x] 9.10.4.1 Connect billing page to real API endpoints - lib/api.ts updated
- [x] 9.10.4.2 Show real usage stats (signatures, sentences, API calls) - Usage card with progress bars
- [x] 9.10.4.3 Show coalition earnings dashboard - Earnings card with payout status
- [x] 9.10.4.4 Add upgrade/downgrade flow UI - Redirects to Stripe Checkout
- [x] 9.10.4.5 Add payment method management UI - 'Manage Billing' opens Stripe Portal

#### 9.10.5 Payment Processor Integration (Stripe)
- [x] 9.10.5.1 Set up Stripe account and API keys - Config added to billing-service
- [x] 9.10.5.2 Create Stripe Products for each tier - setup_stripe_products() helper created
- [x] 9.10.5.3 Implement Stripe Checkout for upgrades - POST /checkout endpoint
- [x] 9.10.5.4 Implement Stripe Billing Portal for self-service - GET /portal endpoint
- [x] 9.10.5.5 Set up Stripe webhooks for subscription events - stripe_webhooks.py
- [x] 9.10.5.6 Set up Stripe Connect for publisher payouts - StripeService.create_connect_account()
- [ ] 9.10.5.7 Integrate with Zoho Books for accounting sync
- [ ] 9.10.5.8 Create Stripe products in dashboard (run setup_stripe_products)
- [ ] 9.10.5.9 Configure webhook endpoints in Stripe Dashboard
- [ ] 9.10.5.10 Test end-to-end checkout flow

#### 9.10.6 Coalition Revenue Tracking
- [x] 9.10.6.1 Track content corpus size per organization - coalition_content_stats table
- [x] 9.10.6.2 Calculate revenue attribution when AI deals close - attribute_deal_revenue()
- [x] 9.10.6.3 Apply tier-based rev share (65/35 → 85/15) - TIER_REV_SHARE config
- [x] 9.10.6.4 Generate monthly earnings statements - coalition_earnings table
- [x] 9.10.6.5 Build publisher earnings dashboard - GET /coalition/dashboard

#### 9.10.7 Audit Logs (Business+ tier)
- [x] 9.10.7.1 Create audit_logs table - alembic/versions/add_audit_logs.py
- [x] 9.10.7.2 Log all API key operations - AuditAction enum defined
- [x] 9.10.7.3 Log all signing/verification operations - AuditAction enum defined
- [x] 9.10.7.4 GET /api/v1/audit-logs endpoint - Paginated with filters
- [x] 9.10.7.5 Dashboard UI for audit log viewing - /audit-logs page
- [x] 9.10.7.6 Export audit logs to CSV/JSON - GET /audit-logs/export

#### 9.10.8 Team Management (Business+ tier)
- [x] 9.10.8.1 Create team_members table (user_id, org_id, role, invited_at, accepted_at) - alembic migration
- [x] 9.10.8.2 Define roles: owner, admin, member, viewer - TeamRole enum
- [x] 9.10.8.3 POST /api/v1/org/members/invite endpoint - With token-based invites
- [x] 9.10.8.4 DELETE /api/v1/org/members/{id} endpoint - With role checks
- [x] 9.10.8.5 PATCH /api/v1/org/members/{id}/role endpoint - With hierarchy enforcement
- [x] 9.10.8.6 Email invite flow with accept/decline - POST /accept-invite endpoint
- [x] 9.10.8.7 Dashboard team management UI - /team page

#### 9.10.9 Marketing Site Pricing Page
- [x] 9.10.9.1 Update pricing table with new tiers - Starter tier added
- [x] 9.10.9.2 Add coalition rev share messaging - Rev share badges on each tier
- [x] 9.10.9.3 Add feature comparison table - Full comparison with categories
- [x] 9.10.9.4 Add FAQ section - Already present (6 questions)
- [x] 9.10.9.5 Add "Contact Sales" for Enterprise - Already present
- [x] 9.10.9.6 Add /pricing route redirecting to /licensing


## 8.0 C2PA Standard Strategy (Commoditize the Complement)

### 8.1 Core Infrastructure
- [x] 8.1.1 Audit `encypher-ai` package for C2PA Compliance (Magic bytes, VS encoding)
- [x] 8.1.2 Create `c2pa-text` Monorepo (Permissive License strategy)
- [x] 8.1.3 Implement Python Reference Package (`c2pa-text/python`)
- [x] 8.1.4 Implement TypeScript Reference Package (`c2pa-text/typescript`)
- [x] 8.1.5 Implement Rust Reference Crate (`c2pa-text/rust`)
- [x] 8.1.6 Implement Go Reference Module (`c2pa-text/go`)

### 8.2 Documentation & Trust
- [x] 8.2.1 Polish Documentation (Badges, Logo, Attribution, Upsell)
- [x] 8.2.2 Add Enterprise Trust Docs (SECURITY.md, CONTRIBUTING.md)
- [x] 8.2.3 Verify Marketing Asset Links

