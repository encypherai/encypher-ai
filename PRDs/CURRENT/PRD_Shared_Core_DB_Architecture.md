# PRD: Shared Core Database Architecture

## Status: Backlog
## Current Goal: Define optimal database architecture for microservices

---

## Overview

Migrate from 13 separate PostgreSQL databases to a **Shared Core + Domain DBs** architecture. This consolidates tightly-coupled identity/auth/billing data into a single shared database while keeping domain-specific data in isolated databases for scalability and security.

---

## Problem Statement

### Current State
- 13 separate PostgreSQL databases on Railway
- Services need cross-database queries that fail (e.g., key-service querying `users.is_super_admin`)
- Data duplication and sync issues between services
- Hardcoded workarounds required (superadmin user IDs)

### Root Cause
Services like `auth-service`, `key-service`, and `billing-service` share a core domain model (users, organizations, API keys) but have separate databases, creating tight coupling across database boundaries.

### Impact
- API key validation fails when checking superadmin status
- Organization tier/features not accessible across services
- Increased latency from cross-service API calls
- Maintenance burden of keeping data in sync

---

## Objectives

- [ ] Consolidate core identity/auth/billing tables into shared database
- [ ] Maintain domain-specific databases for content, analytics, coalition
- [ ] Enable direct SQL queries for cross-cutting concerns
- [ ] Remove hardcoded workarounds (superadmin user IDs)
- [ ] Preserve service autonomy for domain-specific data

---

## Proposed Architecture

### Database Structure

```
┌─────────────────────────────────────────────────────────────────┐
│                    SHARED CORE DATABASE                          │
│                    (postgres-core)                               │
├─────────────────────────────────────────────────────────────────┤
│  users              │ id, email, name, is_super_admin, ...      │
│  organizations      │ id, name, tier, features, limits, ...     │
│  organization_members│ org_id, user_id, role, ...               │
│  api_keys           │ id, org_id, user_id, key_hash, perms, ... │
│  subscriptions      │ org_id, tier, stripe_id, status, ...      │
│  refresh_tokens     │ user_id, token, expires_at, ...           │
│  password_reset_tokens│ user_id, token, expires_at, ...         │
│  email_verification_tokens│ user_id, token, expires_at, ...     │
└─────────────────────────────────────────────────────────────────┘
        ↑ READ/WRITE: auth-service, key-service, billing-service
        ↑ READ-ONLY: enterprise-api, all other services

┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐
│  CONTENT DATABASE   │  │  ANALYTICS DATABASE │  │  COALITION DATABASE │
│  (postgres-content) │  │  (postgres-analytics)│  │  (postgres-coalition)│
├─────────────────────┤  ├─────────────────────┤  ├─────────────────────┤
│  documents          │  │  events             │  │  coalition_members  │
│  merkle_trees       │  │  metrics            │  │  coalition_content  │
│  sentence_records   │  │  aggregations       │  │  licensing_agreements│
│  manifests          │  │  usage_history      │  │  revenue_distributions│
│  embeddings         │  │                     │  │                     │
│  revocation_lists   │  │                     │  │                     │
└─────────────────────┘  └─────────────────────┘  └─────────────────────┘
        ↑ enterprise-api         ↑ analytics-service    ↑ coalition-service

┌─────────────────────┐  ┌─────────────────────┐
│  BILLING LEDGER DB  │  │  NOTIFICATIONS DB   │
│  (postgres-billing) │  │  (postgres-notif)   │
├─────────────────────┤  ├─────────────────────┤
│  invoices           │  │  notifications      │
│  payments           │  │  email_queue        │
│  payment_methods    │  │  delivery_status    │
│  stripe_events      │  │                     │
└─────────────────────┘  └─────────────────────┘
        ↑ billing-service        ↑ notification-service
```

### Service-to-Database Mapping

| Service | Shared Core (RW) | Shared Core (RO) | Domain DB |
|---------|------------------|------------------|-----------|
| auth-service | ✅ | - | - |
| key-service | ✅ | - | - |
| billing-service | ✅ | - | postgres-billing |
| enterprise-api | - | ✅ | postgres-content |
| analytics-service | - | ✅ | postgres-analytics |
| coalition-service | - | ✅ | postgres-coalition |
| notification-service | - | ✅ | postgres-notif |
| encoding-service | - | ✅ | postgres-content |
| verification-service | - | ✅ | postgres-content |

### Connection Strategy

```python
# Services with write access to core
CORE_DATABASE_URL = "postgres://...@postgres-core.railway.internal/railway"

# Services with read-only access to core
CORE_DATABASE_URL_READONLY = "postgres://readonly_user:...@postgres-core.railway.internal/railway"

# Domain-specific databases
CONTENT_DATABASE_URL = "postgres://...@postgres-content.railway.internal/railway"
```

---

## Tasks

### 1.0 Preparation
- [ ] 1.1 Document current database schemas for all 13 databases
- [ ] 1.2 Identify all cross-service data dependencies
- [ ] 1.3 Create consolidated schema for shared core database
- [ ] 1.4 Create read-only PostgreSQL user for core database

### 2.0 Database Migration
- [ ] 2.1 Create new `postgres-core` database on Railway
- [ ] 2.2 Run consolidated schema migration on postgres-core
- [ ] 2.3 Export data from db-auth (users, organizations, org_members, tokens)
- [ ] 2.4 Export data from db-keys (api_keys)
- [ ] 2.5 Import all data to postgres-core
- [ ] 2.6 Verify data integrity (row counts, foreign keys)

### 3.0 Service Updates
- [ ] 3.1 Update auth-service to use postgres-core
- [ ] 3.2 Update key-service to use postgres-core
- [ ] 3.3 Update billing-service to use postgres-core + postgres-billing
- [ ] 3.4 Update enterprise-api to use postgres-core (RO) + postgres-content
- [ ] 3.5 Update analytics-service to use postgres-core (RO) + postgres-analytics
- [ ] 3.6 Update coalition-service to use postgres-core (RO) + postgres-coalition
- [ ] 3.7 Update remaining services for postgres-core (RO)

### 4.0 Code Cleanup
- [ ] 4.1 Remove hardcoded superadmin user IDs from key-service
- [ ] 4.2 Remove cross-service API calls that are now direct queries
- [ ] 4.3 Update Alembic migrations to target correct databases
- [ ] 4.4 Update docker-compose for local development

### 5.0 Testing & Validation
- [ ] 5.1 Test auth flow end-to-end
- [ ] 5.2 Test API key generation and validation
- [ ] 5.3 Test superadmin access without hardcodes
- [ ] 5.4 Test enterprise-api signing with org context
- [ ] 5.5 Load test to verify no performance regression

### 6.0 Deprecation
- [ ] 6.1 Keep old databases for 1 week as backup
- [ ] 6.2 Monitor for any issues
- [ ] 6.3 Delete deprecated databases (db-auth, db-keys, db-users)

---

## Success Criteria

- [ ] All services can query user/org data without cross-service API calls
- [ ] Superadmin check works via direct SQL query
- [ ] No hardcoded user IDs in codebase
- [ ] API key validation includes full org context
- [ ] Domain databases remain isolated (content, analytics, coalition)
- [ ] No data loss during migration
- [ ] No downtime during migration (blue-green deployment)

---

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Data loss during migration | Low | High | Full backup before migration, verify row counts |
| Downtime during cutover | Medium | Medium | Blue-green deployment, feature flags |
| Schema conflicts | Medium | Medium | Document all schemas first, resolve conflicts |
| Performance regression | Low | Medium | Load test before/after, monitor latency |

---

## Databases to Consolidate

### Into postgres-core (DELETE after migration)
- `db-auth` → users, sessions, oauth_tokens, refresh_tokens, password_reset_tokens
- `db-keys` → api_keys (organizations already in db-auth)
- `db-users` → profiles (merge with users table)

### Keep as Domain DBs
- `Postgres-Core` → rename to `postgres-content`
- `Postgres-Content` → merge into `postgres-content`
- `db-analytics` → keep as `postgres-analytics`
- `db-coalition` → keep as `postgres-coalition`
- `db-billing` → keep as `postgres-billing`
- `db-notifications` → keep as `postgres-notif`

### Evaluate for Removal
- `db-encoding` → likely merge into postgres-content
- `db-verification` → likely merge into postgres-content
- `db-web` → evaluate purpose, likely remove

---

## Timeline Estimate

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| Preparation | 4 hours | None |
| Database Migration | 2 hours | Preparation complete |
| Service Updates | 8 hours | Migration complete |
| Code Cleanup | 2 hours | Services updated |
| Testing | 4 hours | All updates complete |
| Deprecation | 1 week monitoring | Testing passed |

**Total Active Work**: ~20 hours (2-3 days)

---

## Completion Notes

_To be filled after implementation_
