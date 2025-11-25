import importlib.util
import sys
import os
import tempfile
from pathlib import Path
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker


def _set_enterprise_app() -> None:
    root = Path(__file__).resolve().parents[1]
    app_init = root / "app" / "__init__.py"
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    spec = importlib.util.spec_from_file_location(
        "app",
        app_init,
        submodule_search_locations=[str(root / "app")],
    )
    if spec and spec.loader:
        module = importlib.util.module_from_spec(spec)
        sys.modules["app"] = module
        spec.loader.exec_module(module)


_set_enterprise_app()

# Now import app modules after setting up the path
from app.database import Base, get_db
from app.main import app


# Test database URL - use PostgreSQL for compatibility with ARRAY types
# In Docker: use internal hostname; locally: use localhost
import os
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://encypher:encypher_dev_password@postgres:5432/encypher"
)


@pytest.fixture(scope="session")
def temp_db_file():
    """Create a temporary database file for the test session."""
    # Create a temporary file
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    
    yield path
    
    # Cleanup
    try:
        os.unlink(path)
    except Exception:
        pass


@pytest_asyncio.fixture(scope="function")
async def async_engine():
    """Create an async engine for testing with PostgreSQL."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
    )
    
    # Tables should already exist in the test database
    # Don't create/drop tables as we're using the shared dev database
    
    yield engine
    
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db(async_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a database session for testing."""
    async_session = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def client(db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create an async HTTP client for testing."""
    
    # Override the get_db dependency
    async def override_get_db():
        yield db
    
    app.dependency_overrides[get_db] = override_get_db
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    
    # Clear overrides
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers() -> dict:
    """Return authentication headers for testing."""
    # Use demo API key - must match DEMO_API_KEY in docker-compose
    return {
        "Authorization": f"Bearer {os.getenv('DEMO_API_KEY', 'demo-api-key-for-testing')}",
        "Content-Type": "application/json"
    }


@pytest.fixture
def organization_id() -> str:
    """Return test organization ID."""
    return os.getenv("DEMO_ORGANIZATION_ID", "org_test")


# Alias for async_client (some tests use this name)
@pytest_asyncio.fixture(scope="function")
async def async_client(client: AsyncClient) -> AsyncClient:
    """Alias for client fixture."""
    return client


# Tier-specific auth headers for testing tier-gated features
# Note: In dev environment, all use demo key which has "demo" tier
# For proper tier testing, create test organizations with different tiers
@pytest.fixture
def starter_auth_headers() -> dict:
    """Return auth headers for a Starter tier organization."""
    return {
        "Authorization": f"Bearer {os.getenv('STARTER_API_KEY', 'demo-api-key-for-testing')}",
        "Content-Type": "application/json"
    }


@pytest.fixture
def professional_auth_headers() -> dict:
    """Return auth headers for a Professional tier organization."""
    return {
        "Authorization": f"Bearer {os.getenv('PROFESSIONAL_API_KEY', 'demo-api-key-for-testing')}",
        "Content-Type": "application/json"
    }


@pytest.fixture
def business_auth_headers() -> dict:
    """Return auth headers for a Business tier organization."""
    return {
        "Authorization": f"Bearer {os.getenv('BUSINESS_API_KEY', 'demo-api-key-for-testing')}",
        "Content-Type": "application/json"
    }


@pytest.fixture
def business_admin_headers() -> dict:
    """Return auth headers for a Business tier admin user."""
    return {
        "Authorization": f"Bearer {os.getenv('BUSINESS_ADMIN_API_KEY', 'demo-api-key-for-testing')}",
        "Content-Type": "application/json"
    }


@pytest.fixture
def business_owner_headers() -> dict:
    """Return auth headers for a Business tier owner user."""
    return {
        "Authorization": f"Bearer {os.getenv('BUSINESS_OWNER_API_KEY', 'demo-api-key-for-testing')}",
        "Content-Type": "application/json"
    }


@pytest.fixture
def enterprise_auth_headers() -> dict:
    """Return auth headers for an Enterprise tier organization."""
    return {
        "Authorization": f"Bearer {os.getenv('ENTERPRISE_API_KEY', 'demo-api-key-for-testing')}",
        "Content-Type": "application/json"
    }


@pytest.fixture
def test_member_id() -> str:
    """Return a test member ID for team management tests."""
    return os.getenv("TEST_MEMBER_ID", "mem_test123")


@pytest.fixture
def owner_member_id() -> str:
    """Return the owner member ID for team management tests."""
    return os.getenv("OWNER_MEMBER_ID", "mem_owner123")


# Configure pytest-asyncio
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "asyncio: mark test as an asyncio test"
    )


_set_enterprise_app()
