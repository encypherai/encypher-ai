"""
Unit tests for Merkle tree implementation.

Tests cover:
- Hash computation
- Node creation
- Tree construction
- Proof generation
- Proof verification
"""
import pytest

from app.utils.merkle import (
    MerkleNode,
    MerkleProof,
    MerkleTree,
    combine_hashes,
    compute_hash,
    compute_leaf_hash,
    verify_proof,
)
from app.utils.merkle.proof import generate_proof


class TestHashing:
    """Test hash computation functions."""
    
    def test_compute_hash_deterministic(self):
        """Hash should be deterministic."""
        text = "Hello, world!"
        hash1 = compute_hash(text)
        hash2 = compute_hash(text)
        assert hash1 == hash2
    
    def test_compute_hash_different_inputs(self):
        """Different inputs should produce different hashes."""
        hash1 = compute_hash("text1")
        hash2 = compute_hash("text2")
        assert hash1 != hash2
    
    def test_compute_hash_length(self):
        """SHA-256 hash should be 64 hex characters."""
        hash_value = compute_hash("test")
        assert len(hash_value) == 64
        assert all(c in '0123456789abcdef' for c in hash_value)
    
    def test_combine_hashes(self):
        """Combining hashes should produce valid hash."""
        left = compute_hash("left")
        right = compute_hash("right")
        combined = combine_hashes(left, right)
        
        assert len(combined) == 64
        assert combined != left
        assert combined != right
    
    def test_combine_hashes_order_matters(self):
        """Hash combination should be order-dependent."""
        left = compute_hash("left")
        right = compute_hash("right")
        
        combined1 = combine_hashes(left, right)
        combined2 = combine_hashes(right, left)
        
        assert combined1 != combined2


class TestMerkleNode:
    """Test MerkleNode class."""
    
    def test_create_leaf_node(self):
        """Create a leaf node with content."""
        content = "This is a sentence."
        hash_value = compute_hash(content)
        
        node = MerkleNode(
            hash=hash_value,
            content=content,
            metadata={'index': 0},
            depth=3  # Set depth > 0 so it's not a root
        )
        
        assert node.hash == hash_value
        assert node.content == content
        assert node.is_leaf
        assert not node.is_root  # depth > 0
        assert node.metadata['index'] == 0
    
    def test_create_branch_node(self):
        """Create a branch node with children."""
        left = MerkleNode(hash=compute_hash("left"), content="left")
        right = MerkleNode(hash=compute_hash("right"), content="right")
        
        parent_hash = combine_hashes(left.hash, right.hash)
        parent = MerkleNode(hash=parent_hash, left=left, right=right)
        
        assert parent.hash == parent_hash
        assert parent.left == left
        assert parent.right == right
        assert not parent.is_leaf
    
    def test_node_serialization(self):
        """Node should serialize to/from dict."""
        node = MerkleNode(
            hash=compute_hash("test"),
            content="test",
            metadata={'index': 5}
        )
        
        data = node.to_dict()
        assert data['hash'] == node.hash
        assert data['content'] == "test"
        assert data['metadata']['index'] == 5
        
        restored = MerkleNode.from_dict(data)
        assert restored.hash == node.hash
        assert restored.content == node.content


class TestMerkleTree:
    """Test MerkleTree class."""
    
    def test_build_tree_single_segment(self):
        """Build tree with single segment."""
        segments = ["Single sentence."]
        tree = MerkleTree(segments)
        
        assert tree.total_leaves == 1
        assert tree.tree_depth == 0
        assert tree.root.is_leaf
        assert tree.root.content == segments[0]
    
    def test_build_tree_two_segments(self):
        """Build tree with two segments."""
        segments = ["First sentence.", "Second sentence."]
        tree = MerkleTree(segments)
        
        assert tree.total_leaves == 2
        assert tree.tree_depth == 1
        assert not tree.root.is_leaf
        assert tree.root.left.content == segments[0]
        assert tree.root.right.content == segments[1]
    
    def test_build_tree_three_segments(self):
        """Build tree with odd number of segments."""
        segments = ["One.", "Two.", "Three."]
        tree = MerkleTree(segments)
        
        assert tree.total_leaves == 3
        assert tree.tree_depth == 2
        # Last segment should be duplicated
        assert len(tree.leaves) == 3
    
    def test_build_tree_many_segments(self):
        """Build tree with many segments."""
        segments = [f"Sentence {i}." for i in range(100)]
        tree = MerkleTree(segments)
        
        assert tree.total_leaves == 100
        assert len(tree.leaves) == 100
        # Depth should be ceil(log2(100)) = 7
        assert tree.tree_depth == 7
    
    def test_find_leaf_by_hash(self):
        """Find leaf node by hash."""
        segments = ["First.", "Second.", "Third."]
        tree = MerkleTree(segments)
        
        target_hash = compute_leaf_hash("Second.")
        leaf = tree.find_leaf(target_hash)
        
        assert leaf is not None
        assert leaf.content == "Second."
        assert leaf.metadata['index'] == 1
    
    def test_find_leaf_by_content(self):
        """Find leaf node by content."""
        segments = ["First.", "Second.", "Third."]
        tree = MerkleTree(segments)
        
        leaf = tree.find_leaf_by_content("Third.")
        
        assert leaf is not None
        assert leaf.content == "Third."
        assert leaf.metadata['index'] == 2
    
    def test_find_leaf_not_found(self):
        """Return None when leaf not found."""
        segments = ["First.", "Second."]
        tree = MerkleTree(segments)
        
        leaf = tree.find_leaf_by_content("Not in tree.")
        assert leaf is None
    
    def test_get_all_nodes(self):
        """Get all nodes in tree."""
        segments = ["One.", "Two.", "Three.", "Four."]
        tree = MerkleTree(segments)
        
        all_nodes = tree.get_all_nodes()
        
        # 4 leaves + 2 branches + 1 root = 7 nodes
        assert len(all_nodes) == 7
        assert all_nodes[0] == tree.root
    
    def test_tree_serialization(self):
        """Tree should serialize to dict."""
        segments = ["First.", "Second."]
        tree = MerkleTree(segments, segmentation_level='sentence')
        
        data = tree.to_dict()
        
        assert data['root_hash'] == tree.root.hash
        assert data['total_leaves'] == 2
        assert data['segmentation_level'] == 'sentence'
        assert len(data['leaves']) == 2
    
    def test_empty_segments_raises_error(self):
        """Building tree with empty segments should raise error."""
        with pytest.raises(ValueError, match="empty segments"):
            MerkleTree([])


class TestMerkleProof:
    """Test Merkle proof generation and verification."""
    
    def test_generate_proof_single_leaf(self):
        """Generate proof for single-leaf tree."""
        segments = ["Only sentence."]
        tree = MerkleTree(segments)
        
        target_hash = compute_leaf_hash(segments[0])
        proof = generate_proof(tree.root, target_hash)
        
        assert proof is not None
        assert proof.target_hash == target_hash
        assert proof.root_hash == tree.root.hash
        assert len(proof.proof_path) == 0  # No siblings
    
    def test_generate_proof_two_leaves(self):
        """Generate proof for two-leaf tree."""
        segments = ["First.", "Second."]
        tree = MerkleTree(segments)
        
        target_hash = compute_leaf_hash("First.")
        proof = generate_proof(tree.root, target_hash)
        
        assert proof is not None
        assert len(proof.proof_path) == 1
        assert proof.proof_path[0].position == 'right'
        assert proof.proof_path[0].hash == compute_leaf_hash("Second.")
    
    def test_generate_proof_many_leaves(self):
        """Generate proof for large tree."""
        segments = [f"Sentence {i}." for i in range(16)]
        tree = MerkleTree(segments)
        
        target_hash = compute_leaf_hash("Sentence 5.")
        proof = generate_proof(tree.root, target_hash)
        
        assert proof is not None
        # For 16 leaves, depth is 4, so 4 proof steps
        assert len(proof.proof_path) == 4
    
    def test_generate_proof_not_found(self):
        """Return None when target not in tree."""
        segments = ["First.", "Second."]
        tree = MerkleTree(segments)
        
        fake_hash = compute_leaf_hash("Not in tree.")
        proof = generate_proof(tree.root, fake_hash)
        
        assert proof is None
    
    def test_verify_proof_valid(self):
        """Verify a valid proof."""
        segments = ["First.", "Second.", "Third.", "Fourth."]
        tree = MerkleTree(segments)
        
        target_hash = compute_leaf_hash("Third.")
        proof = generate_proof(tree.root, target_hash)
        
        assert proof is not None
        is_valid = verify_proof(proof)
        assert is_valid
        assert proof.verified
    
    def test_verify_proof_invalid_root(self):
        """Verify fails with wrong root hash."""
        segments = ["First.", "Second."]
        tree = MerkleTree(segments)
        
        target_hash = compute_leaf_hash("First.")
        proof = generate_proof(tree.root, target_hash)
        
        # Tamper with root hash
        proof.root_hash = compute_hash("fake root")
        
        is_valid = verify_proof(proof)
        assert not is_valid
        assert not proof.verified
    
    def test_verify_proof_invalid_path(self):
        """Verify fails with tampered proof path."""
        segments = ["First.", "Second.", "Third."]
        tree = MerkleTree(segments)
        
        target_hash = compute_leaf_hash("First.")
        proof = generate_proof(tree.root, target_hash)
        
        # Tamper with proof path
        if proof.proof_path:
            proof.proof_path[0].hash = compute_hash("tampered")
        
        is_valid = verify_proof(proof)
        assert not is_valid
    
    def test_proof_serialization(self):
        """Proof should serialize to/from dict."""
        segments = ["First.", "Second."]
        tree = MerkleTree(segments)
        
        target_hash = compute_leaf_hash("First.")
        proof = generate_proof(tree.root, target_hash)
        
        data = proof.to_dict()
        assert data['target_hash'] == target_hash
        assert data['root_hash'] == tree.root.hash
        assert len(data['proof_path']) == len(proof.proof_path)
        
        restored = MerkleProof.from_dict(data)
        assert restored.target_hash == proof.target_hash
        assert restored.root_hash == proof.root_hash
        assert len(restored.proof_path) == len(proof.proof_path)
    
    def test_end_to_end_workflow(self):
        """Test complete workflow: build tree, generate proof, verify."""
        # Create document segments
        segments = [
            "The quick brown fox jumps over the lazy dog.",
            "This is a test sentence for Merkle tree verification.",
            "Cryptographic proofs ensure data integrity.",
            "Blockchain technology uses Merkle trees extensively."
        ]
        
        # Build tree
        tree = MerkleTree(segments, segmentation_level='sentence')
        assert tree.total_leaves == 4
        
        # Generate proof for second sentence
        target_content = segments[1]
        target_hash = compute_leaf_hash(target_content)
        proof = generate_proof(tree.root, target_hash)
        
        assert proof is not None
        assert proof.target_hash == target_hash
        assert proof.root_hash == tree.root.hash
        
        # Verify proof
        is_valid = verify_proof(proof)
        assert is_valid
        
        # Proof should work independently
        # (simulate sending proof to another party)
        proof_data = proof.to_dict()
        received_proof = MerkleProof.from_dict(proof_data)
        
        is_still_valid = verify_proof(received_proof)
        assert is_still_valid


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_unicode_content(self):
        """Handle Unicode content correctly."""
        segments = ["Hello 世界", "Émojis 🎉", "Ñoño"]
        tree = MerkleTree(segments)
        
        assert tree.total_leaves == 3
        leaf = tree.find_leaf_by_content("Hello 世界")
        assert leaf is not None
    
    def test_very_long_segment(self):
        """Handle very long segments."""
        long_segment = "A" * 10000
        segments = [long_segment, "Short."]
        tree = MerkleTree(segments)
        
        assert tree.total_leaves == 2
        proof = generate_proof(tree.root, compute_leaf_hash(long_segment))
        assert proof is not None
        assert verify_proof(proof)
    
    def test_duplicate_segments(self):
        """Handle duplicate segments."""
        segments = ["Same.", "Same.", "Different."]
        tree = MerkleTree(segments)
        
        assert tree.total_leaves == 3
        # Both "Same." segments should have same hash but different indices
        same_hash = compute_leaf_hash("Same.")
        # Find first occurrence
        leaf = tree.find_leaf(same_hash)
        assert leaf is not None
        # Index could be 0 or 1
        assert leaf.metadata['index'] in [0, 1]
    
    def test_power_of_two_segments(self):
        """Tree with power-of-2 segments should be perfectly balanced."""
        segments = [f"S{i}" for i in range(8)]
        tree = MerkleTree(segments)
        
        assert tree.total_leaves == 8
        assert tree.tree_depth == 3  # log2(8) = 3
        
        # All proofs should have same length
        for segment in segments:
            proof = generate_proof(tree.root, compute_leaf_hash(segment))
            assert len(proof.proof_path) == 3
