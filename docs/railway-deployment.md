# Railway Deployment Guide

## Overview

This guide covers deploying the Encypher platform to Railway with multiple microservices.

## Architecture on Railway

```
Railway Project: encypher-ai
├── Environment: staging
│   ├── enterprise-api (Port: dynamic)     ✅ Deployed
│   ├── auth-service (Port: dynamic)       🚧 To Deploy
│   ├── key-service (Port: dynamic)        🚧 To Deploy
│   ├── postgres (Core DB)                 ✅ Deployed
│   ├── postgres-content (Content DB)      ✅ Deployed
│   └── redis                              ✅ Deployed
└── Environment: production
    └── (Same structure, separate instances)
```

## Services Configuration

### 1. Enterprise API (Main API)
- **Config File**: `/railway.json`
- **Dockerfile**: `/enterprise_api/Dockerfile`
- **Required Env Vars**:
  - `CORE_DATABASE_URL` - PostgreSQL connection string
  - `CONTENT_DATABASE_URL` - PostgreSQL connection string  
  - `REDIS_URL` - Redis connection string
  - `KEY_ENCRYPTION_KEY` - 32-byte hex key
  - `ENCRYPTION_NONCE` - 12-byte hex nonce
  - `ENVIRONMENT` - staging/production

### 2. Auth Service
- **Config File**: `/services/auth-service/railway.json`
- **Dockerfile**: `/services/auth-service/Dockerfile`
- **Required Env Vars**:
  - `DATABASE_URL` - PostgreSQL connection string
  - `REDIS_URL` - Redis connection string
  - `JWT_SECRET_KEY` - Secret for JWT signing

### 3. Key Service
- **Config File**: `/services/key-service/railway.json`
- **Dockerfile**: `/services/key-service/Dockerfile`
- **Required Env Vars**:
  - `DATABASE_URL` - PostgreSQL connection string
  - `REDIS_URL` - Redis connection string
  - `KEY_ENCRYPTION_KEY` - Master encryption key

## Deployment Steps

### Step 1: Add New Service via Railway CLI

```bash
# Link to project
railway link

# Create new service
railway service create auth-service

# Set config file path
railway service update --config-path services/auth-service/railway.json

# Set environment variables
railway variables set DATABASE_URL="$CORE_DATABASE_URL"
railway variables set REDIS_URL="$REDIS_URL"
railway variables set JWT_SECRET_KEY="$(openssl rand -hex 32)"
```

### Step 2: Deploy Service

```bash
# Deploy from repo root
railway up
```

### Step 3: Configure Internal Networking

Railway provides internal networking via `*.railway.internal` hostnames:

```
enterprise-api.railway.internal
auth-service.railway.internal
key-service.railway.internal
```

Update service configs to use internal URLs for inter-service communication.

## Environment Variables Reference

### Shared Variables (set at project level)
```bash
# Database URLs (use Railway's reference variables)
CORE_DATABASE_URL=${{Postgres.DATABASE_URL}}
CONTENT_DATABASE_URL=${{Postgres-Content.DATABASE_URL}}
REDIS_URL=${{Redis.REDIS_URL}}
```

### Service-Specific Variables

#### enterprise-api
```bash
ENVIRONMENT=staging
KEY_ENCRYPTION_KEY=<32-byte-hex>
ENCRYPTION_NONCE=<12-byte-hex>
AUTH_SERVICE_URL=http://auth-service.railway.internal
KEY_SERVICE_URL=http://key-service.railway.internal
```

#### auth-service
```bash
JWT_SECRET_KEY=<64-byte-hex>
ENTERPRISE_API_URL=http://enterprise-api.railway.internal
```

## Troubleshooting

### Service Won't Start
1. Check logs: `railway logs`
2. Verify env vars: `railway variables`
3. Check Dockerfile builds locally

### 502 Bad Gateway
- Ensure service listens on `$PORT` env var
- Check healthcheck endpoint responds

### Database Connection Issues
- Use Railway's internal hostnames (*.railway.internal)
- Verify DATABASE_URL format

## Useful Commands

```bash
# View all services
railway status

# View logs for specific service
railway logs -s auth-service

# Set environment variable
railway variables set KEY=VALUE

# Redeploy
railway up

# Open Railway dashboard
railway open
```
