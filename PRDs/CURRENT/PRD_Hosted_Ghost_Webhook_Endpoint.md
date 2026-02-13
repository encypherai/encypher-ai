# PRD: Hosted Ghost Webhook Endpoint

**Status:** Implementation Complete  
**Team:** TEAM_187  
**Created:** 2026-02-13

## Overview

Add a hosted Ghost CMS webhook endpoint to the Enterprise API so users can enable end-to-end C2PA signing of their Ghost content by pointing a single webhook URL at our API — no self-hosted integration service required. Default signing uses `micro_ecc_c2pa` manifest mode with sentence-level embeddings.

## Objectives

- Zero-infrastructure Ghost integration for API users
- Single webhook URL for all Ghost events
- Sensible defaults (micro_ecc_c2pa, sentence-level)
- Reuse existing unified signing service internally
- Store Ghost credentials securely per-organization

## Tasks

### 1.0 Database & Models
- [x] 1.1 Create `ghost_integrations` SQLAlchemy model
- [x] 1.2 Create Alembic migration for `ghost_integrations` table

### 2.0 Schemas
- [x] 2.1 Create Pydantic schemas for Ghost integration CRUD
- [x] 2.2 Create webhook payload schemas

### 3.0 Ghost Integration Service
- [x] 3.1 Ghost Admin API client (JWT auth, read/update posts)
- [x] 3.2 HTML text extraction (port from TypeScript html-utils)
- [x] 3.3 HTML text embedding (port from TypeScript html-utils)
- [x] 3.4 Badge injection logic
- [x] 3.5 Signing orchestration (read → sign → embed → write back)

### 4.0 Router Endpoints
- [x] 4.1 `POST /api/v1/integrations/ghost` — save config
- [x] 4.2 `GET /api/v1/integrations/ghost` — get config (key masked)
- [x] 4.3 `DELETE /api/v1/integrations/ghost` — remove integration
- [x] 4.4 `POST /api/v1/integrations/ghost/webhook` — receive Ghost webhooks
- [x] 4.5 `POST /api/v1/integrations/ghost/sign/{post_id}` — manual sign

### 5.0 Testing
- [x] 5.1 Unit tests for HTML text extraction/embedding — ✅ 12 tests
- [x] 5.2 Unit tests for Ghost Admin API client (JWT) — ✅ 3 tests
- [x] 5.3 Unit tests for webhook payload parsing — ✅ 4 tests
- [x] 5.4 Unit tests for schema validation — ✅ 9 tests
- [x] 5.5 Unit tests for loop prevention — ✅ 4 tests
- [x] 5.6 Unit tests for C2PA detection/stripping — ✅ 6 tests
- [x] 5.7 Unit tests for badge injection — ✅ 5 tests
- [x] 5.8 Unit tests for HTML embedding — ✅ 3 tests
- **Total: 45 tests passing**

### 6.0 Documentation & Wiring
- [x] 6.1 Register router in main.py
- [x] 6.2 Add Traefik route for `/api/v1/integrations`
- [ ] 6.3 Update API docs (auto-generated via FastAPI OpenAPI)

## Success Criteria

- [x] Ghost webhook triggers automatic C2PA signing with default options
- [x] Signed content written back to Ghost post via Admin API
- [x] No infinite webhook loops (in-flight lock)
- [x] All unit tests pass — 45/45
- [x] Integration credentials stored securely per-org

## Technical Design

### Database Table: `ghost_integrations`

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| organization_id | VARCHAR(255) | FK to organization, unique |
| ghost_url | VARCHAR(1000) | Ghost instance URL |
| ghost_admin_api_key | VARCHAR(500) | Encrypted Ghost Admin API key |
| webhook_secret | VARCHAR(255) | Optional webhook verification secret |
| auto_sign_on_publish | BOOLEAN | Default true |
| auto_sign_on_update | BOOLEAN | Default true |
| manifest_mode | VARCHAR(50) | Default 'micro_ecc_c2pa' |
| segmentation_level | VARCHAR(50) | Default 'sentence' |
| badge_enabled | BOOLEAN | Default true |
| created_at | TIMESTAMP | Creation time |
| updated_at | TIMESTAMP | Last update |

### Webhook Authentication

Ghost webhooks don't carry the org's Encypher API key. We use an **opaque webhook token** (`ghwh_...`) scoped to the integration — NOT the org's primary API key.

- Token is generated on integration creation and returned once
- Only the SHA-256 hash is stored in the database
- Token can be regenerated via `POST /api/v1/integrations/ghost/regenerate-token`
- User sets target URL to: `https://api.encypherai.com/api/v1/integrations/ghost/webhook?token=ghwh_xxx`

**Security benefits:**
- Org API key never exposed in webhook URLs or server logs
- Token is independently revocable/rotatable
- Leaked token only grants webhook-trigger access, not full API access

### Loop Prevention

Same approach as the self-hosted integration: in-memory dict of in-flight post IDs with TTL. When we update a Ghost post, the webhook fires again — we skip it if the post is already in-flight.
