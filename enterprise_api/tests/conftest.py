"""
Pytest configuration and fixtures for Enterprise API tests.

Uses PostgreSQL via Docker for full compatibility with production.
Two-Database Architecture:
- Core DB: Customer/billing data
- Content DB: Verification/content data
"""
import importlib.util
import sys
import os
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
from app.database import get_db, get_content_db
from app.main import app


# Test database URLs - Two-Database Architecture
# These match the docker-compose.full-stack.yml configuration
# Core DB: Customer/billing data (organizations, api_keys, etc.)
TEST_CORE_DATABASE_URL = os.getenv(
    "CORE_DATABASE_URL",
    "postgresql+asyncpg://encypher:encypher_dev_password@postgres-core:5432/encypher_core"
)

# Content DB: Verification data (documents, merkle trees, etc.)
TEST_CONTENT_DATABASE_URL = os.getenv(
    "CONTENT_DATABASE_URL",
    "postgresql+asyncpg://encypher:encypher_dev_password@postgres-content:5432/encypher_content"
)

# Legacy alias for backward compatibility
TEST_DATABASE_URL = TEST_CORE_DATABASE_URL


@pytest_asyncio.fixture(scope="function")
async def async_engine():
    """Create an async engine for CORE database testing."""
    engine = create_async_engine(
        TEST_CORE_DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
    )
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def content_engine():
    """Create an async engine for CONTENT database testing."""
    engine = create_async_engine(
        TEST_CONTENT_DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
    )
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db(async_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a CORE database session for testing."""
    async_session = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    async with async_session() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def content_db(content_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a CONTENT database session for testing."""
    async_session = async_sessionmaker(
        content_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    async with async_session() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def client(db: AsyncSession, content_db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create an async HTTP client for testing with both databases."""
    
    # Override the get_db dependency (core database)
    async def override_get_db():
        yield db
    
    # Override the get_content_db dependency
    async def override_get_content_db():
        yield content_db
    
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_content_db] = override_get_content_db
    
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
# These use the API keys created by seed_test_data.sql
@pytest.fixture
def starter_auth_headers() -> dict:
    """Return auth headers for a Starter tier organization."""
    return {
        "Authorization": f"Bearer {os.getenv('STARTER_API_KEY', 'starter-api-key-for-testing')}",
        "Content-Type": "application/json"
    }


@pytest.fixture
def professional_auth_headers() -> dict:
    """Return auth headers for a Professional tier organization."""
    return {
        "Authorization": f"Bearer {os.getenv('PROFESSIONAL_API_KEY', 'professional-api-key-for-testing')}",
        "Content-Type": "application/json"
    }


@pytest.fixture
def business_auth_headers() -> dict:
    """Return auth headers for a Business tier organization."""
    return {
        "Authorization": f"Bearer {os.getenv('BUSINESS_API_KEY', 'business-api-key-for-testing')}",
        "Content-Type": "application/json"
    }


@pytest.fixture
def business_admin_headers() -> dict:
    """Return auth headers for a Business tier admin user."""
    # Uses same org as business, but could be different user in future
    return {
        "Authorization": f"Bearer {os.getenv('BUSINESS_ADMIN_API_KEY', 'business-api-key-for-testing')}",
        "Content-Type": "application/json"
    }


@pytest.fixture
def business_owner_headers() -> dict:
    """Return auth headers for a Business tier owner user."""
    return {
        "Authorization": f"Bearer {os.getenv('BUSINESS_OWNER_API_KEY', 'business-api-key-for-testing')}",
        "Content-Type": "application/json"
    }


@pytest.fixture
def enterprise_auth_headers() -> dict:
    """Return auth headers for an Enterprise tier organization."""
    return {
        "Authorization": f"Bearer {os.getenv('ENTERPRISE_API_KEY', 'enterprise-api-key-for-testing')}",
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
