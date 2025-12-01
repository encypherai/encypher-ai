"""
SQLAlchemy models for Bitstring Status Lists.

Implements W3C StatusList2021 for per-document revocation at scale.
Supports 10+ billion documents with O(1) status lookups.

Architecture:
- StatusListEntry: Maps document_id to (org, list_index, bit_index)
- StatusListMetadata: Tracks list generation state and CDN URLs

Sharding: 131,072 documents per list (16KB bitstring)
"""
from datetime import datetime
from enum import Enum
from uuid import uuid4

from sqlalchemy import (
    Column,
    String,
    Integer,
    Boolean,
    TIMESTAMP,
    ForeignKey,
    Index,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from app.database import Base


# Constants for bitstring sizing
BITS_PER_LIST = 131072  # 2^17 = 131,072 documents per list
BYTES_PER_LIST = BITS_PER_LIST // 8  # 16,384 bytes


class RevocationReason(str, Enum):
    """Standard revocation reasons for audit trail."""
    
    FACTUAL_ERROR = "factual_error"
    LEGAL_TAKEDOWN = "legal_takedown"
    COPYRIGHT_CLAIM = "copyright_claim"
    PRIVACY_REQUEST = "privacy_request"
    PUBLISHER_REQUEST = "publisher_request"
    SECURITY_CONCERN = "security_concern"
    CONTENT_POLICY = "content_policy"
    OTHER = "other"


class StatusListEntry(Base):
    """
    Maps document_id to a position in a bitstring status list.
    
    This is the source of truth for document status. Bitstrings are
    generated from this table by background workers.
    
    Primary key is (organization_id, list_index, bit_index) for efficient
    sharding and bulk operations.
    """
    __tablename__ = "status_list_entries"
    
    # Composite primary key for efficient sharding
    organization_id = Column(
        String(64),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        primary_key=True
    )
    list_index = Column(Integer, primary_key=True)  # Which list (0, 1, 2...)
    bit_index = Column(Integer, primary_key=True)   # Position in list (0-131071)
    
    # Document reference
    document_id = Column(String(64), nullable=False)
    
    # Status (the actual bit value)
    # False = active (bit 0), True = revoked (bit 1) per W3C convention
    revoked = Column(Boolean, default=False, nullable=False)
    
    # Audit trail
    revoked_at = Column(TIMESTAMP(timezone=True), nullable=True)
    revoked_reason = Column(String(50), nullable=True)  # RevocationReason value
    revoked_reason_detail = Column(Text, nullable=True)  # Free-form explanation
    revoked_by = Column(String(64), nullable=True)  # User/API key that revoked
    
    # Reinstatement tracking
    reinstated_at = Column(TIMESTAMP(timezone=True), nullable=True)
    reinstated_by = Column(String(64), nullable=True)
    
    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(
        TIMESTAMP(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    
    __table_args__ = (
        # Fast lookup by document_id (most common query)
        Index('idx_status_entry_document', 'document_id'),
        # Find all revoked docs for an org (for reporting)
        Index('idx_status_entry_org_revoked', 'organization_id', 'revoked'),
        # Efficient list regeneration query
        Index('idx_status_entry_list', 'organization_id', 'list_index'),
    )
    
    def __repr__(self) -> str:
        status = "REVOKED" if self.revoked else "ACTIVE"
        return (
            f"<StatusListEntry("
            f"doc={self.document_id}, "
            f"org={self.organization_id}, "
            f"list={self.list_index}, "
            f"bit={self.bit_index}, "
            f"status={status})>"
        )


class StatusListMetadata(Base):
    """
    Metadata for each generated status list file.
    
    Tracks:
    - Allocation pointer (next available bit_index)
    - Generation state (version, last generated)
    - CDN location (URL, ETag for cache invalidation)
    """
    __tablename__ = "status_list_metadata"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # List identification
    organization_id = Column(
        String(64),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False
    )
    list_index = Column(Integer, nullable=False)
    
    # Allocation tracking
    next_bit_index = Column(Integer, default=0, nullable=False)  # Next available slot
    is_full = Column(Boolean, default=False, nullable=False)  # True when next_bit_index >= BITS_PER_LIST
    
    # Generation state
    current_version = Column(Integer, default=0, nullable=False)  # Incremented on each regeneration
    last_generated_at = Column(TIMESTAMP(timezone=True), nullable=True)
    generation_duration_ms = Column(Integer, nullable=True)  # For monitoring
    
    # CDN location
    cdn_url = Column(String(500), nullable=True)
    cdn_etag = Column(String(64), nullable=True)  # For cache invalidation
    
    # Statistics
    total_documents = Column(Integer, default=0, nullable=False)
    revoked_count = Column(Integer, default=0, nullable=False)
    
    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(
        TIMESTAMP(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    
    __table_args__ = (
        # Unique constraint on org + list_index
        Index('idx_status_meta_org_list', 'organization_id', 'list_index', unique=True),
        # Find lists that need regeneration
        Index('idx_status_meta_stale', 'organization_id', 'last_generated_at'),
    )
    
    def __repr__(self) -> str:
        return (
            f"<StatusListMetadata("
            f"org={self.organization_id}, "
            f"list={self.list_index}, "
            f"next_bit={self.next_bit_index}, "
            f"version={self.current_version})>"
        )
    
    @property
    def status_list_url(self) -> str:
        """Generate the canonical URL for this status list."""
        # TEAM_002: This should be configurable via settings
        base_url = "https://status.encypherai.com/v1"
        return f"{base_url}/{self.organization_id}/list/{self.list_index}"
    
    @property
    def capacity_remaining(self) -> int:
        """Number of documents that can still be added to this list."""
        return max(0, BITS_PER_LIST - self.next_bit_index)
    
    @property
    def utilization_percent(self) -> float:
        """Percentage of list capacity used."""
        return (self.next_bit_index / BITS_PER_LIST) * 100
