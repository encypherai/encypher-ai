"""
Pytest configuration and fixtures for Enterprise API tests.

Uses PostgreSQL via Docker for full compatibility with production.
Two-Database Architecture:
- Core DB: Customer/billing data
- Content DB: Verification/content data
"""
import asyncio
import os
import sys
from pathlib import Path
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


os.environ.setdefault("KEY_ENCRYPTION_KEY", "0" * 64)
os.environ.setdefault("ENCRYPTION_NONCE", "0" * 24)

os.environ.setdefault(
    "CORE_DATABASE_URL",
    "postgresql+asyncpg://encypher:encypher_dev_password@127.0.0.1:55432/encypher_content",
)
os.environ.setdefault(
    "CONTENT_DATABASE_URL",
    "postgresql+asyncpg://encypher:encypher_dev_password@127.0.0.1:55432/encypher_content",
)
os.environ.setdefault("DATABASE_URL", os.environ["CORE_DATABASE_URL"])

root = Path(__file__).resolve().parents[1]
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

# Now import app modules after setting up the path
from app.database import get_content_db, get_db
from app.main import app

# Test database URLs - Two-Database Architecture
# These match the docker-compose.full-stack.yml configuration
# Core DB: Customer/billing data (organizations, api_keys, etc.)
TEST_CORE_DATABASE_URL = os.getenv(
    "CORE_DATABASE_URL",
    "postgresql+asyncpg://encypher:encypher_dev_password@127.0.0.1:55432/encypher_content",
)

# Content DB: Verification data (documents, merkle trees, etc.)
TEST_CONTENT_DATABASE_URL = os.getenv(
    "CONTENT_DATABASE_URL",
    "postgresql+asyncpg://encypher:encypher_dev_password@127.0.0.1:55432/encypher_content",
)

# Legacy alias for backward compatibility
TEST_DATABASE_URL = TEST_CORE_DATABASE_URL


_SEED_LOCK = asyncio.Lock()
_SEEDED = False


async def _ensure_seeded() -> None:
    global _SEEDED
    if _SEEDED:
        return

    async with _SEED_LOCK:
        if _SEEDED:
            return

        engine = create_async_engine(TEST_CORE_DATABASE_URL, echo=False, pool_pre_ping=True)
        async with engine.begin() as conn:
            # Users (used by team management and for a consistent "test user" context)
            await conn.execute(
                text(
                    """
                    INSERT INTO users (email, name, email_verified, is_active, created_at, updated_at)
                    VALUES (:email, :name, TRUE, TRUE, NOW(), NOW())
                    ON CONFLICT (email) DO UPDATE SET
                        name = EXCLUDED.name,
                        email_verified = EXCLUDED.email_verified,
                        is_active = EXCLUDED.is_active,
                        updated_at = NOW();
                    """
                ),
                {"email": "test@encypherai.com", "name": "Test User"},
            )

            user_id = await conn.scalar(text("SELECT id FROM users WHERE email = :email"), {"email": "test@encypherai.com"})
            if not user_id:
                raise RuntimeError("Failed to seed or fetch test user id")

            # Seed organizations expected by demo keys in app.dependencies.DEMO_KEYS
            org_rows = [
                ("org_demo", "Encypher Demo Organization", "seed-org-demo@tests.local", "demo"),
                ("org_starter", "Starter Test Organization", "seed-org-starter@tests.local", "starter"),
                ("org_professional", "Professional Test Organization", "seed-org-professional@tests.local", "professional"),
                ("org_business", "Business Test Organization", "seed-org-business@tests.local", "business"),
                ("org_enterprise", "Enterprise Test Organization", "seed-org-enterprise@tests.local", "enterprise"),
            ]
            for org_id, name, email, tier in org_rows:
                await conn.execute(
                    text(
                        """
                        INSERT INTO organizations (
                            id, name, email, tier, monthly_api_limit, monthly_api_usage,
                            coalition_member, coalition_rev_share, created_at, updated_at
                        )
                        VALUES (
                            :id, :name, :email, :tier, :monthly_api_limit, 0,
                            TRUE, 65, NOW(), NOW()
                        )
                        ON CONFLICT (id) DO UPDATE SET
                            name = EXCLUDED.name,
                            email = EXCLUDED.email,
                            tier = EXCLUDED.tier,
                            monthly_api_limit = EXCLUDED.monthly_api_limit,
                            updated_at = NOW();
                        """
                    ),
                    {
                        "id": org_id,
                        "name": name,
                        "email": email,
                        "tier": tier,
                        "monthly_api_limit": 10000 if tier in {"starter", "demo"} else 100000,
                    },
                )

            # Ensure the test user is an owner of the business org (team endpoints)
            await conn.execute(
                text(
                    """
                    INSERT INTO organization_members (organization_id, user_id, role, joined_at)
                    VALUES (:org_id, :user_id, 'owner', NOW())
                    ON CONFLICT (organization_id, user_id) DO NOTHING;
                    """
                ),
                {"org_id": "org_business", "user_id": user_id},
            )

        await engine.dispose()
        _SEEDED = True


@pytest_asyncio.fixture(scope="function")
async def async_engine():
    """Create an async engine for CORE database testing."""
    await _ensure_seeded()
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
    await _ensure_seeded()
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
