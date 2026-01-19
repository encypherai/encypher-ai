"""
CRUD operations for Merkle tree tables.

Follows the repository pattern for clean separation of concerns.
All operations are async for performance.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import and_, delete, insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.merkle import AttributionReport, MerkleProofCache, MerkleRoot, MerkleSubhash

# ============================================================================
# MerkleRoot CRUD Operations
# ============================================================================


async def create_merkle_root(
    db: AsyncSession,
    organization_id: str,
    document_id: str,
    root_hash: str,
    tree_depth: int,
    leaf_count: int,
    segmentation_level: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> MerkleRoot:
    """
    Create a new Merkle root entry.

    Args:
        db: Database session
        organization_id: Organization that owns the document
        document_id: Unique document identifier
        root_hash: SHA-256 hash of the Merkle tree root
        tree_depth: Height of the tree
        total_leaves: Number of leaf nodes
        segmentation_level: Type of segmentation (word/sentence/paragraph/section)
        metadata: Optional metadata (title, author, etc.)

    Returns:
        Created MerkleRoot instance
    """
    root = MerkleRoot(
        organization_id=organization_id,
        document_id=document_id,
        root_hash=root_hash,
        tree_depth=tree_depth,
        leaf_count=leaf_count,
        segmentation_level=segmentation_level,
        doc_metadata=metadata or {},
    )
    db.add(root)
    await db.commit()
    await db.refresh(root)
    return root


async def get_merkle_root_by_id(db: AsyncSession, root_id: UUID) -> Optional[MerkleRoot]:
    """Get a Merkle root by its ID."""
    result = await db.execute(select(MerkleRoot).where(MerkleRoot.id == root_id))
    return result.scalar_one_or_none()


async def get_merkle_roots_by_document(db: AsyncSession, document_id: str, segmentation_level: Optional[str] = None) -> List[MerkleRoot]:
    """
    Get all Merkle roots for a document.

    Args:
        db: Database session
        document_id: Document identifier
        segmentation_level: Optional filter by segmentation level

    Returns:
        List of MerkleRoot instances
    """
    query = select(MerkleRoot).where(MerkleRoot.document_id == document_id)

    if segmentation_level:
        query = query.where(MerkleRoot.segmentation_level == segmentation_level)

    result = await db.execute(query)
    return list(result.scalars().all())


async def get_merkle_roots_by_organization(
    db: AsyncSession, organization_id: str, segmentation_level: Optional[str] = None, limit: int = 100, offset: int = 0
) -> List[MerkleRoot]:
    """
    Get Merkle roots for an organization with pagination.

    Args:
        db: Database session
        organization_id: Organization identifier
        segmentation_level: Optional filter by segmentation level
        limit: Maximum number of results
        offset: Number of results to skip

    Returns:
        List of MerkleRoot instances
    """
    query = select(MerkleRoot).where(MerkleRoot.organization_id == organization_id)

    if segmentation_level:
        query = query.where(MerkleRoot.segmentation_level == segmentation_level)

    query = query.order_by(MerkleRoot.created_at.desc()).limit(limit).offset(offset)

    result = await db.execute(query)
    return list(result.scalars().all())


async def delete_merkle_root(db: AsyncSession, root_id: UUID) -> bool:
    """
    Delete a Merkle root and all associated subhashes/proofs (cascade).

    Args:
        db: Database session
        root_id: Root identifier

    Returns:
        True if deleted, False if not found
    """
    result = await db.execute(delete(MerkleRoot).where(MerkleRoot.id == root_id))
    await db.commit()
    return result.rowcount > 0


# ============================================================================
# MerkleSubhash CRUD Operations
# ============================================================================


async def create_merkle_subhash(
    db: AsyncSession,
    hash_value: str,
    root_id: UUID,
    node_type: str,
    depth_level: int,
    position_index: int,
    parent_hash: Optional[str] = None,
    left_child_hash: Optional[str] = None,
    right_child_hash: Optional[str] = None,
    text_content: Optional[str] = None,
    segment_metadata: Optional[Dict[str, Any]] = None,
) -> MerkleSubhash:
    """
    Create a new Merkle subhash entry.

    Args:
        db: Database session
        hash_value: SHA-256 hash of the node
        root_id: Reference to the Merkle root
        node_type: Type of node (leaf/branch/root)
        depth_level: Distance from root
        position_index: Position within the level
        parent_hash: Hash of parent node (None for root)
        left_child_hash: Hash of left child (None for leaves)
        right_child_hash: Hash of right child (None for leaves)
        text_content: Original text (only for leaf nodes)
        segment_metadata: Optional metadata

    Returns:
        Created MerkleSubhash instance
    """
    subhash = MerkleSubhash(
        hash_value=hash_value,
        root_id=root_id,
        node_type=node_type,
        depth_level=depth_level,
        position_index=position_index,
        parent_hash=parent_hash,
        left_child_hash=left_child_hash,
        right_child_hash=right_child_hash,
        text_content=text_content,
        segment_metadata=segment_metadata or {},
    )
    db.add(subhash)
    await db.commit()
    await db.refresh(subhash)
    return subhash


async def bulk_create_merkle_subhashes(db: AsyncSession, subhashes: List[Dict[str, Any]]) -> int:
    """
    Bulk insert multiple subhashes for performance.
    Uses SQLAlchemy Core insert() for maximum speed (bypassing ORM).

    Args:
        db: Database session
        subhashes: List of subhash dictionaries

    Returns:
        Number of subhashes created
    """
    if not subhashes:
        return 0

    # Chunk size for optimal bulk insert
    CHUNK_SIZE = 2000
    total_inserted = 0

    for i in range(0, len(subhashes), CHUNK_SIZE):
        chunk = subhashes[i : i + CHUNK_SIZE]
        stmt = insert(MerkleSubhash).values(chunk)
        await db.execute(stmt)
        total_inserted += len(chunk)

    await db.commit()
    return total_inserted


async def find_subhashes_by_hash(db: AsyncSession, hash_value: str, node_type: Optional[str] = None) -> List[MerkleSubhash]:
    """
    Find all subhashes matching a hash value.

    This is the core operation for source attribution - finding which
    documents contain a specific hash.

    Args:
        db: Database session
        hash_value: Hash to search for
        node_type: Optional filter by node type

    Returns:
        List of MerkleSubhash instances with root relationship loaded
    """
    query = select(MerkleSubhash).where(MerkleSubhash.hash_value == hash_value)

    if node_type:
        query = query.where(MerkleSubhash.node_type == node_type)

    # Eagerly load the root relationship
    query = query.options(selectinload(MerkleSubhash.root))

    result = await db.execute(query)
    return list(result.scalars().all())


async def find_subhashes_by_root(db: AsyncSession, root_id: UUID, node_type: Optional[str] = None) -> List[MerkleSubhash]:
    """
    Get all subhashes for a specific Merkle root.

    Args:
        db: Database session
        root_id: Root identifier
        node_type: Optional filter by node type

    Returns:
        List of MerkleSubhash instances
    """
    query = select(MerkleSubhash).where(MerkleSubhash.root_id == root_id)

    if node_type:
        query = query.where(MerkleSubhash.node_type == node_type)

    query = query.order_by(MerkleSubhash.depth_level, MerkleSubhash.position_index)

    result = await db.execute(query)
    return list(result.scalars().all())


async def batch_find_subhashes(db: AsyncSession, hash_values: List[str], node_type: Optional[str] = "leaf") -> Dict[str, List[MerkleSubhash]]:
    """
    Find subhashes for multiple hash values efficiently.

    Args:
        db: Database session
        hash_values: List of hashes to search for
        node_type: Optional filter by node type

    Returns:
        Dictionary mapping hash_value to list of MerkleSubhash instances
    """
    if not hash_values:
        return {}

    query = select(MerkleSubhash).where(MerkleSubhash.hash_value.in_(hash_values))

    if node_type:
        query = query.where(MerkleSubhash.node_type == node_type)

    # Eagerly load roots
    query = query.options(selectinload(MerkleSubhash.root))

    result = await db.execute(query)
    subhashes = result.scalars().all()

    # Group by hash_value
    grouped: Dict[str, List[MerkleSubhash]] = {}
    for subhash in subhashes:
        if subhash.hash_value not in grouped:
            grouped[subhash.hash_value] = []
        grouped[subhash.hash_value].append(subhash)

    return grouped


# ============================================================================
# MerkleProofCache CRUD Operations
# ============================================================================


async def create_proof_cache(
    db: AsyncSession, leaf_hash: str, root_id: UUID, proof_path: List[Dict[str, str]], ttl_hours: int = 24
) -> MerkleProofCache:
    """
    Cache a Merkle proof.

    Args:
        db: Database session
        target_hash: Hash being proved
        root_id: Root identifier
        proof_path: List of {hash, position} dictionaries
        position_bits: Binary path representation
        ttl_hours: Time to live in hours

    Returns:
        Created MerkleProofCache instance
    """
    expires_at = datetime.utcnow() + timedelta(hours=ttl_hours)

    proof = MerkleProofCache(
        leaf_hash=leaf_hash,
        root_id=root_id,
        proof_path=proof_path,
        expires_at=expires_at,
    )
    db.add(proof)
    await db.commit()
    await db.refresh(proof)
    return proof


async def get_cached_proof(db: AsyncSession, leaf_hash: str, root_id: UUID) -> Optional[MerkleProofCache]:
    """
    Get a cached proof if it exists and hasn't expired.

    Args:
        db: Database session
        target_hash: Hash being proved
        root_id: Root identifier

    Returns:
        MerkleProofCache instance or None
    """
    result = await db.execute(
        select(MerkleProofCache).where(
            and_(MerkleProofCache.leaf_hash == leaf_hash, MerkleProofCache.root_id == root_id, MerkleProofCache.expires_at > datetime.utcnow())
        )
    )
    return result.scalar_one_or_none()


async def delete_expired_proofs(db: AsyncSession) -> int:
    """
    Delete all expired proof cache entries.

    Args:
        db: Database session

    Returns:
        Number of proofs deleted
    """
    result = await db.execute(delete(MerkleProofCache).where(MerkleProofCache.expires_at <= datetime.utcnow()))
    await db.commit()
    return result.rowcount


# ============================================================================
# AttributionReport CRUD Operations
# ============================================================================


async def create_attribution_report(
    db: AsyncSession,
    organization_id: str,
    total_segments: int,
    matched_segments: int,
    source_documents: List[Dict[str, Any]],
    target_document_id: Optional[str] = None,
    target_text_hash: Optional[str] = None,
    heat_map_data: Optional[Dict[str, Any]] = None,
    report_metadata: Optional[Dict[str, Any]] = None,
) -> AttributionReport:
    """
    Create a new attribution report.

    Args:
        db: Database session
        organization_id: Organization identifier
        total_segments: Total number of segments scanned
        matched_segments: Number of segments with matches
        source_documents: List of source match objects
        target_document_id: Optional target document identifier
        target_text_hash: Optional hash of target text
        heat_map_data: Optional visualization data
        report_metadata: Optional metadata

    Returns:
        Created AttributionReport instance
    """
    report = AttributionReport(
        organization_id=organization_id,
        target_document_id=target_document_id,
        target_text_hash=target_text_hash,
        total_segments=total_segments,
        matched_segments=matched_segments,
        source_documents=source_documents,
        heat_map_data=heat_map_data,
        report_metadata=report_metadata or {},
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)
    return report


async def get_attribution_report(db: AsyncSession, report_id: UUID) -> Optional[AttributionReport]:
    """Get an attribution report by ID."""
    result = await db.execute(select(AttributionReport).where(AttributionReport.id == report_id))
    return result.scalar_one_or_none()


async def get_attribution_reports_by_organization(
    db: AsyncSession, organization_id: str, limit: int = 50, offset: int = 0
) -> List[AttributionReport]:
    """
    Get attribution reports for an organization with pagination.

    Args:
        db: Database session
        organization_id: Organization identifier
        limit: Maximum number of results
        offset: Number of results to skip

    Returns:
        List of AttributionReport instances
    """
    result = await db.execute(
        select(AttributionReport)
        .where(AttributionReport.organization_id == organization_id)
        .order_by(AttributionReport.scan_timestamp.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(result.scalars().all())


async def delete_attribution_report(db: AsyncSession, report_id: UUID) -> bool:
    """
    Delete an attribution report.

    Args:
        db: Database session
        report_id: Report identifier

    Returns:
        True if deleted, False if not found
    """
    result = await db.execute(delete(AttributionReport).where(AttributionReport.id == report_id))
    await db.commit()
    return result.rowcount > 0
