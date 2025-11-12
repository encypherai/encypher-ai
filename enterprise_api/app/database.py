"""
Database connection module for Encypher Enterprise API.
Uses SQLAlchemy with asyncpg for async PostgreSQL operations.
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.config import settings

# Create async engine
engine = create_async_engine(
    settings.database_url.replace("postgresql://", "postgresql+asyncpg://"),
    echo=settings.is_development,
    pool_size=100,  # Increased from 20 for high concurrency (16 workers × 64 concurrent requests)
    max_overflow=50,  # Increased from 10 to handle burst traffic
    pool_pre_ping=True,
    future=True,
)

# Create session factory
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

# Base class for ORM models
Base = declarative_base()


# Dependency for getting database session
async def get_db():
    """
    Dependency for getting database session in FastAPI endpoints.
    
    Performance optimization: Sessions auto-commit at the end of the request.
    Individual operations use flush() instead of commit() to batch disk writes.

    Usage:
        @app.get("/endpoint")
        async def endpoint(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with async_session_factory() as session:
        try:
            yield session
            # Auto-commit at end of request (batches all flush() operations)
            # Only commit if there are pending changes
            if session.new or session.dirty or session.deleted:
                await session.commit()
        except Exception:
            # Rollback on error
            await session.rollback()
            raise
        finally:
            await session.close()
