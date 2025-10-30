# Backend Architecture Recommendations

**Version:** 1.0  
**Last Updated:** October 28, 2025  
**Status:** Architectural Decision Record (ADR)

## Executive Summary

**Recommendation:** Start with a **unified monolithic architecture** with a **single PostgreSQL database** for V1, then evolve to **logical database separation** (schemas) as you scale, and finally to **physical database separation** only when necessary (>100K organizations or specific performance bottlenecks).

**Rationale:**
- ✅ Faster development and deployment
- ✅ Simpler operations and maintenance
- ✅ Lower infrastructure costs
- ✅ Easier transactions and data consistency
- ✅ PostgreSQL can handle millions of records efficiently
- ✅ Can refactor later without breaking APIs

## Architecture Decision

### Decision: Unified Backend with Single Database (V1)

```
┌─────────────────────────────────────────────────────────┐
│                   encypherai.com                        │
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │         FastAPI Application (Monolith)          │  │
│  │                                                  │  │
│  │  ┌──────────────┐  ┌──────────────┐            │  │
│  │  │   Website    │  │ Enterprise   │            │  │
│  │  │   Routes     │  │  API Routes  │            │  │
│  │  │              │  │              │            │  │
│  │  │ /            │  │ /api/v1/sign │            │  │
│  │  │ /verify/     │  │ /api/v1/verify│           │  │
│  │  │ /dashboard/  │  │ /api/v1/merkle│           │  │
│  │  └──────────────┘  └──────────────┘            │  │
│  │                                                  │  │
│  │  ┌──────────────────────────────────────────┐  │  │
│  │  │        Shared Business Logic             │  │  │
│  │  │  - Signing Service                       │  │  │
│  │  │  - Verification Service                  │  │  │
│  │  │  - Merkle Service                        │  │  │
│  │  │  - Certificate Service                   │  │  │
│  │  └──────────────────────────────────────────┘  │  │
│  └─────────────────────────────────────────────────┘  │
│                         ↓                              │
│  ┌─────────────────────────────────────────────────┐  │
│  │      Single PostgreSQL Database                 │  │
│  │                                                  │  │
│  │  ┌────────────┐  ┌────────────┐  ┌──────────┐  │  │
│  │  │   Core     │  │  Merkle    │  │  Users   │  │  │
│  │  │  Tables    │  │  Tables    │  │  Tables  │  │  │
│  │  │            │  │            │  │          │  │  │
│  │  │ orgs       │  │ merkle_    │  │ users    │  │  │
│  │  │ documents  │  │  roots     │  │ sessions │  │  │
│  │  │ sentences  │  │ merkle_    │  │ api_keys │  │  │
│  │  │ api_keys   │  │  subhashes │  │          │  │  │
│  │  │ certs      │  │ merkle_    │  │          │  │  │
│  │  │            │  │  proofs    │  │          │  │  │
│  │  └────────────┘  └────────────┘  └──────────┘  │  │
│  │                                                  │  │
│  │  All in one database, different tables          │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │              Redis Cache (Optional)             │  │
│  │  - Verification results (5 min TTL)             │  │
│  │  - Session data                                 │  │
│  │  - Rate limiting counters                       │  │
│  └─────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## Detailed Analysis

### Option 1: Single Database (RECOMMENDED for V1)

**Architecture:**
- One FastAPI application
- One PostgreSQL database
- All tables in the same database
- Logical separation via table naming conventions

**Pros:**
- ✅ **Simplicity**: One codebase, one deployment, one database to manage
- ✅ **ACID Transactions**: Easy to maintain data consistency across tables
- ✅ **Foreign Keys**: Can use database-level referential integrity
- ✅ **Joins**: Efficient queries across related data
- ✅ **Lower Cost**: One database instance (~$200/month vs. $600/month for 3)
- ✅ **Faster Development**: No need to coordinate between services
- ✅ **Easier Debugging**: Single log stream, single deployment
- ✅ **Backup/Restore**: One backup strategy, one restore process

**Cons:**
- ⚠️ **Scaling Limits**: Eventually may hit limits (but not until 100K+ orgs)
- ⚠️ **Blast Radius**: Database issue affects everything
- ⚠️ **Schema Changes**: Require downtime or careful migration

**When to Use:**
- ✅ V1 launch (0-10K organizations)
- ✅ Early growth phase (10K-50K organizations)
- ✅ When team size < 10 engineers

**Performance Characteristics:**
- Can handle **1M+ documents** efficiently
- Can handle **100M+ sentences** with proper indexing
- Can handle **10M+ Merkle nodes** with partitioning
- Query latency: <10ms for indexed queries
- Write throughput: 10K+ writes/second

### Option 2: Logical Database Separation (Schemas)

**Architecture:**
- One PostgreSQL database
- Multiple schemas: `core`, `merkle`, `users`
- Same application, different schema prefixes

**Pros:**
- ✅ **Logical Separation**: Clear boundaries between domains
- ✅ **Still One Database**: Easy transactions and joins when needed
- ✅ **Gradual Migration**: Can move schemas to separate DBs later
- ✅ **Access Control**: Can grant different permissions per schema

**Cons:**
- ⚠️ **Complexity**: Need to manage schema prefixes in queries
- ⚠️ **Still Shared Resources**: CPU, memory, connections shared

**When to Use:**
- ✅ Growing phase (50K-100K organizations)
- ✅ When you want logical separation but not physical
- ✅ As a stepping stone to physical separation

**Implementation:**
```sql
-- Create schemas
CREATE SCHEMA core;
CREATE SCHEMA merkle;
CREATE SCHEMA users;

-- Move tables to schemas
ALTER TABLE organizations SET SCHEMA core;
ALTER TABLE documents SET SCHEMA core;
ALTER TABLE merkle_roots SET SCHEMA merkle;
ALTER TABLE merkle_subhashes SET SCHEMA merkle;
ALTER TABLE users SET SCHEMA users;

-- Query with schema prefix
SELECT * FROM core.organizations;
SELECT * FROM merkle.merkle_roots;
```

### Option 3: Physical Database Separation (Microservices)

**Architecture:**
- Three separate PostgreSQL databases
- Three separate services (or one service with multiple DB connections)
- API gateway for routing

**Pros:**
- ✅ **Independent Scaling**: Scale each database independently
- ✅ **Fault Isolation**: Issue in one DB doesn't affect others
- ✅ **Specialized Tuning**: Optimize each DB for its workload
- ✅ **Team Autonomy**: Different teams can own different services

**Cons:**
- ❌ **Complexity**: Much more complex to develop and operate
- ❌ **No Transactions**: Can't use database transactions across services
- ❌ **No Joins**: Can't join data across databases
- ❌ **Higher Cost**: 3x database costs (~$600/month)
- ❌ **Data Consistency**: Need distributed transactions or eventual consistency
- ❌ **Slower Development**: More coordination required

**When to Use:**
- ✅ Mature phase (100K+ organizations)
- ✅ When specific bottlenecks identified
- ✅ When team size > 20 engineers
- ✅ When different services have very different scaling needs

## Recommended Evolution Path

### Phase 1: V1 Launch (Months 1-6)
**Single Database, Single Application**

```
encypherai.com
├── FastAPI Application
└── PostgreSQL Database
    ├── organizations
    ├── documents
    ├── sentence_records
    ├── merkle_roots
    ├── merkle_subhashes
    ├── merkle_proof_cache
    ├── attribution_reports
    ├── api_keys
    ├── certificate_lifecycle
    └── audit_log
```

**Metrics to Watch:**
- Database size: <100GB
- Query latency: <50ms p99
- Connection pool usage: <80%
- CPU usage: <70%

### Phase 2: Growth (Months 7-18)
**Logical Separation with Schemas**

```
encypherai.com
├── FastAPI Application
└── PostgreSQL Database
    ├── core schema
    │   ├── organizations
    │   ├── documents
    │   ├── sentence_records
    │   └── api_keys
    ├── merkle schema
    │   ├── merkle_roots
    │   ├── merkle_subhashes
    │   ├── merkle_proof_cache
    │   └── attribution_reports
    └── users schema
        ├── users
        ├── sessions
        └── permissions
```

**Triggers for Phase 2:**
- Database size: >100GB
- Query latency: >50ms p99
- Need for better logical separation
- Team size: >5 engineers

### Phase 3: Scale (Months 19+)
**Physical Separation (If Needed)**

```
encypherai.com
├── API Gateway
├── Core Service → Core Database
├── Merkle Service → Merkle Database
└── User Service → User Database
```

**Triggers for Phase 3:**
- Database size: >500GB
- Query latency: >100ms p99
- Specific scaling bottlenecks identified
- Team size: >20 engineers
- Need for independent deployments

## Database Optimization Strategies

### 1. Indexing Strategy

**Core Tables:**
```sql
-- Organizations
CREATE INDEX idx_org_tier ON organizations(tier);
CREATE INDEX idx_org_email ON organizations(email);

-- Documents
CREATE INDEX idx_doc_org_date ON documents(organization_id, publication_date DESC);
CREATE INDEX idx_doc_hash ON documents(text_hash);

-- Sentences
CREATE INDEX idx_sentence_hash ON sentence_records(sentence_hash);
CREATE INDEX idx_sentence_doc ON sentence_records(document_id);
```

**Merkle Tables:**
```sql
-- Merkle Roots
CREATE INDEX idx_merkle_root_hash ON merkle_roots(root_hash);
CREATE INDEX idx_merkle_root_doc ON merkle_roots(document_id);

-- Merkle Subhashes (CRITICAL for performance)
CREATE INDEX idx_merkle_subhash_hash ON merkle_subhashes(hash_value);
CREATE INDEX idx_merkle_subhash_root ON merkle_subhashes(root_id);
CREATE INDEX idx_merkle_subhash_type ON merkle_subhashes(node_type);

-- Composite index for common queries
CREATE INDEX idx_merkle_subhash_hash_root ON merkle_subhashes(hash_value, root_id);
```

### 2. Partitioning Strategy

**When to Partition:**
- Table size: >10M rows
- Query patterns: Time-based or org-based

**Example: Partition by Organization**
```sql
-- Partition sentence_records by organization_id
CREATE TABLE sentence_records_partitioned (
    sentence_id VARCHAR(100),
    organization_id VARCHAR(100),
    ...
) PARTITION BY HASH (organization_id);

-- Create partitions
CREATE TABLE sentence_records_p0 PARTITION OF sentence_records_partitioned
    FOR VALUES WITH (MODULUS 4, REMAINDER 0);
CREATE TABLE sentence_records_p1 PARTITION OF sentence_records_partitioned
    FOR VALUES WITH (MODULUS 4, REMAINDER 1);
-- etc.
```

**Example: Partition by Time**
```sql
-- Partition audit_log by month
CREATE TABLE audit_log_partitioned (
    log_id SERIAL,
    created_at TIMESTAMP,
    ...
) PARTITION BY RANGE (created_at);

-- Create monthly partitions
CREATE TABLE audit_log_2025_10 PARTITION OF audit_log_partitioned
    FOR VALUES FROM ('2025-10-01') TO ('2025-11-01');
```

### 3. Caching Strategy

**Redis Cache Layers:**

```python
# Layer 1: Verification Results (5 min TTL)
cache_key = f"verify:{document_id}"
redis.setex(cache_key, 300, json.dumps(verification_result))

# Layer 2: Merkle Proofs (1 hour TTL)
cache_key = f"merkle_proof:{target_hash}:{root_id}"
redis.setex(cache_key, 3600, json.dumps(proof))

# Layer 3: Organization Data (1 hour TTL)
cache_key = f"org:{organization_id}"
redis.setex(cache_key, 3600, json.dumps(org_data))
```

**Cache Invalidation:**
```python
# Invalidate on updates
def update_document(document_id, data):
    # Update database
    db.update(document_id, data)
    
    # Invalidate cache
    redis.delete(f"verify:{document_id}")
    redis.delete(f"doc:{document_id}")
```

### 4. Connection Pooling

**PgBouncer Configuration:**
```ini
[databases]
encypher = host=localhost port=5432 dbname=encypher

[pgbouncer]
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 25
reserve_pool_size = 5
reserve_pool_timeout = 3
```

**Application Connection Pool:**
```python
from sqlalchemy.pool import QueuePool

engine = create_async_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

## API Endpoint Structure

### Unified API Structure

```
encypherai.com/
├── /                          # Website homepage
├── /verify/{document_id}      # Public verification page
├── /dashboard/                # Publisher dashboard
│
├── /api/v1/                   # REST API
│   ├── /sign                  # Sign content
│   ├── /verify                # Verify content
│   ├── /lookup                # Lookup sentence
│   │
│   ├── /merkle/               # Merkle endpoints
│   │   ├── /encode            # Encode document
│   │   ├── /attribute         # Find sources
│   │   └── /detect-plagiarism # Detect plagiarism
│   │
│   ├── /badge/                # Badge endpoints
│   │   └── /verify/{doc_id}  # Badge verification
│   │
│   └── /dashboard/            # Dashboard API
│       ├── /stats             # Usage statistics
│       └── /documents         # Document list
│
└── /embed/                    # Embeddable widgets
    └── /verify.js             # Verification badge
```

### Endpoint Implementation

**Badge Verification Endpoint:**
```python
@router.get("/api/v1/badge/verify/{document_id}")
async def verify_badge(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    cache: Redis = Depends(get_redis)
):
    """
    Lightweight verification endpoint for badge.
    Optimized for speed (<50ms p99).
    """
    # Check cache first
    cache_key = f"badge_verify:{document_id}"
    cached = await cache.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # Query database (optimized query)
    result = await db.execute(
        select(
            Document.document_id,
            Document.title,
            Document.publication_date,
            Document.total_sentences,
            Organization.organization_name,
            Organization.logo_url
        )
        .join(Organization)
        .where(Document.document_id == document_id)
    )
    
    row = result.first()
    if not row:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Build response
    response = {
        "status": "verified",
        "document_id": row.document_id,
        "publisher": {
            "name": row.organization_name,
            "logo_url": row.logo_url
        },
        "metadata": {
            "title": row.title,
            "published_at": row.publication_date.isoformat(),
            "sentence_count": row.total_sentences
        },
        "signature": {
            "algorithm": "Ed25519",
            "standard": "C2PA 2.2",
            "certificate_issuer": "SSL.com"
        },
        "verification_url": f"https://encypherai.com/verify/{document_id}"
    }
    
    # Cache for 5 minutes
    await cache.setex(cache_key, 300, json.dumps(response))
    
    return response
```

**Direct Link Verification Page:**
```python
@router.get("/verify/{document_id}")
async def verification_page(
    document_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Public verification page with SEO optimization.
    """
    # Get document details
    document = await get_document_with_verification(db, document_id)
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Render HTML template with SEO meta tags
    return templates.TemplateResponse(
        "verification.html",
        {
            "request": request,
            "document": document,
            "meta_title": f"Verified: {document.title}",
            "meta_description": f"Verified content from {document.publisher_name}",
            "og_image": document.publisher_logo,
            "canonical_url": f"https://encypherai.com/verify/{document_id}"
        }
    )
```

## Monitoring and Observability

### Key Metrics to Track

**Database Metrics:**
- Query latency (p50, p95, p99)
- Connection pool usage
- Database size
- Index hit rate
- Slow query log

**Application Metrics:**
- API latency per endpoint
- Error rate per endpoint
- Request rate per endpoint
- Cache hit rate
- Queue depth (if using async tasks)

**Business Metrics:**
- Documents signed per day
- Verifications per day
- Active organizations
- API calls per organization

### Alerting Thresholds

```yaml
alerts:
  database:
    - metric: query_latency_p99
      threshold: 100ms
      severity: warning
    
    - metric: connection_pool_usage
      threshold: 80%
      severity: warning
    
    - metric: database_size
      threshold: 80% of allocated
      severity: warning
  
  application:
    - metric: api_error_rate
      threshold: 1%
      severity: critical
    
    - metric: api_latency_p99
      threshold: 500ms
      severity: warning
```

## Cost Analysis

### Option 1: Single Database (Recommended)

**Monthly Costs:**
- PostgreSQL (db.t3.large): $200
- Redis (cache.t3.micro): $20
- Application (Railway/App Runner): $50
- **Total: ~$270/month**

**Scales to:**
- 50K organizations
- 1M documents
- 100M sentences
- 10M Merkle nodes

### Option 2: Logical Separation (Schemas)

**Monthly Costs:**
- PostgreSQL (db.t3.xlarge): $400
- Redis (cache.t3.small): $40
- Application: $50
- **Total: ~$490/month**

**Scales to:**
- 100K organizations
- 5M documents
- 500M sentences
- 50M Merkle nodes

### Option 3: Physical Separation (Microservices)

**Monthly Costs:**
- Core Database (db.t3.large): $200
- Merkle Database (db.t3.xlarge): $400
- User Database (db.t3.medium): $100
- Redis (cache.t3.medium): $80
- 3x Applications: $150
- Load Balancer: $20
- **Total: ~$950/month**

**Scales to:**
- 500K+ organizations
- 10M+ documents
- 1B+ sentences
- 100M+ Merkle nodes

## Final Recommendation

### Start Simple, Scale Smart

**V1 (Now - Month 6):**
- ✅ Single FastAPI application
- ✅ Single PostgreSQL database
- ✅ Redis for caching
- ✅ All endpoints in one codebase
- ✅ Cost: ~$270/month

**V2 (Month 7-18):**
- Consider logical separation (schemas) if:
  - Database size > 100GB
  - Query latency > 50ms p99
  - Team size > 5 engineers

**V3 (Month 19+):**
- Consider physical separation only if:
  - Specific bottlenecks identified
  - Database size > 500GB
  - Team size > 20 engineers
  - Independent scaling required

### Key Principle

> "Premature optimization is the root of all evil" - Donald Knuth

Start with the simplest architecture that meets your needs. PostgreSQL is incredibly powerful and can handle far more than most people think. You can always refactor later when you have real data about bottlenecks.

Your current single-database architecture is **perfect for V1** and will serve you well for years to come.
