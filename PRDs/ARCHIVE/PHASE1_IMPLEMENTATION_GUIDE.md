# Phase 1: Critical Infrastructure Implementation Guide

**Duration**: 2 weeks  
**Team**: 2-3 engineers  
**Priority**: 🔴 CRITICAL - Block production launch  
**Status**: Not Started

---

## 🎯 Objectives

By the end of Phase 1, you will have:
1. ✅ Full observability into system health and performance
2. ✅ Hardened security posture with secrets management
3. ✅ Automated database backups with tested recovery
4. ✅ Comprehensive audit logging for compliance
5. ✅ Alerting system for incident response

---

## 📋 Task Breakdown

### Week 1: Monitoring & Observability

#### Day 1-2: Prometheus + Grafana Setup

**1. Add Dependencies**
```bash
cd enterprise_api
uv add prometheus-client prometheus-fastapi-instrumentator
```

**2. Create Metrics Module**
```python
# enterprise_api/app/monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge
from prometheus_fastapi_instrumentator import Instrumentator

# Request metrics
request_count = Counter(
    'encypher_requests_total',
    'Total requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'encypher_request_duration_seconds',
    'Request duration',
    ['method', 'endpoint']
)

# Business metrics
documents_signed = Counter(
    'encypher_documents_signed_total',
    'Total documents signed',
    ['organization_id']
)

documents_verified = Counter(
    'encypher_documents_verified_total',
    'Total documents verified',
    ['result']
)

# System metrics
active_connections = Gauge(
    'encypher_db_connections_active',
    'Active database connections'
)

cache_hits = Counter(
    'encypher_cache_hits_total',
    'Cache hits'
)

cache_misses = Counter(
    'encypher_cache_misses_total',
    'Cache misses'
)
```

**3. Instrument FastAPI App**
```python
# enterprise_api/app/main.py
from prometheus_fastapi_instrumentator import Instrumentator
from app.monitoring.metrics import request_count, request_duration

# Add after app creation
instrumentator = Instrumentator(
    should_group_status_codes=False,
    should_ignore_untemplated=True,
    should_respect_env_var=True,
    should_instrument_requests_inprogress=True,
    excluded_handlers=["/metrics", "/health"],
    env_var_name="ENABLE_METRICS",
    inprogress_name="encypher_requests_inprogress",
    inprogress_labels=True,
)

instrumentator.instrument(app).expose(app)
```

**4. Add Business Metrics to Endpoints**
```python
# enterprise_api/app/routers/signing.py
from app.monitoring.metrics import documents_signed

@router.post("/sign")
async def sign_document(...):
    result = await signing_service.sign(...)
    
    # Record metric
    documents_signed.labels(
        organization_id=org_details["organization_id"]
    ).inc()
    
    return result
```

**5. Deploy Prometheus**
```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/usr/share/prometheus/console_libraries'
      - '--web.console.templates=/usr/share/prometheus/consoles'

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources

volumes:
  prometheus_data:
  grafana_data:
```

**6. Configure Prometheus**
```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'enterprise-api'
    static_configs:
      - targets: ['host.docker.internal:9000']
    metrics_path: '/metrics'

  - job_name: 'microservices'
    static_configs:
      - targets: 
        - 'host.docker.internal:8001'  # auth-service
        - 'host.docker.internal:8002'  # user-service
        - 'host.docker.internal:8003'  # key-service
        - 'host.docker.internal:8004'  # encoding-service
        - 'host.docker.internal:8005'  # verification-service
        - 'host.docker.internal:8006'  # analytics-service
        - 'host.docker.internal:8007'  # billing-service
        - 'host.docker.internal:8008'  # notification-service
```

**7. Create Grafana Dashboard**
```json
# monitoring/grafana/dashboards/encypher-overview.json
{
  "dashboard": {
    "title": "Encypher Enterprise API",
    "panels": [
      {
        "title": "Request Rate",
        "targets": [
          {
            "expr": "rate(encypher_requests_total[5m])"
          }
        ]
      },
      {
        "title": "Request Duration (p95)",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(encypher_request_duration_seconds_bucket[5m]))"
          }
        ]
      },
      {
        "title": "Documents Signed",
        "targets": [
          {
            "expr": "rate(encypher_documents_signed_total[5m])"
          }
        ]
      },
      {
        "title": "Error Rate",
        "targets": [
          {
            "expr": "rate(encypher_requests_total{status=~\"5..\"}[5m])"
          }
        ]
      }
    ]
  }
}
```

**Testing**:
```bash
# Start monitoring stack
docker-compose -f docker-compose.monitoring.yml up -d

# Access Grafana
open http://localhost:3001
# Login: admin/admin

# Access Prometheus
open http://localhost:9090

# Test metrics endpoint
curl http://localhost:9000/metrics
```

---

#### Day 3-4: Distributed Tracing (OpenTelemetry)

**1. Add Dependencies**
```bash
cd enterprise_api
uv add opentelemetry-api opentelemetry-sdk opentelemetry-instrumentation-fastapi opentelemetry-instrumentation-sqlalchemy opentelemetry-instrumentation-httpx opentelemetry-exporter-jaeger
```

**2. Create Tracing Module**
```python
# enterprise_api/app/monitoring/tracing.py
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

def setup_tracing(app, service_name: str = "encypher-enterprise-api"):
    """Set up OpenTelemetry tracing."""
    
    # Create tracer provider
    trace.set_tracer_provider(TracerProvider())
    tracer_provider = trace.get_tracer_provider()
    
    # Configure Jaeger exporter
    jaeger_exporter = JaegerExporter(
        agent_host_name="localhost",
        agent_port=6831,
    )
    
    # Add span processor
    tracer_provider.add_span_processor(
        BatchSpanProcessor(jaeger_exporter)
    )
    
    # Instrument FastAPI
    FastAPIInstrumentor.instrument_app(app)
    
    # Instrument SQLAlchemy
    SQLAlchemyInstrumentor().instrument()
    
    # Instrument HTTPX (for external API calls)
    HTTPXClientInstrumentor().instrument()
    
    return trace.get_tracer(service_name)

# Get tracer for manual instrumentation
tracer = trace.get_tracer(__name__)
```

**3. Add Tracing to App**
```python
# enterprise_api/app/main.py
from app.monitoring.tracing import setup_tracing

# Add in lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup tracing
    setup_tracing(app)
    logger.info("Tracing initialized")
    
    yield
```

**4. Add Custom Spans**
```python
# enterprise_api/app/services/signing_service.py
from app.monitoring.tracing import tracer

async def sign_document(self, text: str, metadata: dict):
    with tracer.start_as_current_span("sign_document") as span:
        span.set_attribute("document.length", len(text))
        span.set_attribute("organization.id", metadata.get("organization_id"))
        
        # Sign document
        with tracer.start_as_current_span("generate_signature"):
            signature = await self._generate_signature(text)
        
        with tracer.start_as_current_span("embed_metadata"):
            signed_text = await self._embed_metadata(text, signature, metadata)
        
        with tracer.start_as_current_span("store_document"):
            doc_id = await self._store_document(signed_text, metadata)
        
        span.set_attribute("document.id", doc_id)
        
        return signed_text, doc_id
```

**5. Deploy Jaeger**
```yaml
# Add to docker-compose.monitoring.yml
  jaeger:
    image: jaegertracing/all-in-one:latest
    ports:
      - "5775:5775/udp"
      - "6831:6831/udp"
      - "6832:6832/udp"
      - "5778:5778"
      - "16686:16686"  # UI
      - "14268:14268"
      - "14250:14250"
      - "9411:9411"
    environment:
      - COLLECTOR_ZIPKIN_HOST_PORT=:9411
```

**Testing**:
```bash
# Access Jaeger UI
open http://localhost:16686

# Make some requests
curl -X POST http://localhost:9000/api/v1/sign \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"text": "Test", "title": "Test"}'

# View traces in Jaeger UI
```

---

#### Day 5: Centralized Logging (Structured Logging)

**1. Add Dependencies**
```bash
cd enterprise_api
uv add structlog python-json-logger
```

**2. Configure Structured Logging**
```python
# enterprise_api/app/monitoring/logging.py
import structlog
import logging
from pythonjsonlogger import jsonlogger

def setup_logging():
    """Configure structured logging."""
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Configure standard logging
    handler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter(
        '%(timestamp)s %(level)s %(name)s %(message)s'
    )
    handler.setFormatter(formatter)
    
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)

# Get logger
logger = structlog.get_logger()
```

**3. Use Structured Logging**
```python
# enterprise_api/app/routers/signing.py
from app.monitoring.logging import logger

@router.post("/sign")
async def sign_document(...):
    logger.info(
        "document_sign_started",
        organization_id=org_details["organization_id"],
        document_length=len(request.text),
        has_metadata=bool(request.metadata)
    )
    
    try:
        result = await signing_service.sign(...)
        
        logger.info(
            "document_sign_completed",
            organization_id=org_details["organization_id"],
            document_id=result.document_id,
            duration_ms=duration
        )
        
        return result
    except Exception as e:
        logger.error(
            "document_sign_failed",
            organization_id=org_details["organization_id"],
            error=str(e),
            error_type=type(e).__name__
        )
        raise
```

**4. Add Request ID Middleware**
```python
# enterprise_api/app/middleware/request_id.py
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
import structlog

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Add to structlog context
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)
        
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        
        return response

# Add to app
app.add_middleware(RequestIDMiddleware)
```

---

### Week 2: Security & Data Protection

#### Day 6-7: Secrets Management (HashiCorp Vault)

**1. Add Dependencies**
```bash
cd enterprise_api
uv add hvac
```

**2. Deploy Vault**
```yaml
# Add to docker-compose.monitoring.yml
  vault:
    image: vault:latest
    ports:
      - "8200:8200"
    environment:
      - VAULT_DEV_ROOT_TOKEN_ID=dev-token
      - VAULT_DEV_LISTEN_ADDRESS=0.0.0.0:8200
    cap_add:
      - IPC_LOCK
```

**3. Create Vault Client**
```python
# enterprise_api/app/security/vault.py
import hvac
from functools import lru_cache

class VaultClient:
    def __init__(self, url: str, token: str):
        self.client = hvac.Client(url=url, token=token)
        
    def get_secret(self, path: str) -> dict:
        """Get secret from Vault."""
        try:
            response = self.client.secrets.kv.v2.read_secret_version(
                path=path,
                mount_point='secret'
            )
            return response['data']['data']
        except Exception as e:
            logger.error("vault_secret_read_failed", path=path, error=str(e))
            raise
    
    def set_secret(self, path: str, data: dict):
        """Store secret in Vault."""
        try:
            self.client.secrets.kv.v2.create_or_update_secret(
                path=path,
                secret=data,
                mount_point='secret'
            )
            logger.info("vault_secret_stored", path=path)
        except Exception as e:
            logger.error("vault_secret_write_failed", path=path, error=str(e))
            raise

@lru_cache()
def get_vault_client() -> VaultClient:
    """Get cached Vault client."""
    return VaultClient(
        url=os.getenv("VAULT_URL", "http://localhost:8200"),
        token=os.getenv("VAULT_TOKEN")
    )
```

**4. Migrate Secrets to Vault**
```python
# scripts/migrate_secrets_to_vault.py
import os
from app.security.vault import get_vault_client

def migrate_secrets():
    """Migrate secrets from .env to Vault."""
    vault = get_vault_client()
    
    # Database credentials
    vault.set_secret("database", {
        "url": os.getenv("DATABASE_URL"),
        "pool_size": 20
    })
    
    # SSL.com credentials
    vault.set_secret("ssl_com", {
        "api_key": os.getenv("SSL_COM_API_KEY"),
        "account_key": os.getenv("SSL_COM_ACCOUNT_KEY")
    })
    
    # Encryption keys
    vault.set_secret("encryption", {
        "key": os.getenv("KEY_ENCRYPTION_KEY"),
        "nonce": os.getenv("ENCRYPTION_NONCE")
    })
    
    print("✅ Secrets migrated to Vault")

if __name__ == "__main__":
    migrate_secrets()
```

**5. Update Config to Use Vault**
```python
# enterprise_api/app/config.py
from app.security.vault import get_vault_client

class Settings(BaseSettings):
    # Vault configuration
    vault_url: str = "http://localhost:8200"
    vault_token: str
    
    # Other settings remain in env vars
    environment: str = "development"
    
    @property
    def database_url(self) -> str:
        """Get database URL from Vault."""
        vault = get_vault_client()
        secrets = vault.get_secret("database")
        return secrets["url"]
    
    @property
    def ssl_com_api_key(self) -> str:
        """Get SSL.com API key from Vault."""
        vault = get_vault_client()
        secrets = vault.get_secret("ssl_com")
        return secrets["api_key"]
```

---

#### Day 8-9: Automated Backups & Recovery

**1. Create Backup Script**
```bash
# scripts/backup_database.sh
#!/bin/bash

set -e

# Configuration
BACKUP_DIR="/backups"
RETENTION_DAYS=30
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/encypher_backup_$TIMESTAMP.dump"

# Get database URL from Vault
DATABASE_URL=$(vault kv get -field=url secret/database)

# Create backup directory
mkdir -p $BACKUP_DIR

# Perform backup
echo "Starting backup at $(date)"
pg_dump -Fc $DATABASE_URL > $BACKUP_FILE

# Compress backup
gzip $BACKUP_FILE

# Upload to S3 (optional)
if [ -n "$AWS_S3_BUCKET" ]; then
    aws s3 cp ${BACKUP_FILE}.gz s3://$AWS_S3_BUCKET/backups/
    echo "Backup uploaded to S3"
fi

# Clean old backups
find $BACKUP_DIR -name "*.dump.gz" -mtime +$RETENTION_DAYS -delete

echo "Backup completed: ${BACKUP_FILE}.gz"
```

**2. Create Restore Script**
```bash
# scripts/restore_database.sh
#!/bin/bash

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <backup_file>"
    exit 1
fi

BACKUP_FILE=$1
DATABASE_URL=$(vault kv get -field=url secret/database)

# Decompress if needed
if [[ $BACKUP_FILE == *.gz ]]; then
    gunzip -c $BACKUP_FILE > /tmp/restore.dump
    BACKUP_FILE=/tmp/restore.dump
fi

# Restore
echo "Restoring from $BACKUP_FILE"
pg_restore -d $DATABASE_URL --clean --if-exists $BACKUP_FILE

echo "Restore completed"
```

**3. Test Backup & Restore**
```bash
# scripts/test_backup_restore.sh
#!/bin/bash

set -e

echo "Testing backup and restore..."

# 1. Create test data
psql $DATABASE_URL -c "INSERT INTO organizations (organization_id, organization_name) VALUES ('test_org', 'Test Org');"

# 2. Perform backup
./scripts/backup_database.sh

# 3. Delete test data
psql $DATABASE_URL -c "DELETE FROM organizations WHERE organization_id = 'test_org';"

# 4. Restore from backup
LATEST_BACKUP=$(ls -t /backups/*.dump.gz | head -1)
./scripts/restore_database.sh $LATEST_BACKUP

# 5. Verify test data restored
COUNT=$(psql $DATABASE_URL -t -c "SELECT COUNT(*) FROM organizations WHERE organization_id = 'test_org';")

if [ "$COUNT" -eq "1" ]; then
    echo "✅ Backup and restore test PASSED"
else
    echo "❌ Backup and restore test FAILED"
    exit 1
fi
```

**4. Set Up Automated Backups**
```bash
# Add to crontab
# Backup every 6 hours
0 */6 * * * /path/to/scripts/backup_database.sh >> /var/log/encypher-backup.log 2>&1

# Test restore weekly
0 2 * * 0 /path/to/scripts/test_backup_restore.sh >> /var/log/encypher-restore-test.log 2>&1
```

---

#### Day 10: Audit Logging

**1. Create Audit Log Model**
```python
# enterprise_api/app/models/audit_log.py
from sqlalchemy import Column, String, DateTime, JSON, Integer
from app.database import Base
import datetime

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    user_id = Column(String, nullable=True)
    organization_id = Column(String, nullable=False)
    action = Column(String, nullable=False)  # e.g., "document.sign", "key.create"
    resource_type = Column(String, nullable=False)  # e.g., "document", "api_key"
    resource_id = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    request_id = Column(String, nullable=True)
    details = Column(JSON, nullable=True)
    result = Column(String, nullable=False)  # "success" or "failure"
    error_message = Column(String, nullable=True)
```

**2. Create Audit Service**
```python
# enterprise_api/app/services/audit_service.py
from app.models.audit_log import AuditLog
from sqlalchemy.ext.asyncio import AsyncSession

class AuditService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def log_event(
        self,
        action: str,
        resource_type: str,
        organization_id: str,
        resource_id: str = None,
        user_id: str = None,
        ip_address: str = None,
        user_agent: str = None,
        request_id: str = None,
        details: dict = None,
        result: str = "success",
        error_message: str = None
    ):
        """Log an audit event."""
        audit_log = AuditLog(
            user_id=user_id,
            organization_id=organization_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
            request_id=request_id,
            details=details,
            result=result,
            error_message=error_message
        )
        
        self.db.add(audit_log)
        await self.db.commit()
```

**3. Add Audit Logging to Endpoints**
```python
# enterprise_api/app/routers/signing.py
from app.services.audit_service import AuditService

@router.post("/sign")
async def sign_document(
    request: SignRequest,
    org_details: dict = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db),
    http_request: Request = None
):
    audit_service = AuditService(db)
    
    try:
        result = await signing_service.sign(...)
        
        # Log success
        await audit_service.log_event(
            action="document.sign",
            resource_type="document",
            resource_id=result.document_id,
            organization_id=org_details["organization_id"],
            ip_address=http_request.client.host,
            user_agent=http_request.headers.get("user-agent"),
            request_id=http_request.state.request_id,
            details={
                "document_length": len(request.text),
                "has_metadata": bool(request.metadata)
            },
            result="success"
        )
        
        return result
    except Exception as e:
        # Log failure
        await audit_service.log_event(
            action="document.sign",
            resource_type="document",
            organization_id=org_details["organization_id"],
            ip_address=http_request.client.host,
            user_agent=http_request.headers.get("user-agent"),
            request_id=http_request.state.request_id,
            result="failure",
            error_message=str(e)
        )
        raise
```

**4. Create Audit Log Query Endpoints**
```python
# enterprise_api/app/routers/audit.py
from fastapi import APIRouter, Depends
from app.services.audit_service import AuditService

router = APIRouter(prefix="/audit", tags=["Audit"])

@router.get("/logs")
async def get_audit_logs(
    start_date: datetime = None,
    end_date: datetime = None,
    action: str = None,
    resource_type: str = None,
    limit: int = 100,
    org_details: dict = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db)
):
    """Get audit logs for organization."""
    # Query audit logs
    query = db.query(AuditLog).filter(
        AuditLog.organization_id == org_details["organization_id"]
    )
    
    if start_date:
        query = query.filter(AuditLog.timestamp >= start_date)
    if end_date:
        query = query.filter(AuditLog.timestamp <= end_date)
    if action:
        query = query.filter(AuditLog.action == action)
    if resource_type:
        query = query.filter(AuditLog.resource_type == resource_type)
    
    logs = await query.order_by(AuditLog.timestamp.desc()).limit(limit).all()
    
    return {"logs": logs}
```

---

## 🧪 Testing Phase 1

### Integration Tests
```python
# tests/test_monitoring.py
import pytest
from prometheus_client import REGISTRY

def test_metrics_endpoint(client):
    """Test that metrics endpoint returns Prometheus format."""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "encypher_requests_total" in response.text

def test_business_metrics_recorded(client, api_key):
    """Test that business metrics are recorded."""
    # Sign document
    response = client.post(
        "/api/v1/sign",
        headers={"Authorization": f"Bearer {api_key}"},
        json={"text": "Test", "title": "Test"}
    )
    assert response.status_code == 200
    
    # Check metric
    metric = REGISTRY.get_sample_value(
        "encypher_documents_signed_total",
        {"organization_id": "test_org"}
    )
    assert metric > 0

def test_audit_logging(client, api_key, db):
    """Test that audit logs are created."""
    # Sign document
    response = client.post(
        "/api/v1/sign",
        headers={"Authorization": f"Bearer {api_key}"},
        json={"text": "Test", "title": "Test"}
    )
    
    # Check audit log
    audit_log = db.query(AuditLog).filter(
        AuditLog.action == "document.sign"
    ).first()
    
    assert audit_log is not None
    assert audit_log.result == "success"
    assert audit_log.organization_id == "test_org"
```

---

## 📊 Success Criteria

By the end of Phase 1, you should have:

- [ ] **Prometheus metrics** exposed on `/metrics` endpoint
- [ ] **Grafana dashboards** showing request rate, latency, errors
- [ ] **Jaeger tracing** with traces visible for all requests
- [ ] **Structured logging** with JSON format and request IDs
- [ ] **Vault secrets** for all sensitive configuration
- [ ] **Automated backups** running every 6 hours
- [ ] **Backup restoration** tested and documented
- [ ] **Audit logging** for all API operations
- [ ] **Audit log queries** available via API
- [ ] **All tests passing** with >80% coverage

---

## 🚀 Deployment Checklist

- [ ] Deploy monitoring stack (Prometheus, Grafana, Jaeger)
- [ ] Deploy Vault and migrate secrets
- [ ] Set up backup cron jobs
- [ ] Test backup restoration
- [ ] Configure alerting rules in Prometheus
- [ ] Set up PagerDuty/Opsgenie integration
- [ ] Document runbooks for common incidents
- [ ] Train team on monitoring tools
- [ ] Conduct incident response drill

---

## 📚 Additional Resources

- [Prometheus Best Practices](https://prometheus.io/docs/practices/)
- [OpenTelemetry Python](https://opentelemetry.io/docs/instrumentation/python/)
- [HashiCorp Vault Tutorial](https://learn.hashicorp.com/vault)
- [PostgreSQL Backup & Recovery](https://www.postgresql.org/docs/current/backup.html)
- [Grafana Dashboard Examples](https://grafana.com/grafana/dashboards/)

---

**Next**: [Phase 2: Performance & Reliability](./PHASE2_IMPLEMENTATION_GUIDE.md)
