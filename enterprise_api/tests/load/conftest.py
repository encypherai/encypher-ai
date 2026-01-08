"""
Pytest configuration for load tests.

These tests use the real Docker infrastructure without mocks.
Run with: pytest tests/load -m stress

These tests are excluded from the default test run because:
1. They require Docker infrastructure to be running
2. They can take several minutes to complete
3. They may stress system resources
"""
import os
import sys
from pathlib import Path

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


# Mark all tests in this directory as stress tests (excluded by default)
def pytest_collection_modifyitems(items):
    """Mark all load tests as stress tests."""
    load_tests_enabled = os.getenv("LOAD_TESTS", "").lower() == "true"
    for item in items:
        if "load" in str(item.fspath):
            item.add_marker(pytest.mark.stress)
            if not load_tests_enabled:
                item.add_marker(
                    pytest.mark.skip(reason="Load tests are opt-in. Set LOAD_TESTS=true to run.")
                )


# Ensure app is importable
def _set_enterprise_app():
    root = Path(__file__).resolve().parents[2]
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))


_set_enterprise_app()


# Database URL - uses Docker internal network
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://encypher:encypher_dev_password@postgres:5432/encypher"
)


@pytest_asyncio.fixture(scope="function")
async def async_engine():
    """Create an async engine for load testing."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
    )
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db(async_engine) -> AsyncSession:
    """Create a database session for load testing."""
    async_session = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
