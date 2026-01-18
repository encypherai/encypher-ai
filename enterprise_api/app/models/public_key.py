"""
Public Key model for BYOK (Bring Your Own Key) support.

Stores public keys registered by enterprise customers for signature verification.
"""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.sql import func

from app.database import Base


class PublicKey(Base):
    """
    Public key registered by an organization for BYOK verification.

    Enterprise tier customers can register their own signing keys.
    When content signed with their private key is verified, we use
    the registered public key to validate the signature.
    """

    __tablename__ = "public_keys"
    __table_args__ = {"extend_existing": True}

    id = Column(String(64), primary_key=True)

    # Owner
    organization_id = Column(String(64), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)

    # Key metadata
    key_name = Column(String(255), nullable=True)
    key_algorithm = Column(String(20), nullable=False, default="Ed25519")
    key_fingerprint = Column(String(128), nullable=False, unique=True, index=True)

    # The actual public key
    public_key_pem = Column(Text, nullable=False)

    # Status
    is_active = Column(Boolean, nullable=False, default=True)
    is_primary = Column(Boolean, nullable=False, default=False)

    # Usage tracking
    verification_count = Column(Integer, nullable=False, default=0)
    last_used_at = Column(DateTime(timezone=True), nullable=True)

    # Lifecycle
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, server_default=func.now())
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    revoked_reason = Column(String(500), nullable=True)

    def __repr__(self) -> str:
        return f"<PublicKey(id={self.id}, org={self.organization_id}, fingerprint={self.key_fingerprint[:16]}...)>"
