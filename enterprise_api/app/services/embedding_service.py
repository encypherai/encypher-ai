"""
Service for creating and verifying minimal signed embeddings.

Generates compact 64-bit reference IDs and HMAC signatures for portable
content authentication.
"""
import hmac
import hashlib
import time
import random
import logging
from typing import List, Dict, Any, Optional, Tuple
from uuid import UUID
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.content_reference import ContentReference
from app.models.merkle import MerkleRoot

logger = logging.getLogger(__name__)


@dataclass
class EmbeddingReference:
    """Minimal signed embedding reference."""
    ref_id: int
    signature: str
    leaf_hash: str
    leaf_index: int
    text_content: str
    document_id: str
    
    def to_compact_string(self, version: str = "v1") -> str:
        """Generate compact embedding string."""
        ref_hex = format(self.ref_id, '08x')  # 8 hex chars
        sig_short = self.signature[:8]  # First 8 chars
        return f"ency:{version}/{ref_hex}/{sig_short}"
    
    def to_url(self, base_url: str = "https://verify.encypher.ai") -> str:
        """Generate verification URL."""
        ref_hex = format(self.ref_id, '08x')
        return f"{base_url}/{ref_hex}"
    
    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            'ref_id': format(self.ref_id, '08x'),
            'signature': self.signature[:8],
            'leaf_hash': self.leaf_hash,
            'leaf_index': self.leaf_index,
            'text_content': self.text_content,
            'document_id': self.document_id,
            'embedding': self.to_compact_string(),
            'verification_url': self.to_url()
        }


class EmbeddingService:
    """
    Service for creating and verifying minimal signed embeddings.
    
    Generates 64-bit reference IDs with the following structure:
    - Timestamp component (2 bytes): Seconds since 2025-01-01
    - Sequence number (2 bytes): Monotonic counter
    - Random component (2 bytes): Entropy
    - Checksum (2 bytes): XOR of above components
    
    Signatures are HMAC-SHA256 truncated to 8 bytes for compactness.
    """
    
    # Epoch for timestamp component (2025-01-01 00:00:00 UTC)
    EPOCH_2025 = 1735689600
    
    def __init__(self, secret_key: bytes):
        """
        Initialize embedding service.
        
        Args:
            secret_key: Secret key for HMAC signatures (32+ bytes recommended)
        """
        if len(secret_key) < 16:
            raise ValueError("Secret key must be at least 16 bytes")
        
        self.secret_key = secret_key
        self._sequence = 0
        self._last_timestamp = 0
    
    async def create_embeddings(
        self,
        db: AsyncSession,
        organization_id: str,
        document_id: str,
        merkle_root_id: UUID,
        segments: List[str],
        leaf_hashes: List[str],
        c2pa_manifest_url: Optional[str] = None,
        c2pa_manifest_hash: Optional[str] = None,
        license_info: Optional[Dict[str, str]] = None,
        expires_at: Optional[Any] = None
    ) -> List[EmbeddingReference]:
        """
        Create minimal signed embeddings for all segments.
        
        Args:
            db: Database session
            organization_id: Organization ID
            document_id: Document ID
            merkle_root_id: Merkle tree root ID
            segments: List of text segments (sentences)
            leaf_hashes: List of leaf hashes (same order as segments)
            c2pa_manifest_url: Optional C2PA manifest URL
            c2pa_manifest_hash: Optional C2PA manifest hash
            license_info: Optional license information dict
            expires_at: Optional expiration datetime
        
        Returns:
            List of EmbeddingReference objects
        
        Raises:
            ValueError: If segments and leaf_hashes lengths don't match
        """
        if len(segments) != len(leaf_hashes):
            raise ValueError(
                f"Segments ({len(segments)}) and leaf_hashes ({len(leaf_hashes)}) "
                f"must have same length"
            )
        
        embeddings = []
        references_to_insert = []
        
        logger.info(
            f"Creating {len(segments)} embeddings for document {document_id} "
            f"in organization {organization_id}"
        )
        
        for idx, (segment, leaf_hash) in enumerate(zip(segments, leaf_hashes)):
            # Generate unique ref_id
            ref_id = self._generate_ref_id()
            
            # Generate signature
            signature = self._generate_signature(ref_id)
            
            # Create ContentReference object
            reference = ContentReference(
                ref_id=ref_id,
                merkle_root_id=merkle_root_id,
                leaf_hash=leaf_hash,
                leaf_index=idx,
                organization_id=organization_id,
                document_id=document_id,
                text_content=segment,
                text_preview=segment[:200] if segment else None,
                signature_hash=signature,
                c2pa_manifest_url=c2pa_manifest_url,
                c2pa_manifest_hash=c2pa_manifest_hash,
                license_type=license_info.get('type') if license_info else None,
                license_url=license_info.get('url') if license_info else None,
                expires_at=expires_at,
                embedding_metadata={
                    'version': 'v1',
                    'created_by': 'embedding_service'
                }
            )
            
            references_to_insert.append(reference)
            
            embeddings.append(EmbeddingReference(
                ref_id=ref_id,
                signature=signature,
                leaf_hash=leaf_hash,
                leaf_index=idx,
                text_content=segment,
                document_id=document_id
            ))
        
        # Bulk insert all references
        db.add_all(references_to_insert)
        await db.commit()
        
        logger.info(
            f"Successfully created {len(embeddings)} embeddings for document {document_id}"
        )
        
        return embeddings
    
    def _generate_ref_id(self) -> int:
        """
        Generate unique 64-bit reference ID.
        
        Format: TTTTTTTT SSSSSSSS RRRRRRRR CCCCCCCC
        - T (2 bytes): Timestamp component
        - S (2 bytes): Sequence number
        - R (2 bytes): Random component
        - C (2 bytes): Checksum
        
        Returns:
            64-bit integer
        """
        # Timestamp component (2 bytes) - seconds since 2025-01-01
        current_time = int(time.time())
        timestamp = current_time - self.EPOCH_2025
        timestamp_component = timestamp & 0xFFFF  # Last 2 bytes
        
        # Sequence number (2 bytes) - monotonic counter
        # Reset if timestamp changed
        if timestamp != self._last_timestamp:
            self._sequence = 0
            self._last_timestamp = timestamp
        else:
            self._sequence = (self._sequence + 1) & 0xFFFF
        
        # Random component (2 bytes) - entropy
        random_component = random.randint(0, 0xFFFF)
        
        # Combine components
        ref_id = (timestamp_component << 48) | (self._sequence << 32) | (random_component << 16)
        
        # Checksum (2 bytes) - XOR of all components
        checksum = (timestamp_component ^ self._sequence ^ random_component) & 0xFFFF
        ref_id |= checksum
        
        return ref_id
    
    def _generate_signature(self, ref_id: int) -> str:
        """
        Generate HMAC-SHA256 signature for ref_id.
        
        Args:
            ref_id: 64-bit reference ID
        
        Returns:
            Hex-encoded signature (16 characters = 8 bytes)
        """
        # Convert ref_id to bytes (big-endian)
        ref_bytes = ref_id.to_bytes(8, byteorder='big')
        
        # Generate HMAC-SHA256
        hmac_full = hmac.new(self.secret_key, ref_bytes, hashlib.sha256).digest()
        
        # Truncate to first 8 bytes for compactness
        signature_bytes = hmac_full[:8]
        
        # Encode as hex
        return signature_bytes.hex()
    
    def verify_signature(self, ref_id: int, signature: str) -> bool:
        """
        Verify signature matches ref_id.
        
        Args:
            ref_id: 64-bit reference ID
            signature: Hex-encoded signature to verify
        
        Returns:
            True if signature is valid, False otherwise
        """
        expected = self._generate_signature(ref_id)
        
        # Use constant-time comparison to prevent timing attacks
        return hmac.compare_digest(expected, signature)
    
    async def verify_embedding(
        self,
        db: AsyncSession,
        ref_id_hex: str,
        signature_hex: str
    ) -> Optional[ContentReference]:
        """
        Verify an embedding and return the content reference.
        
        Args:
            db: Database session
            ref_id_hex: Hex-encoded reference ID (8 characters)
            signature_hex: Hex-encoded signature (8+ characters)
        
        Returns:
            ContentReference if valid, None otherwise
        """
        try:
            # Parse ref_id from hex
            ref_id = int(ref_id_hex, 16)
        except ValueError:
            logger.warning(f"Invalid ref_id hex: {ref_id_hex}")
            return None
        
        # Verify signature
        if not self.verify_signature(ref_id, signature_hex[:16]):
            logger.warning(f"Invalid signature for ref_id: {ref_id_hex}")
            return None
        
        # Lookup in database
        result = await db.execute(
            select(ContentReference).where(ContentReference.ref_id == ref_id)
        )
        reference = result.scalar_one_or_none()
        
        if not reference:
            logger.warning(f"Reference not found: {ref_id_hex}")
            return None
        
        # Check expiration
        if reference.expires_at and reference.expires_at < time.time():
            logger.warning(f"Reference expired: {ref_id_hex}")
            return None
        
        logger.info(f"Successfully verified embedding: {ref_id_hex}")
        return reference
    
    async def get_reference_by_id(
        self,
        db: AsyncSession,
        ref_id: int
    ) -> Optional[ContentReference]:
        """
        Get content reference by ID.
        
        Args:
            db: Database session
            ref_id: Reference ID (integer)
        
        Returns:
            ContentReference if found, None otherwise
        """
        result = await db.execute(
            select(ContentReference).where(ContentReference.ref_id == ref_id)
        )
        return result.scalar_one_or_none()
    
    async def get_references_by_document(
        self,
        db: AsyncSession,
        document_id: str,
        organization_id: Optional[str] = None
    ) -> List[ContentReference]:
        """
        Get all content references for a document.
        
        Args:
            db: Database session
            document_id: Document ID
            organization_id: Optional organization ID filter
        
        Returns:
            List of ContentReference objects
        """
        query = select(ContentReference).where(
            ContentReference.document_id == document_id
        )
        
        if organization_id:
            query = query.where(ContentReference.organization_id == organization_id)
        
        query = query.order_by(ContentReference.leaf_index)
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    def parse_embedding(self, embedding_str: str) -> Optional[Tuple[str, str, str]]:
        """
        Parse embedding string into components.
        
        Args:
            embedding_str: Embedding string like "ency:v1/a3f9c2e1/8k3mP9xQ"
        
        Returns:
            Tuple of (version, ref_id_hex, signature_hex) or None if invalid
        """
        try:
            if not embedding_str.startswith('ency:'):
                return None
            
            parts = embedding_str[5:].split('/')  # Remove 'ency:' prefix
            
            if len(parts) != 3:
                return None
            
            version, ref_id_hex, signature_hex = parts
            
            # Validate format
            if len(ref_id_hex) != 8:
                return None
            
            if len(signature_hex) < 8:
                return None
            
            return version, ref_id_hex, signature_hex
            
        except Exception as e:
            logger.warning(f"Failed to parse embedding: {embedding_str}, error: {e}")
            return None
