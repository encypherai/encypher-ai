"""
Service for creating and verifying minimal signed embeddings.

Enterprise layer built on top of the free encypher-ai package.
Uses invisible Unicode variation selector embeddings with enterprise features:
- Merkle tree integration for hierarchical authentication
- Database storage for content references
- Batch operations and analytics
- Public verification API
"""
import time
import logging
from typing import List, Dict, Any, Optional, Tuple
from uuid import UUID
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# Import from free encypher-ai package (foundation)
try:
    from encypher.core.unicode_metadata import UnicodeMetadata
    from encypher.core.keys import load_private_key_from_data
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
except ImportError:
    raise ImportError(
        "encypher-ai package not found. "
        "Please install: pip install encypher-ai"
    )

from app.models.content_reference import ContentReference
from app.models.merkle import MerkleRoot

logger = logging.getLogger(__name__)


@dataclass
class EmbeddingReference:
    """
    Minimal signed embedding reference with invisible Unicode embedding.
    
    Uses encypher-ai package for invisible embedding, with enterprise features:
    - Merkle tree integration (leaf_hash, leaf_index)
    - Database persistence (ContentReference model)
    - Verification tracking
    """
    leaf_hash: str
    leaf_index: int
    text_content: str
    embedded_text: str  # Text with invisible Unicode embedding
    document_id: str
    ref_id: Optional[int] = None  # Database ID (optional, set after DB insert)
    
    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            'leaf_index': self.leaf_index,
            'leaf_hash': self.leaf_hash,
            'text_content': self.text_content,
            'embedded_text': self.embedded_text,
            'document_id': self.document_id,
            'has_invisible_embedding': True
        }


class EmbeddingService:
    """
    Enterprise embedding service built on encypher-ai package.
    
    Provides enterprise features on top of the free open-source foundation:
    - Invisible Unicode variation selector embeddings (from encypher-ai)
    - Merkle tree integration for hierarchical authentication
    - Database storage for content references
    - Batch operations and analytics
    - Public verification API
    
    The encypher-ai package handles:
    - Digital signatures (Ed25519)
    - Invisible Unicode embedding
    - Content hash verification
    - Tamper detection
    """
    
    def __init__(self, private_key: Ed25519PrivateKey, signer_id: str):
        """
        Initialize embedding service.
        
        Args:
            private_key: Ed25519 private key for signing (from encypher-ai)
            signer_id: Identifier for the signing key
        """
        self.private_key = private_key
        self.signer_id = signer_id
    
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
        expires_at: Optional[datetime] = None,
        metadata_format: str = "c2pa",  # C2PA-compliant by default
        add_hard_binding: bool = True  # Include hard binding by default
    ) -> List[EmbeddingReference]:
        """
        Create invisible signed embeddings for all segments using encypher-ai.
        
        **C2PA Compliance:**
        By default, embeds full C2PA-compliant manifests as per the Manifests_Text.adoc
        specification. Each embedding includes:
        - C2PA manifest with assertions (actions, hash.data, soft_binding)
        - Hard binding via c2pa.hash.data assertion (optional, enabled by default)
        - Unicode variation selector encoding (U+FE00-FE0F, U+E0100-E01EF)
        - C2PATextManifestWrapper structure
        
        Enterprise features:
        - Stores Merkle tree references in database
        - Links embeddings to organization and document
        - Tracks C2PA manifests and licensing
        - Provides expiration management
        
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
            metadata_format: Format for embeddings ("c2pa" by default, "basic" for minimal)
            add_hard_binding: Include c2pa.hash.data assertion (True by default)
        
        Returns:
            List of EmbeddingReference objects with invisible C2PA-compliant embeddings
        
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
            f"Creating {len(segments)} invisible embeddings for document {document_id} "
            f"in organization {organization_id} using encypher-ai"
        )
        
        current_timestamp = int(time.time())
        
        # Build the full document with sentence-level embeddings
        # For C2PA compliance, we'll add ONE wrapper at the end
        full_document_parts = []
        
        for idx, (segment, leaf_hash) in enumerate(zip(segments, leaf_hashes)):
            # Create custom metadata for enterprise features
            custom_metadata = {
                'document_id': document_id,
                'organization_id': organization_id,
                'merkle_root_id': str(merkle_root_id),
                'leaf_hash': leaf_hash,
                'leaf_index': idx,
            }
            
            if c2pa_manifest_url:
                custom_metadata['c2pa_manifest_url'] = c2pa_manifest_url
            
            if license_info:
                custom_metadata['license'] = license_info
            
            # For sentence-level tracking, just append the segment without C2PA wrapper
            # The C2PA wrapper will be added once at the end for spec compliance
            full_document_parts.append(segment)
            
            # Create ContentReference object for database storage (enterprise feature)
            # Generate unique ref_id using timestamp + index to avoid collisions
            ref_id = int(time.time() * 1000) + idx  # Millisecond timestamp + index
            
            reference = ContentReference(
                ref_id=ref_id,  # Use unique timestamp-based ID
                merkle_root_id=merkle_root_id,
                leaf_hash=leaf_hash,
                leaf_index=idx,
                organization_id=organization_id,
                document_id=document_id,
                text_content=segment,
                text_preview=segment[:200] if segment else None,
                signature_hash="",  # Signature is in the C2PA wrapper
                c2pa_manifest_url=c2pa_manifest_url,
                c2pa_manifest_hash=c2pa_manifest_hash,
                license_type=license_info.get('type') if license_info else None,
                license_url=license_info.get('url') if license_info else None,
                expires_at=expires_at,
                embedding_metadata={
                    'version': 'v1',
                    'created_by': 'embedding_service',
                    'uses_encypher_ai': True,
                    'signer_id': self.signer_id
                }
            )
            
            references_to_insert.append(reference)
        
        # Step 2: Add ONE C2PATextManifestWrapper at the end (C2PA spec compliant)
        # Join all segments back together
        full_document = ''.join(full_document_parts)
        
        # Create document-level metadata
        document_metadata = {
            'document_id': document_id,
            'organization_id': organization_id,
            'merkle_root_id': str(merkle_root_id),
            'total_segments': len(segments),
        }
        
        if c2pa_manifest_url:
            document_metadata['c2pa_manifest_url'] = c2pa_manifest_url
        
        if license_info:
            document_metadata['license'] = license_info
        
        # Embed ONE C2PA wrapper for the entire document
        try:
            logger.info(f"Adding C2PA wrapper for document {document_id} ({len(segments)} segments)")
            embedded_document = UnicodeMetadata.embed_metadata(
                text=full_document,
                private_key=self.private_key,
                signer_id=self.signer_id,
                timestamp=current_timestamp,
                custom_metadata=document_metadata,
                metadata_format=metadata_format,  # C2PA-compliant wrapper
                add_hard_binding=add_hard_binding,
                claim_generator=f"EncypherAI Enterprise API/{organization_id}"
            )
            logger.info(f"Successfully added C2PA wrapper to document {document_id}")
        except Exception as e:
            logger.error(f"Failed to add C2PA wrapper to document: {e}")
            raise ValueError(f"C2PA wrapper embedding failed: {e}")
        
        # Create embedding references for each segment
        # Note: All segments are in the same embedded_document with ONE wrapper
        for idx, (segment, leaf_hash) in enumerate(zip(segments, leaf_hashes)):
            ref_id = int(time.time() * 1000) + idx
            
            embeddings.append(EmbeddingReference(
                leaf_hash=leaf_hash,
                leaf_index=idx,
                text_content=segment,
                embedded_text=embedded_document,  # Full document with ONE wrapper
                document_id=document_id,
                ref_id=ref_id
            ))
        
        # Delete old content references for this document (if re-signing)
        from sqlalchemy import delete
        from app.models.content_reference import ContentReference as ContentReferenceModel
        
        delete_stmt = delete(ContentReferenceModel).where(
            ContentReferenceModel.document_id == document_id,
            ContentReferenceModel.organization_id == organization_id
        )
        result = await db.execute(delete_stmt)
        await db.commit()  # Commit the delete before inserting
        
        logger.info(
            f"Deleted {result.rowcount} old content references for document {document_id}"
        )
        
        # Bulk insert all new references (enterprise feature: database tracking)
        db.add_all(references_to_insert)
        await db.commit()
        
        logger.info(
            f"Successfully created {len(embeddings)} invisible embeddings for document {document_id}"
        )
        
        return embeddings
    
    async def verify_and_extract_embedding(
        self,
        db: AsyncSession,
        text: str,
        public_key_provider
    ) -> Optional[Tuple[ContentReference, Dict[str, Any]]]:
        """
        Extract and verify invisible embedding from text using encypher-ai.
        
        Enterprise features:
        - Looks up Merkle tree reference in database
        - Checks expiration
        - Returns enterprise metadata (organization, document, etc.)
        
        Args:
            db: Database session
            text: Text with invisible embedding
            public_key_provider: Function to get public key by signer_id
        
        Returns:
            Tuple of (ContentReference, verified_metadata) if valid, None otherwise
        """
        try:
            # Use encypher-ai to verify and extract metadata
            is_valid, signer_id, payload = UnicodeMetadata.verify_metadata(
                text=text,
                public_key_provider=public_key_provider
            )
            
            if not is_valid or not payload:
                logger.warning("Invalid or missing embedding in text")
                return None
            
            # Extract enterprise metadata from custom_metadata
            custom_metadata = payload.custom_metadata or {}
            document_id = custom_metadata.get('document_id')
            organization_id = custom_metadata.get('organization_id')
            leaf_index = custom_metadata.get('leaf_index')
            
            if not all([document_id, organization_id, leaf_index is not None]):
                logger.warning("Missing enterprise metadata in embedding")
                return None
            
            # Look up ContentReference in database (enterprise feature)
            result = await db.execute(
                select(ContentReference).where(
                    ContentReference.document_id == document_id,
                    ContentReference.organization_id == organization_id,
                    ContentReference.leaf_index == leaf_index
                )
            )
            reference = result.scalar_one_or_none()
            
            if not reference:
                logger.warning(
                    f"Reference not found in database: doc={document_id}, "
                    f"org={organization_id}, leaf={leaf_index}"
                )
                return None
            
            # Check expiration (enterprise feature)
            if reference.expires_at and reference.expires_at < time.time():
                logger.warning(f"Reference expired: {document_id}")
                return None
            
            logger.info(
                f"Successfully verified invisible embedding: doc={document_id}, "
                f"leaf={leaf_index}"
            )
            
            # Return reference and verified metadata
            verified_metadata = {
                'signer_id': signer_id,
                'timestamp': payload.timestamp,
                'custom_metadata': custom_metadata,
                'format': payload.format,
                'version': payload.version
            }
            
            return reference, verified_metadata
            
        except Exception as e:
            logger.error(f"Error verifying embedding: {e}", exc_info=True)
            return None
    
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
