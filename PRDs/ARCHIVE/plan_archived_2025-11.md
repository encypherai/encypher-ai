# Encypher Commercial - Development Plan

**Last Updated:** November 27, 2025  
**Status:** Production Ready (Core Infrastructure)

---

## Current Goal

Complete `15.0 - Web Service Migration`

---

## Active Work Items

### 🚧 In Progress

- [x] **15.0 Web Service Migration** (Marketing Site Backend) ✅
  - [x] 15.1 Convert pyproject.toml from Poetry to UV
  - [x] 15.2 Add ai-demo router (POST /demo-requests, POST /analytics/events)
  - [x] 15.3 Add publisher-demo router (POST /demo-requests, POST /analytics/events)
  - [x] 15.4 Add sales router (POST /enterprise-requests, POST /general-requests)
  - [x] 15.5 Add email service for notifications
  - [x] 15.6 Update marketing site to use web-service URL
  - [x] 15.7 Test all endpoints (10/10 passed)
  - [x] 15.8 Update documentation

- [ ] **11.0 Production Deployment**
  - [ ] 11.1 Railway deployment configuration
  - [ ] 11.2 Environment variable setup (see `services/ENV_VARS_MAPPING.md`)
  - [ ] 11.3 SSL certificate configuration
  - [ ] 11.4 Domain DNS setup

- [ ] **12.0 Stripe Integration Testing**
  - [ ] 12.1 Create Stripe products in dashboard
  - [ ] 12.2 Configure webhook endpoints
  - [ ] 12.3 Test end-to-end checkout flow

### 📋 Pending

- [ ] **13.0 JavaScript/TypeScript SDK**
  - See `PRDs/CURRENT/PRD_JavaScript_SDK.md`
  - Feature parity with Python SDK
  - React hooks and Next.js integration

- [ ] **14.0 CI/CD Pipeline**
  - [ ] 14.1 GitHub Actions for microservices
  - [ ] 14.2 Automated testing on PR
  - [ ] 14.3 Deployment automation

---

## Recently Completed (Nov 2025)

### Security & Quality Audit ✅
- Dependency version audit and updates (64 packages)
- Docker image security scanning (Trivy)
- Secret scanning (detect-secrets pre-commit)
- Type checking configuration (mypy)
- Test coverage setup (pytest-cov)
- Ruff security rules - all passing

### Database-per-Service Migration ✅
- All 9 microservices with isolated databases
- Alembic migrations run on startup
- Full auth flow tested (signup → login → API key → verify)
- 29/29 endpoint tests passing

### Enterprise API Test Fixes ✅
- Fixed Merkle endpoints (MerkleRoot.id, segment_metadata)
- Fixed schema/model alignment
- Added is_demo flag to demo keys
- 279 tests passing, 54 skipped (expected)

---

## Documentation Index

| Document | Location | Description |
|----------|----------|-------------|
| Architecture | `docs/architecture/DATABASE_ARCHITECTURE.md` | Database-per-service design |
| Environment Vars | `services/ENV_VARS_MAPPING.md` | Shared variables mapping |
| Railway Deploy | `docs/railway-deployment.md` | Deployment guide |
| Pricing Strategy | `docs/pricing/PRICING_STRATEGY.md` | Tier pricing and coalition |
| API Reference | `enterprise_api/README.md` | Enterprise API documentation |
| SDK Reference | `enterprise_sdk/README.md` | Python SDK documentation |

---

## Quick Commands

```bash
# Start all microservices
docker-compose -f docker-compose.microservices.yml up

# Run security checks
ruff check services/ enterprise_api/app/ --select=S

# Run tests
cd enterprise_api && uv run pytest tests/ -v

# Check service health
python scripts/test_microservices.py
```

---

## Historical Plans

Completed PRDs and historical plans are archived in `PRDs/ARCHIVE/`.
