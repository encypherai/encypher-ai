# Monorepo Structure (Current Setup)

**Decision:** Keep existing monorepo structure  
**Date:** October 28, 2025  
**Rationale:** Already working well with shared DB, CI/CD, and local dev

## Current Repository Structure

```
encypherai-commercial/
├── enterprise_api/              # Enterprise API (FastAPI)
│   ├── app/
│   │   ├── api/v1/             # API endpoints
│   │   ├── models/             # Database models
│   │   ├── schemas/            # Pydantic schemas
│   │   ├── services/           # Business logic
│   │   └── utils/              # Utilities
│   ├── scripts/
│   ├── tests/
│   └── main.py
│
├── website/                     # Public website
│   ├── backend/                # Website backend functions
│   │   ├── embedding.py        # Basic embedding tools
│   │   ├── verification.py     # Public verification
│   │   └── analytics.py        # Analytics (writes to DB)
│   ├── frontend/               # Website frontend
│   │   ├── app/
│   │   ├── components/
│   │   └── public/
│   └── package.json
│
├── shared/                      # Shared code
│   ├── database/               # Shared DB access
│   │   ├── connection.py
│   │   └── models.py
│   ├── utils/
│   └── types/
│
├── docs/                        # Documentation
│   ├── api/
│   ├── legal/
│   └── architecture/
│
├── .github/
│   └── workflows/
│       ├── deploy-api.yml      # Deploy API on changes
│       └── deploy-website.yml  # Deploy website on changes
│
├── pyproject.toml              # Python dependencies
├── uv.lock
└── README.md
```

## Why This Works Well

### 1. Shared Database Access ✅

**Website analytics can write directly to DB:**

```python
# website/backend/analytics.py
from shared.database import get_db_session
from enterprise_api.app.models import AnalyticsEvent

async def track_verification(document_id: str, source: str):
    """Track verification event in shared database"""
    async with get_db_session() as db:
        event = AnalyticsEvent(
            event_type="verification",
            document_id=document_id,
            source=source,
            timestamp=datetime.utcnow()
        )
        db.add(event)
        await db.commit()
```

**No API calls needed** - direct DB access is faster and simpler.

### 2. Shared Code ✅

**Website can use Enterprise API functions:**

```python
# website/backend/embedding.py
from enterprise_api.app.utils.embedding import embed_uuid
from enterprise_api.app.utils.crypto import sign_content

async def embed_text_for_public_tool(text: str):
    """Use same embedding logic as Enterprise API"""
    # Reuse enterprise_api code
    embedded = embed_uuid(text, uuid="public-tool-uuid")
    return embedded
```

**Benefits:**
- No code duplication
- Same logic for public tools and API
- Easy to maintain

### 3. Unified CI/CD ✅

**Current workflow (keep this!):**

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  detect-changes:
    runs-on: ubuntu-latest
    outputs:
      api: ${{ steps.changes.outputs.api }}
      website: ${{ steps.changes.outputs.website }}
    steps:
      - uses: actions/checkout@v3
      - uses: dorny/paths-filter@v2
        id: changes
        with:
          filters: |
            api:
              - 'enterprise_api/**'
              - 'shared/**'
            website:
              - 'website/**'
              - 'shared/**'

  deploy-api:
    needs: detect-changes
    if: needs.detect-changes.outputs.api == 'true'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Railway
        run: railway up --service api

  deploy-website:
    needs: detect-changes
    if: needs.detect-changes.outputs.website == 'true'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Vercel
        run: vercel --prod
```

**Smart deployment:**
- ✅ Only deploys what changed
- ✅ Shared code triggers both
- ✅ Fast and efficient

### 4. Local Development ✅

**Current setup (keep this!):**

```bash
# One terminal - run both
npm run dev

# Or separate terminals
# Terminal 1 - API
cd enterprise_api
uv run uvicorn main:app --reload --port 8000

# Terminal 2 - Website
cd website/frontend
npm run dev
```

**Benefits:**
- ✅ Test public tools end-to-end
- ✅ No CORS issues (same origin in dev)
- ✅ Fast iteration

## Recommended Structure Improvements

### 1. Clarify Shared Code

```
shared/
├── database/
│   ├── __init__.py
│   ├── connection.py       # DB connection pool
│   ├── base.py            # Base model class
│   └── session.py         # Session management
│
├── models/                 # Shared models
│   ├── __init__.py
│   ├── analytics.py       # Analytics events
│   └── common.py          # Common models
│
├── utils/
│   ├── __init__.py
│   ├── crypto.py          # Shared crypto utils
│   └── validation.py      # Shared validation
│
└── config/
    ├── __init__.py
    └── settings.py        # Shared settings
```

### 2. Clear Boundaries

**Enterprise API:**
- `/api/v1/*` - Authenticated API for customers
- Requires API key
- Rate limited per tier
- Full feature set

**Website Backend:**
- `/tools/*` - Public tools (free, rate limited)
- `/verify/*` - Public verification
- `/analytics` - Internal analytics
- No API key required (or separate key)

**Example:**

```python
# enterprise_api/main.py
app = FastAPI()

# Enterprise API routes
app.include_router(signing_router, prefix="/api/v1")
app.include_router(verification_router, prefix="/api/v1")
app.include_router(merkle_router, prefix="/api/v1")

# website/backend/main.py
website_app = FastAPI()

# Public tool routes
website_app.include_router(public_tools_router, prefix="/tools")
website_app.include_router(public_verify_router, prefix="/verify")

# Mount website app under main app
app.mount("/", website_app)
```

### 3. Database Schema Organization

**Keep one database, organize with schemas or prefixes:**

```sql
-- Enterprise API tables
CREATE TABLE organizations (...);
CREATE TABLE documents (...);
CREATE TABLE api_keys (...);

-- Website tables (prefixed or in schema)
CREATE TABLE website_analytics (...);
CREATE TABLE public_verifications (...);
CREATE TABLE tool_usage (...);

-- Or use schemas
CREATE SCHEMA enterprise;
CREATE SCHEMA website;

CREATE TABLE enterprise.organizations (...);
CREATE TABLE website.analytics (...);
```

### 4. Environment Configuration

**Shared `.env` for local dev:**

```bash
# Database (shared)
DATABASE_URL=postgresql://localhost/encypherai
REDIS_URL=redis://localhost:6379

# Enterprise API
SSL_COM_API_KEY=...
JWT_SECRET=...

# Website
NEXT_PUBLIC_SITE_URL=http://localhost:3000
ANALYTICS_ENABLED=true

# Feature flags
ENABLE_PUBLIC_TOOLS=true
ENABLE_MERKLE_API=true
```

## Deployment Strategy

### Option 1: Separate Deployments (Current - Keep This!)

**API Deployment (Railway):**
```yaml
# railway.toml
[build]
builder = "NIXPACKS"
buildCommand = "cd enterprise_api && uv sync"

[deploy]
startCommand = "cd enterprise_api && uv run uvicorn main:app --host 0.0.0.0 --port $PORT"
```

**Website Deployment (Vercel):**
```json
// vercel.json
{
  "buildCommand": "cd website/frontend && npm run build",
  "outputDirectory": "website/frontend/.next"
}
```

**Benefits:**
- ✅ Independent scaling
- ✅ API on Railway (better for Python)
- ✅ Website on Vercel (better for Next.js)

### Option 2: Unified Deployment (Alternative)

Deploy both from same container:

```dockerfile
# Dockerfile
FROM python:3.11

# Install Python deps
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync

# Install Node deps
COPY website/frontend/package.json ./
RUN npm install

# Copy code
COPY . .

# Build frontend
RUN cd website/frontend && npm run build

# Start both
CMD ["sh", "-c", "uv run uvicorn enterprise_api.main:app & cd website/frontend && npm start"]
```

**Not recommended** - separate deployments are better.

## Verification Badge in Monorepo

### Where to Put Badge Code

**Option 1: In Website Repo (Recommended)**

```
website/
├── frontend/
│   └── public/
│       └── embed/
│           ├── verify.js       # Badge script
│           └── verify.css      # Badge styles
```

**Served from:**
```
https://encypherai.com/embed/verify.js
```

**Option 2: Separate CDN Repo**

Only if you want versioning and separate deployment:

```
encypherai-cdn/
└── embed/
    ├── v1/
    │   └── verify.js
    └── latest/
        └── verify.js
```

**For your case: Option 1** (keep in website)

### Badge API Endpoint

**Add to Enterprise API:**

```python
# enterprise_api/app/api/v1/endpoints/badge.py

@router.get("/badge/verify/{document_id}")
async def verify_badge(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    cache: Redis = Depends(get_redis)
):
    """Lightweight verification for badge"""
    # Implementation from VERIFICATION_BADGE_SPEC.md
    ...
```

**Or add to Website Backend:**

```python
# website/backend/badge.py

@router.get("/api/badge/verify/{document_id}")
async def verify_badge(document_id: str):
    """
    Badge verification endpoint
    Uses shared database access
    """
    from shared.database import get_db_session
    from enterprise_api.app.models import Document
    
    async with get_db_session() as db:
        # Query database directly
        result = await db.execute(
            select(Document).where(Document.document_id == document_id)
        )
        doc = result.scalar_one_or_none()
        
        if not doc:
            raise HTTPException(404, "Not found")
        
        return {
            "status": "verified",
            "document_id": doc.document_id,
            # ... rest of response
        }
```

**Recommendation:** Add to Enterprise API (cleaner separation)

## Migration Path (If You Ever Need to Split)

**You probably won't need this**, but if you grow to 50+ engineers:

```bash
# Extract website to separate repo (preserving history)
git subtree split --prefix=website -b website-branch
cd ../encypherai-website
git init
git pull ../encypherai-commercial website-branch

# Extract enterprise_api to separate repo
git subtree split --prefix=enterprise_api -b api-branch
cd ../encypherai-api
git init
git pull ../encypherai-commercial api-branch
```

But **don't do this now!** Your current setup is working well.

## Summary

### ✅ Keep Your Current Monorepo

**Your setup has:**
- ✅ Shared database access (website analytics → DB)
- ✅ Shared code (website uses API functions)
- ✅ Working CI/CD (auto-deploy on changes)
- ✅ Easy local dev (run both together)

**Don't change to separate repos** - you'd lose these benefits!

### Improvements to Make

1. **Clarify shared code structure** - organize `shared/` folder
2. **Document boundaries** - what's Enterprise API vs. Website
3. **Add badge endpoint** - to Enterprise API or Website backend
4. **Keep CI/CD** - it's already working well!

### When to Split (Not Now!)

Only split if:
- Team size > 20 engineers
- Different teams own API vs. Website
- Need independent release cycles
- Specific scaling bottlenecks

**For now:** Your monorepo is the right choice! ✅
