from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

SQLALCHEMY_DATABASE_URI = str(settings.SQLALCHEMY_DATABASE_URI)

engine = create_engine(
    SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=10,
    pool_recycle=3600,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Dependency for getting async DB session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
