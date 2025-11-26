"""
Pytest configuration for load tests.

These tests use the real Docker infrastructure without mocks.
"""
import os
import sys
from pathlib import Path

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker


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
