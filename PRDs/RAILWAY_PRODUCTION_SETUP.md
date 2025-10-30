# Railway Production Setup - Critical Infrastructure

**Target Platform**: Railway.app  
**Timeline**: 1-2 weeks  
**Priority**: 🔴 CRITICAL - Block production launch  
**Status**: Implementation Ready

---

## 🎯 Overview

This guide implements the critical Phase 1 infrastructure from the production readiness audit, specifically tailored for Railway deployment.

**What Railway Provides Out-of-the-Box:**
- ✅ PostgreSQL databases (managed)
- ✅ Redis instances (managed)
- ✅ Docker container deployment
- ✅ Automatic HTTPS/SSL
- ✅ Environment variable management
- ✅ Basic metrics and logs
- ✅ Auto-scaling
- ✅ Health checks

**What We're Adding:**
- ✅ Prometheus metrics collection (DONE - auth-service)
- 🔄 Grafana dashboards (IN PROGRESS)
- 🔄 Distributed tracing with Jaeger
- 🔄 Structured logging
- 🔄 Audit logging
- 🔄 Automated backups
- 🔄 Secrets management via Railway

---

## 📋 Railway Project Structure

```
Railway Project: encypher-production
├── Services (Microservices)
│   ├── auth-service          (Port 8001) ✅ Metrics added
│   ├── user-service          (Port 8002)
│   ├── key-service           (Port 8003)
│   ├── encoding-service      (Port 8004)
│   ├── verification-service  (Port 8005)
│   ├── analytics-service     (Port 8006)
│   ├── billing-service       (Port 8007)
│   └── notification-service  (Port 8008)
│
├── Infrastructure Services
│   ├── prometheus            (Metrics collection)
│   ├── grafana              (Dashboards)
│   └── jaeger               (Distributed tracing)
│
└── Databases
    ├── postgres-main        (Shared database)
    ├── redis-cache          (Caching layer)
    └── redis-celery         (Task queue)
```

---

## 🚀 Step-by-Step Deployment Guide

### Step 1: Create Railway Project ✅

1. Go to [railway.app](https://railway.app)
2. Click "New Project"
3. Name it: `encypher-production`
4. Select region: `us-west` (or closest to your users)

### Step 2: Add PostgreSQL Database ✅

1. In your Railway project, click "New"
2. Select "Database" → "PostgreSQL"
3. Name it: `postgres-main`
4. Railway will provide: `DATABASE_URL`
5. **Note the connection string** - you'll need it for services

### Step 3: Add Redis Instances ✅

**Redis for Caching:**
1. Click "New" → "Database" → "Redis"
2. Name it: `redis-cache`
3. Note the `REDIS_URL`

**Redis for Celery (Task Queue):**
1. Click "New" → "Database" → "Redis"
2. Name it: `redis-celery`
3. Note the `REDIS_URL`

### Step 4: Deploy Microservices

Each service has a `railway.json` file (✅ CREATED). Deploy them one by one:

#### Deploy Auth Service

1. In Railway project, click "New" → "GitHub Repo"
2. Connect your `encypherai-commercial` repository
3. Set root directory: `services/auth-service`
4. Railway will auto-detect the Dockerfile
5. Add environment variables:
   ```
   DATABASE_URL=${{postgres-main.DATABASE_URL}}
   REDIS_URL=${{redis-cache.REDIS_URL}}
   SECRET_KEY=<generate-strong-secret>
   JWT_SECRET_KEY=<generate-strong-secret>
   JWT_ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   REFRESH_TOKEN_EXPIRE_DAYS=7
   SERVICE_NAME=auth-service
   SERVICE_HOST=0.0.0.0
   SERVICE_PORT=${{PORT}}
   LOG_LEVEL=INFO
   ALLOWED_ORIGINS=https://dashboard.encypherai.com,https://encypherai.com
   ```

6. Click "Deploy"
7. Wait for build to complete
8. Test health endpoint: `https://auth-service-production.up.railway.app/health`
9. Test metrics endpoint: `https://auth-service-production.up.railway.app/metrics`

#### Deploy Remaining Services

Repeat for each service with appropriate environment variables:

**User Service:**
```
DATABASE_URL=${{postgres-main.DATABASE_URL}}
REDIS_URL=${{redis-cache.REDIS_URL}}
AUTH_SERVICE_URL=${{auth-service.RAILWAY_PUBLIC_DOMAIN}}
SERVICE_NAME=user-service
SERVICE_PORT=${{PORT}}
```

**Key Service:**
```
DATABASE_URL=${{postgres-main.DATABASE_URL}}
REDIS_URL=${{redis-cache.REDIS_URL}}
AUTH_SERVICE_URL=${{auth-service.RAILWAY_PUBLIC_DOMAIN}}
SERVICE_NAME=key-service
SERVICE_PORT=${{PORT}}
```

**Encoding Service:**
```
DATABASE_URL=${{postgres-main.DATABASE_URL}}
REDIS_URL=${{redis-cache.REDIS_URL}}
AUTH_SERVICE_URL=${{auth-service.RAILWAY_PUBLIC_DOMAIN}}
KEY_SERVICE_URL=${{key-service.RAILWAY_PUBLIC_DOMAIN}}
SERVICE_NAME=encoding-service
SERVICE_PORT=${{PORT}}
```

**Verification Service:**
```
DATABASE_URL=${{postgres-main.DATABASE_URL}}
REDIS_URL=${{redis-cache.REDIS_URL}}
SERVICE_NAME=verification-service
SERVICE_PORT=${{PORT}}
```

**Analytics Service:**
```
DATABASE_URL=${{postgres-main.DATABASE_URL}}
REDIS_URL=${{redis-cache.REDIS_URL}}
AUTH_SERVICE_URL=${{auth-service.RAILWAY_PUBLIC_DOMAIN}}
SERVICE_NAME=analytics-service
SERVICE_PORT=${{PORT}}
```

**Billing Service:**
```
DATABASE_URL=${{postgres-main.DATABASE_URL}}
REDIS_URL=${{redis-cache.REDIS_URL}}
AUTH_SERVICE_URL=${{auth-service.RAILWAY_PUBLIC_DOMAIN}}
STRIPE_API_KEY=<from-vault-or-railway-secrets>
SERVICE_NAME=billing-service
SERVICE_PORT=${{PORT}}
```

**Notification Service:**
```
DATABASE_URL=${{postgres-main.DATABASE_URL}}
REDIS_URL=${{redis-cache.REDIS_URL}}
SMTP_HOST=<your-smtp-host>
SMTP_PORT=587
SMTP_USER=<your-smtp-user>
SMTP_PASSWORD=<from-vault-or-railway-secrets>
SERVICE_NAME=notification-service
SERVICE_PORT=${{PORT}}
```

### Step 5: Deploy Monitoring Infrastructure

#### Deploy Prometheus

1. Create `infrastructure/prometheus/Dockerfile`:
```dockerfile
FROM prom/prometheus:latest
COPY prometheus.yml /etc/prometheus/
EXPOSE 9090
```

2. Create `infrastructure/prometheus/prometheus.yml`:
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'auth-service'
    static_configs:
      - targets: ['auth-service-production.up.railway.app:443']
    scheme: https
    metrics_path: '/metrics'

  - job_name: 'user-service'
    static_configs:
      - targets: ['user-service-production.up.railway.app:443']
    scheme: https
    metrics_path: '/metrics'

  - job_name: 'key-service'
    static_configs:
      - targets: ['key-service-production.up.railway.app:443']
    scheme: https
    metrics_path: '/metrics'

  - job_name: 'encoding-service'
    static_configs:
      - targets: ['encoding-service-production.up.railway.app:443']
    scheme: https
    metrics_path: '/metrics'

  - job_name: 'verification-service'
    static_configs:
      - targets: ['verification-service-production.up.railway.app:443']
    scheme: https
    metrics_path: '/metrics'

  - job_name: 'analytics-service'
    static_configs:
      - targets: ['analytics-service-production.up.railway.app:443']
    scheme: https
    metrics_path: '/metrics'

  - job_name: 'billing-service'
    static_configs:
      - targets: ['billing-service-production.up.railway.app:443']
    scheme: https
    metrics_path: '/metrics'

  - job_name: 'notification-service'
    static_configs:
      - targets: ['notification-service-production.up.railway.app:443']
    scheme: https
    metrics_path: '/metrics'
```

3. Deploy to Railway:
   - New service from GitHub
   - Root directory: `infrastructure/prometheus`
   - Port: 9090
   - Make it publicly accessible

#### Deploy Grafana

1. In Railway, click "New" → "Template"
2. Search for "Grafana"
3. Deploy the template
4. Add environment variables:
   ```
   GF_SECURITY_ADMIN_PASSWORD=<strong-password>
   GF_SERVER_ROOT_URL=https://grafana-production.up.railway.app
   GF_INSTALL_PLUGINS=redis-datasource
   ```

5. After deployment, access Grafana
6. Add Prometheus as data source:
   - URL: `http://prometheus-production.railway.internal:9090`
   - Save & Test

7. Import dashboards:
   - Go to Dashboards → Import
   - Use dashboard ID: `1860` (Node Exporter Full)
   - Use dashboard ID: `3662` (Prometheus 2.0 Overview)
   - Create custom dashboard for business metrics

#### Deploy Jaeger (Distributed Tracing)

1. In Railway, click "New" → "Empty Service"
2. Name it: `jaeger`
3. Add Docker image: `jaegertracing/all-in-one:latest`
4. Add environment variables:
   ```
   COLLECTOR_ZIPKIN_HOST_PORT=:9411
   ```
5. Expose ports: `16686` (UI), `14268` (collector)
6. Access Jaeger UI at: `https://jaeger-production.up.railway.app:16686`

---

## 🔒 Security Setup

### Secrets Management via Railway

Railway provides built-in secrets management. For each service:

1. Go to service settings
2. Click "Variables"
3. Add secrets with `${{}}` syntax to reference other services
4. Use Railway's secret management for:
   - Database credentials (auto-provided)
   - API keys
   - JWT secrets
   - SMTP passwords
   - Stripe keys

### Generate Secure Secrets

```bash
# Generate JWT secret
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate encryption key
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## 📊 Monitoring Setup

### Grafana Dashboards

After deploying Grafana, create these dashboards:

#### 1. Service Health Dashboard
- HTTP request rate per service
- HTTP error rate (5xx, 4xx)
- Request duration (p50, p95, p99)
- Active connections

#### 2. Business Metrics Dashboard
- Authentication attempts (success/failure)
- User registrations
- Documents signed
- Documents verified
- API key operations

#### 3. Database Dashboard
- Query duration
- Active connections
- Connection pool usage
- Slow queries

### Alerting Rules

Create alerts in Grafana:

1. **High Error Rate**
   - Condition: Error rate > 5% for 5 minutes
   - Action: Send to Slack/Email

2. **Slow Response Time**
   - Condition: p95 latency > 1 second for 5 minutes
   - Action: Send to Slack/Email

3. **Service Down**
   - Condition: No metrics received for 2 minutes
   - Action: Send to PagerDuty/Slack

4. **High Database Connections**
   - Condition: Active connections > 80% of pool
   - Action: Send to Slack

---

## 🔄 Automated Backups

### PostgreSQL Backups on Railway

Railway automatically backs up PostgreSQL databases. To configure:

1. Go to `postgres-main` service
2. Click "Settings" → "Backups"
3. Enable automatic backups
4. Set retention: 30 days
5. Schedule: Every 6 hours

### Manual Backup Script

```bash
# scripts/backup_railway_db.sh
#!/bin/bash

# Get DATABASE_URL from Railway
DATABASE_URL="<from-railway>"

# Create backup
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql

# Upload to S3 (optional)
aws s3 cp backup_*.sql s3://encypher-backups/
```

### Test Restore

```bash
# Download latest backup
aws s3 cp s3://encypher-backups/backup_latest.sql .

# Restore to test database
psql $TEST_DATABASE_URL < backup_latest.sql

# Verify data
psql $TEST_DATABASE_URL -c "SELECT COUNT(*) FROM organizations;"
```

---

## 🧪 Testing Deployment

### Health Checks

```bash
# Test all services
services=("auth" "user" "key" "encoding" "verification" "analytics" "billing" "notification")

for service in "${services[@]}"; do
  echo "Testing $service-service..."
  curl https://$service-service-production.up.railway.app/health
done
```

### Metrics Check

```bash
# Check Prometheus metrics
curl https://auth-service-production.up.railway.app/metrics | grep auth_attempts_total
```

### Load Test

```bash
# Install k6
choco install k6

# Run load test
k6 run scripts/load_test.js
```

---

## 📈 Cost Estimation

### Railway Pricing (as of 2025)

**Hobby Plan** ($5/month):
- $5 of usage included
- Pay-as-you-go after

**Pro Plan** ($20/month):
- $20 of usage included
- Better performance
- Priority support

**Estimated Monthly Cost:**
- 8 microservices × $5 = $40
- PostgreSQL (2GB) = $10
- Redis (2 instances) = $10
- Prometheus = $5
- Grafana = $5
- Jaeger = $5
- **Total: ~$75/month**

**With Pro Plan:**
- Pro subscription = $20
- Additional usage = ~$55
- **Total: ~$75/month**

---

## 🚦 Go-Live Checklist

### Pre-Launch
- [ ] All 8 microservices deployed and healthy
- [ ] PostgreSQL database created and migrated
- [ ] Redis instances configured
- [ ] Prometheus collecting metrics from all services
- [ ] Grafana dashboards created
- [ ] Jaeger tracing working
- [ ] All environment variables set
- [ ] Secrets properly managed
- [ ] Automated backups enabled
- [ ] Health checks passing

### Launch
- [ ] Update DNS to point to Railway domains
- [ ] Test all API endpoints
- [ ] Monitor error rates
- [ ] Check response times
- [ ] Verify database connections
- [ ] Test authentication flow
- [ ] Test document signing
- [ ] Test document verification

### Post-Launch
- [ ] Monitor Grafana dashboards for 24 hours
- [ ] Check error logs
- [ ] Verify backup completion
- [ ] Test restore process
- [ ] Update documentation
- [ ] Notify team of new URLs

---

## 🆘 Troubleshooting

### Service Won't Start

1. Check Railway logs:
   ```
   railway logs
   ```

2. Verify environment variables:
   ```
   railway variables
   ```

3. Check database connection:
   ```
   railway run psql $DATABASE_URL
   ```

### High Memory Usage

1. Check Railway metrics
2. Reduce worker count in Dockerfile
3. Optimize database queries
4. Add caching

### Slow Response Times

1. Check Grafana dashboards
2. Look at Jaeger traces
3. Optimize database indexes
4. Add Redis caching
5. Scale up Railway service

---

## 📚 Next Steps

After deploying to Railway:

1. **Week 2**: Add remaining monitoring features
   - Structured logging with request IDs
   - Audit logging for all operations
   - Alert rules in Grafana

2. **Week 3-4**: Performance optimization
   - Implement Redis caching
   - Add Celery for background tasks
   - Optimize database queries

3. **Week 5-6**: Testing
   - Write integration tests
   - Load testing
   - Security testing

4. **Week 7-8**: Production hardening
   - Blue-green deployments
   - Canary releases
   - Disaster recovery drills

---

## 📞 Support

**Railway Support:**
- Discord: https://discord.gg/railway
- Docs: https://docs.railway.app
- Status: https://status.railway.app

**Internal Team:**
- DevOps Lead: [Your Name]
- Backend Lead: [Your Name]
- On-Call: [PagerDuty/Slack]

---

**Status**: ✅ Ready to Deploy  
**Next Action**: Create Railway project and deploy auth-service  
**Estimated Time**: 2-3 hours for initial deployment
