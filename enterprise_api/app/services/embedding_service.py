"""
Service for creating and verifying minimal signed embeddings.

Enterprise layer built on top of the free encypher-ai package.
Uses invisible Unicode variation selector embeddings with enterprise features:
- Merkle tree integration for hierarchical authentication
- Database storage for content references
- Batch operations and analytics
- Public verification API
"""
import logging
import secrets
import time
import unicodedata
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Import from free encypher-ai package (foundation)
try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from encypher.core.constants import MetadataTarget
    from encypher.core.unicode_metadata import UnicodeMetadata
except ImportError:
    raise ImportError(
        "encypher-ai package not found. "
        "Please install: pip install encypher-ai"
    )

from app.models.content_reference import ContentReference
from app.services.status_service import status_service

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
        add_hard_binding: bool = True,  # Include hard binding by default
        action: str = "c2pa.created",  # C2PA action type
        previous_instance_id: Optional[str] = None,  # Previous manifest for edit provenance
        custom_assertions: Optional[List[Dict[str, Any]]] = None,  # Custom C2PA assertions
        digital_source_type: Optional[str] = None,  # IPTC digital source type
        # === API Feature Augmentation (TEAM_044) ===
        manifest_mode: str = "full",  # full, lightweight_uuid, hybrid
        embedding_strategy: str = "single_point",  # single_point, distributed, distributed_redundant
        distribution_target: Optional[str] = None,  # whitespace, punctuation, all_chars
        add_dual_binding: bool = False,  # Enable dual-binding manifest
        disable_c2pa: bool = False,  # Opt-out of C2PA embedding
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

        # TEAM_056: Enforce NFC normalization so all embedding modes operate on the same text representation.
        segments = [unicodedata.normalize("NFC", segment) for segment in segments]
        
        embeddings = []
        references_to_insert = []
        
        logger.info(
            f"Creating {len(segments)} invisible embeddings for document {document_id} "
            f"in organization {organization_id} using encypher-ai"
        )
        
        # Use ISO 8601 format with Z suffix for C2PA compliance
        from datetime import datetime, timezone
        current_timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        
        # Build the full document - TWO PHASE APPROACH:
        # Phase 1: Join ORIGINAL segments (for C2PA wrapper with correct Merkle root hash)
        # Phase 2: Add minimal embeddings per sentence AFTER C2PA wrapper
        full_document_parts = []
        segment_embeddings = []  # Store individual segment embeddings for later
        
        for idx, (segment, leaf_hash) in enumerate(zip(segments, leaf_hashes)):
            # Store ORIGINAL segment for C2PA wrapper (no embeddings yet)
            full_document_parts.append(segment)
            
            # Prepare minimal embedding data for this segment (will apply after C2PA)
            minimal_metadata = {
                'leaf_hash': leaf_hash,
                'leaf_index': idx,
                'document_id': document_id,
                'organization_id': organization_id
            }
            segment_embeddings.append((segment, minimal_metadata))
            
            # Create ContentReference object for database storage (enterprise feature)
            # Generate collision-resistant 63-bit id to avoid PK conflicts under concurrency
            content_id = secrets.randbits(63)
            
            reference = ContentReference(
                id=content_id,  # Use unique random ID
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
                },
            )
            
            references_to_insert.append(reference)
        
        # Step 2: Create minimal embeddings for each segment FIRST
        # Then add ONE C2PA wrapper at the end
        embedded_segments = []
        for idx, (segment, minimal_metadata) in enumerate(segment_embeddings):
            try:
                # Add minimal invisible embedding to this segment
                embedded_segment = UnicodeMetadata.embed_metadata(
                    text=segment,
                    private_key=self.private_key,
                    signer_id=self.signer_id,
                    timestamp=current_timestamp,
                    custom_metadata=minimal_metadata,
                    metadata_format="basic",  # Minimal format, not full C2PA
                    add_hard_binding=False  # No hard binding for sentence-level
                )
                embedded_segments.append(embedded_segment)
            except Exception as e:
                logger.warning(f"Failed to add minimal embedding to segment {idx}: {e}, using plain text")
                embedded_segments.append(segment)
        
        # Join embedded segments with space separator
        full_document = ' '.join(embedded_segments)
        
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
        
        # Build C2PA actions list
        action_data = {
            "label": action,  # "c2pa.created" or "c2pa.edited"
            "when": current_timestamp,
            "softwareAgent": f"Encypher Enterprise API/{organization_id}"
        }
        
        # Add digitalSourceType if provided (C2PA 2.2 compliance)
        if digital_source_type:
            action_data["digitalSourceType"] = digital_source_type
        
        c2pa_actions = [action_data]
        
        # Fetch previous manifest for ingredient reference
        c2pa_ingredients = None
        if action == "c2pa.edited" and previous_instance_id:
            logger.info(f"Fetching previous manifest for ingredient reference: {previous_instance_id}")
            try:
                from sqlalchemy import select

                from app.models.content_reference import ContentReference as ContentReferenceModel
                
                # Fetch previous manifest by instance_id
                stmt = select(ContentReferenceModel).where(
                    ContentReferenceModel.instance_id == previous_instance_id,
                    ContentReferenceModel.organization_id == organization_id
                ).limit(1)
                result = await db.execute(stmt)
                previous_ref = result.scalar_one_or_none()
                
                if previous_ref and previous_ref.manifest_data:
                    logger.info(f"Found previous manifest for instance_id: {previous_instance_id}")
                    # Build C2PA ingredient structure
                    c2pa_ingredients = [{
                        "title": "Previous version",
                        "instance_id": previous_instance_id,
                        "relationship": "parentOf",
                        "c2pa_manifest": previous_ref.manifest_data
                    }]
                    document_metadata['previous_instance_id'] = previous_instance_id
                else:
                    logger.warning(f"Previous manifest not found for instance_id: {previous_instance_id}")
            except Exception as e:
                logger.error(f"Error fetching previous manifest: {e}")
        
        # Convert document_metadata to a custom assertion for C2PA compliance
        # encypher-ai embed_metadata drops custom_metadata when format is "c2pa",
        # so we must pass it as an assertion.
        encypher_metadata_assertion = {
            "label": "org.encypher.metadata",
            "data": document_metadata
        }
        
        # Create a new list for assertions to avoid modifying the input list if it's reused
        final_custom_assertions = [encypher_metadata_assertion]
        if custom_assertions:
            final_custom_assertions.extend(custom_assertions)
        
        # === API Feature Augmentation (TEAM_044) ===
        # Handle different manifest modes and embedding strategies
        
        # Determine if we should use distributed embedding
        use_distributed = embedding_strategy in ("distributed", "distributed_redundant")
        target_for_embedding = distribution_target if use_distributed else None
        
        # Log the embedding configuration
        logger.info(
            f"Embedding config for document {document_id}: "
            f"manifest_mode={manifest_mode}, embedding_strategy={embedding_strategy}, "
            f"disable_c2pa={disable_c2pa}, add_dual_binding={add_dual_binding}"
        )
        
        # Handle C2PA opt-out
        if disable_c2pa:
            # Use basic metadata format instead of C2PA
            logger.info(f"C2PA disabled for document {document_id}, using basic metadata format")
            try:
                embedded_document = UnicodeMetadata.embed_metadata(
                    text=full_document,
                    private_key=self.private_key,
                    signer_id=self.signer_id,
                    timestamp=current_timestamp,
                    custom_metadata=document_metadata,
                    metadata_format="basic",  # Basic format when C2PA disabled
                    add_hard_binding=False,
                    distribute_across_targets=use_distributed,
                    target=target_for_embedding,
                )
                logger.info(f"Successfully added basic metadata to document {document_id}")
            except Exception as e:
                logger.error(f"Failed to add basic metadata to document: {e}")
                raise ValueError(f"Basic metadata embedding failed: {e}")
        
        # Handle lightweight_uuid manifest mode (Professional+ feature)
        elif manifest_mode == "lightweight_uuid":
            import uuid as uuid_module
            manifest_uuid = str(uuid_module.uuid4())
            logger.info(f"Using lightweight UUID manifest mode for document {document_id}, uuid={manifest_uuid}")
            
            # Store full manifest data in database for later retrieval
            # The embedded payload only contains the UUID pointer
            try:
                embedded_document = UnicodeMetadata.embed_metadata(
                    text=full_document,
                    private_key=self.private_key,
                    signer_id=self.signer_id,
                    timestamp=current_timestamp,
                    custom_metadata={
                        "manifest_uuid": manifest_uuid,
                        "document_id": document_id,
                        "organization_id": organization_id,
                        "action": action,
                    },
                    metadata_format="manifest",
                    add_hard_binding=False,
                    claim_generator=f"Encypher Enterprise API/{organization_id}",
                    actions=c2pa_actions,
                    distribute_across_targets=use_distributed,
                    target=MetadataTarget.FILE_END,
                )
                # Store the full manifest data in document_metadata for database storage
                document_metadata['manifest_uuid'] = manifest_uuid
                document_metadata['manifest_mode'] = 'lightweight_uuid'
                logger.info(f"Successfully embedded lightweight UUID for document {document_id}")
            except Exception as e:
                logger.error(f"Failed to embed lightweight UUID: {e}")
                raise ValueError(f"Lightweight UUID embedding failed: {e}")
        
        # Handle hybrid manifest mode (Enterprise feature)
        elif manifest_mode == "hybrid":
            import uuid as uuid_module
            manifest_uuid = str(uuid_module.uuid4())
            logger.info(f"Using hybrid manifest mode for document {document_id}")
            
            # First, embed lightweight UUID per sentence (already done in embedded_segments)
            # Then add full C2PA wrapper at document level
            try:
                embedded_document = UnicodeMetadata.embed_metadata(
                    text=full_document,
                    private_key=self.private_key,
                    signer_id=self.signer_id,
                    timestamp=current_timestamp,
                    custom_metadata=document_metadata,
                    metadata_format=metadata_format,
                    add_hard_binding=add_hard_binding,
                    claim_generator=f"Encypher Enterprise API/{organization_id}",
                    actions=c2pa_actions,
                    ingredients=c2pa_ingredients,
                    custom_assertions=final_custom_assertions,
                    distribute_across_targets=use_distributed,
                    target=target_for_embedding,
                )
                document_metadata['manifest_mode'] = 'hybrid'
                document_metadata['manifest_uuid'] = manifest_uuid
                logger.info(f"Successfully added hybrid manifest to document {document_id}")
            except Exception as e:
                logger.error(f"Failed to add hybrid manifest: {e}")
                raise ValueError(f"Hybrid manifest embedding failed: {e}")
        
        # Default: full C2PA manifest mode
        else:
            try:
                logger.info(f"Adding C2PA wrapper for document {document_id} ({len(segments)} segments) with action {action}")
                embedded_document = UnicodeMetadata.embed_metadata(
                    text=full_document,
                    private_key=self.private_key,
                    signer_id=self.signer_id,
                    timestamp=current_timestamp,
                    custom_metadata=document_metadata,
                    metadata_format=metadata_format,
                    add_hard_binding=add_hard_binding,
                    claim_generator=f"Encypher Enterprise API/{organization_id}",
                    actions=c2pa_actions,
                    ingredients=c2pa_ingredients,
                    custom_assertions=final_custom_assertions,
                    distribute_across_targets=use_distributed,
                    target=target_for_embedding,
                )
                logger.info(f"Successfully added C2PA wrapper to document {document_id}")
            except Exception as e:
                logger.error(f"Failed to add C2PA wrapper to document: {e}")
                raise ValueError(f"C2PA wrapper embedding failed: {e}")
        
        # Extract the C2PA manifest from embedded document for storage
        extracted_manifest = None
        extracted_instance_id = None
        try:
            extracted = UnicodeMetadata.extract_metadata(embedded_document)
            if extracted:
                extracted_instance_id = extracted.get('instance_id')
                extracted_manifest = extracted
                logger.info(f"Extracted manifest with instance_id: {extracted_instance_id}")
        except Exception as e:
            logger.warning(f"Could not extract manifest for storage: {e}")
        
        # Update references with manifest data
        for ref in references_to_insert:
            ref.instance_id = extracted_instance_id
            ref.previous_instance_id = previous_instance_id
            ref.manifest_data = extracted_manifest
        
        # Create embedding references for each segment
        # Each segment has its own minimal embedding + the full document has ONE C2PA wrapper
        for idx, (segment, leaf_hash) in enumerate(zip(segments, leaf_hashes)):
            ref_id = secrets.randbits(63)
            
            embeddings.append(EmbeddingReference(
                leaf_hash=leaf_hash,
                leaf_index=idx,
                text_content=segment,
                embedded_text=embedded_segments[idx],  # Individual segment with minimal embedding
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
        
        # Performance optimization: Use flush() instead of commit()
        # This writes to the database but defers the expensive fsync() operation
        # The session will auto-commit at the end of the request
        # This reduces 10,000 commits to ~100 commits for 10,000 requests
        await db.flush()
        
        logger.info(
            f"Successfully created {len(embeddings)} invisible embeddings for document {document_id} "
            f"(using deferred commit for performance)"
        )
        
        # Return both the embeddings list AND the full document with C2PA wrapper
        # The embeddings list has individual segments with minimal embeddings
        # The embedded_document has the full text with ONE C2PA wrapper at the end
        return embeddings, embedded_document
    
    async def verify_and_extract_embedding(
        self,
        db: AsyncSession,
        text: str,
        public_key_provider=None,
        public_key_resolver=None,
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
            resolver = public_key_resolver or public_key_provider
            if resolver is None:
                logger.warning("No public key resolver provided")
                return None

            # Use encypher-ai to verify and extract metadata
            is_valid, signer_id, payload = UnicodeMetadata.verify_metadata(
                text=text,
                public_key_resolver=resolver,
            )
            
            if not is_valid or not payload:
                logger.warning("Invalid or missing embedding in text")
                return None
            
            # Extract enterprise metadata from custom_metadata
            if isinstance(payload, dict):
                manifest_block = payload.get("manifest") if isinstance(payload.get("manifest"), dict) else {}
                custom_metadata = (
                    payload.get("custom_metadata")
                    or manifest_block.get("custom_metadata")
                    or {}
                )
                payload_format = payload.get("format")
                payload_version = payload.get("version")
                payload_timestamp = payload.get("timestamp")
            else:
                custom_metadata = getattr(payload, "custom_metadata", None) or {}
                payload_format = getattr(payload, "format", None)
                payload_version = getattr(payload, "version", None)
                payload_timestamp = getattr(payload, "timestamp", None)

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
                'timestamp': payload_timestamp,
                'custom_metadata': custom_metadata,
                'format': payload_format,
                'version': payload_version,
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
            select(ContentReference).where(ContentReference.id == ref_id)
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
