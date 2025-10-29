"""
Merkle proof generation and verification.

Provides cryptographic proofs that a text segment belongs to a document.
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
import logging

from .node import MerkleNode
from .hashing import combine_hashes

logger = logging.getLogger(__name__)


@dataclass
class ProofStep:
    """
    A single step in a Merkle proof.
    
    Attributes:
        hash: Hash of the sibling node
        position: Position of sibling ('left' or 'right')
    """
    hash: str
    position: str  # 'left' or 'right'
    
    def to_dict(self) -> Dict[str, str]:
        """Serialize to dictionary."""
        return {'hash': self.hash, 'position': self.position}
    
    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> 'ProofStep':
        """Deserialize from dictionary."""
        return cls(hash=data['hash'], position=data['position'])


@dataclass
class MerkleProof:
    """
    Cryptographic proof that a segment belongs to a document.
    
    A Merkle proof consists of:
    - Target hash (the leaf being proved)
    - Root hash (the document root)
    - Proof path (sibling hashes from leaf to root)
    
    Attributes:
        target_hash: Hash of the text segment being proved
        root_hash: Hash of the Merkle tree root
        proof_path: List of sibling hashes along the path
        verified: Whether the proof has been verified
    """
    target_hash: str
    root_hash: str
    proof_path: List[ProofStep] = field(default_factory=list)
    verified: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize proof to dictionary."""
        return {
            'target_hash': self.target_hash,
            'root_hash': self.root_hash,
            'proof_path': [step.to_dict() for step in self.proof_path],
            'verified': self.verified
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MerkleProof':
        """Deserialize proof from dictionary."""
        return cls(
            target_hash=data['target_hash'],
            root_hash=data['root_hash'],
            proof_path=[ProofStep.from_dict(step) for step in data['proof_path']],
            verified=data.get('verified', False)
        )
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"MerkleProof("
            f"target={self.target_hash[:8]}..., "
            f"root={self.root_hash[:8]}..., "
            f"steps={len(self.proof_path)}, "
            f"verified={self.verified})"
        )


def generate_proof(tree_root: MerkleNode, target_hash: str) -> Optional[MerkleProof]:
    """
    Generate a Merkle proof for a target hash.
    
    Args:
        tree_root: Root node of the Merkle tree
        target_hash: Hash of the leaf to prove
    
    Returns:
        MerkleProof if target found, None otherwise
    """
    proof_path: List[ProofStep] = []
    
    def find_path(node: MerkleNode) -> bool:
        """
        Recursively find path from target to root.
        
        Returns:
            True if target found in this subtree
        """
        # Found the target
        if node.hash == target_hash:
            return True
        
        # Leaf node but not the target
        if node.is_leaf:
            return False
        
        # Try left subtree
        if node.left and find_path(node.left):
            # Target is in left subtree, add right sibling to proof
            if node.right and node.right != node.left:
                proof_path.append(ProofStep(hash=node.right.hash, position='right'))
            else:
                # Duplicated node (odd number of leaves)
                proof_path.append(ProofStep(hash=node.left.hash, position='right'))
            return True
        
        # Try right subtree
        if node.right and node.right != node.left and find_path(node.right):
            # Target is in right subtree, add left sibling to proof
            proof_path.append(ProofStep(hash=node.left.hash, position='left'))
            return True
        
        return False
    
    # Find the path
    if not find_path(tree_root):
        logger.warning(f"Target hash {target_hash[:8]}... not found in tree")
        return None
    
    # Create proof
    proof = MerkleProof(
        target_hash=target_hash,
        root_hash=tree_root.hash,
        proof_path=proof_path
    )
    
    logger.debug(
        f"Generated proof: {len(proof_path)} steps, "
        f"target={target_hash[:8]}..., root={tree_root.hash[:8]}..."
    )
    
    return proof


def verify_proof(proof: MerkleProof) -> bool:
    """
    Verify a Merkle proof.
    
    Reconstructs the root hash from the target hash and proof path.
    If the reconstructed root matches the expected root, the proof is valid.
    
    Args:
        proof: Merkle proof to verify
    
    Returns:
        True if proof is valid, False otherwise
    """
    current_hash = proof.target_hash
    
    # Apply each proof step
    for step in proof.proof_path:
        if step.position == 'left':
            # Sibling is on the left
            current_hash = combine_hashes(step.hash, current_hash)
        else:
            # Sibling is on the right
            current_hash = combine_hashes(current_hash, step.hash)
    
    # Check if reconstructed root matches expected root
    is_valid = current_hash == proof.root_hash
    
    if is_valid:
        logger.debug(f"Proof verified successfully: {proof.target_hash[:8]}...")
    else:
        logger.warning(
            f"Proof verification failed: "
            f"expected {proof.root_hash[:8]}..., "
            f"got {current_hash[:8]}..."
        )
    
    # Update proof object
    proof.verified = is_valid
    
    return is_valid


def batch_generate_proofs(tree_root: MerkleNode, 
                          target_hashes: List[str]) -> List[Optional[MerkleProof]]:
    """
    Generate proofs for multiple targets efficiently.
    
    Args:
        tree_root: Root node of the Merkle tree
        target_hashes: List of hashes to prove
    
    Returns:
        List of proofs (None for hashes not found)
    """
    return [generate_proof(tree_root, target) for target in target_hashes]


def batch_verify_proofs(proofs: List[MerkleProof]) -> List[bool]:
    """
    Verify multiple proofs efficiently.
    
    Args:
        proofs: List of proofs to verify
    
    Returns:
        List of verification results
    """
    return [verify_proof(proof) for proof in proofs]
