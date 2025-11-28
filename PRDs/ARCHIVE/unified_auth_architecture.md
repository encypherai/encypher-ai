# Unified Authentication & Organization Architecture

**Status:** ✅ COMPLETE (Core Architecture)  
**Date:** November 25, 2025  
**Completed:** November 27, 2025  
**Author:** Cascade AI  
**Note:** Phase 4 (Auth Service JWT updates) deferred - current API key auth is sufficient  

## 1. Executive Summary

The current architecture has a **split-brain authentication problem** where the Enterprise API and Microservices maintain separate, incompatible data models for API keys and organizations. This prevents:
- Proper tier-based feature gating
- Unified billing and usage tracking
- Consistent API key management across services
- Automated testing with different tier configurations

This PRD defines the migration to a **unified authentication architecture** with a single source of truth.

---

## 2. Current State (Problem)

### 2.1 Data Model Conflicts

| Aspect | Microservices (Key Service) | Enterprise API |
|--------|---------------------------|----------------|
| **API Keys Table** | `api_keys` (user_id, key_hash, permissions) | `api_keys` (api_key, organization_id, can_sign) |
| **User/Org Model** | `users` table (user-centric) | `organizations` table (org-centric) |
| **Tier Storage** | `users.tier` | `organizations.tier` |
| **Auth Method** | JWT tokens + API key hash lookup | Bearer token + demo key bypass |

### 2.2 Architecture Diagram (Current - Broken)

```
┌─────────────────────────────────────────────────────────────────┐
│                     Shared PostgreSQL Database                   │
├─────────────────────────────────────────────────────────────────┤
│  api_keys (microservices)  │  organizations (enterprise_api)    │
│  - id, user_id, key_hash   │  - organization_id, tier           │
│  - permissions (JSON)      │  - can_sign, can_verify            │
│  - NO organization link    │  - NO user link                    │
│                            │                                     │
│  users                     │  api_keys (CONFLICT - different    │
│  - id, email, tier         │    schema expected by enterprise)  │
└─────────────────────────────────────────────────────────────────┘
         │                              │
         ▼                              ▼
┌─────────────────┐            ┌─────────────────┐
│  Key Service    │            │  Enterprise API │
│  Auth Service   │            │  (demo bypass)  │
│  Billing Service│            │                 │
└─────────────────┘            └─────────────────┘
```

### 2.3 Specific Issues

1. **No Organization Concept in Microservices**: Key Service tracks `user_id` but Enterprise API needs `organization_id` with tier/features
2. **Incompatible API Key Schemas**: Cannot share keys between services
3. **Demo Key Bypass**: Enterprise API hardcodes demo keys instead of using proper auth
4. **No Unified Tier Management**: Tier is stored in both `users.tier` and `organizations.tier`
5. **Testing Impossible**: Cannot create test organizations with different tiers

---

## 3. Target State (Solution)

### 3.1 Unified Data Model

```sql
-- Organizations: The billing/subscription entity
CREATE TABLE organizations (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE,
    
    -- Subscription/Tier
    tier VARCHAR(32) NOT NULL DEFAULT 'starter',  -- starter, professional, business, enterprise
    stripe_customer_id VARCHAR(255),
    stripe_subscription_id VARCHAR(255),
    
    -- Feature flags (derived from tier, can be overridden)
    features JSONB NOT NULL DEFAULT '{}',
    
    -- Usage limits
    monthly_api_limit INTEGER DEFAULT 10000,
    monthly_api_usage INTEGER DEFAULT 0,
    
    -- Coalition
    coalition_member BOOLEAN DEFAULT TRUE,
    coalition_rev_share INTEGER DEFAULT 65,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

-- Users: Individual accounts (can belong to organizations)
CREATE TABLE users (
    id VARCHAR(64) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    hashed_password VARCHAR(255),
    
    -- OAuth
    oauth_provider VARCHAR(32),
    oauth_id VARCHAR(255),
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    last_login TIMESTAMPTZ
);

-- Organization Members: Links users to organizations with roles
CREATE TABLE organization_members (
    id VARCHAR(64) PRIMARY KEY,
    organization_id VARCHAR(64) NOT NULL REFERENCES organizations(id),
    user_id VARCHAR(64) NOT NULL REFERENCES users(id),
    role VARCHAR(32) NOT NULL DEFAULT 'member',  -- owner, admin, member, viewer
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(organization_id, user_id)
);

-- API Keys: Tied to organizations, not users
CREATE TABLE api_keys (
    id VARCHAR(64) PRIMARY KEY,
    organization_id VARCHAR(64) NOT NULL REFERENCES organizations(id),
    
    -- Key data
    name VARCHAR(255) NOT NULL,
    key_hash VARCHAR(255) NOT NULL UNIQUE,
    key_prefix VARCHAR(20) NOT NULL,  -- For display: "ency_abc..."
    
    -- Permissions (can restrict below org tier)
    permissions JSONB NOT NULL DEFAULT '["sign", "verify", "lookup"]',
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_revoked BOOLEAN DEFAULT FALSE,
    
    -- Usage
    last_used_at TIMESTAMPTZ,
    usage_count INTEGER DEFAULT 0,
    
    -- Metadata
    created_by VARCHAR(64) REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    revoked_at TIMESTAMPTZ
);
```

### 3.2 Architecture Diagram (Target)

```
┌─────────────────────────────────────────────────────────────────┐
│                     Shared PostgreSQL Database                   │
├─────────────────────────────────────────────────────────────────┤
│  organizations          │  users              │  api_keys       │
│  - id, name, tier       │  - id, email        │  - id, org_id   │
│  - features (JSONB)     │  - hashed_password  │  - key_hash     │
│  - stripe_customer_id   │                     │  - permissions  │
│                         │                     │                 │
│  organization_members   │                     │                 │
│  - org_id, user_id      │                     │                 │
│  - role                 │                     │                 │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
              ▼               ▼               ▼
      ┌───────────┐   ┌───────────┐   ┌───────────┐
      │   Auth    │   │   Key     │   │Enterprise │
      │  Service  │   │  Service  │   │   API     │
      │(JWT/OAuth)│   │(API Keys) │   │(C2PA ops) │
      └───────────┘   └───────────┘   └───────────┘
              │               │               │
              └───────────────┼───────────────┘
                              ▼
                    ┌─────────────────┐
                    │  Unified Auth   │
                    │  Middleware     │
                    │  (validates &   │
                    │   returns org)  │
                    └─────────────────┘
```

### 3.3 Authentication Flow

```
1. Request arrives with Bearer token (API key)
2. Key Service validates:
   - Hash lookup in api_keys table
   - Check is_active, is_revoked, expires_at
   - Load organization with tier/features
3. Return to caller:
   {
     "organization_id": "org_xxx",
     "organization_name": "Acme Corp",
     "tier": "business",
     "features": {
       "team_management": true,
       "audit_logs": true,
       "merkle_enabled": true,
       ...
     },
     "permissions": ["sign", "verify", "lookup"]
   }
4. Enterprise API uses this for authorization
```

---

## 4. Work Breakdown Structure (WBS)

### Phase 1: Database Schema Migration (P0) ✅
- [x] **1.1** Create unified schema with `organizations` table (001_core_schema.sql)
- [x] **1.2** Create `users` and `organization_members` tables
- [x] **1.3** Create unified `api_keys` table with `organization_id`
- [x] **1.4** Add `features` JSONB column with tier-based defaults
- [x] **1.5** Create seed data script for test organizations (004_seed_test_data.sql)

### Phase 2: Key Service Updates (P0) ✅
- [x] **2.1** Update Key Service models to use `organization_id`
- [x] **2.2** Add `/api/v1/keys/validate` endpoint that returns org + tier + features
- [x] **2.3** Add Organization model to Key Service
- [ ] **2.4** Update key creation to require `organization_id` (needs service update)

### Phase 3: Enterprise API Integration (P0) ✅
- [x] **3.1** Update `dependencies.py` with tier-specific demo keys
- [x] **3.2** Update `get_current_organization` to call Key Service /validate
- [x] **3.3** Update `key_service_client.py` to use /validate endpoint
- [x] **3.4** Add `_normalize_org_context` for consistent response structure

### Phase 4: Auth Service Updates (P1)
- [ ] **4.1** Add organization context to JWT tokens
- [ ] **4.2** Update login flow to include organization selection (for multi-org users)
- [ ] **4.3** Add organization creation on first signup (default: Starter tier)

### Phase 5: Testing Infrastructure (P0) ✅
- [x] **5.1** Update `start-dev.ps1` to run migrations on Docker startup
- [x] **5.2** Create seed data for all tiers (demo, starter, professional, business, enterprise)
- [x] **5.3** Update test fixtures in `conftest.py` with tier-specific API keys
- [x] **5.4** Run full test suite to verify - 46 core API tests passing

### Phase 6: Documentation & Cleanup (P2)
- [ ] **6.1** Update architecture diagrams in README
- [ ] **6.2** Document the unified auth flow
- [ ] **6.3** Remove deprecated code (old api_keys schema references)

---

## 5. Migration Strategy

### 5.1 Database Migration Order

```sql
-- Step 1: Add organization_id to api_keys (nullable initially)
ALTER TABLE api_keys ADD COLUMN organization_id VARCHAR(64);

-- Step 2: Create organizations table
CREATE TABLE IF NOT EXISTS organizations (...);

-- Step 3: Create default organization for existing keys
INSERT INTO organizations (id, name, tier) 
VALUES ('org_default', 'Default Organization', 'starter');

-- Step 4: Link existing keys to default org
UPDATE api_keys SET organization_id = 'org_default' WHERE organization_id IS NULL;

-- Step 5: Make organization_id NOT NULL
ALTER TABLE api_keys ALTER COLUMN organization_id SET NOT NULL;

-- Step 6: Add foreign key constraint
ALTER TABLE api_keys ADD CONSTRAINT fk_api_keys_org 
    FOREIGN KEY (organization_id) REFERENCES organizations(id);
```

### 5.2 Backward Compatibility

During migration:
1. Key Service accepts keys with or without organization_id
2. Enterprise API falls back to demo behavior if Key Service unavailable
3. Gradual rollout: Enable unified auth per-environment

---

## 6. Test Data Seed

```sql
-- Starter Tier (basic features only)
INSERT INTO organizations (id, name, tier, features) VALUES
('org_starter', 'Starter Test Org', 'starter', '{
  "team_management": false,
  "audit_logs": false,
  "merkle_enabled": false,
  "max_team_members": 1
}');

-- Professional Tier
INSERT INTO organizations (id, name, tier, features) VALUES
('org_professional', 'Professional Test Org', 'professional', '{
  "team_management": false,
  "audit_logs": false,
  "merkle_enabled": false,
  "sentence_tracking": true,
  "max_team_members": 5
}');

-- Business Tier (team management, audit logs)
INSERT INTO organizations (id, name, tier, features) VALUES
('org_business', 'Business Test Org', 'business', '{
  "team_management": true,
  "audit_logs": true,
  "merkle_enabled": true,
  "max_team_members": 10
}');

-- Enterprise Tier (all features)
INSERT INTO organizations (id, name, tier, features) VALUES
('org_enterprise', 'Enterprise Test Org', 'enterprise', '{
  "team_management": true,
  "audit_logs": true,
  "merkle_enabled": true,
  "sso_enabled": true,
  "max_team_members": -1
}');

-- API Keys for each org
INSERT INTO api_keys (id, organization_id, name, key_hash, key_prefix, permissions) VALUES
('key_starter', 'org_starter', 'Starter Key', 'hash_starter', 'ency_sta', '["sign","verify"]'),
('key_professional', 'org_professional', 'Professional Key', 'hash_prof', 'ency_pro', '["sign","verify","lookup"]'),
('key_business', 'org_business', 'Business Key', 'hash_bus', 'ency_bus', '["sign","verify","lookup"]'),
('key_enterprise', 'org_enterprise', 'Enterprise Key', 'hash_ent', 'ency_ent', '["sign","verify","lookup"]');
```

---

## 7. Success Criteria

1. **Single Source of Truth**: All services use the same `organizations` and `api_keys` tables
2. **Tier-Based Testing**: Tests can authenticate as different tiers and verify feature gating
3. **Zero Demo Bypasses**: No hardcoded keys in application code
4. **Automated Setup**: `docker-compose up` creates all necessary tables and seed data
5. **All Tests Pass**: Existing + new tests pass with unified auth

---

## 8. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Breaking existing API keys | High | Migration script preserves existing keys |
| Service downtime during migration | Medium | Blue-green deployment, feature flags |
| Performance regression | Medium | Redis caching for key validation |
| Test flakiness | Low | Deterministic seed data, isolated test DBs |

---

## 9. Timeline

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| Phase 1: DB Migration | 2 hours | None |
| Phase 2: Key Service | 3 hours | Phase 1 |
| Phase 3: Enterprise API | 2 hours | Phase 2 |
| Phase 4: Auth Service | 2 hours | Phase 1 |
| Phase 5: Testing | 2 hours | Phase 3 |
| Phase 6: Documentation | 1 hour | Phase 5 |

**Total Estimated Time: 12 hours**

---

## 10. Appendix: Feature Flags by Tier

| Feature | Starter | Professional | Business | Enterprise |
|---------|---------|--------------|----------|------------|
| C2PA Signing | ✅ | ✅ | ✅ | ✅ |
| C2PA Verification | ✅ | ✅ | ✅ | ✅ |
| Sentence Tracking | ❌ | ✅ | ✅ | ✅ |
| Streaming API | ❌ | ✅ | ✅ | ✅ |
| Merkle Trees | ❌ | ❌ | ✅ | ✅ |
| Batch Operations | ❌ | ❌ | ✅ | ✅ |
| Team Management | ❌ | ❌ | ✅ | ✅ |
| Audit Logs | ❌ | ❌ | ✅ | ✅ |
| BYOK | ❌ | ❌ | ✅ | ✅ |
| SSO/SAML | ❌ | ❌ | ❌ | ✅ |
| Custom Assertions | ❌ | ❌ | ❌ | ✅ |
| Max Team Members | 1 | 5 | 10 | Unlimited |
| Coalition Rev Share | 65% | 70% | 80% | 85% |
