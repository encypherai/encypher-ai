"""
Blacklisted token model for token revocation.
"""
from sqlalchemy import Column, Integer, String, DateTime, func

from app.core.database import Base


class BlacklistedToken(Base):
    """
    Model for storing revoked/blacklisted tokens.
    This is used to implement token revocation on logout.
    """
    __tablename__ = "blacklisted_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True)
    blacklisted_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
