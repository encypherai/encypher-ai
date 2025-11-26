"""
Service layer for Merkle tree operations.

Combines CRUD operations with Merkle tree logic to provide
high-level business operations.
"""
from typing import List, Optional, Dict, Any, Tuple
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import merkle as merkle_crud
from app.utils.merkle import MerkleTree, MerkleProof
from app.utils.segmentation import HierarchicalSegmenter, normalize_for_hashing
from app.models.merkle import MerkleRoot, MerkleSubhash, AttributionReport

logger = logging.getLogger(__name__)


class MerkleService:
    """
    Service for Merkle tree operations.
    
    Provides high-level operations that combine database access
    with Merkle tree construction and proof generation.
    """
    
    @staticmethod
    async def encode_document(
        db: AsyncSession,
        organization_id: str,
        document_id: str,
        text: str,
        segmentation_levels: List[str] = ["sentence"],
        metadata: Optional[Dict[str, Any]] = None,
        include_words: bool = False
    ) -> Dict[str, MerkleRoot]:
        """
        Encode a document into Merkle trees at multiple segmentation levels.
        
        Args:
            db: Database session
            organization_id: Organization identifier
            document_id: Document identifier
            text: Document text
            segmentation_levels: Levels to encode (word/sentence/paragraph/section)
            metadata: Optional document metadata
            include_words: Whether to include word-level segmentation
        
        Returns:
            Dictionary mapping segmentation level to MerkleRoot
        """
        # Segment the text at all levels
        segmenter = HierarchicalSegmenter(text, include_words=include_words)
        
        roots = {}
        
        for level in segmentation_levels:
            try:
                # Get segments for this level
                segments = segmenter.get_segments(level)
                
                if not segments:
                    logger.warning(f"No segments found for level {level}")
                    continue
                
                # Build Merkle tree
                tree = MerkleTree(segments, segmentation_level=level, metadata=metadata)
                
                # Store root in database
                root = await merkle_crud.create_merkle_root(
                    db=db,
                    organization_id=organization_id,
                    document_id=document_id,
                    root_hash=tree.root.hash,
                    tree_depth=tree.tree_depth,
                    total_leaves=tree.total_leaves,
                    segmentation_level=level,
                    metadata=metadata
                )
                
                # Store all subhashes for efficient lookup
                subhashes_data = []
                for node in tree.get_all_nodes():
                    subhash_data = {
                        'hash_value': node.hash,
                        'root_id': root.id,  # Use 'id' not 'root_id'
                        'node_type': 'leaf' if node.is_leaf else ('root' if node.is_root else 'branch'),
                        'depth_level': node.depth,
                        'position_index': node.position,
                        'parent_hash': None,  # Could be computed if needed
                        'left_child_hash': node.left.hash if node.left else None,
                        'right_child_hash': node.right.hash if node.right and node.right != node.left else None,
                        'text_content': node.content if node.is_leaf else None,
                        'segment_metadata': node.metadata  # Match model column name
                    }
                    subhashes_data.append(subhash_data)
                
                # Bulk insert subhashes
                await merkle_crud.bulk_create_merkle_subhashes(db, subhashes_data)
                
                roots[level] = root
                logger.info(f"Encoded document {document_id} at {level} level: {tree.total_leaves} leaves")
                
            except Exception as e:
                logger.error(f"Error encoding document at {level} level: {e}")
                raise
        
        return roots
    
    @staticmethod
    async def find_sources(
        db: AsyncSession,
        text_segment: str,
        segmentation_level: str = "sentence",
        normalize: bool = True
    ) -> List[Tuple[MerkleSubhash, MerkleRoot]]:
        """
        Find source documents containing a text segment.
        
        Args:
            db: Database session
            text_segment: Text to search for
            segmentation_level: Level to search at
            normalize: Whether to normalize text before hashing
        
        Returns:
            List of (subhash, root) tuples for matching sources
        """
        # Compute hash of the segment
        if normalize:
            normalized = normalize_for_hashing(text_segment, lowercase=True, normalize_unicode_chars=True)
            from app.utils.merkle import compute_hash
            segment_hash = compute_hash(normalized)
        else:
            from app.utils.merkle import compute_hash
            segment_hash = compute_hash(text_segment)
        
        # Find all subhashes matching this hash
        subhashes = await merkle_crud.find_subhashes_by_hash(
            db=db,
            hash_value=segment_hash,
            node_type='leaf'  # Only search leaf nodes
        )
        
        # Return subhashes with their roots
        results = [(subhash, subhash.root) for subhash in subhashes]
        
        logger.info(f"Found {len(results)} sources for segment hash {segment_hash[:8]}...")
        return results
    
    @staticmethod
    async def generate_attribution_report(
        db: AsyncSession,
        organization_id: str,
        target_text: str,
        segmentation_level: str = "sentence",
        target_document_id: Optional[str] = None,
        include_heat_map: bool = True
    ) -> AttributionReport:
        """
        Generate a plagiarism detection / source attribution report.
        
        Args:
            db: Database session
            organization_id: Organization identifier
            target_text: Text to analyze
            segmentation_level: Level to analyze at
            target_document_id: Optional target document identifier
            include_heat_map: Whether to generate heat map data
        
        Returns:
            AttributionReport instance
        """
        # Segment the target text
        segmenter = HierarchicalSegmenter(target_text)
        segments = segmenter.get_segments(segmentation_level)
        
        total_segments = len(segments)
        matched_segments = 0
        source_matches: Dict[str, Dict[str, Any]] = {}
        heat_map_positions = []
        
        # Check each segment
        for idx, segment in enumerate(segments):
            sources = await MerkleService.find_sources(
                db=db,
                text_segment=segment,
                segmentation_level=segmentation_level
            )
            
            if sources:
                matched_segments += 1
                heat_map_positions.append({
                    'index': idx,
                    'segment': segment[:100],  # Truncate for storage
                    'matched': True,
                    'source_count': len(sources)
                })
                
                # Aggregate by source document
                for subhash, root in sources:
                    doc_id = root.document_id
                    if doc_id not in source_matches:
                        source_matches[doc_id] = {
                            'document_id': doc_id,
                            'organization_id': root.organization_id,
                            'segmentation_level': root.segmentation_level,
                            'matched_segments': 0,
                            'total_leaves': root.total_leaves,
                            'doc_metadata': root.doc_metadata
                        }
                    source_matches[doc_id]['matched_segments'] += 1
            else:
                heat_map_positions.append({
                    'index': idx,
                    'segment': segment[:100],
                    'matched': False,
                    'source_count': 0
                })
        
        # Calculate match percentages and sort by relevance
        source_documents = []
        for doc_data in source_matches.values():
            match_percentage = (doc_data['matched_segments'] / total_segments) * 100
            doc_data['match_percentage'] = round(match_percentage, 2)
            doc_data['confidence_score'] = round(match_percentage / 100, 3)
            source_documents.append(doc_data)
        
        # Sort by match percentage (descending)
        source_documents.sort(key=lambda x: x['match_percentage'], reverse=True)
        
        # Generate heat map data
        heat_map_data = None
        if include_heat_map:
            heat_map_data = {
                'positions': heat_map_positions,
                'total_segments': total_segments,
                'matched_segments': matched_segments,
                'match_percentage': round((matched_segments / total_segments) * 100, 2) if total_segments > 0 else 0
            }
        
        # Create report
        from app.utils.merkle import compute_hash
        target_hash = compute_hash(target_text)
        
        report = await merkle_crud.create_attribution_report(
            db=db,
            organization_id=organization_id,
            target_document_id=target_document_id,
            target_text_hash=target_hash,
            total_segments=total_segments,
            matched_segments=matched_segments,
            source_documents=source_documents,
            heat_map_data=heat_map_data,
            report_metadata={
                'segmentation_level': segmentation_level,
                'text_length': len(target_text)
            }
        )
        
        logger.info(
            f"Generated attribution report: {matched_segments}/{total_segments} segments matched, "
            f"{len(source_documents)} source documents found"
        )
        
        return report
    
    @staticmethod
    async def verify_segment_in_document(
        db: AsyncSession,
        text_segment: str,
        document_id: str,
        segmentation_level: str = "sentence"
    ) -> Optional[MerkleProof]:
        """
        Verify that a text segment exists in a specific document.
        
        Args:
            db: Database session
            text_segment: Text segment to verify
            document_id: Document identifier
            segmentation_level: Level to verify at
        
        Returns:
            MerkleProof if segment found, None otherwise
        """
        # Find the root for this document
        roots = await merkle_crud.get_merkle_roots_by_document(
            db=db,
            document_id=document_id,
            segmentation_level=segmentation_level
        )
        
        if not roots:
            logger.warning(f"No Merkle root found for document {document_id} at {segmentation_level} level")
            return None
        
        root = roots[0]  # Use the first (most recent) root
        
        # Compute hash of segment
        from app.utils.merkle import compute_hash
        normalized = normalize_for_hashing(text_segment, lowercase=True, normalize_unicode_chars=True)
        segment_hash = compute_hash(normalized)
        
        # Check cache first
        cached_proof = await merkle_crud.get_cached_proof(
            db=db,
            target_hash=segment_hash,
            root_id=root.root_id
        )
        
        if cached_proof:
            # Reconstruct proof from cache
            proof = MerkleProof(
                target_hash=cached_proof.target_hash,
                root_hash=root.root_hash,
                proof_path=cached_proof.proof_path,
                verified=True
            )
            logger.info(f"Retrieved cached proof for {segment_hash[:8]}...")
            return proof
        
        # Get all subhashes for this root to reconstruct the tree
        # (In production, you might want to cache the tree structure)
        subhashes = await merkle_crud.find_subhashes_by_root(
            db=db,
            root_id=root.root_id
        )
        
        # Find the target subhash
        target_subhash = None
        for subhash in subhashes:
            if subhash.hash_value == segment_hash and subhash.node_type == 'leaf':
                target_subhash = subhash
                break
        
        if not target_subhash:
            logger.info(f"Segment not found in document {document_id}")
            return None
        
        # For now, return a simple proof indicating the segment was found
        # Full proof generation would require reconstructing the tree
        # or storing the tree structure
        proof = MerkleProof(
            target_hash=segment_hash,
            root_hash=root.root_hash,
            proof_path=[],  # Would need tree reconstruction for full path
            verified=True
        )
        
        logger.info(f"Verified segment in document {document_id}")
        return proof
