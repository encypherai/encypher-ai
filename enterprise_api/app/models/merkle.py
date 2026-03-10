"""
SQLAlchemy models for Merkle tree tables.

These models map to the database tables created by migration 002_enterprise_api_schema.sql.
Updated to use unified schema with organizations.id as FK.
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    TIMESTAMP,
    CheckConstraint,
    Column,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
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

    # Primary key - matches migration: id UUID PRIMARY KEY
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    # FK to unified schema organizations.id
    organization_id = Column(String(64), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    document_id = Column(String(64), nullable=False, index=True)
    root_hash = Column(String(64), nullable=False, index=True)
    algorithm = Column(String(20), nullable=False, default="sha256")
    leaf_count = Column(Integer, nullable=False)
    tree_depth = Column(Integer, nullable=False, default=0)
    segmentation_level = Column(String(50), nullable=False)
    doc_metadata = Column(JSONB, default={})
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow)

    # Relationships
    subhashes = relationship("MerkleSubhash", back_populates="root", cascade="all, delete-orphan")
    proof_cache = relationship("MerkleProofCache", back_populates="root", cascade="all, delete-orphan")

    # Constraints - match migration
    __table_args__ = (
        CheckConstraint("tree_depth >= 0", name="merkle_roots_tree_depth_check"),
        CheckConstraint("leaf_count > 0", name="merkle_roots_leaf_count_check"),
        CheckConstraint("segmentation_level IN ('sentence', 'paragraph', 'section')", name="merkle_roots_segmentation_level_check"),
        Index("idx_merkle_roots_org", "organization_id"),
    )

    def __repr__(self):
        return f"<MerkleRoot(id={self.id}, doc={self.document_id}, level={self.segmentation_level})>"


class MerkleSubhash(Base):
    """
    Index of all hashes (leaves and branches) in Merkle trees.

    This table enables efficient lookup of any hash value to find
    which document(s) contain that hash.
    """

    __tablename__ = "merkle_subhashes"

    # Primary key - matches migration: id UUID PRIMARY KEY
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    hash_value = Column(String(64), nullable=False, index=True)
    # FK to merkle_roots.id (not root_id)
    root_id = Column(PGUUID(as_uuid=True), ForeignKey("merkle_roots.id", ondelete="CASCADE"), nullable=False)
    node_type = Column(String(20), nullable=False)
    depth_level = Column(Integer, nullable=False)
    position_index = Column(Integer, nullable=False)
    parent_hash = Column(String(64), nullable=True, index=True)
    left_child_hash = Column(String(64), nullable=True)
    right_child_hash = Column(String(64), nullable=True)
    text_content = Column(Text, nullable=True)  # Only for leaf nodes
    segment_metadata = Column(JSONB, default={})

    # Relationships
    root = relationship("MerkleRoot", back_populates="subhashes")

    # Constraints - match migration
    __table_args__ = (
        CheckConstraint("node_type IN ('leaf', 'branch', 'root')", name="merkle_subhashes_node_type_check"),
        CheckConstraint("depth_level >= 0", name="merkle_subhashes_depth_level_check"),
        CheckConstraint("position_index >= 0", name="merkle_subhashes_position_index_check"),
        Index("idx_subhashes_hash", "hash_value"),
        Index("idx_subhashes_root", "root_id"),
    )

    def __repr__(self):
        return f"<MerkleSubhash(hash={self.hash_value[:8]}..., type={self.node_type})>"


class MerkleProofCache(Base):
    """
    Cache for generated Merkle proofs.

    Stores proofs to avoid regenerating them for frequently accessed hashes.
    Proofs expire after 24 hours by default.

    NOTE: This table is not in the migration - it's an application-level cache.
    Consider using Redis instead for production.
    """

    __tablename__ = "merkle_proof_cache"

    # Primary key
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    # FK to merkle_roots.id
    root_id = Column(PGUUID(as_uuid=True), ForeignKey("merkle_roots.id", ondelete="CASCADE"), nullable=False)
    leaf_hash = Column(String(64), nullable=False)
    proof_path = Column(JSONB, nullable=False)  # Array of {hash, position} objects
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow)
    expires_at = Column(TIMESTAMP(timezone=True), nullable=False)

    # Relationships
    root = relationship("MerkleRoot", back_populates="proof_cache")

    # Constraints
    __table_args__ = (
        Index("idx_proof_cache_leaf", "leaf_hash"),
        Index("idx_proof_cache_root", "root_id"),
        Index("idx_proof_cache_expires", "expires_at"),
    )

    def __repr__(self):
        return f"<MerkleProofCache(leaf_hash={self.leaf_hash[:8]}..., expires={self.expires_at})>"


class AttributionReport(Base):
    """
    Plagiarism detection and source attribution reports.

    Stores the results of scanning a target document against
    the repository of source documents.
    """

    __tablename__ = "attribution_reports"

    # Primary key - matches migration: id UUID PRIMARY KEY
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    # FK to unified schema organizations.id
    organization_id = Column(String(64), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    target_document_id = Column(String(64), nullable=True, index=True)
    target_text_hash = Column(String(64), nullable=True)
    scan_timestamp = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow, index=True)
    total_segments = Column(Integer, nullable=False)
    matched_segments = Column(Integer, nullable=False)
    source_documents = Column(JSONB, nullable=False, default=[])  # Array of source match objects
    heat_map_data = Column(JSONB, nullable=True)  # Visualization data
    report_metadata = Column(JSONB, default={})

    # Constraints - match migration
    __table_args__ = (
        CheckConstraint("total_segments >= 0", name="attribution_reports_total_segments_check"),
        CheckConstraint("matched_segments >= 0", name="attribution_reports_matched_segments_check"),
        CheckConstraint("matched_segments <= total_segments", name="chk_matched_le_total"),
        Index("idx_attribution_org", "organization_id"),
        Index("idx_attribution_scan", "scan_timestamp"),
    )

    def __repr__(self):
        return f"<AttributionReport(id={self.id}, matches={self.matched_segments}/{self.total_segments})>"
