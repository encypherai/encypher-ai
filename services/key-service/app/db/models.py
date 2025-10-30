"""
SQLAlchemy database models for Key Service
"""
from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()


def generate_uuid():
    """Generate a UUID string"""
    return str(uuid.uuid4())


class ApiKey(Base):
    """API Key model"""
    __tablename__ = "api_keys"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, nullable=False, index=True)
    
    # Key information
    name = Column(String, nullable=False)
    key_hash = Column(String, nullable=False, unique=True, index=True)  # SHA-256 hash
    key_prefix = Column(String, nullable=False)  # First few chars for display (e.g., "ency_abc...")
    fingerprint = Column(String, nullable=False)  # Short identifier
    
    # Permissions
    permissions = Column(JSON, nullable=False, default=list)  # ["sign", "verify", "read"]
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_revoked = Column(Boolean, default=False, nullable=False)
    
    # Usage tracking
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    usage_count = Column(Integer, default=0, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    description = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)
    
    def __repr__(self):
        return f"<ApiKey(id={self.id}, name={self.name}, user_id={self.user_id})>"


class KeyUsage(Base):
    """API Key usage tracking"""
    __tablename__ = "key_usage"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    key_id = Column(String, nullable=False, index=True)
    user_id = Column(String, nullable=False, index=True)
    
    # Request information
    endpoint = Column(String, nullable=True)
    method = Column(String, nullable=True)
    status_code = Column(Integer, nullable=True)
    
    # Client information
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<KeyUsage(id={self.id}, key_id={self.key_id})>"


class KeyRotation(Base):
    """API Key rotation history"""
    __tablename__ = "key_rotations"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    old_key_id = Column(String, nullable=False, index=True)
    new_key_id = Column(String, nullable=False, index=True)
    user_id = Column(String, nullable=False, index=True)
    
    # Rotation information
    reason = Column(String, nullable=True)
    rotated_by = Column(String, nullable=True)  # user_id or "system"
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<KeyRotation(id={self.id}, old_key_id={self.old_key_id}, new_key_id={self.new_key_id})>"
