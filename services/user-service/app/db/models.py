"""SQLAlchemy database models for User Service"""

import uuid

from sqlalchemy import JSON, Boolean, Column, DateTime, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class UserProfile(Base):
    """User profile model"""

    __tablename__ = "user_profiles"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, unique=True, index=True)

    display_name = Column(String, nullable=True)
    bio = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    company = Column(String, nullable=True)
    location = Column(String, nullable=True)
    website = Column(String, nullable=True)

    preferences = Column(JSON, nullable=True)
    extra_metadata = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<UserProfile(id={self.id}, user_id={self.user_id})>"


class Team(Base):
    """Team model"""

    __tablename__ = "teams"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    owner_id = Column(String, nullable=False, index=True)

    description = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)

    extra_metadata = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Team(id={self.id}, name={self.name})>"
