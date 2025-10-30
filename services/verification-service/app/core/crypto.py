"""Cryptographic verification operations"""
import hashlib
from typing import Tuple
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization


def verify_signature(content: str, signature_hex: str, public_key_pem: str) -> Tuple[bool, str]:
    """
    Verify Ed25519 signature
    
    Returns:
        (is_valid, error_message)
    """
    try:
        public_key = serialization.load_pem_public_key(public_key_pem.encode())
        signature = bytes.fromhex(signature_hex)
        public_key.verify(signature, content.encode())
        return True, ""
    except Exception as e:
        return False, str(e)


def verify_content_hash(content: str, expected_hash: str) -> bool:
    """Verify content hash matches"""
    actual_hash = hashlib.sha256(content.encode()).hexdigest()
    return actual_hash == expected_hash


def check_tampering(original_content: str, current_content: str) -> Tuple[bool, float]:
    """
    Check if content has been tampered with
    
    Returns:
        (is_tampered, similarity_score)
    """
    if original_content == current_content:
        return False, 1.0
    
    # Simple similarity check
    original_hash = hashlib.sha256(original_content.encode()).hexdigest()
    current_hash = hashlib.sha256(current_content.encode()).hexdigest()
    
    if original_hash == current_hash:
        return False, 1.0
    
    # Calculate similarity (simplified)
    similarity = len(set(original_content) & set(current_content)) / max(len(set(original_content)), len(set(current_content)))
    
    return True, similarity
