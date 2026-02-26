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
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, cast
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Import from free encypher-ai package (foundation)
try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from encypher.core.constants import MetadataTarget
    from encypher.core.unicode_metadata import UnicodeMetadata
except ImportError:
    raise ImportError("encypher-ai package not found. Please install: pip install encypher-ai")

from app.models.content_reference import ContentReference
from app.utils.embedding_signature import compute_signature_hash
from app.services.status_service import status_service
from app.utils.zw_crypto import (
    create_minimal_signed_uuid,
    derive_signing_key_from_private_key,
    embed_signature_safely,
)

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
            "leaf_index": self.leaf_index,
            "leaf_hash": self.leaf_hash,
            "text_content": self.text_content,
            "embedded_text": self.embedded_text,
            "document_id": self.document_id,
            "has_invisible_embedding": True,
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

    @staticmethod
    def _get_api_version() -> str:
        """Get the enterprise-api version for claim_generator."""
        from app import __version__

        return __version__

    @staticmethod
    def _reconstruct_with_separators(
        original_text: str,
        segments: List[str],
        embedded_segments: List[str],
    ) -> str:
        """Reconstruct the full document preserving original inter-segment whitespace.

        Sentence segmentation produces spans that exclude the whitespace (including
        blank lines / \\n\\n) between them.  Joining with a plain space discards those
        separators, which breaks ATX heading detection in Markdown renderers.  This
        helper locates each segment in the NFC-normalised original text and re-inserts
        whatever was between adjacent segment spans so block structure is preserved.
        """
        if not segments:
            return ""

        normalised = unicodedata.normalize("NFC", original_text)
        result: list[str] = []
        pos = 0

        for orig, emb in zip(segments, embedded_segments):
            seg_pos = normalised.find(orig, pos)
            if seg_pos == -1:
                # Fallback: segment not found verbatim - append with a space separator
                if result:
                    result.append(" ")
                result.append(emb)
                continue
            # Preserve any content (whitespace/newlines) between previous end and this segment
            if seg_pos > pos:
                result.append(normalised[pos:seg_pos])
            result.append(emb)
            pos = seg_pos + len(orig)

        # Preserve any trailing content after the last segment
        if pos < len(normalised):
            result.append(normalised[pos:])

        return "".join(result)

    async def create_embeddings(
        self,
        db: AsyncSession,
        organization_id: str,
        document_id: str,
        merkle_root_id: Optional[UUID],
        segments: List[str],
        leaf_hashes: List[str],
        merkle_root_hash: Optional[str] = None,
        merkle_segmentation_level: Optional[str] = None,
        c2pa_manifest_url: Optional[str] = None,
        c2pa_manifest_hash: Optional[str] = None,
        license_info: Optional[Dict[str, Optional[str]]] = None,
        expires_at: Optional[datetime] = None,
        metadata_format: str = "c2pa",  # C2PA-compliant by default
        add_hard_binding: bool = True,  # Include hard binding by default
        action: str = "c2pa.created",  # C2PA action type
        previous_instance_id: Optional[str] = None,  # Previous manifest for edit provenance
        custom_assertions: Optional[List[Dict[str, Any]]] = None,  # Custom C2PA assertions
        digital_source_type: Optional[str] = None,  # IPTC digital source type
        # === API Feature Augmentation (TEAM_044) ===
        manifest_mode: str = "full",  # full, lightweight_uuid, minimal_uuid, hybrid, micro
        ecc: bool = True,  # Reed-Solomon error correction for micro mode
        embed_c2pa: bool = True,  # Embed C2PA manifest in content for micro mode
        embedding_strategy: str = "single_point",  # single_point, distributed, distributed_redundant
        distribution_target: Optional[str] = None,  # whitespace, punctuation, all_chars
        add_dual_binding: bool = False,  # Enable dual-binding manifest
        disable_c2pa: bool = False,  # Opt-out of C2PA embedding
        store_c2pa_manifest: bool = True,  # Persist extracted C2PA manifest in DB
        processing_metadata: Optional[Dict[str, Any]] = None,
        organization_name: Optional[str] = None,
        original_text: Optional[str] = None,  # Original unsegmented document text for separator-preserving reconstruction
    ) -> Tuple[List[EmbeddingReference], str]:
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
            merkle_root_hash: Optional Merkle root hash for linkage/assertions
            merkle_segmentation_level: Optional segmentation level for Merkle linkage
            segments: List of text segments (sentences)
            leaf_hashes: List of leaf hashes (same order as segments)
            c2pa_manifest_url: Optional C2PA manifest URL
            c2pa_manifest_hash: Optional C2PA manifest hash
            license_info: Optional license information dict
            expires_at: Optional expiration datetime
            metadata_format: Format for embeddings ("c2pa" by default, "basic" for minimal)
            add_hard_binding: Include c2pa.hash.data assertion (True by default)

        Returns:
            Tuple of (embedding references, embedded document)

        Raises:
            ValueError: If segments and leaf_hashes lengths don't match
        """
        if len(segments) != len(leaf_hashes):
            raise ValueError(f"Segments ({len(segments)}) and leaf_hashes ({len(leaf_hashes)}) must have same length")

        # TEAM_056: Enforce NFC normalization so all embedding modes operate on the same text representation.
        segments = [unicodedata.normalize("NFC", segment) for segment in segments]

        embeddings = []
        references_to_insert = []

        logger.info(f"Creating {len(segments)} invisible embeddings for document {document_id} in organization {organization_id} using encypher-ai")

        # Use ISO 8601 format with Z suffix for C2PA compliance
        from datetime import datetime, timezone

        current_timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        # Build the full document - TWO PHASE APPROACH:
        # Phase 1: Join ORIGINAL segments (for C2PA wrapper with correct Merkle root hash)
        # Phase 2: Add minimal embeddings per sentence AFTER C2PA wrapper
        per_segment_uuid_mode = manifest_mode == "minimal_uuid"
        full_document_parts = []
        segment_embeddings: list[tuple[str, Dict[str, Any]]] = []  # Store individual segment embeddings for later

        for idx, (segment, leaf_hash) in enumerate(zip(segments, leaf_hashes)):
            # Store ORIGINAL segment for C2PA wrapper (no embeddings yet)
            full_document_parts.append(segment)

            # Prepare minimal embedding data for this segment (will apply after C2PA)
            minimal_metadata: Dict[str, Any]
            if per_segment_uuid_mode:
                manifest_uuid = str(uuid.uuid4())
                minimal_metadata = {"manifest_uuid": manifest_uuid}
            else:
                minimal_metadata = {
                    "leaf_hash": leaf_hash,
                    "leaf_index": idx,
                    "document_id": document_id,
                    "organization_id": organization_id,
                }
            segment_embeddings.append((segment, minimal_metadata))

            # Create ContentReference object for database storage (enterprise feature)
            # Generate collision-resistant 63-bit id to avoid PK conflicts under concurrency
            content_id = secrets.randbits(63)

            embedding_metadata = {
                "version": "v1",
                "created_by": "embedding_service",
                "uses_encypher_ai": True,
                "signer_id": self.signer_id,
            }
            if merkle_root_id:
                embedding_metadata["merkle_root_id"] = str(merkle_root_id)
            if merkle_root_hash:
                embedding_metadata["merkle_root_hash"] = merkle_root_hash
            if merkle_segmentation_level:
                embedding_metadata["merkle_segmentation_level"] = merkle_segmentation_level
            if processing_metadata:
                embedding_metadata["processing"] = processing_metadata
            if per_segment_uuid_mode:
                embedding_metadata["manifest_uuid"] = minimal_metadata.get("manifest_uuid")
                embedding_metadata["manifest_mode"] = "minimal_uuid"

            reference = ContentReference(
                id=content_id,  # Use unique random ID
                merkle_root_id=merkle_root_id,
                leaf_hash=leaf_hash,
                leaf_index=idx,
                organization_id=organization_id,
                document_id=document_id,
                text_content=None,
                text_preview=None,
                signature_hash=compute_signature_hash(content_id),
                c2pa_manifest_url=c2pa_manifest_url,
                c2pa_manifest_hash=c2pa_manifest_hash,
                license_type=license_info.get("type") if license_info else None,
                license_url=license_info.get("url") if license_info else None,
                expires_at=expires_at,
                embedding_metadata=embedding_metadata,
            )

            references_to_insert.append(reference)

        # Step 2: Create minimal embeddings for each segment FIRST
        # Then add ONE C2PA wrapper at the end
        # NOTE: Skip this for zw_embedding/micro modes (they handle embeddings in their own branches)
        # TEAM_088: Skip per-segment basic embeddings for document-level signing
        # (single segment = entire document). The C2PA wrapper already covers the
        # whole document, and the basic embedding's default WHITESPACE target
        # inserts invisible characters mid-text instead of at the end.
        is_document_level = len(segments) == 1
        embedded_segments = []
        if manifest_mode in ("zw_embedding", "micro"):
            # For zw_embedding, use original segments (embeddings added in their own branches)
            embedded_segments = segments
        elif is_document_level:
            # Document-level: skip per-segment basic embedding; C2PA wrapper suffices
            embedded_segments = list(segments)
        else:
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
                        add_hard_binding=False,  # No hard binding for sentence-level
                    )
                    embedded_segments.append(embedded_segment)
                except Exception as e:
                    logger.warning(f"Failed to add minimal embedding to segment {idx}: {e}, using plain text")
                    embedded_segments.append(segment)

        # TEAM_088: For document-level signing, preserve original text structure
        # (newlines, paragraph breaks) instead of joining with spaces.
        if is_document_level:
            full_document = embedded_segments[0]
        else:
            # Join embedded segments with space separator
            full_document = " ".join(embedded_segments)

        # Create document-level metadata
        document_metadata: Dict[str, Any] = {
            "document_id": document_id,
            "organization_id": organization_id,
            "merkle_root_id": str(merkle_root_id) if merkle_root_id else None,
            "merkle_root_hash": merkle_root_hash,
            "merkle_segmentation_level": merkle_segmentation_level,
            "total_segments": len(segments),
            "manifest_mode": manifest_mode,
        }
        if processing_metadata:
            document_metadata["processing"] = processing_metadata

        if c2pa_manifest_url:
            document_metadata["c2pa_manifest_url"] = c2pa_manifest_url

        if license_info:
            document_metadata["license"] = license_info

        document_metadata_jsonld: Dict[str, Any] = {
            "@context": "https://schema.org",
            "@type": "CreativeWork",
            "identifier": document_id,
            "name": document_id,
            "publisher": {
                "@type": "Organization",
                "identifier": organization_name or organization_id,
            },
        }
        if license_info and license_info.get("url"):
            document_metadata_jsonld["license"] = license_info.get("url")
        if c2pa_manifest_url:
            document_metadata_jsonld["url"] = c2pa_manifest_url

        # Build C2PA actions list
        action_data = {
            "label": action,  # "c2pa.created" or "c2pa.edited"
            "when": current_timestamp,
            "softwareAgent": "Encypher Enterprise API",
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
                stmt = (
                    select(ContentReferenceModel)
                    .where(ContentReferenceModel.instance_id == previous_instance_id, ContentReferenceModel.organization_id == organization_id)
                    .limit(1)
                )
                result = await db.execute(stmt)
                previous_ref = result.scalar_one_or_none()

                if previous_ref and previous_ref.manifest_data:
                    logger.info(f"Found previous manifest for instance_id: {previous_instance_id}")
                    # Build C2PA ingredient structure
                    c2pa_ingredients = [
                        {
                            "title": "Previous version",
                            "instance_id": previous_instance_id,
                            "relationship": "inputTo",
                            "c2pa_manifest": previous_ref.manifest_data,
                        }
                    ]
                    document_metadata["previous_instance_id"] = previous_instance_id
                    document_metadata_jsonld["isBasedOn"] = {
                        "@type": "CreativeWork",
                        "identifier": previous_instance_id,
                    }
                else:
                    logger.warning(f"Previous manifest not found for instance_id: {previous_instance_id}")
            except Exception as e:
                logger.error(f"Error fetching previous manifest: {e}")

        # Create a new list for assertions to avoid modifying the input list if it's reused
        final_custom_assertions = list(custom_assertions) if custom_assertions else []

        if merkle_root_hash:
            merkle_assertion_data: Dict[str, Any] = {
                "root_hash": merkle_root_hash,
                "total_segments": len(segments),
            }
            if merkle_root_id:
                merkle_assertion_data["root_id"] = str(merkle_root_id)
            if merkle_segmentation_level:
                merkle_assertion_data["segmentation_level"] = merkle_segmentation_level

            has_merkle_assertion = any(
                isinstance(assertion, dict) and assertion.get("label") == "com.encypher.merkle.v1"
                for assertion in final_custom_assertions
            )
            if not has_merkle_assertion:
                final_custom_assertions.append(
                    {
                        "label": "com.encypher.merkle.v1",
                        "data": merkle_assertion_data,
                    }
                )

        # === API Feature Augmentation (TEAM_044) ===
        # Handle different manifest modes and embedding strategies

        # Determine if we should use distributed embedding
        use_distributed = embedding_strategy in ("distributed", "distributed_redundant")
        target_for_embedding = distribution_target if use_distributed else None

        # Log the embedding configuration
        logger.info(
            f"Embedding config for document {document_id}: "
            f"manifest_mode={manifest_mode}, ecc={ecc}, embed_c2pa={embed_c2pa}, "
            f"embedding_strategy={embedding_strategy}, "
            f"disable_c2pa={disable_c2pa}, add_dual_binding={add_dual_binding}, "
            f"store_c2pa_manifest={store_c2pa_manifest}"
        )

        # Handle C2PA opt-out
        if disable_c2pa:
            if per_segment_uuid_mode:
                logger.info(
                    "C2PA disabled for document %s; skipping document-level manifest for minimal_uuid",
                    document_id,
                )
                embedded_document = full_document
            else:
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
            manifest_uuid = str(uuid.uuid4())
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
                    claim_generator=f"encypher-enterprise-api/{self._get_api_version()}",
                    actions=c2pa_actions,
                    custom_assertions=final_custom_assertions,
                    distribute_across_targets=use_distributed,
                    target=MetadataTarget.FILE_END,
                )
                # Store the full manifest data in document_metadata for database storage
                document_metadata["manifest_uuid"] = manifest_uuid
                document_metadata["manifest_mode"] = "lightweight_uuid"
                logger.info(f"Successfully embedded lightweight UUID for document {document_id}")
            except Exception as e:
                logger.error(f"Failed to embed lightweight UUID: {e}")
                raise ValueError(f"Lightweight UUID embedding failed: {e}")

        # Handle minimal_uuid manifest mode (Professional+ feature)
        elif manifest_mode == "minimal_uuid":
            logger.info(
                "Using minimal UUID manifest mode for document %s with per-segment UUID pointers",
                document_id,
            )

            try:
                embedded_document = UnicodeMetadata.embed_metadata(
                    text=full_document,
                    private_key=self.private_key,
                    signer_id=self.signer_id,
                    timestamp=current_timestamp,
                    custom_metadata=document_metadata_jsonld,
                    metadata_format=metadata_format,
                    add_hard_binding=add_hard_binding,
                    claim_generator=f"encypher-enterprise-api/{self._get_api_version()}",
                    actions=c2pa_actions,
                    ingredients=c2pa_ingredients,
                    custom_assertions=final_custom_assertions,
                    distribute_across_targets=use_distributed,
                    target=target_for_embedding,
                )
                logger.info(f"Successfully added C2PA wrapper to minimal_uuid document {document_id}")
            except Exception as e:
                logger.error(f"Failed to embed minimal UUID with C2PA wrapper: {e}")
                raise ValueError(f"Minimal UUID embedding failed: {e}")

        # Handle hybrid manifest mode (Enterprise feature)
        elif manifest_mode == "hybrid":
            manifest_uuid = str(uuid.uuid4())
            logger.info(f"Using hybrid manifest mode for document {document_id}")

            # First, embed lightweight UUID per sentence (already done in embedded_segments)
            # Then add full C2PA wrapper at document level
            try:
                embedded_document = UnicodeMetadata.embed_metadata(
                    text=full_document,
                    private_key=self.private_key,
                    signer_id=self.signer_id,
                    timestamp=current_timestamp,
                    custom_metadata=document_metadata_jsonld,
                    metadata_format=metadata_format,
                    add_hard_binding=add_hard_binding,
                    claim_generator=f"encypher-enterprise-api/{self._get_api_version()}",
                    actions=c2pa_actions,
                    ingredients=c2pa_ingredients,
                    custom_assertions=final_custom_assertions,
                    distribute_across_targets=use_distributed,
                    target=target_for_embedding,
                )
                document_metadata["manifest_mode"] = "hybrid"
                document_metadata["manifest_uuid"] = manifest_uuid
                logger.info(f"Successfully added hybrid manifest to document {document_id}")
            except Exception as e:
                logger.error(f"Failed to add hybrid manifest: {e}")
                raise ValueError(f"Hybrid manifest embedding failed: {e}")

        # Handle zw_embedding manifest mode (Word-compatible, 132 chars/sentence)
        elif manifest_mode == "zw_embedding":
            logger.info(
                "Using zw_embedding manifest mode for document %s with Word-compatible signatures",
                document_id,
            )

            try:
                # Derive HMAC signing key from org's private key
                signing_key = derive_signing_key_from_private_key(self.private_key)

                # Build document with ZW signatures per segment
                zw_embedded_segments = []
                for idx, (segment, leaf_hash) in enumerate(zip(segments, leaf_hashes)):
                    # Generate UUID for this segment
                    segment_uuid = uuid.uuid4()

                    # Create minimal signed UUID (132 chars, Word-compatible)
                    zw_signature = create_minimal_signed_uuid(segment_uuid, signing_key)

                    # Embed signature safely (before terminal punctuation)
                    embedded_segment = embed_signature_safely(segment, zw_signature)
                    zw_embedded_segments.append(embedded_segment)

                    # Update the reference with ZW-specific metadata
                    if idx < len(references_to_insert):
                        ref_any = cast(Any, references_to_insert[idx])
                        if hasattr(ref_any, "embedding_metadata"):
                            ref_any.embedding_metadata = ref_any.embedding_metadata or {}
                            ref_any.embedding_metadata["manifest_mode"] = "zw_embedding"
                            ref_any.embedding_metadata["segment_uuid"] = str(segment_uuid)
                            ref_any.embedding_metadata["zw_signature_length"] = len(zw_signature)

                # Join segments to form embedded document (no C2PA wrapper)
                embedded_document = " ".join(zw_embedded_segments)
                document_metadata["manifest_mode"] = "zw_embedding"
                document_metadata["zw_encoding"] = "base4_word_safe"
                document_metadata["signature_chars_per_segment"] = 132

                logger.info(
                    f"Successfully embedded ZW signatures for document {document_id}: "
                    f"{len(segments)} segments, 132 chars each"
                )
            except Exception as e:
                logger.error(f"Failed to embed ZW signatures: {e}")
                raise ValueError(f"ZW embedding failed: {e}")

        # TEAM_166: Unified "micro" manifest mode — flag-driven.
        # Two orthogonal flags control behaviour:
        #   ecc=True  → Reed-Solomon error correction (44 chars, default)
        #   ecc=False → plain HMAC (36 chars)
        #   embed_c2pa=True  → full C2PA document manifest embedded in content (default)
        #   embed_c2pa=False → per-sentence markers only; C2PA manifest DB-only
        # A C2PA-compatible manifest is ALWAYS generated and extracted.
        # store_c2pa_manifest controls DB persistence; embed_c2pa controls in-content embedding.
        elif manifest_mode == "micro":
            use_ecc = ecc
            use_embed_c2pa = embed_c2pa
            chars_per_segment = 44 if use_ecc else 36

            logger.info(
                "Using micro manifest mode for document %s (ecc=%s, embed_c2pa=%s, %d chars/segment)",
                document_id, use_ecc, use_embed_c2pa, chars_per_segment,
            )

            try:
                # --- Phase 1: Import the appropriate crypto module ---
                if use_ecc:
                    from app.utils.vs256_rs_crypto import (
                        create_minimal_signed_uuid as micro_create,
                        derive_signing_key_from_private_key as micro_derive_key,
                        embed_signature_safely as micro_embed_safely,
                    )
                else:
                    from app.utils.vs256_crypto import (
                        create_minimal_signed_uuid as micro_create,
                        derive_signing_key_from_private_key as micro_derive_key,
                        embed_signature_safely as micro_embed_safely,
                    )

                signing_key = micro_derive_key(self.private_key)

                # --- Phase 2: Embed per-sentence markers ---
                micro_embedded_segments = []
                for idx, (segment, leaf_hash) in enumerate(zip(segments, leaf_hashes)):
                    segment_uuid = uuid.uuid4()
                    micro_signature = micro_create(
                        segment_uuid,
                        signing_key,
                        sentence_text=segment,
                    )
                    embedded_segment = micro_embed_safely(segment, micro_signature)
                    micro_embedded_segments.append(embedded_segment)

                    if idx < len(references_to_insert):
                        ref_any = cast(Any, references_to_insert[idx])
                        if hasattr(ref_any, "embedding_metadata"):
                            ref_any.embedding_metadata = ref_any.embedding_metadata or {}
                            ref_any.embedding_metadata["manifest_mode"] = "micro"
                            ref_any.embedding_metadata["segment_uuid"] = str(segment_uuid)
                            ref_any.embedding_metadata["micro_signature_length"] = len(micro_signature)
                            ref_any.embedding_metadata["ecc"] = use_ecc
                            if use_ecc:
                                ref_any.embedding_metadata["rs_parity_symbols"] = 8

                # Reconstruct full document preserving original whitespace (e.g. \n\n before
                # ATX headings).  When original_text is available, use it as the reference
                # for inter-segment separators; otherwise fall back to space-joining.
                if original_text is not None:
                    full_document = EmbeddingService._reconstruct_with_separators(
                        original_text, segments, micro_embedded_segments
                    )
                else:
                    full_document = " ".join(micro_embedded_segments)

                # --- Phase 3: Always generate C2PA manifest ---
                # We always create the manifest via embed_metadata so we can
                # extract it for DB storage.  If embed_c2pa=False we then
                # discard the wrapper from the returned content.
                c2pa_wrapped_document = UnicodeMetadata.embed_metadata(
                    text=full_document,
                    private_key=self.private_key,
                    signer_id=self.signer_id,
                    timestamp=current_timestamp,
                    custom_metadata=document_metadata_jsonld,
                    metadata_format=metadata_format,
                    add_hard_binding=add_hard_binding,
                    claim_generator=f"encypher-enterprise-api/{self._get_api_version()}",
                    actions=c2pa_actions,
                    ingredients=c2pa_ingredients,
                    custom_assertions=final_custom_assertions,
                    distribute_across_targets=use_distributed,
                    target=target_for_embedding,
                )

                # --- Phase 4: Extract C2PA manifest for DB storage ---
                micro_manifest = None
                try:
                    extracted = UnicodeMetadata.extract_metadata(c2pa_wrapped_document)
                    if extracted:
                        micro_manifest = extracted
                except Exception as manifest_err:
                    logger.warning("micro: could not extract manifest for DB storage: %s", manifest_err)

                # Choose what goes into the returned document
                if use_embed_c2pa:
                    embedded_document = c2pa_wrapped_document
                else:
                    embedded_document = full_document

                # --- Phase 5: Compute segment location ---
                from app.utils.segmentation import segment_paragraphs, segment_sentences

                paragraphs = segment_paragraphs("\n\n".join(segments))
                sentence_location: dict[int, dict[str, int]] = {}
                global_sent_idx = 0
                for para_idx, para_text in enumerate(paragraphs):
                    para_sentences = segment_sentences(para_text)
                    for sent_in_para, _sent in enumerate(para_sentences):
                        if global_sent_idx < len(segments):
                            sentence_location[global_sent_idx] = {
                                "paragraph_index": para_idx,
                                "sentence_in_paragraph": sent_in_para,
                            }
                        global_sent_idx += 1

                # --- Phase 6: Store manifest + segment location in DB ---
                if store_c2pa_manifest:
                    for idx, ref in enumerate(references_to_insert):
                        ref_any = cast(Any, ref)
                        ref_any.manifest_data = micro_manifest
                        if hasattr(ref_any, "embedding_metadata"):
                            ref_any.embedding_metadata = ref_any.embedding_metadata or {}
                            location = sentence_location.get(idx, {
                                "paragraph_index": 0,
                                "sentence_in_paragraph": idx,
                            })
                            ref_any.embedding_metadata["segment_location"] = location
                            ref_any.embedding_metadata["total_segments"] = len(segments)

                document_metadata["manifest_mode"] = "micro"
                document_metadata["ecc"] = use_ecc
                document_metadata["embed_c2pa"] = use_embed_c2pa
                if use_ecc:
                    document_metadata["micro_encoding"] = "base256_variation_selectors_rs"
                    document_metadata["rs_parity_symbols"] = 8
                else:
                    document_metadata["micro_encoding"] = "base256_variation_selectors"
                document_metadata["signature_chars_per_segment"] = chars_per_segment
                document_metadata["c2pa_manifest_embedded"] = use_embed_c2pa

                logger.info(
                    "Successfully embedded micro markers for document %s: "
                    "%d segments, %d chars each (ecc=%s, embed_c2pa=%s)",
                    document_id, len(segments), chars_per_segment,
                    use_ecc, use_embed_c2pa,
                )
            except Exception as e:
                logger.error("Failed to embed micro markers: %s", e)
                raise ValueError(f"micro embedding failed: {e}")

        # Default: full C2PA manifest mode
        else:
            try:
                logger.info(f"Adding C2PA wrapper for document {document_id} ({len(segments)} segments) with action {action}")
                embedded_document = UnicodeMetadata.embed_metadata(
                    text=full_document,
                    private_key=self.private_key,
                    signer_id=self.signer_id,
                    timestamp=current_timestamp,
                    custom_metadata=document_metadata_jsonld,
                    metadata_format=metadata_format,
                    add_hard_binding=add_hard_binding,
                    claim_generator=f"encypher-enterprise-api/{self._get_api_version()}",
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
                extracted_instance_id = extracted.get("instance_id")
                extracted_manifest = extracted
                logger.info(f"Extracted manifest with instance_id: {extracted_instance_id}")
        except Exception as e:
            logger.warning(f"Could not extract manifest for storage: {e}")

        # Update references with manifest data
        # TEAM_166: micro mode stores manifest_data in its own branch;
        # skip overwriting it here.
        for ref in references_to_insert:
            ref_any = cast(Any, ref)
            ref_any.instance_id = extracted_instance_id
            ref_any.previous_instance_id = previous_instance_id
            if manifest_mode != "micro":
                ref_any.manifest_data = None

            if manifest_mode == "micro" and not store_c2pa_manifest:
                ref_any.manifest_data = None

        # Create embedding references for each segment
        # Each segment has its own minimal embedding + the full document has ONE C2PA wrapper
        for idx, (segment, leaf_hash) in enumerate(zip(segments, leaf_hashes)):
            ref_id = secrets.randbits(63)

            embeddings.append(
                EmbeddingReference(
                    leaf_hash=leaf_hash,
                    leaf_index=idx,
                    text_content=segment,
                    embedded_text=embedded_segments[idx],  # Individual segment with minimal embedding
                    document_id=document_id,
                    ref_id=ref_id,
                )
            )

        # Delete old content references for this document (if re-signing)
        from sqlalchemy import delete

        from app.models.content_reference import ContentReference as ContentReferenceModel

        delete_stmt = delete(ContentReferenceModel).where(
            ContentReferenceModel.document_id == document_id, ContentReferenceModel.organization_id == organization_id
        )
        result = await db.execute(delete_stmt)
        await db.commit()  # Commit the delete before inserting
        deleted_count = int(getattr(result, "rowcount", 0) or 0)
        logger.info(f"Deleted {deleted_count} old content references for document {document_id}")

        # Bulk insert all new references (enterprise feature: database tracking)
        db.add_all(references_to_insert)

        # Performance optimization: Use flush() instead of commit()
        # This writes to the database but defers the expensive fsync() operation
        # The session will auto-commit at the end of the request
        # This reduces 10,000 commits to ~100 commits for 10,000 requests
        await db.flush()

        logger.info(f"Successfully created {len(embeddings)} invisible embeddings for document {document_id} (using deferred commit for performance)")

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
                payload_dict = cast(Dict[str, Any], payload)
                manifest_value = payload_dict.get("manifest")
                manifest_block = cast(Dict[str, Any], manifest_value) if isinstance(manifest_value, dict) else {}
                custom_metadata = payload_dict.get("custom_metadata") or manifest_block.get("custom_metadata") or {}
                payload_format = payload_dict.get("format")
                payload_version = payload_dict.get("version")
                payload_timestamp = payload_dict.get("timestamp")
            else:
                custom_metadata = getattr(payload, "custom_metadata", None) or {}
                payload_format = getattr(payload, "format", None)
                payload_version = getattr(payload, "version", None)
                payload_timestamp = getattr(payload, "timestamp", None)

            if not isinstance(custom_metadata, dict):
                custom_metadata = {}

            manifest_uuid = custom_metadata.get("manifest_uuid")
            if manifest_uuid:
                result = await db.execute(
                    select(ContentReference).where(
                        ContentReference.embedding_metadata["manifest_uuid"].as_string() == manifest_uuid
                    )
                )
                reference = result.scalar_one_or_none()
                if reference:
                    document_id = cast(Optional[str], reference.document_id)
                    organization_id = cast(Optional[str], reference.organization_id)
                    leaf_index = cast(Optional[int], reference.leaf_index)
                else:
                    logger.warning("Reference not found for manifest_uuid=%s", manifest_uuid)
                    return None
            else:
                document_id = cast(Optional[str], custom_metadata.get("document_id"))
                organization_id = cast(Optional[str], custom_metadata.get("organization_id"))
                leaf_index = cast(Optional[int], custom_metadata.get("leaf_index"))

                if not all([document_id, organization_id, leaf_index is not None]):
                    logger.warning("Missing enterprise metadata in embedding")
                    return None

                # Look up ContentReference in database (enterprise feature)
                result = await db.execute(
                    select(ContentReference).where(
                        ContentReference.document_id == document_id,
                        ContentReference.organization_id == organization_id,
                        ContentReference.leaf_index == leaf_index,
                    )
                )
                reference = result.scalar_one_or_none()

            if not reference:
                logger.warning(f"Reference not found in database: doc={document_id}, org={organization_id}, leaf={leaf_index}")
                return None

            # Check expiration (enterprise feature)
            if reference.expires_at and reference.expires_at < time.time():
                logger.warning(f"Reference expired: {document_id}")
                return None

            logger.info(f"Successfully verified invisible embedding: doc={document_id}, leaf={leaf_index}")

            # Return reference and verified metadata
            verified_metadata = {
                "signer_id": signer_id,
                "timestamp": payload_timestamp,
                "custom_metadata": custom_metadata,
                "format": payload_format,
                "version": payload_version,
            }

            return reference, verified_metadata

        except Exception as e:
            logger.error(f"Error verifying embedding: {e}", exc_info=True)
            return None

    async def get_reference_by_id(self, db: AsyncSession, ref_id: int) -> Optional[ContentReference]:
        """
        Get content reference by ID.

        Args:
            db: Database session
            ref_id: Reference ID (integer)

        Returns:
            ContentReference if found, None otherwise
        """
        result = await db.execute(select(ContentReference).where(ContentReference.id == ref_id))
        return result.scalar_one_or_none()

    async def get_references_by_document(self, db: AsyncSession, document_id: str, organization_id: Optional[str] = None) -> List[ContentReference]:
        """
        Get all content references for a document.

        Args:
            db: Database session
            document_id: Document ID
            organization_id: Optional organization ID filter

        Returns:
            List of ContentReference objects
        """
        query = select(ContentReference).where(ContentReference.document_id == document_id)

        if organization_id:
            query = query.where(ContentReference.organization_id == organization_id)

        query = query.order_by(ContentReference.leaf_index)

        result = await db.execute(query)
        return list(result.scalars().all())
