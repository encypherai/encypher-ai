"""
SQLAlchemy models for Merkle tree tables.

These models map to the database tables created by migrations 006-009.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import (
    Column, String, Integer, TIMESTAMP, ForeignKey, 
    CheckConstraint, Index, JSON, LargeBinary, Boolean
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship

from app.database import Base


class MerkleRoot(Base):
    """
    Merkle tree root hashes for source documents.
    
    Stores the root hash and metadata for a Merkle tree built from
    a document at a specific segmentation level.
    """
    __tablename__ = "merkle_roots"
    
    root_id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    organization_id = Column(String(255), ForeignKey("organizations.organization_id", ondelete="CASCADE"), nullable=False)
    document_id = Column(String(255), nullable=False, index=True)
    root_hash = Column(String(64), nullable=False, index=True)
    tree_depth = Column(Integer, nullable=False)
    total_leaves = Column(Integer, nullable=False)
    segmentation_level = Column(String(50), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    doc_metadata = Column("metadata", JSON, default={})
    
    # Relationships
    subhashes = relationship("MerkleSubhash", back_populates="root", cascade="all, delete-orphan")
    proof_cache = relationship("MerkleProofCache", back_populates="root", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        CheckConstraint('tree_depth >= 0', name='chk_tree_depth_positive'),
        CheckConstraint('total_leaves > 0', name='chk_total_leaves_positive'),
        CheckConstraint("segmentation_level IN ('word', 'sentence', 'paragraph', 'section')", 
                       name='chk_valid_segmentation_level'),
        Index('idx_merkle_roots_org_level', 'organization_id', 'segmentation_level'),
        Index('idx_merkle_roots_created_at', 'created_at'),
    )
    
    def __repr__(self):
        return f"<MerkleRoot(root_id={self.root_id}, doc={self.document_id}, level={self.segmentation_level})>"


class MerkleSubhash(Base):
    """
    Index of all hashes (leaves and branches) in Merkle trees.
    
    This table enables efficient lookup of any hash value to find
    which document(s) contain that hash.
    """
    __tablename__ = "merkle_subhashes"
    
    subhash_id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    hash_value = Column(String(64), nullable=False, index=True)
    root_id = Column(PGUUID(as_uuid=True), ForeignKey("merkle_roots.root_id", ondelete="CASCADE"), nullable=False)
    node_type = Column(String(20), nullable=False)
    depth_level = Column(Integer, nullable=False)
    position_index = Column(Integer, nullable=False)
    parent_hash = Column(String(64), nullable=True, index=True)
    left_child_hash = Column(String(64), nullable=True)
    right_child_hash = Column(String(64), nullable=True)
    text_content = Column(String, nullable=True)  # Only for leaf nodes
    seg_metadata = Column("segment_metadata", JSON, default={})
    
    # Relationships
    root = relationship("MerkleRoot", back_populates="subhashes")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("node_type IN ('leaf', 'branch', 'root')", name='chk_valid_node_type'),
        CheckConstraint('depth_level >= 0', name='chk_depth_level_positive'),
        CheckConstraint('position_index >= 0', name='chk_position_index_positive'),
        Index('idx_merkle_subhashes_hash_root', 'hash_value', 'root_id'),
        Index('idx_merkle_subhashes_node_type', 'node_type'),
    )
    
    def __repr__(self):
        return f"<MerkleSubhash(hash={self.hash_value[:8]}..., type={self.node_type})>"


class MerkleProofCache(Base):
    """
    Cache for generated Merkle proofs.
    
    Stores proofs to avoid regenerating them for frequently accessed hashes.
    Proofs expire after 24 hours by default.
    """
    __tablename__ = "merkle_proof_cache"
    
    cache_id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    target_hash = Column(String(64), nullable=False)
    root_id = Column(PGUUID(as_uuid=True), ForeignKey("merkle_roots.root_id", ondelete="CASCADE"), nullable=False)
    proof_path = Column(JSON, nullable=False)  # Array of {hash, position} objects
    position_bits = Column(LargeBinary, nullable=False)  # Binary path representation
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    expires_at = Column(TIMESTAMP, nullable=False)
    
    # Relationships
    root = relationship("MerkleRoot", back_populates="proof_cache")
    
    # Constraints
    __table_args__ = (
        Index('idx_merkle_proof_cache_target_root', 'target_hash', 'root_id'),
        Index('idx_merkle_proof_cache_expires', 'expires_at'),
    )
    
    def __repr__(self):
        return f"<MerkleProofCache(target={self.target_hash[:8]}..., expires={self.expires_at})>"


class AttributionReport(Base):
    """
    Plagiarism detection and source attribution reports.
    
    Stores the results of scanning a target document against
    the repository of source documents.
    """
    __tablename__ = "attribution_reports"
    
    report_id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    organization_id = Column(String(255), ForeignKey("organizations.organization_id", ondelete="CASCADE"), nullable=False)
    target_document_id = Column(String(255), nullable=True, index=True)
    target_text_hash = Column(String(64), nullable=True)
    scan_timestamp = Column(TIMESTAMP, nullable=False, default=datetime.utcnow, index=True)
    total_segments = Column(Integer, nullable=False)
    matched_segments = Column(Integer, nullable=False)
    source_documents = Column(JSON, nullable=False, default=[])  # Array of source match objects
    heat_map_data = Column(JSON, nullable=True)  # Visualization data
    report_meta = Column("report_metadata", JSON, default={})
    
    # Constraints
    __table_args__ = (
        CheckConstraint('total_segments >= 0', name='chk_total_segments_positive'),
        CheckConstraint('matched_segments >= 0', name='chk_matched_segments_positive'),
        CheckConstraint('matched_segments <= total_segments', name='chk_matched_le_total'),
        Index('idx_attribution_reports_org_timestamp', 'organization_id', 'scan_timestamp'),
    )
    
    def __repr__(self):
        return f"<AttributionReport(report_id={self.report_id}, matches={self.matched_segments}/{self.total_segments})>"
