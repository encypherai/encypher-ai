"""
Merkle tree node implementation.

Represents a single node in a Merkle tree (leaf or branch).
"""
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class MerkleNode:
    """
    A node in a Merkle tree.
    
    Attributes:
        hash: SHA-256 hash value of this node
        left: Left child node (None for leaves)
        right: Right child node (None for leaves)
        content: Original text content (only for leaf nodes)
        metadata: Additional metadata (index, position, etc.)
        depth: Distance from root (0 = root)
        position: Position within depth level (0-indexed, left-to-right)
    """
    hash: str
    left: Optional['MerkleNode'] = None
    right: Optional['MerkleNode'] = None
    content: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    depth: int = 0
    position: int = 0
    
    @property
    def is_leaf(self) -> bool:
        """Check if this is a leaf node."""
        return self.left is None and self.right is None
    
    @property
    def is_root(self) -> bool:
        """Check if this is a root node (depth 0)."""
        return self.depth == 0
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize node to dictionary.
        
        Returns:
            Dictionary representation of the node
        """
        result = {
            'hash': self.hash,
            'depth': self.depth,
            'position': self.position,
            'is_leaf': self.is_leaf,
            'metadata': self.metadata,
        }
        
        if self.content is not None:
            result['content'] = self.content
        
        if self.left:
            result['left_hash'] = self.left.hash
        
        if self.right:
            result['right_hash'] = self.right.hash
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MerkleNode':
        """
        Deserialize node from dictionary.
        
        Note: This creates a standalone node without children.
        Use MerkleTree.from_dict() to reconstruct full trees.
        
        Args:
            data: Dictionary representation
        
        Returns:
            MerkleNode instance
        """
        return cls(
            hash=data['hash'],
            content=data.get('content'),
            metadata=data.get('metadata', {}),
            depth=data.get('depth', 0),
            position=data.get('position', 0),
        )
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        if self.is_leaf:
            content_preview = self.content[:30] + '...' if self.content and len(self.content) > 30 else self.content
            return f"MerkleNode(leaf, hash={self.hash[:8]}..., content='{content_preview}')"
        else:
            return f"MerkleNode(branch, hash={self.hash[:8]}..., depth={self.depth})"
    
    def __eq__(self, other: object) -> bool:
        """Compare nodes by hash."""
        if not isinstance(other, MerkleNode):
            return False
        return self.hash == other.hash
    
    def __hash__(self) -> int:
        """Hash for use in sets/dicts."""
        return hash(self.hash)
