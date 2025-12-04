"""
Database connection and session management.
"""
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from app.core.config import settings

# Create SQLAlchemy async engine
engine = create_async_engine(
    settings.DATABASE_URL
    # connect_args can be used for specific driver options if needed, e.g., for SSL
)

# Create AsyncSessionLocal class
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False # Often useful for FastAPI to keep objects accessible after commit
)

# Create Base class for models
Base = declarative_base()

# Dependency to get DB session
async def get_db() -> AsyncSession:
    """
    Dependency for FastAPI endpoints to get an async database session.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            # Optionally, commit here if you want all operations within a request to be a single transaction
            # await session.commit() 
        except Exception:
            # Rollback in case of an exception during the request handling
            # await session.rollback()
            raise
        finally:
            # The 'async with' block handles closing the session automatically.
            pass
