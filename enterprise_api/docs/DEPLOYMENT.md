# Encypher Enterprise API - Deployment Guide

This guide covers deploying the Encypher Enterprise API to Railway (recommended) or other platforms.

## Table of Contents

1. [Railway Deployment (Recommended)](#railway-deployment)
2. [Environment Variables](#environment-variables)
3. [Database Setup](#database-setup)
4. [SSL/TLS Configuration](#ssltls-configuration)
5. [Monitoring & Logging](#monitoring--logging)
6. [Troubleshooting](#troubleshooting)

---

## Railway Deployment

Railway provides managed PostgreSQL and automatic SSL/TLS certificates.

### Prerequisites

- Railway account (https://railway.app)
- Railway CLI installed: `npm install -g @railway/cli`
- GitHub repository access (for this repo)

### Step 1: Create Railway Project

```bash
# Login to Railway
railway login

# Create new project
railway init
# Select: "Empty Project"

# Link to this directory
cd enterprise_api
railway link
```

### Step 2: Add PostgreSQL Database

```bash
# Add PostgreSQL service
railway add postgresql

# Railway automatically sets DATABASE_URL environment variable
railway variables
```

### Step 3: Set Environment Variables

```bash
# Generate encryption keys
KEY_ENCRYPTION_KEY=$(openssl rand -hex 32)
ENCRYPTION_NONCE=$(openssl rand -hex 12)

# Set variables in Railway
railway variables set KEY_ENCRYPTION_KEY=$KEY_ENCRYPTION_KEY
railway variables set ENCRYPTION_NONCE=$ENCRYPTION_NONCE
railway variables set SSL_COM_API_KEY=<your-ssl-com-api-key>
railway variables set SSL_COM_API_URL=https://api.ssl.com/v1
railway variables set API_BASE_URL=https://api.encypherai.com
railway variables set ENVIRONMENT=preview
railway variables set MARKETING_DOMAIN=encypher.ai
railway variables set INFRASTRUCTURE_DOMAIN=encypherai.com
```

### Step 4: Initialize Database

```bash
# Connect to Railway PostgreSQL
railway run python scripts/init_db.py

# Verify tables created
railway run psql $DATABASE_URL -c "\dt"
```

### Step 5: Deploy Application

```bash
# Deploy to Railway
railway up

# Check deployment status
railway status

# View logs
railway logs

# Open in browser
railway open
```

### Step 6: Configure Custom Domain

1. Go to Railway dashboard → Your project
2. Click on your service → Settings → Domains
3. Add custom domain: `api.encypherai.com`
4. Configure DNS:
   - Type: `CNAME`
   - Name: `api`
   - Value: `<your-railway-domain>.up.railway.app`

Railway automatically provisions SSL/TLS certificates via Let's Encrypt.

---

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection URL | `postgresql://user:pass@host:5432/db` |
| `KEY_ENCRYPTION_KEY` | 32-byte hex key | `abcdef0123456789...` (64 chars) |
| `ENCRYPTION_NONCE` | 12-byte hex nonce | `abcdef012345...` (24 chars) |
| `SSL_COM_API_KEY` | SSL.com API key | `ssl_com_key_123...` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ENVIRONMENT` | Environment mode | `development` |
| `SSL_COM_API_URL` | SSL.com API endpoint | `https://api.ssl.com/v1` |
| `API_BASE_URL` | Public API URL | `https://api.encypherai.com` |
| `RATE_LIMIT_PER_MINUTE` | Rate limit | `60` |
| `MARKETING_DOMAIN` | Marketing domain | `encypher.ai` |
| `INFRASTRUCTURE_DOMAIN` | Infrastructure domain | `encypherai.com` |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | OTLP HTTP endpoint for distributed tracing (optional, disabled when unset) | _(unset)_ |
| `OTEL_SERVICE_NAME` | Service name reported to tracing backend | `enterprise-api` |

### Generating Encryption Keys

```bash
# Generate KEY_ENCRYPTION_KEY (32 bytes = 64 hex chars)
openssl rand -hex 32

# Generate ENCRYPTION_NONCE (12 bytes = 24 hex chars)
openssl rand -hex 12
```

**IMPORTANT:** Store these keys securely! Never commit them to version control.

---

## Database Setup

### PostgreSQL Requirements

- PostgreSQL 15 or higher
- Minimum 1GB RAM
- 10GB storage (recommended)

### Schema Migration

The database schema is defined in `scripts/init_db.sql`. To apply:

```bash
# Via Railway
railway run python scripts/init_db.py

# Via direct connection
psql $DATABASE_URL -f scripts/init_db.sql
```

### Database Tables

- `organizations` - Organization accounts
- `documents` - Signed documents
- `sentence_records` - Individual sentence tracking
- `api_keys` - API key authentication
- `certificate_lifecycle` - SSL.com certificate tracking
- `audit_log` - Audit trail for compliance

### Database Backups

Railway provides automatic daily backups. To create manual backup:

```bash
# Via Railway CLI
railway run pg_dump $DATABASE_URL > backup.sql

# Restore
railway run psql $DATABASE_URL < backup.sql
```

---

## SSL/TLS Configuration

### Railway (Automatic)

Railway automatically provisions SSL/TLS certificates via Let's Encrypt when you add a custom domain.

### Custom SSL Certificate

If using SSL.com certificates for the API itself (not for content signing):

1. Order SSL certificate from SSL.com
2. Download certificate files
3. Configure in Railway dashboard:
   - Settings → Custom Domain → Advanced
   - Upload certificate + private key

---

## Monitoring & Logging

### Railway Logs

```bash
# View real-time logs
railway logs

# View logs for specific service
railway logs -s <service-name>

# Filter logs
railway logs | grep ERROR
```

### Application Logs

The API uses Python's `logging` module:

```python
import logging
logger = logging.getLogger(__name__)

logger.info("Request received")
logger.error("Error occurred", exc_info=True)
```

### Health Check Endpoint

Monitor API health:

```bash
curl https://api.encypherai.com/health

# Expected response:
# {
#   "status": "healthy",
#   "environment": "preview",
#   "version": "1.0.0-preview"
# }
```

The `/readyz` endpoint performs deeper dependency probes and is suitable for load-balancer readiness checks:

```bash
curl https://api.encypherai.com/readyz

# Expected response when all services are healthy:
# {
#   "status": "ready",
#   "database": "ok",
#   "redis": "ok",
#   "key_service": "ok",
#   "auth_service": "ok",
#   "version": "1.0.0-preview"
# }
```

`status` is `"degraded"` (not `"ready"`) if `database`, `key_service`, or `auth_service` is not `"ok"`. External services (`key_service`, `auth_service`) are probed with a 2-second timeout.

### Railway Monitoring

Railway provides built-in monitoring:
- CPU usage
- Memory usage
- Network traffic
- Request metrics

Access via Railway dashboard → Metrics.

---

## Troubleshooting

### Database Connection Issues

**Problem:** `could not connect to server`

**Solution:**
```bash
# Verify DATABASE_URL is set
railway variables | grep DATABASE_URL

# Test connection
railway run psql $DATABASE_URL -c "SELECT 1"

# Check PostgreSQL service status
railway status
```

### Import Errors

**Problem:** `ModuleNotFoundError: No module named 'encypher'`

**Solution:**
```bash
# Verify encypher-ai is installed
railway run python -c "import encypher; print(encypher.__version__)"

# Reinstall dependencies
railway run pip install -r requirements.txt
```

### API Key Authentication Failing

**Problem:** `Invalid API key`

**Solution:**
```bash
# Check if API keys exist in database
railway run psql $DATABASE_URL -c "SELECT api_key, organization_id FROM api_keys LIMIT 5"

# Regenerate test API key
railway run python scripts/init_db.py
```

### SSL.com API Errors

**Problem:** `SSL_COM_API_ERROR`

**Solution:**
```bash
# Verify SSL.com API key is set
railway variables | grep SSL_COM_API_KEY

# Test SSL.com API connection
curl -H "Authorization: Bearer $SSL_COM_API_KEY" https://api.ssl.com/v1/orders
```

### Performance Issues

**Problem:** Slow response times

**Solutions:**
1. **Scale up Railway instance:**
   - Dashboard → Settings → Resources
   - Increase RAM/CPU

2. **Enable connection pooling:**
   - Already configured in `app/database.py`
   - Default: 20 connections, 10 overflow

3. **Add database indexes:**
   - Already defined in `init_db.sql`
   - Verify: `railway run psql $DATABASE_URL -c "\di"`

---

## Production Checklist

Before going to production:

- [ ] Environment set to `production`
- [ ] SSL.com API using production endpoint
- [ ] Custom domain configured with SSL/TLS
- [ ] Database backups enabled
- [ ] Monitoring/alerting configured
- [ ] API keys rotated from test keys
- [ ] Rate limiting configured per plan
- [ ] Encryption keys stored securely (not in repo)
- [ ] Error reporting configured (e.g., Sentry)
- [ ] Load testing completed
- [ ] Security audit completed

---

## Alternative Deployment Options

### Docker Deployment

```dockerfile
# Dockerfile (if needed for other platforms)
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t encypher-enterprise-api .
docker run -p 8000:8000 --env-file .env encypher-enterprise-api
```

### AWS Deployment

1. Use AWS Elastic Beanstalk or ECS
2. RDS for PostgreSQL
3. Secrets Manager for environment variables
4. CloudFront for CDN
5. Route53 for DNS

### GCP Deployment

1. Use Cloud Run or App Engine
2. Cloud SQL for PostgreSQL
3. Secret Manager for environment variables
4. Cloud Load Balancing
5. Cloud DNS

---

## Support

For deployment issues:
- **Email:** devops@encypherai.com
- **Slack:** #deployment (internal)
- **Docs:** https://docs.encypherai.com/deployment
