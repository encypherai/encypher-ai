# Environment Variables Mapping

This document maps which shared environment variables are used by each service.

## All Services (13 total)

### Backend Microservices (10)
1. auth-service (port 8001)
2. user-service (port 8002)
3. key-service (port 8003)
4. encoding-service (port 8004)
5. verification-service (port 8005)
6. analytics-service (port 8006)
7. billing-service (port 8007)
8. notification-service (port 8008)
9. coalition-service (port 8009)
10. api-gateway (port 8000)

### APIs (1)
11. enterprise-api (port 9000)

### Frontend Apps (2)
12. marketing-site (port 3000, Next.js)
13. dashboard (port 3001, Next.js)

---

## Shared Variables (Set in Railway Shared Variables)

| Variable | Description | Used By |
|----------|-------------|---------|
| `DATABASE_URL` | Core DB connection (users, orgs, billing) | auth-service, key-service, billing-service, user-service, notification-service |
| `CONTENT_DATABASE_URL` | Content DB connection (documents, analytics) | encoding-service, verification-service, analytics-service, coalition-service |
| `REDIS_URL` | Redis cache connection | ALL backend services |
| `JWT_SECRET_KEY` | JWT signing key | auth-service |
| `NEXTAUTH_SECRET` | NextAuth session secret | marketing-site, dashboard |
| `ALLOWED_ORIGINS` | CORS allowed origins | ALL backend services |
| `AUTH_SERVICE_URL` | Internal auth service URL | key-service, billing-service, encoding-service, verification-service, analytics-service, notification-service, coalition-service |
| `KEY_SERVICE_URL` | Internal key service URL | encoding-service, verification-service, enterprise-api |
| `NEXT_PUBLIC_API_URL` | Public API URL (for frontends) | marketing-site, dashboard |
| `NEXT_PUBLIC_MARKETING_SITE_URL` | Public marketing site URL | marketing-site, dashboard |
| `NEXT_PUBLIC_DASHBOARD_URL` | Public dashboard URL | marketing-site, dashboard |
| `MARKETING_SITE_URL` | Marketing site URL (backend use) | auth-service, notification-service |
| `DASHBOARD_URL` | Dashboard URL (backend use) | auth-service, notification-service |
| `ENVIRONMENT` | Environment name | ALL services |
| `LOG_LEVEL` | Logging level | ALL backend services |

## Service-Specific Variables

### auth-service
- `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` - Google OAuth
- `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET` - GitHub OAuth
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS` - Email sending
- `VERIFICATION_TOKEN_EXPIRE_HOURS`, `PASSWORD_RESET_TOKEN_EXPIRE_HOURS`

### billing-service
- `STRIPE_API_KEY` - Stripe secret key
- `STRIPE_WEBHOOK_SECRET` - Stripe webhook signing secret
- `STRIPE_PRICE_*` - Stripe price IDs for each plan

### notification-service
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS` - Email sending
- `EMAIL_FROM`, `EMAIL_FROM_NAME`

### coalition-service
- `REVENUE_SPLIT_ENCYPHER`, `REVENUE_SPLIT_MEMBERS`
- `MIN_PAYOUT_THRESHOLD`, `AUTO_ONBOARD_FREE_TIER`

### encoding-service
- `DEFAULT_ENCODING`, `MAX_DOCUMENT_SIZE`, `SUPPORTED_FORMATS`

### key-service
- `KEY_PREFIX`, `KEY_LENGTH`

### enterprise-api
- `DATABASE_URL` / `CORE_DATABASE_URL` — Core DB (publisher_rights_profiles, formal_notices, notice_evidence_chain, rights_licensing_requests, rights_licensing_agreements, rights_audit_log, content_detection_events, known_crawlers)
- `CONTENT_DATABASE_URL` — Content DB (content_references — rights_snapshot, rights_resolution_url columns)
- `API_BASE_URL` — Base URL used to build `rights_resolution_url` in sign responses (e.g., `https://api.encypherai.com`)
- `KEY_ENCRYPTION_KEY`, `ENCRYPTION_NONCE` — C2PA signing key encryption
- `RATE_LIMIT_PER_MINUTE` — Rate limit for all endpoints including public rights lookup

## Database Assignment

| Database | Services |
|----------|----------|
| **postgres-core** (sensitive data) | auth-service, key-service, billing-service, user-service, notification-service, enterprise-api (rights/org data) |
| **postgres-content** (content data) | encoding-service, verification-service, analytics-service, coalition-service, enterprise-api (content_references) |

## Railway Configuration

### Shared Variables (Project-level)
Set these in Railway: **Project Settings > Variables > Shared Variables**

```bash
# Databases
DATABASE_URL=${{Postgres-Core.DATABASE_URL}}
CONTENT_DATABASE_URL=${{Postgres-Content.DATABASE_URL}}
REDIS_URL=${{Redis.REDIS_URL}}

# Security
JWT_SECRET_KEY=<generate-secure-key>
NEXTAUTH_SECRET=<generate-secure-key>

# URLs (Staging)
MARKETING_SITE_URL=https://marketing-site-staging-xxx.up.railway.app
DASHBOARD_URL=https://dashboard-staging-xxx.up.railway.app
API_URL=https://auth-service-staging-xxx.up.railway.app

# URLs (Production)
# MARKETING_SITE_URL=https://www.encypherai.com
# DASHBOARD_URL=https://dashboard.encypherai.com
# API_URL=https://api.encypherai.com

# CORS
ALLOWED_ORIGINS=https://encypherai.com,https://www.encypherai.com,https://dashboard.encypherai.com

# Internal Service URLs (use Railway private networking)
AUTH_SERVICE_URL=http://auth-service.railway.internal:8001
KEY_SERVICE_URL=http://key-service.railway.internal:8003

# Environment
ENVIRONMENT=staging
LOG_LEVEL=INFO
```

### Per-Service Variables
Each service should have its own service-specific variables set directly on the service.

Example for **billing-service**:
```bash
STRIPE_API_KEY=sk_live_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
```
