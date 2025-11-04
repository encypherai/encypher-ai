import importlib.util
import sys
import os
import tempfile
from pathlib import Path
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine, event
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool


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
from app.database import Base
from app.main import app
from app.dependencies import get_db


# Test database URL - use in-memory SQLite for speed
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


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
    """Create an async engine for testing with SQLite."""
    # Use in-memory database with shared cache for speed
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Drop all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
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
    # Use demo API key from settings
    return {
        "X-API-Key": os.getenv("DEMO_API_KEY", "demo-key-test"),
        "Content-Type": "application/json"
    }


@pytest.fixture
def organization_id() -> str:
    """Return test organization ID."""
    return os.getenv("DEMO_ORGANIZATION_ID", "org_test")


# Configure pytest-asyncio
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "asyncio: mark test as an asyncio test"
    )


_set_enterprise_app()
