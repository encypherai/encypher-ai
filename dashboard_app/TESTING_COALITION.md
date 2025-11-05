# Coalition Testing Guide

Quick reference for running coalition tests.

---

## Prerequisites

### Backend
```powershell
cd dashboard_app\backend
uv sync
```

### Frontend
```powershell
cd dashboard_app\frontend
npm install
```

---

## Running Tests

### Backend API Tests

**All coalition API tests:**
```powershell
cd dashboard_app\backend
uv run pytest tests\api\test_coalition_api_async.py -v
```

**Specific test class:**
```powershell
uv run pytest tests\api\test_coalition_api_async.py::TestCoalitionStatsEndpoint -v
```

**Single test:**
```powershell
uv run pytest tests\api\test_coalition_api_async.py::TestCoalitionStatsEndpoint::test_get_stats_success -v
```

**With coverage:**
```powershell
uv run pytest tests\api\test_coalition_api_async.py --cov=app.api.endpoints.coalition --cov-report=html
```

### End-to-End Tests

**All E2E tests:**
```powershell
cd dashboard_app\backend
uv run pytest tests\e2e\test_coalition_flow.py -v -m e2e
```

**Specific scenario:**
```powershell
uv run pytest tests\e2e\test_coalition_flow.py::TestCoalitionUserJourney::test_complete_coalition_flow -v
```

### Frontend Component Tests

**All coalition tests:**
```powershell
cd dashboard_app\frontend
npm test -- --testPathPattern=coalition
```

**CoalitionPage tests:**
```powershell
npm test -- CoalitionPage.test.tsx
```

**Hook tests:**
```powershell
npm test -- useCoalition.test.tsx
```

**Watch mode:**
```powershell
npm test -- --watch --testPathPattern=coalition
```

**With coverage:**
```powershell
npm test -- --coverage --testPathPattern=coalition
```

### Load Tests

**Install locust (if not installed):**
```powershell
cd dashboard_app\backend
uv add --dev locust
```

**Start load test:**
```powershell
cd dashboard_app\backend\tests\load
uv run locust -f test_coalition_load.py --host=http://localhost:8000
```

**Access web UI:**
- Open browser: http://localhost:8089
- Configure number of users and spawn rate
- Start test and monitor results

**Headless mode (automated):**
```powershell
# Normal load (100 users, 10 min)
uv run locust -f test_coalition_load.py --host=http://localhost:8000 --users 100 --spawn-rate 10 --run-time 10m --headless

# Peak load (1000 users, 30 min)
uv run locust -f test_coalition_load.py --host=http://localhost:8000 --users 1000 --spawn-rate 50 --run-time 30m --headless

# Stress test (10K users, 1 hour)
uv run locust -f test_coalition_load.py --host=http://localhost:8000 --users 10000 --spawn-rate 100 --run-time 1h --headless
```

---

## Security Testing

### Dependency Scanning

**Backend:**
```powershell
cd dashboard_app\backend
uv run pip-audit
```

**Frontend:**
```powershell
cd dashboard_app\frontend
npm audit
npm audit fix  # Fix automatically if possible
```

### OWASP ZAP Scan

**Quick scan:**
```powershell
zap-cli quick-scan http://localhost:8000
```

**Full scan:**
```powershell
zap-cli active-scan http://localhost:8000
```

### Manual Security Checklist

Follow the comprehensive checklist:
```powershell
# Open in editor
code dashboard_app\COALITION_SECURITY_AUDIT.md
```

---

## Test Data Setup

### Create Test Users

**Python script:**
```python
# dashboard_app/backend/scripts/create_test_users.py
import asyncio
from app.core.database import get_db
from app.models.user import User
from app.models.coalition import CoalitionMember

async def create_test_users():
    async for db in get_db():
        # Create regular user
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed",
            is_active=True
        )
        db.add(user)
        
        # Create admin user
        admin = User(
            email="admin@example.com",
            username="admin",
            hashed_password="hashed",
            is_active=True,
            is_superuser=True
        )
        db.add(admin)
        
        await db.commit()
        print("Test users created!")

if __name__ == "__main__":
    asyncio.run(create_test_users())
```

**Run:**
```powershell
cd dashboard_app\backend
uv run python scripts\create_test_users.py
```

### Seed Test Data

**Create sample content and revenue:**
```powershell
cd dashboard_app\backend
uv run python scripts\seed_coalition_data.py
```

---

## Continuous Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/coalition-tests.yml
name: Coalition Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install UV
        run: pip install uv
      - name: Install dependencies
        run: |
          cd dashboard_app/backend
          uv sync
      - name: Run coalition API tests
        run: |
          cd dashboard_app/backend
          uv run pytest tests/api/test_coalition_api_async.py -v
      - name: Run E2E tests
        run: |
          cd dashboard_app/backend
          uv run pytest tests/e2e/test_coalition_flow.py -v -m e2e

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install dependencies
        run: |
          cd dashboard_app/frontend
          npm ci
      - name: Run coalition tests
        run: |
          cd dashboard_app/frontend
          npm test -- --testPathPattern=coalition --coverage
```

---

## Performance Benchmarks

### Expected Response Times

| Endpoint | Target (p95) | Acceptable (p99) |
|----------|--------------|------------------|
| GET /coalition/stats | < 200ms | < 500ms |
| GET /coalition/revenue | < 300ms | < 600ms |
| GET /coalition/content/performance | < 250ms | < 550ms |
| POST /coalition/content | < 500ms | < 1000ms |
| POST /coalition/access-log | < 100ms | < 300ms |
| GET /coalition/admin/overview | < 400ms | < 800ms |

### Database Query Optimization

**Check slow queries:**
```sql
-- PostgreSQL
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
WHERE query LIKE '%coalition%'
ORDER BY mean_exec_time DESC
LIMIT 10;
```

**Add missing indexes:**
```sql
CREATE INDEX IF NOT EXISTS idx_coalition_members_user_id ON coalition_members(user_id);
CREATE INDEX IF NOT EXISTS idx_content_items_user_id ON content_items(user_id);
CREATE INDEX IF NOT EXISTS idx_content_access_logs_content_id ON content_access_logs(content_id);
CREATE INDEX IF NOT EXISTS idx_revenue_transactions_user_id ON revenue_transactions(user_id);
```

---

## Troubleshooting

### Tests Failing

**Database connection issues:**
```powershell
# Check database is running
psql -U postgres -c "SELECT 1"

# Reset test database
cd dashboard_app\backend
uv run alembic downgrade base
uv run alembic upgrade head
```

**Import errors:**
```powershell
# Reinstall dependencies
cd dashboard_app\backend
uv sync --reinstall
```

**Frontend test errors:**
```powershell
# Clear cache
cd dashboard_app\frontend
npm test -- --clearCache

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

### Load Test Issues

**Connection refused:**
- Ensure backend server is running: `uv run uvicorn app.main:app --reload`
- Check host URL matches server address

**High error rate:**
- Reduce spawn rate
- Check database connection pool size
- Monitor server resources (CPU, memory)

**Slow response times:**
- Check database query performance
- Verify indexes exist
- Monitor network latency

---

## Test Reports

### Generate Coverage Report

**Backend:**
```powershell
cd dashboard_app\backend
uv run pytest tests\api\test_coalition_api_async.py --cov=app.api.endpoints.coalition --cov-report=html
# Open htmlcov\index.html
```

**Frontend:**
```powershell
cd dashboard_app\frontend
npm test -- --coverage --testPathPattern=coalition
# Open coverage\lcov-report\index.html
```

### Load Test Report

After running locust, download report:
- Click "Download Data" tab in Locust UI
- Save statistics, failures, and exceptions
- Generate charts from CSV data

---

## Best Practices

1. **Run tests before committing**
   ```powershell
   # Quick check
   cd dashboard_app\backend
   uv run pytest tests\api\test_coalition_api_async.py -v
   
   cd dashboard_app\frontend
   npm test -- --testPathPattern=coalition
   ```

2. **Use watch mode during development**
   ```powershell
   # Frontend
   npm test -- --watch --testPathPattern=coalition
   ```

3. **Run E2E tests before merging**
   ```powershell
   cd dashboard_app\backend
   uv run pytest tests\e2e\test_coalition_flow.py -v -m e2e
   ```

4. **Load test before major releases**
   ```powershell
   uv run locust -f test_coalition_load.py --host=http://staging.encypherai.com --users 1000 --spawn-rate 50 --run-time 30m --headless
   ```

5. **Security scan weekly**
   ```powershell
   cd dashboard_app\backend
   uv run pip-audit
   
   cd dashboard_app\frontend
   npm audit
   ```

---

## Quick Commands Reference

```powershell
# Backend API tests
cd dashboard_app\backend; uv run pytest tests\api\test_coalition_api_async.py -v

# E2E tests
cd dashboard_app\backend; uv run pytest tests\e2e\test_coalition_flow.py -v -m e2e

# Frontend tests
cd dashboard_app\frontend; npm test -- --testPathPattern=coalition

# Load test (web UI)
cd dashboard_app\backend\tests\load; uv run locust -f test_coalition_load.py --host=http://localhost:8000

# Security scan
cd dashboard_app\backend; uv run pip-audit
cd dashboard_app\frontend; npm audit

# All tests
cd dashboard_app\backend; uv run pytest -v
cd dashboard_app\frontend; npm test
```
