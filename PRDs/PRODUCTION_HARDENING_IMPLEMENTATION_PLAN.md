# Production Hardening Implementation Plan

**Timeline**: 2 weeks  
**Approach**: Local testing first, then Railway deployment  
**Current Score**: 72/100 → **Target**: 90/100

---

## 🎯 Implementation Strategy

### Phase Approach:
1. **Implement locally** with docker-compose
2. **Test thoroughly** on local environment
3. **Deploy to Railway** once validated
4. **Monitor and iterate**

---

## 📋 Week 1: Critical Monitoring & Security

### Day 1-2: Add Metrics to All Services ✅ (Started)

**Goal**: Every service exposes Prometheus metrics

**Tasks**:
- [x] Auth service metrics (DONE)
- [ ] Copy metrics module to all other services
- [ ] Add service-specific business metrics
- [ ] Test metrics endpoints locally

**Implementation**:
```bash
# For each service:
1. Copy app/monitoring/ from auth-service
2. Update metrics.py with service-specific metrics
3. Add setup_metrics(app) to main.py
4. Test: curl http://localhost:800X/metrics
```

**Local Testing**:
```bash
# Start service
cd services/user-service
uv run python -m app.main

# Check metrics
curl http://localhost:8002/metrics | grep -E "user_|http_"
```

---

### Day 3: Structured Logging with Request IDs

**Goal**: All logs are JSON-formatted with request tracking

**Tasks**:
- [ ] Create logging middleware
- [ ] Add request ID generation
- [ ] Configure structured logging (structlog)
- [ ] Add to all services
- [ ] Test log output

**Implementation**:

Create `services/auth-service/app/middleware/logging.py`:
```python
import uuid
import structlog
from starlette.middleware.base import BaseHTTPMiddleware

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Bind request context
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            client_ip=request.client.host
        )
        
        logger = structlog.get_logger()
        logger.info("request_started")
        
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        
        logger.info("request_completed", status_code=response.status_code)
        
        return response
```

**Dependencies**:
```bash
cd services/auth-service
uv add structlog python-json-logger
```

**Local Testing**:
```bash
# Start service and make request
curl http://localhost:8001/health -v

# Check logs for JSON format with request_id
```

---

### Day 4: Audit Logging

**Goal**: Track all security-critical operations

**Tasks**:
- [ ] Create audit_log database table
- [ ] Create audit logging service
- [ ] Add audit logging to endpoints
- [ ] Test audit log queries

**Implementation**:

Create `services/auth-service/app/models/audit_log.py`:
```python
from sqlalchemy import Column, String, DateTime, JSON, Integer
from datetime import datetime
from ..db.models import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    user_id = Column(String, nullable=True, index=True)
    organization_id = Column(String, nullable=True, index=True)
    action = Column(String, nullable=False, index=True)
    resource_type = Column(String, nullable=False)
    resource_id = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    request_id = Column(String, nullable=True)
    details = Column(JSON, nullable=True)
    result = Column(String, nullable=False)  # success/failure
    error_message = Column(String, nullable=True)
```

Create `services/auth-service/app/services/audit_service.py`:
```python
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.audit_log import AuditLog
from datetime import datetime

class AuditService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def log(
        self,
        action: str,
        resource_type: str,
        result: str = "success",
        user_id: str = None,
        organization_id: str = None,
        resource_id: str = None,
        ip_address: str = None,
        user_agent: str = None,
        request_id: str = None,
        details: dict = None,
        error_message: str = None
    ):
        audit_log = AuditLog(
            timestamp=datetime.utcnow(),
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
        return audit_log
```

**Local Testing**:
```bash
# Make authenticated request
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'

# Check audit logs in database
psql $DATABASE_URL -c "SELECT * FROM audit_logs ORDER BY timestamp DESC LIMIT 5;"
```

---

### Day 5: Local Docker Compose with Monitoring

**Goal**: Run entire stack locally with monitoring

**Tasks**:
- [ ] Create comprehensive docker-compose.yml
- [ ] Add Prometheus, Grafana, Jaeger
- [ ] Configure service discovery
- [ ] Test full stack locally

**Implementation**:

Create `docker-compose.monitoring.yml`:
```yaml
version: '3.8'

services:
  # Databases
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: encypher
      POSTGRES_USER: encypher
      POSTGRES_PASSWORD: encypher_dev
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis-cache:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  redis-celery:
    image: redis:7-alpine
    ports:
      - "6380:6379"

  # Monitoring
  prometheus:
    build: ./infrastructure/prometheus
    ports:
      - "9090:9090"
    volumes:
      - prometheus_data:/prometheus

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      GF_SECURITY_ADMIN_PASSWORD: admin
      GF_INSTALL_PLUGINS: redis-datasource
    volumes:
      - grafana_data:/var/lib/grafana
      - ./infrastructure/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./infrastructure/grafana/datasources:/etc/grafana/provisioning/datasources

  jaeger:
    image: jaegertracing/all-in-one:latest
    ports:
      - "5775:5775/udp"
      - "6831:6831/udp"
      - "6832:6832/udp"
      - "5778:5778"
      - "16686:16686"
      - "14268:14268"
      - "14250:14250"
      - "9411:9411"
    environment:
      COLLECTOR_ZIPKIN_HOST_PORT: ":9411"

  # Microservices
  auth-service:
    build: ./services/auth-service
    ports:
      - "8001:8001"
    environment:
      DATABASE_URL: postgresql://encypher:encypher_dev@postgres:5432/encypher
      REDIS_URL: redis://redis-cache:6379
      SERVICE_PORT: 8001
      LOG_LEVEL: INFO
    depends_on:
      - postgres
      - redis-cache

  user-service:
    build: ./services/user-service
    ports:
      - "8002:8002"
    environment:
      DATABASE_URL: postgresql://encypher:encypher_dev@postgres:5432/encypher
      REDIS_URL: redis://redis-cache:6379
      AUTH_SERVICE_URL: http://auth-service:8001
      SERVICE_PORT: 8002
    depends_on:
      - postgres
      - redis-cache
      - auth-service

  key-service:
    build: ./services/key-service
    ports:
      - "8003:8003"
    environment:
      DATABASE_URL: postgresql://encypher:encypher_dev@postgres:5432/encypher
      REDIS_URL: redis://redis-cache:6379
      AUTH_SERVICE_URL: http://auth-service:8001
      SERVICE_PORT: 8003
    depends_on:
      - postgres
      - redis-cache
      - auth-service

  encoding-service:
    build: ./services/encoding-service
    ports:
      - "8004:8004"
    environment:
      DATABASE_URL: postgresql://encypher:encypher_dev@postgres:5432/encypher
      REDIS_URL: redis://redis-cache:6379
      AUTH_SERVICE_URL: http://auth-service:8001
      KEY_SERVICE_URL: http://key-service:8003
      SERVICE_PORT: 8004
    depends_on:
      - postgres
      - redis-cache
      - auth-service
      - key-service

  verification-service:
    build: ./services/verification-service
    ports:
      - "8005:8005"
    environment:
      DATABASE_URL: postgresql://encypher:encypher_dev@postgres:5432/encypher
      REDIS_URL: redis://redis-cache:6379
      SERVICE_PORT: 8005
    depends_on:
      - postgres
      - redis-cache

  analytics-service:
    build: ./services/analytics-service
    ports:
      - "8006:8006"
    environment:
      DATABASE_URL: postgresql://encypher:encypher_dev@postgres:5432/encypher
      REDIS_URL: redis://redis-cache:6379
      AUTH_SERVICE_URL: http://auth-service:8001
      SERVICE_PORT: 8006
    depends_on:
      - postgres
      - redis-cache
      - auth-service

  billing-service:
    build: ./services/billing-service
    ports:
      - "8007:8007"
    environment:
      DATABASE_URL: postgresql://encypher:encypher_dev@postgres:5432/encypher
      REDIS_URL: redis://redis-cache:6379
      AUTH_SERVICE_URL: http://auth-service:8001
      SERVICE_PORT: 8007
    depends_on:
      - postgres
      - redis-cache
      - auth-service

  notification-service:
    build: ./services/notification-service
    ports:
      - "8008:8008"
    environment:
      DATABASE_URL: postgresql://encypher:encypher_dev@postgres:5432/encypher
      REDIS_URL: redis://redis-cache:6379
      SERVICE_PORT: 8008
    depends_on:
      - postgres
      - redis-cache

volumes:
  postgres_data:
  prometheus_data:
  grafana_data:
```

**Local Testing**:
```bash
# Start entire stack
docker-compose -f docker-compose.monitoring.yml up -d

# Check all services are healthy
docker-compose -f docker-compose.monitoring.yml ps

# Access monitoring
open http://localhost:9090  # Prometheus
open http://localhost:3000  # Grafana (admin/admin)
open http://localhost:16686 # Jaeger

# Test service endpoints
for port in {8001..8008}; do
  echo "Testing port $port..."
  curl http://localhost:$port/health
done
```

---

## 📋 Week 2: Performance & Resilience

### Day 6-7: Redis Caching Implementation

**Goal**: Reduce database load with intelligent caching

**Tasks**:
- [ ] Add caching dependencies
- [ ] Create cache service
- [ ] Add caching to frequently accessed data
- [ ] Test cache hit rates

**Implementation**:

Add dependencies:
```bash
cd services/auth-service
uv add aiocache redis
```

Create `services/auth-service/app/services/cache_service.py`:
```python
from aiocache import Cache
from aiocache.serializers import JsonSerializer
import hashlib

class CacheService:
    def __init__(self, redis_url: str):
        self.cache = Cache(
            Cache.REDIS,
            endpoint=redis_url.split("://")[1].split(":")[0],
            port=int(redis_url.split(":")[-1]),
            serializer=JsonSerializer(),
            namespace="encypher"
        )
    
    def _make_key(self, prefix: str, *args) -> str:
        """Generate cache key from prefix and arguments."""
        key_parts = [prefix] + [str(arg) for arg in args]
        key_string = ":".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    async def get(self, prefix: str, *args):
        """Get value from cache."""
        key = self._make_key(prefix, *args)
        return await self.cache.get(key)
    
    async def set(self, prefix: str, value, ttl: int = 300, *args):
        """Set value in cache with TTL in seconds."""
        key = self._make_key(prefix, *args)
        await self.cache.set(key, value, ttl=ttl)
    
    async def delete(self, prefix: str, *args):
        """Delete value from cache."""
        key = self._make_key(prefix, *args)
        await self.cache.delete(key)
    
    async def clear_pattern(self, pattern: str):
        """Clear all keys matching pattern."""
        # Implementation depends on Redis version
        pass
```

Use in endpoints:
```python
from app.services.cache_service import CacheService

cache = CacheService(settings.REDIS_URL)

@router.get("/users/{user_id}")
async def get_user(user_id: str):
    # Try cache first
    cached_user = await cache.get("user", user_id)
    if cached_user:
        return cached_user
    
    # Fetch from database
    user = await db.query(User).filter(User.id == user_id).first()
    
    # Cache for 5 minutes
    await cache.set("user", user.dict(), ttl=300, user_id)
    
    return user
```

**Local Testing**:
```bash
# Make request twice
time curl http://localhost:8001/api/v1/users/123  # First: slow (DB)
time curl http://localhost:8001/api/v1/users/123  # Second: fast (cache)

# Check Redis
redis-cli
> KEYS encypher:*
> GET encypher:user:123
```

---

### Day 8: Circuit Breakers & Retry Logic

**Goal**: Handle service failures gracefully

**Tasks**:
- [ ] Add circuit breaker library
- [ ] Implement circuit breakers for service calls
- [ ] Add retry logic with exponential backoff
- [ ] Test failure scenarios

**Implementation**:

Add dependencies:
```bash
cd services/auth-service
uv add pybreaker tenacity
```

Create `services/auth-service/app/utils/resilience.py`:
```python
from pybreaker import CircuitBreaker
from tenacity import retry, stop_after_attempt, wait_exponential
import httpx

# Circuit breaker for external services
auth_service_breaker = CircuitBreaker(
    fail_max=5,
    timeout_duration=60,
    name="auth_service"
)

key_service_breaker = CircuitBreaker(
    fail_max=5,
    timeout_duration=60,
    name="key_service"
)

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def call_with_retry(url: str, method: str = "GET", **kwargs):
    """Make HTTP call with retry logic."""
    async with httpx.AsyncClient() as client:
        if method == "GET":
            response = await client.get(url, **kwargs)
        elif method == "POST":
            response = await client.post(url, **kwargs)
        
        response.raise_for_status()
        return response.json()

@auth_service_breaker
async def call_auth_service(endpoint: str, **kwargs):
    """Call auth service with circuit breaker."""
    url = f"{settings.AUTH_SERVICE_URL}{endpoint}"
    return await call_with_retry(url, **kwargs)
```

**Local Testing**:
```bash
# Stop auth service
docker-compose -f docker-compose.monitoring.yml stop auth-service

# Try to call dependent service
curl http://localhost:8002/api/v1/users/me

# Should fail gracefully with circuit breaker message
# Restart auth service
docker-compose -f docker-compose.monitoring.yml start auth-service

# Circuit breaker should recover automatically
```

---

### Day 9: Background Task Queue (Celery)

**Goal**: Handle long-running operations asynchronously

**Tasks**:
- [ ] Add Celery to services that need it
- [ ] Create task definitions
- [ ] Configure Celery workers
- [ ] Test task execution

**Implementation**:

Add dependencies:
```bash
cd services/encoding-service
uv add celery[redis]
```

Create `services/encoding-service/app/tasks/celery_app.py`:
```python
from celery import Celery
from ..core.config import settings

celery_app = Celery(
    "encypher",
    broker=settings.REDIS_CELERY_URL,
    backend=settings.REDIS_CELERY_URL
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
)
```

Create `services/encoding-service/app/tasks/signing_tasks.py`:
```python
from .celery_app import celery_app
from ..services.encoding_service import EncodingService

@celery_app.task(name="sign_document_batch")
def sign_document_batch(documents: list, metadata: dict):
    """Sign multiple documents asynchronously."""
    service = EncodingService()
    results = []
    
    for doc in documents:
        result = service.sign_document(doc, metadata)
        results.append(result)
    
    return results

@celery_app.task(name="sign_large_document")
def sign_large_document(document_id: str, content: str, metadata: dict):
    """Sign a large document asynchronously."""
    service = EncodingService()
    return service.sign_document(content, metadata)
```

Update endpoint to use tasks:
```python
from app.tasks.signing_tasks import sign_document_batch

@router.post("/sign/batch")
async def sign_batch(documents: list):
    # Queue task
    task = sign_document_batch.delay(documents, metadata)
    
    return {
        "task_id": task.id,
        "status": "queued",
        "message": "Batch signing started"
    }

@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    task = celery_app.AsyncResult(task_id)
    
    return {
        "task_id": task_id,
        "status": task.state,
        "result": task.result if task.ready() else None
    }
```

Add Celery worker to docker-compose:
```yaml
  encoding-worker:
    build: ./services/encoding-service
    command: celery -A app.tasks.celery_app worker --loglevel=info
    environment:
      DATABASE_URL: postgresql://encypher:encypher_dev@postgres:5432/encypher
      REDIS_CELERY_URL: redis://redis-celery:6379
    depends_on:
      - postgres
      - redis-celery
```

**Local Testing**:
```bash
# Start Celery worker
docker-compose -f docker-compose.monitoring.yml up -d encoding-worker

# Submit batch job
curl -X POST http://localhost:8004/api/v1/sign/batch \
  -H "Content-Type: application/json" \
  -d '{"documents":[...]}'

# Check task status
curl http://localhost:8004/api/v1/tasks/{task_id}

# Monitor Celery
docker-compose -f docker-compose.monitoring.yml logs -f encoding-worker
```

---

### Day 10: Integration Testing

**Goal**: Comprehensive tests for all services

**Tasks**:
- [ ] Set up pytest with async support
- [ ] Write integration tests for each service
- [ ] Test service-to-service communication
- [ ] Test with monitoring enabled

**Implementation**:

Create `services/auth-service/tests/integration/test_auth_flow.py`:
```python
import pytest
import httpx
from datetime import datetime

@pytest.mark.asyncio
async def test_complete_auth_flow():
    """Test complete authentication flow."""
    base_url = "http://localhost:8001"
    
    async with httpx.AsyncClient() as client:
        # 1. Register user
        register_response = await client.post(
            f"{base_url}/api/v1/auth/signup",
            json={
                "email": f"test_{datetime.now().timestamp()}@example.com",
                "password": "SecurePass123!",
                "name": "Test User"
            }
        )
        assert register_response.status_code == 201
        user_data = register_response.json()
        
        # 2. Login
        login_response = await client.post(
            f"{base_url}/api/v1/auth/login",
            json={
                "email": user_data["email"],
                "password": "SecurePass123!"
            }
        )
        assert login_response.status_code == 200
        tokens = login_response.json()
        assert "access_token" in tokens
        assert "refresh_token" in tokens
        
        # 3. Verify token
        verify_response = await client.post(
            f"{base_url}/api/v1/auth/verify",
            headers={"Authorization": f"Bearer {tokens['access_token']}"}
        )
        assert verify_response.status_code == 200
        
        # 4. Refresh token
        refresh_response = await client.post(
            f"{base_url}/api/v1/auth/refresh",
            json={"refresh_token": tokens["refresh_token"]}
        )
        assert refresh_response.status_code == 200
        new_tokens = refresh_response.json()
        assert "access_token" in new_tokens
        
        # 5. Logout
        logout_response = await client.post(
            f"{base_url}/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {new_tokens['access_token']}"}
        )
        assert logout_response.status_code == 200

@pytest.mark.asyncio
async def test_metrics_endpoint():
    """Test that metrics are being collected."""
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8001/metrics")
        assert response.status_code == 200
        
        metrics_text = response.text
        assert "auth_attempts_total" in metrics_text
        assert "http_requests_total" in metrics_text

@pytest.mark.asyncio
async def test_audit_logging():
    """Test that audit logs are created."""
    # Make authenticated request
    # Check database for audit log entry
    pass
```

Run tests:
```bash
# Start services
docker-compose -f docker-compose.monitoring.yml up -d

# Run integration tests
cd services/auth-service
uv run pytest tests/integration/ -v

# Check coverage
uv run pytest tests/ --cov=app --cov-report=html
```

---

## 📊 Progress Tracking

### Week 1 Checklist:
- [ ] Day 1-2: Add metrics to all services
- [ ] Day 3: Structured logging
- [ ] Day 4: Audit logging
- [ ] Day 5: Local docker-compose with monitoring

### Week 2 Checklist:
- [ ] Day 6-7: Redis caching
- [ ] Day 8: Circuit breakers & retry logic
- [ ] Day 9: Celery background tasks
- [ ] Day 10: Integration testing

### Validation Checklist:
- [ ] All services expose /metrics endpoint
- [ ] All services log in JSON format with request IDs
- [ ] Audit logs capture all security operations
- [ ] Prometheus scrapes all services successfully
- [ ] Grafana dashboards show real data
- [ ] Jaeger shows distributed traces
- [ ] Redis caching reduces database load
- [ ] Circuit breakers prevent cascading failures
- [ ] Celery processes background tasks
- [ ] Integration tests pass at 80%+ coverage

---

## 🚀 Deployment to Railway

After local validation:

### Week 3: Railway Deployment
1. Deploy services one by one
2. Deploy monitoring infrastructure
3. Configure environment variables
4. Test in production
5. Monitor for 48 hours

### Week 4: Optimization
1. Tune cache TTLs
2. Optimize database queries
3. Add more dashboards
4. Load testing
5. Security audit

---

## 📈 Expected Improvements

**Production Readiness Score**:
- Current: 72/100
- After Week 1: 82/100
- After Week 2: 90/100
- After Railway Deploy: 92/100

**Specific Improvements**:
- Observability: 40 → 90
- Security: 65 → 85
- Performance: 70 → 88
- Resilience: 50 → 90
- Testing: 60 → 85

---

## 🎯 Success Criteria

### Week 1:
- ✅ All services have metrics
- ✅ Structured logging working
- ✅ Audit logs capturing events
- ✅ Full stack runs locally with monitoring
- ✅ Can view metrics in Grafana

### Week 2:
- ✅ Cache hit rate > 60%
- ✅ Circuit breakers prevent failures
- ✅ Background tasks process successfully
- ✅ Integration tests pass
- ✅ Test coverage > 80%

### Week 3:
- ✅ All services deployed to Railway
- ✅ Monitoring working in production
- ✅ No critical errors for 48 hours
- ✅ Response times < 200ms p95
- ✅ Error rate < 0.1%

---

**Status**: Ready to implement  
**Next Action**: Start Day 1-2 (Add metrics to all services)  
**Estimated Time**: 2 weeks for complete implementation
