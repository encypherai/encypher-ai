"""
Merkle tree utilities for hierarchical content attribution.

This package provides:
- MerkleNode: Node class for tree construction
- MerkleTree: Tree builder and manager
- Proof generation and verification
- Hash computation utilities
"""
# Import normalize_for_hashing from segmentation
from app.utils.segmentation import normalize_for_hashing

from .hashing import combine_hashes, compute_hash, compute_leaf_hash, compute_normalized_hash
from .node import MerkleNode
from .proof import MerkleProof, generate_proof, verify_proof
from .tree import MerkleTree

__all__ = [
    "MerkleNode",
    "MerkleTree",
    "compute_hash",
    "compute_leaf_hash",
    "combine_hashes",
    "compute_normalized_hash",
    "MerkleProof",
    "generate_proof",
    "verify_proof",
    "normalize_for_hashing",
]
