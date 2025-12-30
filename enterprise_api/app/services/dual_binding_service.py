"""
Dual-Binding Manifest Service (TEAM_044 - Patent FIG. 10).

Implements dual-binding manifest construction as a proprietary enterprise feature.
This creates tamper-evident manifests by binding both the content hash and
the manifest's own hash into the final signature.

Patent Reference: FIG. 10 - Dual-Binding Manifest Construction
"""
import hashlib
import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple, Union

import cbor2
from cryptography.hazmat.primitives.asymmetric import ed25519

logger = logging.getLogger(__name__)

# Type alias for signing keys
SigningKey = Union[ed25519.Ed25519PrivateKey, Any]


class DualBindingService:
    """
    Service for creating dual-binding manifests.
    
    Dual-binding provides enhanced tamper-evidence by:
    1. Hashing the text content → H_text
    2. Creating a preliminary manifest with placeholder self_hash
    3. Hashing the preliminary manifest → H_preliminary
    4. Replacing placeholder with H_preliminary
    5. Signing the final manifest
    
    This creates a circular binding where the manifest contains its own hash,
    making any modification detectable.
    """
    
    PLACEHOLDER_HASH = "0" * 64  # 64-char placeholder for SHA-256
    
    def __init__(self, private_key: SigningKey, signer_id: str):
        """
        Initialize dual-binding service.
        
        Args:
            private_key: Ed25519 signing key
            signer_id: Signer identifier
        """
        self.private_key = private_key
        self.signer_id = signer_id
    
    def create_dual_binding_manifest(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
        assertions: Optional[Dict[str, Any]] = None,
    ) -> Tuple[bytes, Dict[str, Any]]:
        """
        Create a dual-binding manifest for the given text.
        
        Args:
            text: Text content to bind
            metadata: Optional metadata to include
            assertions: Optional C2PA assertions
            
        Returns:
            Tuple of (signed manifest bytes, manifest info dict)
        """
        timestamp = datetime.now(timezone.utc)
        
        # Step 1: Hash the text content
        h_text = hashlib.sha256(text.encode('utf-8')).hexdigest()
        logger.debug(f"H_text: {h_text[:16]}...")
        
        # Step 2: Create preliminary manifest with placeholder
        preliminary_manifest = {
            "version": "1.0",
            "type": "dual_binding",
            "signer_id": self.signer_id,
            "timestamp": timestamp.isoformat(),
            "content_hash": h_text,
            "content_hash_algorithm": "sha256",
            "self_hash": self.PLACEHOLDER_HASH,  # Placeholder
            "self_hash_algorithm": "sha256",
            "metadata": metadata or {},
            "assertions": assertions or {},
        }
        
        # Step 3: Hash the preliminary manifest
        preliminary_bytes = cbor2.dumps(preliminary_manifest)
        h_preliminary = hashlib.sha256(preliminary_bytes).hexdigest()
        logger.debug(f"H_preliminary: {h_preliminary[:16]}...")
        
        # Step 4: Replace placeholder with actual hash
        final_manifest = preliminary_manifest.copy()
        final_manifest["self_hash"] = h_preliminary
        
        # Step 5: Sign the final manifest
        final_bytes = cbor2.dumps(final_manifest)
        signature = self.private_key.sign(final_bytes)
        
        # Create signed manifest
        signed_manifest = {
            "manifest": final_manifest,
            "signature": signature.hex(),
            "signature_algorithm": "ed25519",
        }
        
        signed_bytes = cbor2.dumps(signed_manifest)
        
        manifest_info = {
            "content_hash": h_text,
            "self_hash": h_preliminary,
            "signer_id": self.signer_id,
            "timestamp": timestamp,
            "signature": signature.hex()[:32] + "...",
        }
        
        logger.info(
            f"Created dual-binding manifest: content_hash={h_text[:16]}..., "
            f"self_hash={h_preliminary[:16]}..."
        )
        
        return signed_bytes, manifest_info
    
    def verify_dual_binding(
        self,
        manifest_bytes: bytes,
        text: str,
        public_key: ed25519.Ed25519PublicKey,
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Verify a dual-binding manifest.
        
        Args:
            manifest_bytes: Signed manifest bytes
            text: Original text content
            public_key: Ed25519 public key for verification
            
        Returns:
            Tuple of (is_valid, message, manifest_info)
        """
        from cryptography.exceptions import InvalidSignature
        
        try:
            # Decode signed manifest
            signed_manifest = cbor2.loads(manifest_bytes)
            manifest = signed_manifest["manifest"]
            signature = bytes.fromhex(signed_manifest["signature"])
            
            # Verify content hash
            h_text = hashlib.sha256(text.encode('utf-8')).hexdigest()
            if manifest["content_hash"] != h_text:
                return False, "Content hash mismatch - text has been modified", None
            
            # Verify self-hash (dual-binding check)
            stored_self_hash = manifest["self_hash"]
            
            # Recreate preliminary manifest to verify self-hash
            preliminary_manifest = manifest.copy()
            preliminary_manifest["self_hash"] = self.PLACEHOLDER_HASH
            preliminary_bytes = cbor2.dumps(preliminary_manifest)
            computed_self_hash = hashlib.sha256(preliminary_bytes).hexdigest()
            
            if stored_self_hash != computed_self_hash:
                return False, "Self-hash mismatch - manifest has been tampered", None
            
            # Verify signature
            manifest_bytes_for_sig = cbor2.dumps(manifest)
            
            try:
                public_key.verify(signature, manifest_bytes_for_sig)
            except InvalidSignature:
                return False, "Signature verification failed", None
            
            manifest_info = {
                "content_hash": manifest["content_hash"],
                "self_hash": manifest["self_hash"],
                "signer_id": manifest["signer_id"],
                "timestamp": manifest["timestamp"],
                "dual_binding_verified": True,
            }
            
            return True, "Dual-binding verification successful", manifest_info
            
        except Exception as e:
            logger.error(f"Dual-binding verification error: {e}")
            return False, f"Verification error: {str(e)}", None


def create_dual_binding_manifest(
    text: str,
    private_key: SigningKey,
    signer_id: str,
    metadata: Optional[Dict[str, Any]] = None,
    assertions: Optional[Dict[str, Any]] = None,
) -> Tuple[bytes, Dict[str, Any]]:
    """
    Convenience function to create a dual-binding manifest.
    
    Args:
        text: Text content to bind
        private_key: Ed25519 signing key
        signer_id: Signer identifier
        metadata: Optional metadata
        assertions: Optional assertions
        
    Returns:
        Tuple of (signed manifest bytes, manifest info)
    """
    service = DualBindingService(private_key, signer_id)
    return service.create_dual_binding_manifest(text, metadata, assertions)
