# Database Migrations

## Two-Database Architecture

Encypher uses a **two-database architecture** for security, scalability, and compliance:

### Core Database (`encypher_core`)
**Purpose:** Sensitive customer and billing data

**Tables:**
- `organizations` - Billing entities, subscriptions, certificates
- `users` - User accounts
- `organization_members` - User-org relationships
- `organization_invites` - Pending invitations
- `api_keys` - API key management
- `sessions` - User sessions
- `refresh_tokens` - Auth tokens
- `subscription_history` - Billing history
- `usage_records` - API usage tracking
- `key_usage` - Key usage metrics
- `key_rotations` - Key rotation history
- `certificate_lifecycle` - SSL.com certificate tracking
- `batch_requests` - Batch operation tracking
- `batch_items` - Batch item details
- `c2pa_assertion_schemas` - Custom C2PA schemas
- `c2pa_assertion_templates` - C2PA templates
- `audit_logs` - Security audit trail

**Access:** Requires authentication. Contains PII and billing data.

### Content Database (`encypher_content`)
**Purpose:** Verification and content data (semi-public)

**Tables:**
- `documents` - Signed documents with C2PA manifests
- `sentence_records` - Individual sentences for plagiarism detection
- `merkle_roots` - Merkle tree root hashes
- `merkle_subhashes` - Merkle tree nodes
- `merkle_proof_cache` - Cached verification proofs
- `content_references` - Signed content embeddings
- `attribution_reports` - Plagiarism scan results

**Access:** Verification queries can be public. No PII stored.

## Directory Structure

```
services/migrations/
├── README.md                    # This file
├── core_db/                     # Core database migrations
│   ├── 001_core_schema.sql      # Main schema
│   └── 002_seed_test_data.sql   # Test data
└── content_db/                  # Content database migrations
    └── 001_content_schema.sql   # Main schema
```

## Environment Variables

```bash
# Core Database (customer/billing data)
CORE_DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/encypher_core

# Content Database (verification data)
CONTENT_DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/encypher_content

# Legacy (falls back to core)
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/encypher_core
```

## Railway Deployment

On Railway, create two PostgreSQL services:

1. **encypher-core-db**
   - Database name: `encypher_core`
   - Run migrations from `core_db/`

2. **encypher-content-db**
   - Database name: `encypher_content`
   - Run migrations from `content_db/`

Set environment variables in your Railway service:
```
CORE_DATABASE_URL=${{encypher-core-db.DATABASE_URL}}
CONTENT_DATABASE_URL=${{encypher-content-db.DATABASE_URL}}
```

## Local Development (Docker)

The `docker-compose.full-stack.yml` automatically creates both databases:

```bash
# Start both databases
docker-compose -f docker-compose.full-stack.yml up -d postgres-core postgres-content

# Migrations run automatically via docker-entrypoint-initdb.d
```

## Benefits

1. **Security Isolation** - Customer data separated from public verification data
2. **Scalability** - Scale verification workloads independently
3. **Compliance** - Different retention policies per database
4. **Performance** - Heavy verification queries don't impact auth/billing
5. **Cost Optimization** - Right-size each database for its workload
