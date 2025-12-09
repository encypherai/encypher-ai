"""
SQLAlchemy model for content_references table.

Stores minimal signed embeddings that link text segments to Merkle trees.
"""
from datetime import datetime

from sqlalchemy import (
    JSON,
    TIMESTAMP,
    BigInteger,
    CheckConstraint,
    Column,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship

from app.database import Base


class ContentReference(Base):
    """
    Minimal signed embedding references for portable content authentication.
    
    Each reference represents a single text segment (typically a sentence)
    with a compact 64-bit ID and HMAC signature that can be embedded in content.
    
    Embedding format: ency:v1/{ref_id_hex}/{signature_hex}
    Example: ency:v1/a3f9c2e1/8k3mP9xQ (28 bytes)
    """
    __tablename__ = "content_references"
    
    # Primary identifier (64-bit integer for compact embeddings)
    ref_id = Column(BigInteger, primary_key=True)
    
    # Link to Merkle tree system (nullable for free tier - no Merkle tree)
    merkle_root_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("merkle_roots.id", ondelete="CASCADE"),  # Updated to use unified schema
        nullable=True,  # Free tier has no Merkle tree
        index=True
    )
    leaf_hash = Column(String(64), nullable=False, index=True)
    leaf_index = Column(Integer, nullable=False)
    
    # Document metadata - FK to unified schema organizations.id
    organization_id = Column(
        String(64),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    document_id = Column(String(64), nullable=False, index=True)
    
    # Content information
    text_content = Column(Text, nullable=True)
    text_preview = Column(String(200), nullable=True)
    
    # C2PA and licensing
    c2pa_manifest_url = Column(String(500), nullable=True)
    c2pa_manifest_hash = Column(String(64), nullable=True)
    license_type = Column(String(100), nullable=True)
    license_url = Column(String(500), nullable=True)
    
    # C2PA Provenance Chain
    instance_id = Column(String(255), nullable=True, index=True)  # C2PA manifest instance_id
    previous_instance_id = Column(String(255), nullable=True, index=True)  # Previous version for edit chain
    manifest_data = Column(JSON, nullable=True)  # Full C2PA manifest for ingredient references
    
    # Verification data
    signature_hash = Column(String(64), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow, index=True)
    expires_at = Column(TIMESTAMP, nullable=True, index=True)
    
    # Status List (W3C StatusList2021) for per-document revocation
    # TEAM_002: Added for bitstring status list support
    status_list_index = Column(Integer, nullable=True)  # Which list (0, 1, 2...)
    status_bit_index = Column(Integer, nullable=True)   # Position in list (0-131071)
    status_list_url = Column(String(500), nullable=True)  # CDN URL for status list
    
    # Additional metadata
    embedding_metadata = Column(JSON, default={})
    
    # Relationships
    merkle_root = relationship("MerkleRoot", backref="content_references")
    
    # Constraints
    __table_args__ = (
        CheckConstraint('leaf_index >= 0', name='chk_content_refs_leaf_index_positive'),
        Index('idx_content_refs_org_doc', 'organization_id', 'document_id'),
        Index('idx_content_refs_org_created', 'organization_id', 'created_at'),
    )
    
    def to_compact_string(self, version: str = "v1") -> str:
        """
        Generate compact embedding string.
        
        Args:
            version: Embedding format version
        
        Returns:
            Compact string like "ency:v1/a3f9c2e1/8k3mP9xQ"
        """
        ref_hex = format(self.ref_id, '08x')  # 8 hex characters
        sig_short = self.signature_hash[:8]  # First 8 characters
        return f"ency:{version}/{ref_hex}/{sig_short}"
    
    def to_verification_url(self, base_url: str = "https://verify.encypher.ai") -> str:
        """
        Generate public verification URL.
        
        Args:
            base_url: Base URL for verification service
        
        Returns:
            URL like "https://verify.encypher.ai/a3f9c2e1"
        """
        ref_hex = format(self.ref_id, '08x')
        return f"{base_url}/{ref_hex}"
    
    def to_dict(self, include_text: bool = False) -> dict:
        """
        Serialize to dictionary for API responses.
        
        Args:
            include_text: Whether to include full text_content
        
        Returns:
            Dictionary representation
        """
        data = {
            'ref_id': format(self.ref_id, '08x'),
            'leaf_hash': self.leaf_hash,
            'leaf_index': self.leaf_index,
            'document_id': self.document_id,
            'text_preview': self.text_preview,
            'embedding': self.to_compact_string(),
            'verification_url': self.to_verification_url(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        
        if include_text and self.text_content:
            data['text_content'] = self.text_content
        
        if self.c2pa_manifest_url:
            data['c2pa_manifest_url'] = self.c2pa_manifest_url
        
        if self.license_type:
            data['license'] = {
                'type': self.license_type,
                'url': self.license_url
            }
        
        return data
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        ref_hex = format(self.ref_id, '08x')
        return (
            f"<ContentReference("
            f"ref_id={ref_hex}, "
            f"doc={self.document_id}, "
            f"leaf_index={self.leaf_index})>"
        )
