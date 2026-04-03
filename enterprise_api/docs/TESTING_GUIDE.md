# Testing Guide

## Overview

The Enterprise API uses **SQLite in-memory databases** for automated testing, providing fast, isolated, and reproducible test execution without requiring PostgreSQL.

---

## Quick Start

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_c2pa_validator.py -v

# Run with coverage
uv run pytest --cov=app --cov-report=html

# Run only unit tests
uv run pytest -m unit

# Run only integration tests
uv run pytest -m integration
```

---

## Test Database

### Architecture

- **Production**: PostgreSQL with JSONB
- **Testing**: SQLite in-memory with JSON
- **Compatibility**: Database-agnostic models using `JSONType`

### How It Works

1. **Per-Test Isolation**: Each test gets a fresh database
2. **Automatic Setup**: Tables created before each test
3. **Automatic Teardown**: Database destroyed after each test
4. **Fast Execution**: In-memory = no disk I/O

### Fixtures

```python
@pytest_asyncio.fixture
async def db(async_engine) -> AsyncSession:
    """Provides a clean database session for each test."""
    pass

@pytest_asyncio.fixture
async def client(db) -> AsyncClient:
    """Provides an HTTP client with database override."""
    pass

@pytest.fixture
def auth_headers() -> dict:
    """Provides authentication headers."""
    pass
```

---

## Writing Tests

### Basic Test Structure

```python
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from httpx import AsyncClient

@pytest.mark.asyncio
class TestMyFeature:
    """Test my feature."""

    async def test_database_operation(self, db: AsyncSession):
        """Test direct database operation."""
        # Your test code here
        pass

    async def test_api_endpoint(self, client: AsyncClient, auth_headers: dict):
        """Test API endpoint."""
        response = await client.post(
            "/api/v1/endpoint",
            json={"data": "value"},
            headers=auth_headers
        )
        assert response.status_code == 200
```

### Test Markers

```python
@pytest.mark.unit
def test_unit():
    """Unit test - no external dependencies."""
    pass

@pytest.mark.integration
async def test_integration(db):
    """Integration test - uses database."""
    pass

@pytest.mark.performance
async def test_performance():
    """Performance test - measures speed."""
    pass

@pytest.mark.slow
async def test_slow():
    """Slow test - takes > 1 second."""
    pass
```

---

## Test Organization

```
tests/
├── conftest.py                    # Shared fixtures
├── test_database_setup.py         # Database infrastructure tests
├── test_c2pa_validator.py         # C2PA validation unit tests
├── test_c2pa_api.py               # C2PA API integration tests
├── test_c2pa_performance.py       # C2PA performance tests
└── ...
```

---

## Database Compatibility

### JSONType Implementation

The `JSONType` TypeDecorator automatically selects the correct JSON type:

```python
from sqlalchemy.types import TypeDecorator
from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import JSONB

class JSONType(TypeDecorator):
    """Database-agnostic JSON type."""
    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(JSONB())
        else:
            return dialect.type_descriptor(JSON())
```

### Usage in Models

```python
from app.models.c2pa_schema import JSONType

class MyModel(Base):
    __tablename__ = "my_table"

    # Works with both PostgreSQL and SQLite
    data = Column(JSONType, nullable=False)
```

---

## Running Tests

### All Tests

```bash
uv run pytest
```

### Specific File

```bash
uv run pytest tests/test_c2pa_validator.py
```

### Specific Test

```bash
uv run pytest tests/test_c2pa_validator.py::TestC2PAValidator::test_validate_location_assertion_valid
```

### With Verbose Output

```bash
uv run pytest -v
```

### With Coverage

```bash
uv run pytest --cov=app --cov-report=html
# Open htmlcov/index.html
```

### Filter by Marker

```bash
# Run only unit tests
uv run pytest -m unit

# Run only integration tests
uv run pytest -m integration

# Run only performance tests
uv run pytest -m performance

# Exclude slow tests
uv run pytest -m "not slow"
```

---

## Live Production E2E Tests

These tests exercise the production API directly and are **opt-in**. They are located in
`enterprise_api/tests/e2e_live` and are skipped unless explicitly enabled.

### Configuration

Provide credentials via environment variables or a local `.env.prod` file stored in
`enterprise_api/tests/e2e_live/.env.prod` (gitignored).

Supported variables:

- `LIVE_API_TESTS=true` (required to run)
- `LIVE_API_KEY` (production test org API key)
- `LIVE_API_BASE_URL` (defaults to `https://api.encypher.com` when set in `.env.prod`)
- `LIVE_API_TIMEOUT` (optional timeout in seconds, default 30)

`.env.prod` example:

```bash
API_KEY=ency_...
BASE_URL=https://api.encypher.com
```

### Run Live Tests

```bash
LIVE_API_TESTS=true uv run pytest enterprise_api/tests/e2e_live -m e2e
```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh

      - name: Install dependencies
        run: uv sync

      - name: Run tests
        run: uv run pytest --cov=app --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## Performance Benchmarks

### Test Execution Speed

- **Database setup**: < 50ms per test
- **Unit tests**: < 10ms per test
- **Integration tests**: < 100ms per test
- **Full test suite**: < 10 seconds

### Comparison

| Database | Setup Time | Test Time | Cleanup Time |
|----------|------------|-----------|--------------|
| SQLite (memory) | 10ms | 1ms | 5ms |
| PostgreSQL | 500ms | 50ms | 200ms |

**Speedup**: ~50x faster with SQLite

---

## Best Practices

### 1. Test Isolation

✅ **DO**: Each test should be independent
```python
async def test_create_schema(self, db):
    schema = C2PASchema(...)
    db.add(schema)
    await db.commit()
    # Test passes, database cleaned up automatically
```

❌ **DON'T**: Rely on data from previous tests
```python
async def test_depends_on_previous(self, db):
    # This will fail - previous test's data is gone
    schema = await db.get(C2PASchema, "some-id")
```

### 2. Use Fixtures

✅ **DO**: Use fixtures for common setup
```python
@pytest.fixture
def sample_schema():
    return {
        "namespace": "com.test",
        "label": "com.test.example.v1",
        "schema": {"type": "object"}
    }

async def test_with_fixture(self, db, sample_schema):
    schema = C2PASchema(**sample_schema)
    db.add(schema)
```

### 3. Test Real Scenarios

✅ **DO**: Test realistic use cases
```python
async def test_full_workflow(self, client, auth_headers):
    # Create schema
    response = await client.post("/api/v1/c2pa/schemas", ...)
    assert response.status_code == 201

    # Validate assertion
    response = await client.post("/api/v1/c2pa/validate", ...)
    assert response.status_code == 200
```

### 4. Clear Assertions

✅ **DO**: Use descriptive assertions
```python
assert response.status_code == 200, f"Expected 200, got {response.status_code}"
assert "errors" not in data, f"Unexpected errors: {data.get('errors')}"
```

---

## Troubleshooting

### Issue: Tests fail with "table does not exist"

**Solution**: Ensure models are imported in `conftest.py`:
```python
from app.models.c2pa_schema import C2PASchema
from app.models.c2pa_template import C2PAAssertionTemplate
```

### Issue: Tests are slow

**Solution**: Check if you're using the in-memory database:
```python
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"  # ✓ Fast
TEST_DATABASE_URL = "sqlite+aiosqlite:///test.db"   # ✗ Slow
```

### Issue: Database not cleaned between tests

**Solution**: Ensure you're using the `db` fixture with `scope="function"`:
```python
@pytest_asyncio.fixture(scope="function")  # ✓ Correct
async def db(async_engine):
    ...
```

---

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-asyncio documentation](https://pytest-asyncio.readthedocs.io/)
- [SQLAlchemy testing guide](https://docs.sqlalchemy.org/en/20/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites)
- [FastAPI testing guide](https://fastapi.tiangolo.com/tutorial/testing/)

---

## Summary

✅ **Fast**: SQLite in-memory = 50x faster than PostgreSQL
✅ **Isolated**: Each test gets a clean database
✅ **Simple**: No external dependencies required
✅ **Compatible**: Same models work in production and testing
✅ **CI-Friendly**: Easy to integrate with GitHub Actions, etc.

**Happy Testing!** 🎉
