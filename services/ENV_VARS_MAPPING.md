# Environment Variables Mapping

This document maps which shared environment variables are used by each service.

## All Services (13 total)

### Backend Microservices (9)
1. auth-service
2. key-service
3. billing-service
4. user-service
5. notification-service
6. encoding-service
7. verification-service
8. analytics-service
9. coalition-service

### APIs (1)
10. enterprise-api

### Frontend Apps (2)
11. marketing-site (Next.js)
12. dashboard (Next.js)

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

## Database Assignment

| Database | Services |
|----------|----------|
| **postgres-core** (sensitive data) | auth-service, key-service, billing-service, user-service, notification-service |
| **postgres-content** (content data) | encoding-service, verification-service, analytics-service, coalition-service |

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
