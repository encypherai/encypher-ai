"""
Hashing utilities for Merkle trees.

Provides SHA-256 hashing for text segments and hash combining for tree construction.
"""
import hashlib
from typing import Optional


def compute_hash(data: str, encoding: str = 'utf-8') -> str:
    """
    Compute SHA-256 hash of text data.
    
    Args:
        data: Text content to hash
        encoding: Text encoding (default: utf-8)
    
    Returns:
        Hexadecimal hash string (64 characters)
    
    Example:
        >>> compute_hash("Hello, world!")
        '315f5bdb76d078c43b8ac0064e4a0164612b1fce77c869345bfc94c75894edd3'
    """
    return hashlib.sha256(data.encode(encoding)).hexdigest()


def combine_hashes(left_hash: str, right_hash: str) -> str:
    """
    Combine two hashes to create a parent hash.
    
    This is the core operation for building Merkle trees.
    The hashes are concatenated and then hashed again.
    
    Args:
        left_hash: Hash of left child node
        right_hash: Hash of right child node
    
    Returns:
        Combined hash (parent node hash)
    
    Example:
        >>> left = compute_hash("left")
        >>> right = compute_hash("right")
        >>> parent = combine_hashes(left, right)
    """
    combined = left_hash + right_hash
    return compute_hash(combined)


def normalize_text(text: str, 
                   lowercase: bool = False,
                   remove_whitespace: bool = False,
                   remove_punctuation: bool = False) -> str:
    """
    Normalize text before hashing for better matching.
    
    Args:
        text: Input text
        lowercase: Convert to lowercase
        remove_whitespace: Remove extra whitespace
        remove_punctuation: Remove punctuation
    
    Returns:
        Normalized text
    """
    result = text
    
    if lowercase:
        result = result.lower()
    
    if remove_whitespace:
        # Replace multiple spaces with single space
        result = ' '.join(result.split())
    
    if remove_punctuation:
        # Remove common punctuation
        import string
        result = result.translate(str.maketrans('', '', string.punctuation))
    
    return result


def compute_normalized_hash(text: str,
                           lowercase: bool = False,
                           remove_whitespace: bool = False,
                           remove_punctuation: bool = False) -> str:
    """
    Compute hash of normalized text.
    
    This is useful for matching text that may have minor variations.
    
    Args:
        text: Input text
        lowercase: Convert to lowercase before hashing
        remove_whitespace: Remove extra whitespace before hashing
        remove_punctuation: Remove punctuation before hashing
    
    Returns:
        Hash of normalized text
    """
    normalized = normalize_text(
        text,
        lowercase=lowercase,
        remove_whitespace=remove_whitespace,
        remove_punctuation=remove_punctuation
    )
    return compute_hash(normalized)
