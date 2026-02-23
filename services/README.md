# Encypher Microservices

This directory contains the microservices architecture for the Encypher platform. Each service is independently deployable and communicates via HTTP/gRPC.

## 🏗️ Architecture Overview

The Encypher platform uses a microservices architecture with all services running in Docker.

```
┌─────────────────────────────────────────────────────────────┐
│                   Traefik API Gateway                        │
│                      (Port 8000)                             │
│         Routes /api/v1/* to appropriate services             │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌───────▼────────┐   ┌───────▼────────┐   ┌───────▼────────┐
│  Auth Service  │   │  User Service  │   │  Key Service   │
│   (Port 8001)  │   │   (Port 8002)  │   │   (Port 8003)  │
└────────────────┘   └────────────────┘   └────────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌───────▼────────┐   ┌───────▼────────┐   ┌───────▼────────┐
│Encoding Service│   │Verification Svc│   │Analytics Svc   │
│   (Port 8004)  │   │   (Port 8005)  │   │   (Port 8006)  │
└────────────────┘   └────────────────┘   └────────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌───────▼────────┐   ┌───────▼────────┐   ┌───────▼────────┐
│Billing Service │   │Notification Svc│   │ Enterprise API │
│   (Port 8007)  │   │   (Port 8008)  │   │   (Port 9000)  │
└────────────────┘   └────────────────┘   └────────────────┘
```

## 📦 Services

### All Services

| Service | Port | Database | Status | Description |
|---------|------|----------|--------|-------------|
| **Traefik** | 8000 | - | ✅ Active | API Gateway, routes to microservices |
| [**auth-service**](./auth-service/) | 8001 | postgres-core | ✅ Active | Authentication, JWT, OAuth |
| [**web-service**](./web-service/) | 8002 | postgres-core | ✅ Active | Marketing forms, demo requests, analytics |
| [**key-service**](./key-service/) | 8003 | postgres-core | ✅ Active | API keys, organizations |
| [**encoding-service**](./encoding-service/) | 8004 | postgres-core | ✅ Active | C2PA encoding |
| [**verification-service**](./verification-service/) | 8005 | postgres-core | ✅ Active | Content verification |
| [**analytics-service**](./analytics-service/) | 8006 | postgres-core | ✅ Active | Usage metrics |
| [**billing-service**](./billing-service/) | 8007 | postgres-core | ✅ Active | Subscriptions, Stripe |
| [**notification-service**](./notification-service/) | 8008 | postgres-core | ✅ Active | Email, notifications |
| **enterprise-api** | 9000 | core + content | ✅ Active | C2PA sign/verify API, Rights Management System |

### Infrastructure

| Service | Port | Description |
|---------|------|-------------|
| **PostgreSQL Core** | 5432 | Core business data (users, orgs, keys) |
| **PostgreSQL Content** | 5433 | Content data (documents, verification) |
| **Redis Cache** | 6379 | Caching, sessions, rate limiting |
| **Redis Celery** | 6380 | Background task queue |

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **Docker & Docker Compose**
- **PostgreSQL** (or use Docker)
- **Redis** (or use Docker)
- **UV** package manager

### Run All Services (Development)

```bash
# From the services directory
cd services

# Start all services with Docker Compose
docker-compose -f docker-compose.dev.yml up --build

# Or start individual services
cd auth-service
uv sync
uv run python -m app.main
```

### Run Individual Service

```bash
# Navigate to service directory
cd services/auth-service

# Install dependencies
uv sync

# Configure environment
cp .env.example .env
# Edit .env with your configuration

# Run the service
uv run python -m app.main
```

## 🔧 Development

### Adding a New Service

1. **Create service directory:**
   ```bash
   mkdir services/new-service
   cd services/new-service
   ```

2. **Initialize UV project:**
   ```bash
   uv init
   ```

3. **Add dependencies:**
   ```bash
   uv add fastapi uvicorn sqlalchemy pydantic
   uv add --dev pytest black ruff mypy
   ```

4. **Create service structure:**
   ```
   new-service/
   ├── app/
   │   ├── __init__.py
   │   ├── main.py
   │   ├── api/
   │   ├── core/
   │   ├── db/
   │   ├── models/
   │   └── services/
   ├── tests/
   ├── .env.example
   ├── Dockerfile
   ├── README.md
   ├── pyproject.toml
   └── agents.md
   ```

5. **Add to docker-compose.dev.yml**

6. **Document in this README**

### Service Development Guidelines

#### Package Management
**ALWAYS use UV:**
```bash
# Add dependency
uv add package-name

# Add dev dependency
uv add --dev pytest

# Never edit pyproject.toml directly
# Never use pip
```

#### Service Structure
All services should follow this structure:
```
service-name/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app
│   ├── api/
│   │   └── v1/
│   │       └── endpoints.py # API routes
│   ├── core/
│   │   ├── config.py        # Configuration
│   │   └── security.py      # Security utilities
│   ├── db/
│   │   ├── models.py        # SQLAlchemy models
│   │   └── session.py       # Database session
│   ├── models/
│   │   └── schemas.py       # Pydantic schemas
│   └── services/
│       └── service.py       # Business logic
├── tests/
├── .env.example
├── Dockerfile
├── README.md
├── pyproject.toml
└── agents.md                # Development constraints
```

#### API Versioning
- All endpoints under `/api/v1/`
- Health check at `/health`
- Metrics at `/metrics` (if enabled)

#### Configuration
- Use Pydantic Settings for configuration
- Load from environment variables
- Provide `.env.example` template

#### Testing
```bash
# Run tests
uv run pytest

# With coverage
uv run pytest --cov=app --cov-report=html

# Integration tests
uv run pytest tests/integration/
```

## 🔐 Security

### Authentication Flow
1. User authenticates with **auth-service**
2. Receives JWT access token + refresh token
3. Includes token in `Authorization: Bearer <token>` header
4. Services verify token with **auth-service**

### Inter-Service Communication
- Services communicate via HTTP/gRPC
- Use service mesh (Istio/Linkerd) in production
- Mutual TLS for service-to-service auth

### Secrets Management
- Use environment variables
- Kubernetes secrets in production
- Vault for sensitive data

## 📊 Monitoring & Observability

### Health Checks
All services expose `/health` endpoint:
```json
{
  "status": "healthy",
  "service": "service-name",
  "version": "1.0.0",
  "dependencies": {
    "database": "healthy",
    "redis": "healthy"
  }
}
```

### Metrics
- Prometheus metrics at `/metrics`
- Custom business metrics
- Request latency, error rates

### Logging
- Structured JSON logs
- Correlation IDs for request tracing
- Log levels: DEBUG, INFO, WARNING, ERROR

### Tracing
- OpenTelemetry integration
- Distributed tracing across services
- Jaeger/Zipkin for visualization

## 🐳 Docker & Deployment

### Docker Compose (Development)
```bash
# Start all services
docker-compose -f docker-compose.dev.yml up

# Start specific service
docker-compose -f docker-compose.dev.yml up auth-service

# View logs
docker-compose -f docker-compose.dev.yml logs -f auth-service

# Stop all
docker-compose -f docker-compose.dev.yml down
```

### Production Deployment
- Kubernetes manifests in `/k8s/`
- Helm charts for easy deployment
- CI/CD with GitHub Actions
- Blue-green deployments

### Railway Deployment (Monorepo)

Services that depend on `shared_commercial_libs` have a local copy in their `shared_libs/` directory.

**Automatic Sync:** A GitHub Action (`.github/workflows/sync-shared-libs.yml`) automatically syncs changes from `shared_commercial_libs/` to each service's `shared_libs/` folder whenever the shared library is updated.

**Railway Root Directory Settings:**
- **auth-service**: `services/auth-service`
- **notification-service**: `services/notification-service`
- **enterprise_api**: `enterprise_api`

**How it works:**
1. Developer updates `shared_commercial_libs/`
2. GitHub Action copies changes to `services/*/shared_libs/`
3. Railway detects changes and rebuilds affected services
4. Dockerfiles install from local `shared_libs/` directory

**Manual Sync (if needed):**
```bash
# From repo root
cp -r shared_commercial_libs services/auth-service/shared_libs
cp -r shared_commercial_libs services/notification-service/shared_libs
```

## 🔄 Service Dependencies

### auth-service
- **Depends on:** PostgreSQL, Redis
- **Used by:** All other services (token verification)

### key-service
- **Depends on:** PostgreSQL, auth-service
- **Used by:** encoding-service, verification-service

### encoding-service
- **Depends on:** key-service, auth-service
- **Used by:** API clients, dashboard

### verification-service
- **Depends on:** key-service, auth-service
- **Used by:** API clients, dashboard

### user-service
- **Depends on:** PostgreSQL, auth-service
- **Used by:** Dashboard, billing-service

### billing-service
- **Depends on:** PostgreSQL, user-service, auth-service
- **Used by:** Dashboard, API gateway

### analytics-service
- **Depends on:** ClickHouse, auth-service
- **Used by:** Dashboard, reporting

### notification-service
- **Depends on:** Redis, auth-service
- **Used by:** All services (async notifications)

## 🧪 Testing Strategy

### Unit Tests
- Test individual functions/classes
- Mock external dependencies
- Fast execution (<1s per test)

### Integration Tests
- Test service endpoints
- Use test database
- Test inter-service communication

### End-to-End Tests
- Test complete user flows
- Use Docker Compose test environment
- Run before deployment

## 📚 Documentation

Each service should have:
- **README.md** - Setup, API docs, usage
- **agents.md** - Development constraints, known issues
- **API.md** - Detailed API reference (if complex)
- **ARCHITECTURE.md** - Service architecture (if complex)

## 🔗 Related Documentation

- [Enterprise API](../enterprise_api/README.md) - Main API documentation
- [Dashboard App](../dashboard_app/README.md) - Dashboard integration
- [Architecture Docs](../docs/architecture/) - System architecture

## 🤝 Contributing

### Adding New Endpoints
1. Add route in `api/v1/endpoints.py`
2. Add schema in `models/schemas.py`
3. Add business logic in `services/`
4. Add tests in `tests/`
5. Update README.md

### Modifying Database Schema
1. Update model in `db/models.py`
2. Create migration (Alembic)
3. Test migration up/down
4. Update documentation

### Service Communication
- Use async HTTP clients (httpx)
- Implement circuit breakers
- Add retry logic with exponential backoff
- Handle timeouts gracefully

## 🐛 Troubleshooting

### Service Won't Start
```bash
# Check logs
docker-compose -f docker-compose.dev.yml logs service-name

# Check database connection
uv run python -c "from app.db.session import engine; print(engine.url)"

# Check environment variables
cat .env
```

### Database Connection Issues
```bash
# Test PostgreSQL connection
psql -h localhost -U postgres -d encypher_auth

# Check if database exists
psql -h localhost -U postgres -l
```

### Token Verification Fails
```bash
# Check auth-service is running
curl http://localhost:8001/health

# Verify token manually
curl -X POST http://localhost:8001/api/v1/auth/verify \
  -H "Authorization: Bearer <token>"
```

## 📄 License

Proprietary - Encypher Corporation. All rights reserved.
