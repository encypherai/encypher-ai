"""
SQLAlchemy database models for Encoding Service
"""

from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()


def generate_uuid():
    """Generate a UUID string"""
    return str(uuid.uuid4())


class EncodedDocument(Base):
    """Encoded document model"""

    __tablename__ = "encoded_documents"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, nullable=False, index=True)

    # Document information
    document_id = Column(String, nullable=False, unique=True, index=True)
    original_content = Column(Text, nullable=False)
    encoded_content = Column(Text, nullable=False)
    content_hash = Column(String, nullable=False)

    # Signature information
    signature = Column(Text, nullable=False)
    signer_id = Column(String, nullable=False)
    signing_key_id = Column(String, nullable=True)  # Reference to key service

    # Manifest
    manifest = Column(JSON, nullable=False)

    # Extra metadata
    extra_metadata = Column(JSON, nullable=True)
    format = Column(String, nullable=False, default="text")
    encoding_method = Column(String, nullable=False, default="unicode")

    # Status
    is_active = Column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<EncodedDocument(id={self.id}, document_id={self.document_id})>"


class SigningOperation(Base):
    """Signing operation audit log"""

    __tablename__ = "signing_operations"

    id = Column(String, primary_key=True, default=generate_uuid)
    document_id = Column(String, nullable=False, index=True)
    user_id = Column(String, nullable=False, index=True)

    # Operation details
    operation_type = Column(String, nullable=False)  # sign, embed, verify
    status = Column(String, nullable=False)  # success, failed
    error_message = Column(Text, nullable=True)

    # Performance metrics
    processing_time_ms = Column(Integer, nullable=True)
    content_size_bytes = Column(Integer, nullable=True)

    # Client information
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)

    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<SigningOperation(id={self.id}, document_id={self.document_id}, status={self.status})>"
