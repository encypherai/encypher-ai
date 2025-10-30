# Enterprise API - Agent Development Guide

## Overview
Production-ready FastAPI service providing C2PA-compliant content signing and verification with enterprise features including Merkle trees, source attribution, and plagiarism detection.

## Current Status
✅ **Production Ready** - Fully functional with comprehensive features
✅ **Well Documented** - Extensive README with API reference
✅ **Clean Architecture** - Proper separation of concerns

## Architecture

### Tech Stack
- **Framework**: FastAPI (async)
- **Database**: PostgreSQL (async with SQLAlchemy)
- **Package Manager**: UV
- **Authentication**: API Key + JWT
- **Crypto**: encypher-ai core library
- **Deployment**: Railway/Docker

### Directory Structure
```
enterprise_api/
├── app/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Settings (Pydantic)
│   ├── database.py          # Database session
│   ├── dependencies.py      # Dependency injection
│   ├── api/
│   │   └── v1/
│   │       └── api.py       # API router aggregation
│   ├── routers/             # API endpoints
│   │   ├── signing.py       # POST /api/v1/sign
│   │   ├── verification.py  # POST /api/v1/verify
│   │   ├── lookup.py        # POST /api/v1/lookup
│   │   ├── dashboard.py     # GET /api/v1/dashboard
│   │   └── onboarding.py    # Onboarding endpoints
│   ├── models/              # Data models
│   │   ├── db_models.py     # SQLAlchemy models
│   │   ├── request_models.py
│   │   ├── response_models.py
│   │   ├── merkle.py
│   │   └── organization.py
│   ├── schemas/             # Pydantic schemas
│   │   ├── merkle.py
│   │   └── provisioning.py
│   ├── services/            # Business logic
│   │   ├── merkle_service.py
│   │   └── provisioning_service.py
│   ├── crud/                # Database operations
│   │   └── merkle.py
│   ├── middleware/          # Custom middleware
│   │   └── tier_check.py
│   └── utils/               # Utilities
│       ├── crypto_utils.py
│       ├── sentence_parser.py
│       ├── ssl_com_client.py
│       ├── quota.py
│       └── feature_flags.py
├── docs/
│   ├── API.md               # Complete API reference
│   ├── DEPLOYMENT.md
│   └── QUICKSTART.md
├── migrations/              # Database migrations
├── scripts/
│   ├── init_db.sql
│   └── init_db.py
├── tests/
├── pyproject.toml
└── README.md
```

## API Endpoints

### Core Endpoints (All Tiers)
| Endpoint | Method | Description | Tier |
|----------|--------|-------------|------|
| `/api/v1/sign` | POST | Sign content with C2PA manifest | All |
| `/api/v1/verify` | POST | Verify signed content | All |
| `/api/v1/lookup` | POST | Lookup sentence provenance | Pro+ |
| `/stats` | GET | Usage statistics | All |

### Enterprise Endpoints
| Endpoint | Method | Description | Tier |
|----------|--------|-------------|------|
| `/api/v1/enterprise/merkle/encode` | POST | Encode document into Merkle tree | Enterprise |
| `/api/v1/enterprise/merkle/attribute` | POST | Find source documents | Enterprise |
| `/api/v1/enterprise/merkle/detect-plagiarism` | POST | Detect plagiarism | Enterprise |

### Management Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/metrics` | GET | Prometheus metrics |
| `/docs` | GET | Swagger UI (dev only) |
| `/redoc` | GET | ReDoc (dev only) |

## Development Constraints

### Package Management
**CRITICAL**: Always use UV
```bash
# Add dependency
uv add fastapi sqlalchemy

# Add dev dependency
uv add --dev pytest pytest-asyncio

# Never edit pyproject.toml directly
# Never use pip
```

### Database Migrations
```bash
# Create migration
uv run alembic revision --autogenerate -m "description"

# Apply migrations
uv run alembic upgrade head

# Rollback
uv run alembic downgrade -1
```

### Running Locally
```bash
# Setup
cd enterprise_api
cp .env.example .env
# Edit .env with your config

# Install dependencies
uv sync

# Run database migrations
uv run python scripts/init_db.py

# Start server
uv run uvicorn app.main:app --reload --port 9000
```

### Testing
```bash
# Run all tests
uv run pytest

# With coverage
uv run pytest --cov=app --cov-report=html

# Integration tests only
uv run pytest tests/integration/

# Specific test file
uv run pytest tests/test_signing.py -v
```

## Configuration

### Environment Variables
**Required**:
- `DATABASE_URL` - PostgreSQL connection string
- `JWT_SECRET_KEY` - Secret for JWT signing
- `ENCRYPTION_KEY` - For sensitive data encryption

**Optional**:
- `DEMO_API_KEY` - Demo key for testing (bypasses DB)
- `DEMO_PRIVATE_KEY_HEX` - Demo signing key
- `SSL_COM_API_URL` - SSL.com API endpoint
- `SSL_COM_API_KEY` - SSL.com API key
- `ENVIRONMENT` - production/staging/development

### Feature Flags
```python
# In app/utils/feature_flags.py
FEATURES = {
    "merkle_trees": True,
    "source_attribution": True,
    "plagiarism_detection": True,
    "auto_provisioning": False,
}
```

## Integration Points

### With encypher-ai (core)
- Uses for C2PA manifest generation
- Uses for signature verification
- Uses for metadata embedding

### With SSL.com
- Certificate provisioning
- Certificate lifecycle management
- Automated renewal

### With Dashboard App
- Dashboard backend calls this API
- Proxies all signing operations
- Uses `/api/v1/sign`, `/api/v1/verify`

### With WordPress Plugin
- Plugin calls this API directly
- Uses `/api/v1/sign`, `/api/v1/verify`
- Requires API key authentication

### With Enterprise SDK
- SDK wraps this API
- Provides Python client
- Handles authentication, retries

## Authentication & Authorization

### API Key Authentication
```python
# Header format
Authorization: Bearer encypher_...

# Demo mode (bypasses database)
DEMO_API_KEY=demo-key-local
```

### Tier-Based Access
- **Free**: Basic signing/verification
- **Professional**: + Sentence lookup
- **Enterprise**: + Merkle trees, attribution, plagiarism

### Rate Limiting
| Tier | Requests/Second | Requests/Month |
|------|----------------|----------------|
| Free | 10 | 1,000 |
| Professional | 50 | 10,000 |
| Enterprise | Unlimited | Unlimited |

## Database Schema

### Core Tables
- `organizations` - Customer organizations
- `api_keys` - API key management
- `documents` - Signed documents metadata
- `sentences` - Sentence-level tracking
- `merkle_roots` - Merkle tree roots
- `merkle_subhashes` - Merkle tree nodes
- `merkle_proof_cache` - Cached proofs

### Indexes
- `idx_documents_org_id` - Organization lookup
- `idx_sentences_doc_id` - Document sentences
- `idx_merkle_roots_doc_id` - Merkle tree lookup
- `idx_api_keys_key_hash` - Fast key lookup

## Performance Considerations

### Benchmarks (Target)
| Operation | Avg Latency | P95 | P99 |
|-----------|-------------|-----|-----|
| Sign (1KB) | 45ms | 78ms | 120ms |
| Sign (10KB) | 67ms | 105ms | 150ms |
| Verify | 23ms | 45ms | 67ms |
| Lookup | 34ms | 56ms | 89ms |
| Merkle Encode | 123ms | 200ms | 300ms |

### Optimization Strategies
- Async database operations
- Connection pooling
- Caching (Redis for production)
- Batch operations where possible
- Lazy loading of relationships

## Security Considerations

### Data Protection
- API keys hashed with bcrypt
- Private keys encrypted at rest
- TLS 1.3 in transit
- SQL injection prevention (parameterized queries)

### Input Validation
- Pydantic models for all inputs
- Max content size limits
- Sanitized error messages (no stack traces in prod)

### Secrets Management
- Environment variables for secrets
- Kubernetes secrets in production
- Vault integration (optional)

## Monitoring & Observability

### Health Checks
```bash
curl http://localhost:9000/health
```

Response:
```json
{
  "status": "healthy",
  "service": "enterprise-api",
  "version": "1.0.0-preview",
  "database": "connected"
}
```

### Metrics
- Request count by endpoint
- Response time percentiles
- Error rates
- Database connection pool stats
- Active API keys

### Logging
- Structured JSON logs
- Request/response logging
- Error tracking with stack traces
- Correlation IDs for tracing

## Common Development Tasks

### Adding a New Endpoint
1. Create route in `app/routers/new_router.py`
2. Add request/response models in `app/models/`
3. Add business logic in `app/services/`
4. Add database operations in `app/crud/`
5. Register router in `app/api/v1/api.py`
6. Add tests in `tests/`
7. Update `docs/API.md`

### Adding a New Database Table
1. Add model in `app/models/db_models.py`
2. Create migration: `uv run alembic revision --autogenerate -m "add table"`
3. Review and edit migration file
4. Apply: `uv run alembic upgrade head`
5. Add CRUD operations in `app/crud/`
6. Add tests

### Modifying an Endpoint
1. Update route handler in `app/routers/`
2. Update request/response models if needed
3. Update business logic in `app/services/`
4. Update tests
5. Update `docs/API.md`
6. Test backward compatibility

## Testing Strategy

### Unit Tests
- Test individual functions
- Mock external dependencies
- Fast execution

### Integration Tests
- Test API endpoints
- Use test database
- Test authentication/authorization

### End-to-End Tests
- Test complete workflows
- Test with real encypher-ai library
- Test Merkle tree operations

### Test Coverage Goals
- Routes: 90%+
- Services: 90%+
- Utils: 80%+
- Overall: 85%+

## Deployment

### Docker
```bash
# Build
docker build -t encypher-enterprise-api .

# Run
docker run -p 9000:9000 \
  -e DATABASE_URL=postgresql://... \
  -e JWT_SECRET_KEY=... \
  encypher-enterprise-api
```

### Railway
```bash
# Deploy
railway up

# View logs
railway logs

# Environment variables set in Railway dashboard
```

### Kubernetes
```bash
# Apply manifests
kubectl apply -f k8s/

# Check status
kubectl get pods -l app=enterprise-api

# View logs
kubectl logs -f deployment/enterprise-api
```

## Troubleshooting

### Database Connection Issues
```bash
# Test connection
psql $DATABASE_URL

# Check migrations
uv run alembic current

# Reset database (dev only!)
uv run alembic downgrade base
uv run alembic upgrade head
```

### API Key Not Working
```bash
# Check API key in database
psql $DATABASE_URL -c "SELECT * FROM api_keys WHERE key_hash = encode(digest('encypher_...', 'sha256'), 'hex');"

# Use demo key for testing
export DEMO_API_KEY=demo-key-local
```

### Slow Performance
```bash
# Check database query performance
psql $DATABASE_URL -c "SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"

# Check connection pool
# Add logging in app/database.py

# Enable query logging
export LOG_LEVEL=DEBUG
```

## Known Issues

### None Critical
The API is production-ready with no major known issues.

### Minor Enhancements
1. **Add Redis caching** - For frequently accessed data
2. **Add request queuing** - For rate limiting
3. **Add webhook support** - For async notifications
4. **Add batch endpoints** - Sign/verify multiple documents

## Future Enhancements

### High Priority
1. **Redis Integration** - Caching and session management
2. **Webhook System** - Event notifications
3. **Batch Operations** - Bulk signing/verification
4. **GraphQL API** - Alternative to REST

### Medium Priority
5. **WebSocket Support** - Real-time updates
6. **gRPC Endpoints** - For service-to-service
7. **API Versioning** - v2 with breaking changes
8. **Advanced Analytics** - Usage patterns, insights

### Low Priority
9. **Multi-region Support** - Geographic distribution
10. **Custom Domains** - White-label API
11. **API Marketplace** - Third-party integrations

## Dependencies on Other Components

### Required
- `encypher-ai` - Core signing/verification
- PostgreSQL - Data persistence
- SSL.com API - Certificate provisioning (optional)

### Optional
- Redis - Caching (recommended for production)
- Prometheus - Metrics collection
- Sentry - Error tracking

### Used By
- Dashboard App - Primary consumer
- WordPress Plugin - Direct API calls
- Enterprise SDK - Python client wrapper
- Third-party integrations

## Best Practices

### API Design
- RESTful endpoints
- Consistent error responses
- Versioned API (`/api/v1/`)
- Comprehensive documentation

### Code Organization
- Routers for endpoints
- Services for business logic
- CRUD for database operations
- Utils for shared functionality

### Error Handling
```python
# Standard error response
{
  "success": false,
  "error": "Human-readable message",
  "error_code": "ERROR_CODE",
  "status_code": 400,
  "request_id": "req_abc123"
}
```

### Async Best Practices
- Use `async/await` for I/O operations
- Use async database sessions
- Avoid blocking operations
- Use background tasks for long operations

## License
Proprietary - EncypherAI Commercial Suite
