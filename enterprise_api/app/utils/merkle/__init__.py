"""
Merkle tree utilities for hierarchical content attribution.

This package provides:
- MerkleNode: Node class for tree construction
- MerkleTree: Tree builder and manager
- Proof generation and verification
- Hash computation utilities
"""
from .node import MerkleNode
from .tree import MerkleTree
from .hashing import compute_hash, combine_hashes, compute_normalized_hash
from .proof import MerkleProof, generate_proof, verify_proof

# Import normalize_for_hashing from segmentation
from app.utils.segmentation import normalize_for_hashing

__all__ = [
    "MerkleNode",
    "MerkleTree",
    "compute_hash",
    "combine_hashes",
    "compute_normalized_hash",
    "MerkleProof",
    "generate_proof",
    "verify_proof",
    "normalize_for_hashing",
]
