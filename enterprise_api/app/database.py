"""
Database connection module for Encypher Enterprise API.

Two-Database Architecture:
- Core DB: Customer/billing data (organizations, api_keys, subscriptions)
- Content DB: Verification data (documents, merkle trees, sentences)

Uses SQLAlchemy with asyncpg for async PostgreSQL operations.
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from app.config import settings


def _normalize_url(url: str) -> str:
    """Ensure URL uses asyncpg driver."""
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://")
    return url


# ============================================
# CORE DATABASE (Customer/Billing Data)
# ============================================
# Tables: organizations, users, api_keys, subscriptions, audit_logs, etc.
core_engine = create_async_engine(
    _normalize_url(settings.core_database_url_resolved),
    echo=settings.is_development,
    pool_size=settings.core_db_pool_size,
    max_overflow=settings.core_db_max_overflow,
    pool_recycle=1800,
    pool_timeout=30,
    pool_pre_ping=True,
    future=True,
)

core_session_factory = async_sessionmaker(
    core_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

# ============================================
# CONTENT DATABASE (Verification Data)
# ============================================
# Tables: documents, sentence_records, merkle_roots, merkle_subhashes, etc.
content_engine = create_async_engine(
    _normalize_url(settings.content_database_url_resolved),
    echo=settings.is_development,
    pool_size=settings.content_db_pool_size,
    max_overflow=settings.content_db_max_overflow,
    pool_recycle=1800,
    pool_timeout=30,
    pool_pre_ping=True,
    future=True,
)

content_session_factory = async_sessionmaker(
    content_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

# ============================================
# LEGACY ALIASES (Backward Compatibility)
# ============================================
# Default to core database for backward compatibility
engine = core_engine
async_session_factory = core_session_factory

# Base class for ORM models
Base = declarative_base()


# ============================================
# DEPENDENCY INJECTION
# ============================================


async def get_db():
    """
    Get a session for the CORE database (customer/billing data).

    Use this for:
    - Organization lookups
    - API key validation
    - User authentication
    - Billing operations
    - Audit logging
    """
    async with core_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_core_db():
    """Explicit alias for get_db() - core database session."""
    async with core_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_content_db():
    """
    Get a session for the CONTENT database (verification data).

    Use this for:
    - Document storage
    - Sentence records
    - Merkle tree operations
    - Attribution reports
    - Content verification
    """
    async with content_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
