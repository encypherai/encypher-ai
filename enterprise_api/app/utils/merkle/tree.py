"""
Merkle tree implementation for hierarchical content attribution.

Builds Merkle trees from text segments and provides proof generation.
"""
from typing import List, Optional, Dict, Any
import logging

from .node import MerkleNode
from .hashing import compute_hash, combine_hashes

logger = logging.getLogger(__name__)


class MerkleTree:
    """
    Merkle tree for hierarchical text attribution.
    
    Builds a binary tree where:
    - Leaf nodes contain text segments and their hashes
    - Branch nodes contain combined hashes of their children
    - Root node hash represents the entire document
    
    Attributes:
        root: Root node of the tree
        leaves: List of leaf nodes (in order)
        segmentation_level: Type of segmentation (sentence/paragraph/section)
        total_leaves: Number of leaf nodes
        tree_depth: Height of the tree
    """
    
    def __init__(self, 
                 segments: List[str],
                 segmentation_level: str = 'sentence',
                 metadata: Optional[Dict[str, Any]] = None):
        """
        Build a Merkle tree from text segments.
        
        Args:
            segments: List of text segments (sentences, paragraphs, etc.)
            segmentation_level: Type of segmentation
            metadata: Additional metadata for the tree
        
        Raises:
            ValueError: If segments list is empty
        """
        if not segments:
            raise ValueError("Cannot build Merkle tree from empty segments list")
        
        self.segmentation_level = segmentation_level
        self.metadata = metadata or {}
        self.leaves: List[MerkleNode] = []
        self.total_leaves = len(segments)
        
        # Build the tree
        self.root = self._build_tree(segments)
        self.tree_depth = self._calculate_depth(self.root)
        
        logger.debug(
            f"Built Merkle tree: {self.total_leaves} leaves, "
            f"depth {self.tree_depth}, root hash {self.root.hash[:8]}..."
        )
    
    def _build_tree(self, segments: List[str]) -> MerkleNode:
        """
        Build Merkle tree from segments using bottom-up approach.
        
        Args:
            segments: List of text segments
        
        Returns:
            Root node of the tree
        """
        # Create leaf nodes
        current_level = []
        for i, segment in enumerate(segments):
            segment_hash = compute_hash(segment)
            node = MerkleNode(
                hash=segment_hash,
                content=segment,
                metadata={
                    'index': i,
                    'level': self.segmentation_level,
                    'length': len(segment)
                },
                depth=0,  # Will be updated later
                position=i
            )
            current_level.append(node)
            self.leaves.append(node)
        
        # Build tree bottom-up
        depth = 0
        while len(current_level) > 1:
            next_level = []
            
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                
                # If odd number of nodes, duplicate the last one
                if i + 1 < len(current_level):
                    right = current_level[i + 1]
                else:
                    right = left
                
                # Create parent node
                parent_hash = combine_hashes(left.hash, right.hash)
                parent = MerkleNode(
                    hash=parent_hash,
                    left=left,
                    right=right,
                    depth=depth,
                    position=i // 2
                )
                
                next_level.append(parent)
            
            current_level = next_level
            depth += 1
        
        # Update depth values (root is at highest depth, leaves at 0)
        root = current_level[0]
        self._update_depths(root, depth)
        
        return root
    
    def _update_depths(self, node: MerkleNode, max_depth: int) -> None:
        """
        Update depth values so root=0 and leaves=max_depth.
        
        Args:
            node: Current node
            max_depth: Maximum depth in tree
        """
        node.depth = max_depth - node.depth
        
        if node.left:
            self._update_depths(node.left, max_depth)
        if node.right and node.right != node.left:
            self._update_depths(node.right, max_depth)
    
    def _calculate_depth(self, node: MerkleNode) -> int:
        """
        Calculate tree depth (height).
        
        Args:
            node: Root node
        
        Returns:
            Tree depth (0 for single node)
        """
        if node.is_leaf:
            return 0
        
        left_depth = self._calculate_depth(node.left) if node.left else 0
        right_depth = self._calculate_depth(node.right) if node.right and node.right != node.left else 0
        
        return 1 + max(left_depth, right_depth)
    
    def find_leaf(self, target_hash: str) -> Optional[MerkleNode]:
        """
        Find a leaf node by its hash.
        
        Args:
            target_hash: Hash to search for
        
        Returns:
            Leaf node if found, None otherwise
        """
        for leaf in self.leaves:
            if leaf.hash == target_hash:
                return leaf
        return None
    
    def find_leaf_by_content(self, content: str) -> Optional[MerkleNode]:
        """
        Find a leaf node by its content.
        
        Args:
            content: Text content to search for
        
        Returns:
            Leaf node if found, None otherwise
        """
        target_hash = compute_hash(content)
        return self.find_leaf(target_hash)
    
    def get_all_nodes(self) -> List[MerkleNode]:
        """
        Get all nodes in the tree (breadth-first order).
        
        Returns:
            List of all nodes
        """
        nodes = []
        queue = [self.root]
        
        while queue:
            node = queue.pop(0)
            nodes.append(node)
            
            if node.left:
                queue.append(node.left)
            if node.right and node.right != node.left:
                queue.append(node.right)
        
        return nodes
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize tree to dictionary.
        
        Returns:
            Dictionary representation
        """
        return {
            'root_hash': self.root.hash,
            'total_leaves': self.total_leaves,
            'tree_depth': self.tree_depth,
            'segmentation_level': self.segmentation_level,
            'metadata': self.metadata,
            'leaves': [leaf.to_dict() for leaf in self.leaves]
        }
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"MerkleTree("
            f"leaves={self.total_leaves}, "
            f"depth={self.tree_depth}, "
            f"root={self.root.hash[:8]}...)"
        )
