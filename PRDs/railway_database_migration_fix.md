# PRD: Railway Database Migration Fix

**Status:** 🔄 IN PROGRESS  
**Date:** November 27, 2025  
**Priority:** P0 - All services failing to boot

## Progress Log

### Nov 27, 2025 - 9:15 PM
- ✅ **Fixed DATABASE_URL issue** - Railway variable references `${{db-auth.DATABASE_URL}}` weren't resolving
- ✅ Set actual DATABASE_URL values directly for all 9 services
- ✅ Redeployed all services
- ✅ **Auth-service is now running!** Migrations completed successfully
- ✅ Created shared database startup library (`encypher_commercial_shared.db`)

### Nov 27, 2025 - 9:10 PM
- ✅ Created 9 PostgreSQL databases on Railway (renamed to db-auth, db-keys, etc.)
- ✅ Linked each database to its corresponding service via `DATABASE_URL`
- ✅ Redeployed all services
- ⚠️ Found schema drift issue: `refresh_tokens` table missing `revoked` column
- ✅ Fixed migration to always check for missing columns
- ❌ Railway variable references not resolving (empty DATABASE_URL)

---

## 1. Problem Statement

All microservices are failing to boot on Railway with errors like:
```
alembic.util.exc.CommandError: Can't locate revision identified by '003'
```

### Root Cause Analysis

There's a **fundamental architecture mismatch** between:

1. **Local Development (Docker)**: Uses **database-per-service** architecture with 9 separate databases
2. **Railway Production**: Uses **two shared databases** (core + content)

Each service has its own Alembic migrations expecting to run against an isolated database, but on Railway they all point to the same shared databases, causing:
- Migration revision conflicts (multiple services trying to track different `001` revisions)
- Schema collisions (services expecting different table structures)
- Missing tables (services expecting tables created by other services' migrations)

---

## 2. Current Architecture Audit

### 2.1 Database Configuration

| Service | Local DB | Railway DB | Alembic Migrations |
|---------|----------|------------|-------------------|
| auth-service | `encypher_auth` | `DATABASE_URL` (core) | `001_initial_schema.py` |
| key-service | `encypher_keys` | `DATABASE_URL` (core) | `001_initial_schema.py` |
| billing-service | `encypher_billing` | `DATABASE_URL` (core) | `001_initial_schema.py` |
| user-service | `encypher_users` | `DATABASE_URL` (core) | `001_initial_schema.py` |
| notification-service | `encypher_notifications` | `DATABASE_URL` (core) | `001_initial_schema.py` |
| encoding-service | `encypher_encoding` | `CONTENT_DATABASE_URL` | `001_initial_schema.py` |
| verification-service | `encypher_verification` | `CONTENT_DATABASE_URL` | `001_initial_schema.py` |
| analytics-service | `encypher_analytics` | `CONTENT_DATABASE_URL` | `001_initial_schema.py` |
| coalition-service | `encypher_coalition` | `CONTENT_DATABASE_URL` | `001_initial_schema.py` |

### 2.2 Shared SQL Migrations (services/migrations/)

| File | Purpose | Target DB |
|------|---------|-----------|
| `001_core_schema.sql` | Core tables (orgs, users, keys) | core |
| `002_enterprise_api_schema.sql` | Content tables (docs, merkle) | content |
| `003_billing_coalition_schema.sql` | Billing & coalition tables | core |
| `004_seed_test_data.sql` | Test data | both |

### 2.3 The Conflict

When services boot on Railway:
1. `auth-service` runs `alembic upgrade head` → creates `alembic_version` table with revision `001`
2. `key-service` runs `alembic upgrade head` → sees `alembic_version` says `001` but expects different schema
3. `billing-service` runs → fails because it expects revision `003` (from shared migrations?)
4. All services fail with revision conflicts

---

## 3. Solution Options

### Option A: Shared Database with Unified Migrations (Recommended)
**Approach:** Use the shared SQL migrations for Railway, disable per-service Alembic

**Pros:**
- Matches Railway's two-database architecture
- Single source of truth for schema
- Simpler deployment

**Cons:**
- Different behavior local vs production
- Need to manually run migrations on Railway

### Option B: Per-Service Schemas (PostgreSQL Schemas)
**Approach:** Each service uses its own PostgreSQL schema within shared DB

**Pros:**
- Maintains service isolation
- Each service can run its own migrations

**Cons:**
- More complex configuration
- Need to update all connection strings

### Option C: Skip Alembic on Railway
**Approach:** Disable `alembic upgrade head` in Dockerfiles for Railway

**Pros:**
- Quick fix
- Services boot immediately

**Cons:**
- Manual migration management
- Risk of schema drift

---

## 4. Implementation Plan (Database-per-Service on Railway)

### Phase 1: Create Databases on Railway ✅

Created 9 PostgreSQL databases on Railway:

| Database | Service | Status |
|----------|---------|--------|
| `db-auth` | auth-service | ✅ Created |
| `db-keys` | key-service | ✅ Created |
| `db-billing` | billing-service | ✅ Created |
| `db-users` | user-service | ✅ Created |
| `db-notifications` | notification-service | ✅ Created |
| `db-encoding` | encoding-service | ✅ Created |
| `db-verification` | verification-service | ✅ Created |
| `db-analytics` | analytics-service | ✅ Created |
| `db-coalition` | coalition-service | ✅ Created |

### Phase 2: Link Databases to Services ✅

Set `DATABASE_URL` environment variable for each service:

```bash
# Commands executed:
railway variables --service auth-service --set "DATABASE_URL=${{db-auth.DATABASE_URL}}"
railway variables --service key-service --set "DATABASE_URL=${{db-keys.DATABASE_URL}}"
railway variables --service billing-service --set "DATABASE_URL=${{db-billing.DATABASE_URL}}"
railway variables --service user-service --set "DATABASE_URL=${{db-users.DATABASE_URL}}"
railway variables --service notification-service --set "DATABASE_URL=${{db-notifications.DATABASE_URL}}"
railway variables --service encoding-service --set "DATABASE_URL=${{db-encoding.DATABASE_URL}}"
railway variables --service verification-service --set "DATABASE_URL=${{db-verification.DATABASE_URL}}"
railway variables --service analytics-service --set "DATABASE_URL=${{db-analytics.DATABASE_URL}}"
railway variables --service coalition-service --set "DATABASE_URL=${{db-coalition.DATABASE_URL}}"
```

### Phase 3: Redeploy Services

- [ ] **3.1** Redeploy all services to pick up new DATABASE_URL
- [ ] **3.2** Verify Alembic migrations run successfully on each service
- [ ] **3.3** Check health endpoints for all services

### Phase 4: Service Configuration Updates

- [ ] **3.1** Audit each service's database expectations
  - [ ] auth-service - needs: users, sessions, refresh_tokens
  - [ ] key-service - needs: organizations, api_keys, key_usage
  - [ ] billing-service - needs: organizations, subscription_history, usage_records
  - [ ] user-service - needs: users, organization_members
  - [ ] notification-service - needs: users, organizations
  - [ ] encoding-service - needs: documents, sentence_records
  - [ ] verification-service - needs: documents, merkle_roots
  - [ ] analytics-service - needs: usage_records
  - [ ] coalition-service - needs: coalition tables

- [ ] **3.2** Update service models to match shared schema
  - Ensure ORM models match `services/migrations/*.sql`

### Phase 4: Testing & Deployment

- [ ] **4.1** Test locally with two-database setup
- [ ] **4.2** Deploy to Railway staging
- [ ] **4.3** Verify all services boot successfully
- [ ] **4.4** Run integration tests

---

## 5. Service-by-Service Audit

### 5.1 auth-service
- **Database:** `DATABASE_URL` (core)
- **Tables Expected:** users, sessions, refresh_tokens, email_verification_tokens
- **Alembic:** `001_initial_schema.py`
- **Status:** ❓ Need to verify schema alignment

### 5.2 key-service
- **Database:** `DATABASE_URL` (core)
- **Tables Expected:** organizations, api_keys, key_usage, key_rotations
- **Alembic:** `001_initial_schema.py`
- **Status:** ❓ Need to verify schema alignment

### 5.3 billing-service
- **Database:** `DATABASE_URL` (core)
- **Tables Expected:** organizations, subscription_history, usage_records, invoices
- **Alembic:** `001_initial_schema.py`
- **Status:** ❓ Need to verify schema alignment

### 5.4 user-service
- **Database:** `DATABASE_URL` (core)
- **Tables Expected:** users, organization_members, user_profiles
- **Alembic:** `001_initial_schema.py`
- **Status:** ❓ Need to verify schema alignment

### 5.5 notification-service
- **Database:** `DATABASE_URL` (core)
- **Tables Expected:** notifications, email_templates
- **Alembic:** `001_initial_schema.py`
- **Status:** ❓ Need to verify schema alignment

### 5.6 encoding-service
- **Database:** `CONTENT_DATABASE_URL` (content)
- **Tables Expected:** documents, sentence_records, signing_operations
- **Alembic:** `001_initial_schema.py`
- **Status:** ❓ Need to verify schema alignment

### 5.7 verification-service
- **Database:** `CONTENT_DATABASE_URL` (content)
- **Tables Expected:** documents, merkle_roots, verification_logs
- **Alembic:** `001_initial_schema.py`
- **Status:** ❓ Need to verify schema alignment

### 5.8 analytics-service
- **Database:** `CONTENT_DATABASE_URL` (content)
- **Tables Expected:** usage_metrics, aggregated_metrics
- **Alembic:** `001_initial_schema.py`
- **Status:** ❓ Need to verify schema alignment

### 5.9 coalition-service
- **Database:** `CONTENT_DATABASE_URL` (content)
- **Tables Expected:** coalition_members, licensing_agreements, revenue_distributions
- **Alembic:** `001_initial_schema.py`
- **Status:** ❓ Need to verify schema alignment

---

## 6. Immediate Fix (Quick Patch)

To unblock Railway deployment immediately:

```dockerfile
# In each service's Dockerfile, change:
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app ..."]

# To:
CMD ["sh", "-c", "if [ \"$SKIP_MIGRATIONS\" != \"true\" ]; then alembic upgrade head; fi && uvicorn app.main:app ..."]
```

Then set `SKIP_MIGRATIONS=true` in Railway for all services.

---

## 7. Success Criteria

- [ ] All 9 microservices boot successfully on Railway
- [ ] No Alembic revision conflicts
- [ ] All API endpoints respond correctly
- [ ] Database schema matches expected tables
- [ ] Health checks pass for all services

---

## 8. Notes

- The `services/migrations/*.sql` files are the source of truth for Railway
- Local development can continue using database-per-service for isolation
- Consider documenting this architecture difference in `docs/architecture/`
