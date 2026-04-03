# TEAM_187 — Hosted Ghost Webhook Endpoint

**Status:** Implementation Complete
**Started:** 2026-02-13
**Task:** Add a hosted Ghost CMS webhook endpoint to the Enterprise API so users can enable end-to-end signing of Ghost content with a single webhook URL — no self-hosted integration service required.

## Design

### User Flow
1. User creates a custom integration in Ghost Admin → gets Admin API key
2. User stores Ghost URL + Admin API key in Encypher dashboard (via `/api/v1/integrations/ghost` endpoint)
3. User points Ghost webhooks at `https://api.encypher.com/api/v1/integrations/ghost/webhook`
4. Our API handles everything: receive webhook → read post → extract text → sign → embed → write back

### Architecture
- New router: `enterprise_api/app/routers/integrations.py`
- New service: `enterprise_api/app/services/ghost_integration.py` (Ghost Admin API client + HTML utils)
- New schemas: `enterprise_api/app/schemas/integration_schemas.py`
- New DB table: `ghost_integrations` (stores per-org Ghost credentials)
- New Alembic migration for the table
- Signing reuses the existing `execute_unified_signing` service internally

### Endpoints
- `POST /api/v1/integrations/ghost` — Save Ghost integration config (URL, admin API key)
- `GET /api/v1/integrations/ghost` — Get current config (key masked)
- `DELETE /api/v1/integrations/ghost` — Remove integration
- `POST /api/v1/integrations/ghost/regenerate-token` — Regenerate webhook token
- `POST /api/v1/integrations/ghost/webhook?token=ghwh_...` — Receive Ghost webhooks (authenticated by scoped token)
- `POST /api/v1/integrations/ghost/sign/{post_id}` — Manual sign trigger

### Default Signing Options
- `manifest_mode`: `micro_ecc_c2pa`
- `segmentation_level`: `sentence`
- `index_for_attribution`: `true`
- `action`: auto-detected (`c2pa.created` / `c2pa.edited`)

## Files Created/Modified

### New Files — Enterprise API
- `enterprise_api/app/models/ghost_integration.py` — SQLAlchemy model with `webhook_token_hash`
- `enterprise_api/app/schemas/integration_schemas.py` — Pydantic schemas for CRUD + webhook + token regeneration
- `enterprise_api/app/services/ghost_integration.py` — Ghost Admin API client, HTML utils, signing orchestration
- `enterprise_api/app/routers/integrations.py` — Router with 6 endpoints (CRUD + regenerate-token + webhook + manual sign)
- `enterprise_api/alembic/versions/20260213_190000_add_ghost_integrations.py` — DB migration
- `enterprise_api/tests/test_ghost_integration.py` — 62 unit tests

### New Files — Dashboard
- `apps/dashboard/src/app/integrations/page.tsx` — Integrations page with card grid
- `apps/dashboard/src/app/integrations/GhostIntegrationCard.tsx` — Ghost 3-step setup wizard + connected state
- `apps/dashboard/src/app/integrations/CopyButton.tsx` — Copy-to-clipboard with visual feedback

### Modified Files
- `enterprise_api/app/models/__init__.py` — Added GhostIntegration import/export
- `enterprise_api/app/main.py` — Registered integrations router
- `enterprise_api/pyproject.toml` — Added PyJWT dependency
- `services/api-gateway/dynamic.yml` — Added `/api/v1/integrations` to Traefik enterprise-api route
- `apps/dashboard/src/lib/api.ts` — Added Ghost integration API methods + types
- `apps/dashboard/src/app/docs/page.tsx` — Added cross-link to Integrations page
- `apps/dashboard/src/components/CommandPalette.tsx` — Added Integrations command

## Test Results
- **62 tests passing** in `enterprise_api/tests/test_ghost_integration.py`
- **Dashboard build passes** (`next build`)
- All imports verified clean

## Session Log
- Researched Enterprise API structure (routers, signing service, schemas)
- Designed hosted endpoint architecture (Option A: Python in Enterprise API)
- Created PRD, model, schemas, service, router, migration, tests
- Fixed void element handling in HTML parser (img tags inside skip cards)
- Added PyJWT dependency for Ghost Admin API JWT auth
- Added Traefik route for `/api/v1/integrations`
- **Security upgrade:** Replaced `?api_key=` with opaque webhook token (`ghwh_...`)
  - Token generated on integration creation, SHA-256 hash stored in DB
  - Token regeneration endpoint added
  - Org API key never exposed in webhook URLs or logs
- Created PRD for Integrations Dashboard page (Ghost, WordPress, future)
- **62 tests passing** (up from 45 after adding token tests)
- Built Integrations page with Ghost setup wizard, CopyButton, connected state
- **Dashboard layout rewrite:** sidebar + header hybrid
  - Deep Navy (#1B2F50) sidebar with grouped nav + icons (matches brand guidelines)
  - Collapsible sidebar (icon-only mode)
  - Slim top header: theme toggle, notifications, user avatar
  - Nav groups: Main, Publish, Insights, Enterprise, Account
  - Fixed tier gating: `free`/`enterprise` only (removed stale `businessOnly`/`starter`)
  - Integrations visible to all users, Webhooks/Team enterprise-only
  - Mobile: slide-out drawer preserved
- **Dashboard UX/UI upgrade** (brand design schema alignment)
  - Sidebar logo: always visible — full logo expanded, checkmark icon collapsed
  - Removed all emojis from Docs page (replaced with branded SVG icons + gradient backgrounds)
  - Removed all emojis from Support page (replaced with branded SVG icons + gradient backgrounds)
  - Standardized all page headers: `text-2xl` + `text-sm text-muted-foreground mt-1` subtitle
  - Pages updated: Overview, Docs, Integrations, Support, Playground, API Keys, Analytics, Settings, Billing, Webhooks, Team
  - Overview: tightened hero messaging, brand-consistent Cyber Teal gradient on Success Rate card, added Integrations to Quick Links, refined C2PA badge copy
  - Docs: removed design-system Card dependency, custom card layout with icon+gradient+arrow pattern
  - Integrations: section labels now use uppercase tracking pattern matching Docs
- **Analytics bug fix:** user identity resolution in analytics-service endpoints
  - Root cause: fabricated `user_{uuid}` prefix when no org_id present didn't match any DB column
  - Fix: added `_resolve_identity()` helper that returns raw `organization_id` or raw `user_id`
  - The service layer's `user_or_org_filter` already checks both `UsageMetric.user_id` and `UsageMetric.organization_id` columns
  - Fixed all 8 endpoint functions in `analytics-service/app/api/v1/endpoints.py`
  - Result: test user now sees 283 API calls, 134 docs signed, 53 verifications, 99.8% success rate
- **Analytics page layout upgrade**
  - Stat cards: upgraded to match Overview's icon+gradient treatment (branded SVG icons)
  - Bar chart: added Y-axis labels, gradient bars, hover tooltips, axis lines
  - Removed redundant "Getting Started" and "Need Help?" sections (already on Overview)
- **Analytics chart fix:** bars were invisible because percentage heights didn't resolve
  - Root cause: parent flex children lacked explicit `height: 100%` for percentage-based bar heights
  - Fix: added `style={{ height: '100%' }}` to bar wrapper divs
- **Fake Operational Notes replaced** with accurate "Quick Reference" tips
  - Old notes claimed features that don't exist (audit log exports, webhook alerting, compliance snapshots)
  - New tips reference real functionality: time range selector, CSV export, latency targets
- **Tier gating audit and fix** across entire dashboard
  - `audit-logs/page.tsx`: `['business', 'enterprise']` → `userTier === 'enterprise'`; default `'starter'` → `'free'`; CTA "Upgrade to Business" → "Upgrade to Enterprise"
  - `team/page.tsx`: same pattern — removed stale `business` tier, fixed default and CTA
  - `playground/page.tsx`: simplified `Tier` type from 4 values to `'free' | 'enterprise'`; updated `tierOrder`, `tierColors`, `tierLabels`
  - `TemplateSelector.tsx`: "Business+ tier required" → "Enterprise tier required"
  - `api.ts`: updated 2 JSDoc comments from "Business+" to "Enterprise"
  - `DashboardLayout.tsx`: added `IconAuditLogs` component; added Audit Logs to Enterprise nav group
- **FEATURE_MATRIX.md rewritten** (v1.0 → v2.0)
  - Replaced stale 4-tier model (Free/Pro/Business/Enterprise) with actual 2-tier (Free + Enterprise)
  - Added: add-ons table, bundles table, revenue share, enterprise sub-tiers, dashboard gating implementation section
  - All features now accurately reflect what's implemented vs. what's enterprise-only
- **Full documentation SSOT audit and cleanup** (3-phase)
  - Phase 1: Fixed 3 critical SSOT docs
    - `README.md`: rewrote Product Tiers section to 2-tier model, fixed Architecture Decision section, added SSOT reference table in Documentation section, fixed deprecated `enterprise_sdk` link
    - `docs/pricing/PRICING_STRATEGY.md`: v2.2 → v3.0 rewrite — consolidated to 2-tier, updated all 8 revenue projection examples, fixed rev share tables (60/40 coalition, 80/20 self-service), replaced inline feature matrix with pointer to FEATURE_MATRIX.md, fixed GTM pricing alignment table, fixed implementation checklist tier references
    - `DOCUMENTATION_INDEX.md`: fixed all stale tier refs (Free/Professional → Free), removed deprecated `enterprise_sdk` links, updated Quick Start to point to FEATURE_MATRIX + PRICING_STRATEGY instead of archived audit docs, fixed service port list
  - Phase 2: Archived stale completion docs
    - Moved to `docs/archive/`: AUDIT_COMPLETE.md, IMPLEMENTATION_COMPLETE.md, DOCUMENTATION_AUDIT.md, STREAMING_FEATURES_SUMMARY.md
    - Created `docs/archive/README.md` explaining why each was archived
    - Fixed `MICROSERVICES_FEATURES.md`: "Free, Professional, Enterprise" → "Free, Enterprise"
  - Phase 3: Established SSOT pointers
    - Added SSOT reference table to README.md Documentation section (6 topics with canonical locations)
    - All docs now point to `packages/pricing-config/src/` and `FEATURE_MATRIX.md` as the SSOTs
  - Note: ~526 stale tier references remain in PRDs, team files, SDK auto-generated docs, and node_modules — these are historical/generated and not worth chasing

## Suggested Git Commit Message

```
feat: hosted Ghost webhook endpoint + Integrations dashboard page

Backend (enterprise-api):
- POST/GET/DELETE /api/v1/integrations/ghost — CRUD for Ghost config
- POST /api/v1/integrations/ghost/regenerate-token — rotate webhook token
- POST /api/v1/integrations/ghost/webhook?token=ghwh_... — receive webhooks
- POST /api/v1/integrations/ghost/sign/{post_id} — manual sign trigger
- Ghost Admin API client with JWT auth (PyJWT)
- HTML text extraction/embedding ported from TypeScript ghost-provenance
- Loop prevention via in-flight lock with TTL
- Badge injection into Ghost codeinjection_foot
- Default signing: micro_ecc_c2pa + sentence-level + attribution indexing
- Alembic migration for ghost_integrations table
- Traefik route added for /api/v1/integrations

Security:
- Webhook auth uses scoped opaque token (ghwh_...) not org API key
- Token SHA-256 hashed for storage, shown once on creation
- Independently revocable via regenerate-token endpoint

Dashboard (apps/dashboard):
- Sidebar + header hybrid layout (replaces top nav bar)
  - Deep Navy (#1B2F50) sidebar with grouped nav + icons
  - Collapsible to icon-only mode (checkmark logo when collapsed)
  - Slim top header: theme toggle, notifications, user avatar
  - Nav groups: Main, Publish, Insights, Enterprise, Account
- /integrations page with card grid (Ghost, WordPress, Substack, Medium)
- Ghost 3-step setup wizard (URL → API key → copy webhook URL)
- CopyButton component with visual feedback
- Connected state: stats, config summary, regenerate token, disconnect
- Cross-links from Docs page, CommandPalette integration
- Fixed tier gating: free/enterprise only (removed stale businessOnly)
- UX/UI design upgrade across all dashboard pages:
  - Removed all emojis (Docs, Support) → branded SVG icons with gradient bgs
  - Standardized page headers (text-2xl + subtitle) across 11 pages
  - Brand-consistent color palette (Deep Navy, Azure Blue, Cyber Teal)
  - Overview: tightened messaging, Integrations quick link, C2PA badge copy

Bug fix (analytics-service):
- Fixed user identity resolution in all analytics endpoints
- Removed fabricated `user_` prefix that didn't match DB data
- Added `_resolve_identity()` helper for consistent identity extraction
- Analytics data now correctly returned for users with/without organizations

Bug fix (analytics chart):
- Fixed invisible bars: added explicit height context for percentage-based sizing
- Replaced fake "Operational Notes" with accurate "Quick Reference" tips

Tier gating cleanup:
- Removed stale Professional/Business tiers from all dashboard code
- Simplified to 2-tier model: free + enterprise
- Fixed audit-logs, team, playground, TemplateSelector, api.ts
- Added Audit Logs to sidebar Enterprise nav group with icon
- FEATURE_MATRIX.md rewritten v1.0 → v2.0 (2-tier + add-ons)

Tests: 62 enterprise API tests passing, dashboard build clean

Ref: PRDs/CURRENT/PRD_Hosted_Ghost_Webhook_Endpoint.md
Ref: PRDs/CURRENT/PRD_Integrations_Dashboard_Page.md
```
