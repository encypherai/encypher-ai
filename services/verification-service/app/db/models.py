"""SQLAlchemy database models for Verification Service"""
from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()


def generate_uuid():
    return str(uuid.uuid4())


class VerificationResult(Base):
    """Verification result model"""
    __tablename__ = "verification_results"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    document_id = Column(String, nullable=False, index=True)
    user_id = Column(String, nullable=True, index=True)
    
    # Verification details
    is_valid = Column(Boolean, nullable=False)
    is_tampered = Column(Boolean, nullable=False, default=False)
    signature_valid = Column(Boolean, nullable=False)
    hash_valid = Column(Boolean, nullable=False)
    
    # Scores and metrics
    confidence_score = Column(Float, nullable=False, default=0.0)
    similarity_score = Column(Float, nullable=True)
    
    # Content information
    content_hash = Column(String, nullable=False)
    signature = Column(Text, nullable=False)
    signer_id = Column(String, nullable=True)
    
    # Verification metadata
    verification_method = Column(String, nullable=False, default="signature")
    error_message = Column(Text, nullable=True)
    warnings = Column(JSON, nullable=True)
    
    # Performance
    verification_time_ms = Column(Integer, nullable=True)
    
    # Client info
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<VerificationResult(id={self.id}, document_id={self.document_id}, is_valid={self.is_valid})>"


class VerificationLog(Base):
    """Verification audit log"""
    __tablename__ = "verification_logs"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    document_id = Column(String, nullable=False, index=True)
    user_id = Column(String, nullable=True, index=True)
    
    operation_type = Column(String, nullable=False)  # verify_signature, verify_document, check_tampering
    status = Column(String, nullable=False)  # success, failed
    result = Column(String, nullable=False)  # valid, invalid, tampered
    
    processing_time_ms = Column(Integer, nullable=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<VerificationLog(id={self.id}, document_id={self.document_id}, result={self.result})>"
