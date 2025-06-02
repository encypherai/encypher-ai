import os
import asyncio
from typing import AsyncGenerator, Generator

import pytest
from httpx import AsyncClient, ASGITransport # Use ASGITransport
from fastapi.testclient import TestClient # Keep for potential other uses or type hints if necessary
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

# --- Environment Variable Setup for Testing ---
# This MUST be done BEFORE importing application modules that load settings or init DB.
TEST_DB_FILENAME = "test_db_for_pytest.db"
TEST_DATABASE_URL_VAL = f"sqlite+aiosqlite:///./{TEST_DB_FILENAME}"
os.environ["DATABASE_URL"] = TEST_DATABASE_URL_VAL
os.environ["DB_ECHO"] = "False" # Ensure DB echo is off for tests unless needed

# --- Application Imports ---
# Now that DATABASE_URL is set, these imports will use the test DB configuration.
from app.core.database import get_db, Base, AsyncSessionLocal as AppAsyncSessionLocal # Import app's session maker
from app.main import app as fastapi_app
from app.core.config import settings

# --- Verification of Settings Override (Optional but good for sanity check) ---
if settings.DATABASE_URL != TEST_DATABASE_URL_VAL:
    raise RuntimeError(
        f"DATABASE_URL not overridden correctly for tests! "
        f"Expected: {TEST_DATABASE_URL_VAL}, Got: {settings.DATABASE_URL}. "
        f"Ensure os.environ is set BEFORE app imports."
    )

# --- Test Database Engine and Session Configuration ---
# This engine is specifically for conftest.py to manage the test DB (create/drop tables).
# The application itself will use its own engine, configured via the overridden settings.DATABASE_URL.
test_engine = create_async_engine(TEST_DATABASE_URL_VAL, echo=False)

# This sessionmaker is used by the `db` fixture and `override_get_db` for tests.
TestAsyncSessionLocal = async_sessionmaker(
    bind=test_engine, class_=AsyncSession, autocommit=False, autoflush=False
)


# --- Pytest Fixtures ---
@pytest.fixture(scope="session", autouse=True)
async def setup_test_database() -> AsyncGenerator[None, None]:
    """Create tables before tests run and drop them after tests are done."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await test_engine.dispose()
    
    # Clean up the test database file
    # Adding a small delay and retry might also help on Windows if it's a race condition
    # For now, let's rely on proper disposal.
    if os.path.exists(TEST_DB_FILENAME):
        try:
            os.remove(TEST_DB_FILENAME)
        except PermissionError as e:
            print(f"Could not remove test DB {TEST_DB_FILENAME} on first attempt: {e}. Retrying might be needed or check for unclosed sessions.")


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency override for FastAPI's get_db that uses the test database session."""
    async with TestAsyncSessionLocal() as session:
        yield session


@pytest.fixture(scope="function")
async def client(setup_test_database: None) -> AsyncGenerator[AsyncClient, None]:
    """Provides an AsyncClient for making API requests to the FastAPI app in tests."""
    fastapi_app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=fastapi_app), base_url="http://test") as ac:
        yield ac
    fastapi_app.dependency_overrides.clear()  # Clear overrides after test


@pytest.fixture(scope="function")
async def db(setup_test_database: None) -> AsyncGenerator[AsyncSession, None]:
    """Provides a direct SQLAlchemy AsyncSession to the test database for service tests."""
    async with TestAsyncSessionLocal() as session:
        yield session
