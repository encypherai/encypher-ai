"""
API endpoints for minimal signed embeddings.

Enterprise tier endpoints for creating and managing content embeddings.
Built on top of the free encypher-ai package with enterprise features.
"""

import logging
import time
import unicodedata
from typing import Any, Dict, List, Optional, Union, cast
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.tier_config import is_enterprise_tier
from app.models.merkle import MerkleRoot
from app.schemas.embeddings import (
    EmbeddingInfo,
    EncodeWithEmbeddingsRequest,
    EncodeWithEmbeddingsResponse,
    MerkleTreeInfo,
    MerkleTreeLevelInfo,
)
from app.services.embedding_service import EmbeddingService
from app.services.merkle_service import MerkleService
from app.services.organization_bootstrap import ensure_organization_exists
from app.services.provisioning_service import ProvisioningService
from app.services.status_service import status_service
from app.utils.crypto_utils import load_organization_private_key
from app.utils.quota import QuotaManager, QuotaType
from app.utils.segmentation import build_processing_metadata

logger = logging.getLogger(__name__)


# ============================================================================
# Document Encoding with Embeddings
# ============================================================================


async def encode_document_with_embeddings(
    *,
    request: EncodeWithEmbeddingsRequest,
    organization: Dict,
    core_db: AsyncSession,
    content_db: AsyncSession,
) -> EncodeWithEmbeddingsResponse:
    """
    Encode a document with invisible signed embeddings using encypher-ai.

    Enterprise features:
    - Merkle tree integration for hierarchical authentication
    - Database storage for content tracking
    - Per-sentence invisible embeddings
    - Public verification API

    Args:
    """
    start_time = time.time()
    organization_id = organization["organization_id"]

    document_text = unicodedata.normalize("NFC", request.text)

    try:
        logger.info(
            "Encoding document %s with invisible embeddings for org %s (%s) at %s level",
            request.document_id,
            organization_id,
            organization["organization_name"],
            request.segmentation_level,
        )

        await ensure_organization_exists(core_db, organization)

        if not organization.get("is_demo", False) and not organization_id.startswith("user_"):
            await ProvisioningService._ensure_organization_certificate(
                db=core_db,
                organization_id=organization_id,
                organization_name=organization.get("organization_name") or organization_id,
                authorization=None,
            )

        # Load organization's private key for signing
        # For user-level orgs (is_demo=true), use the demo key
        is_demo = organization.get("is_demo", False)

        if is_demo or organization_id.startswith("user_"):
            # Use demo key for user-level orgs and demo accounts
            from app.utils.crypto_utils import get_demo_private_key

            private_key = get_demo_private_key()
            signer_id = organization_id
            logger.info(f"Using demo key for org {organization_id}")
        else:
            try:
                private_key = await load_organization_private_key(organization_id, core_db)
                # organization_id already has "org_" prefix (e.g., "org_demo")
                signer_id = organization_id
            except ValueError as e:
                logger.error(f"Failed to load private key for org {organization_id}: {e}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "code": "NO_PRIVATE_KEY",
                        "message": "Organization has no private key configured. Please complete certificate onboarding first.",
                        "details": str(e),
                    },
                )

        # === TEAM_145: Tier Gating (consolidated to free/enterprise/strategic_partner) ===
        # Free tier now has access to most features. Only enterprise-only features are gated.
        tier = organization.get("tier", "free").lower()
        is_enterprise = is_enterprise_tier(tier)

        # Dual binding requires Enterprise
        if request.add_dual_binding and not is_enterprise:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "FEATURE_NOT_AVAILABLE",
                    "message": "Dual-binding manifest requires Enterprise tier",
                    "required_tier": "enterprise",
                    "current_tier": tier,
                    "upgrade_url": "/billing/upgrade",
                },
            )

        # Distributed redundant (ECC) requires Enterprise
        if request.embedding_strategy == "distributed_redundant" and not is_enterprise:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "FEATURE_NOT_AVAILABLE",
                    "message": "Distributed redundant embedding (ECC) requires Enterprise tier",
                    "required_tier": "enterprise",
                    "current_tier": tier,
                    "upgrade_url": "/billing/upgrade",
                },
            )

        logger.info(
            f"Tier gating passed for org {organization_id} (tier={tier}): "
            f"manifest_mode={request.manifest_mode}, embedding_strategy={request.embedding_strategy}"
        )

        # Validate custom assertions and/or template-based assertions if provided.
        # Templates are meant to be usable by Business+ customers while schema/template authoring
        # remains Enterprise-only.
        raw_assertions: List[Dict[str, Any]] = []

        effective_template_id = request.template_id
        if effective_template_id is None:
            row = await core_db.execute(
                text("SELECT default_c2pa_template_id FROM organizations WHERE id = :org_id"),
                {"org_id": organization_id},
            )
            effective_template_id = row.scalar_one_or_none()

        if request.rights:
            features = organization.get("features", {})
            custom_assertions_enabled = False
            if isinstance(features, dict):
                custom_assertions_enabled = features.get("custom_assertions", False)
            custom_assertions_enabled = custom_assertions_enabled or organization.get("custom_assertions_enabled", False)

            if not custom_assertions_enabled:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={
                        "code": "FEATURE_NOT_AVAILABLE",
                        "message": "Custom assertion templates require Business tier or higher",
                        "upgrade_url": "/billing/upgrade",
                    },
                )

            rights_payload = request.rights.dict(exclude_none=True)
            embargo_until = rights_payload.get("embargo_until")
            if embargo_until is not None and hasattr(embargo_until, "isoformat"):
                rights_payload["embargo_until"] = embargo_until.isoformat()
            if rights_payload:
                raw_assertions.append({"label": "com.encypher.rights.v1", "data": rights_payload})

        if effective_template_id:
            features = organization.get("features", {})
            custom_assertions_enabled = False
            if isinstance(features, dict):
                custom_assertions_enabled = features.get("custom_assertions", False)
            custom_assertions_enabled = custom_assertions_enabled or organization.get("custom_assertions_enabled", False)

            if not custom_assertions_enabled:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={
                        "code": "FEATURE_NOT_AVAILABLE",
                        "message": "Custom assertion templates require Business tier or higher",
                        "upgrade_url": "/billing/upgrade",
                    },
                )

            from sqlalchemy import select

            from app.models.c2pa_template import C2PAAssertionTemplate

            stmt = (
                select(C2PAAssertionTemplate)
                .where(
                    C2PAAssertionTemplate.id == effective_template_id,
                    ((C2PAAssertionTemplate.organization_id == organization_id) | (C2PAAssertionTemplate.is_public)),
                    C2PAAssertionTemplate.is_active,
                )
                .limit(1)
            )
            result = await core_db.execute(stmt)
            template = result.scalar_one_or_none()

            template_data: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None
            if template:
                template_data = cast(Union[Dict[str, Any], List[Dict[str, Any]]], template.template_data or {})
            else:
                from app.services.c2pa_builtin_templates import get_builtin_template

                builtin = get_builtin_template(template_id=effective_template_id)
                if builtin is not None:
                    template_data = builtin.get("template_data") or {}

            if template_data is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "code": "TEMPLATE_NOT_FOUND",
                        "message": "Assertion template not found",
                    },
                )

            assertions_payload: List[Dict[str, Any]] = []
            if isinstance(template_data, dict):
                assertions_payload = [assertion for assertion in (template_data.get("assertions") or []) if isinstance(assertion, dict)]
            elif isinstance(template_data, list):
                assertions_payload = [assertion for assertion in template_data if isinstance(assertion, dict)]

            for assertion in assertions_payload:
                if not isinstance(assertion, dict):
                    continue
                label = assertion.get("label")
                if not label:
                    continue
                data = assertion.get("data")
                if data is None:
                    data = assertion.get("default_data")
                if data is None:
                    # Skip optional assertions with no default payload.
                    continue
                raw_assertions.append({"label": label, "data": data})

        if request.custom_assertions:
            raw_assertions.extend(request.custom_assertions)

        try:
            await ensure_organization_exists(core_db, organization)
            _list_index, bit_index, status_list_url = await status_service.allocate_status_index(
                db=core_db,
                organization_id=organization_id,
                document_id=request.document_id,
            )
        except Exception as exc:
            logger.error("Failed to allocate status list index: %s", exc, exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "code": "STATUS_LIST_ALLOCATION_FAILED",
                    "message": "Failed to allocate status list entry",
                },
            ) from exc

        validated_assertions = None
        if raw_assertions and request.validate_assertions:
            from sqlalchemy import select

            from app.models.c2pa_schema import C2PASchema
            from app.services.c2pa_validator import validator

            # Fetch registered schemas for this organization
            registered_schemas: Dict[str, Dict[str, Any]] = {}
            for assertion in raw_assertions:
                label = assertion.get("label")
                if label and label not in registered_schemas:
                    stmt = (
                        select(C2PASchema)
                        .where(
                            C2PASchema.label == label,
                            ((C2PASchema.organization_id == organization_id) | (C2PASchema.is_public)),
                        )
                        .order_by(C2PASchema.created_at.desc())
                    )
                    result = await core_db.execute(stmt)
                    schema_model = result.scalar_one_or_none()
                    if schema_model:
                        registered_schemas[label] = schema_model.json_schema

            # Validate all assertions
            all_valid, validation_results = validator.validate_custom_assertions(
                raw_assertions,
                registered_schemas,
            )

            if not all_valid:
                logger.warning(f"Custom assertion validation failed for document {request.document_id}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "code": "INVALID_ASSERTIONS",
                        "message": "One or more custom assertions failed validation",
                        "validation_results": validation_results,
                    },
                )

            validated_assertions = raw_assertions
            logger.info(f"Validated {len(validated_assertions)} custom assertions for document {request.document_id}")
        elif raw_assertions:
            # Use assertions without validation
            validated_assertions = raw_assertions
            logger.info(f"Using {len(validated_assertions)} custom assertions without validation")

        status_assertion = {
            "label": "org.encypher.status",
            "data": {
                "statusListCredential": status_list_url,
                "statusListIndex": str(bit_index),
            },
        }

        if validated_assertions is None:
            validated_assertions = []
        else:
            validated_assertions = list(validated_assertions)
        validated_assertions.append(status_assertion)

        # Initialize embedding service with organization's key
        embedding_service = EmbeddingService(private_key, signer_id)

        # Free tier (document-level): Skip Merkle tree and segmentation
        # Just create ONE C2PA wrapper for the entire document
        merkle_root_id: Optional[UUID] = None
        processing_metadata: Optional[Dict[str, Any]] = None
        if request.segmentation_level == "document":
            logger.info("Document-level signing (free tier) - no segmentation")
            from app.utils.merkle import compute_leaf_hash

            segments = [document_text]  # Single segment = entire document
            leaf_hashes = [compute_leaf_hash(document_text)]  # Single hash for entire document
            merkle_root_id = None  # No Merkle tree for free tier
            merkle_root: Optional[MerkleRoot] = None
            merkle_roots: Dict[str, MerkleRoot] = {}
            merkle_trees = None
            processing_metadata = build_processing_metadata(
                segmentation_level=request.segmentation_level,
                segmentation_levels=None,
                include_words=False,
            )
        else:
            merkle_levels = request.segmentation_levels
            if not merkle_levels:
                merkle_levels = [request.segmentation_level]

            processing_metadata = build_processing_metadata(
                segmentation_level=request.segmentation_level,
                segmentation_levels=merkle_levels,
                include_words=False,
            )

            merkle_metadata = dict(request.metadata or {})
            merkle_metadata["processing"] = processing_metadata

            index_for_attribution = request.index_for_attribution
            if index_for_attribution is None:
                index_for_attribution = is_enterprise_tier(organization.get("tier", "free"))

            if index_for_attribution:
                # Pass features dict with nma_member flag for quota check
                quota_features = dict(organization.get("features", {}))
                if organization.get("nma_member"):
                    quota_features["nma_member"] = True
                await QuotaManager.check_quota(
                    db=core_db,
                    organization_id=organization_id,
                    quota_type=QuotaType.MERKLE_ENCODING,
                    increment=len(merkle_levels),
                    features=quota_features,
                )

            logger.info(
                "Enterprise tier - building Merkle trees at levels=%s (indexed=%s)",
                merkle_levels,
                index_for_attribution,
            )

            merkle_roots = await MerkleService.encode_document(
                db=content_db,
                organization_id=organization_id,
                document_id=request.document_id,
                text=document_text,
                segmentation_levels=merkle_levels,
                metadata=merkle_metadata,
                include_words=False,
            )

            merkle_root = merkle_roots.get(request.segmentation_level) or next(iter(merkle_roots.values()))
            merkle_root_id = cast(UUID, merkle_root.id)

            merkle_trees = {
                level: MerkleTreeLevelInfo(
                    root_hash=root.root_hash,
                    total_leaves=root.leaf_count,
                    tree_depth=root.tree_depth,
                    indexed=index_for_attribution,
                )
                for level, root in merkle_roots.items()
            }

            # Get segments and hashes
            from app.utils.segmentation import HierarchicalSegmenter

            segmenter = HierarchicalSegmenter(document_text, include_words=False)
            segments = segmenter.get_segments(request.segmentation_level)

            # Compute leaf hashes
            from app.utils.merkle import compute_leaf_hash

            leaf_hashes = [compute_leaf_hash(segment) for segment in segments]

        # Step 3: Generate minimal signed embeddings
        license_info = None
        if request.license:
            license_info = {"type": request.license.type, "url": request.license.url}

        # Returns: (embeddings_list, full_document_with_c2pa_wrapper)
        embeddings, embedded_content = await embedding_service.create_embeddings(
            db=content_db,
            organization_id=organization_id,
            document_id=request.document_id,
            merkle_root_id=merkle_root_id,  # None for free tier
            merkle_root_hash=merkle_root.root_hash if merkle_root else None,
            merkle_segmentation_level=merkle_root.segmentation_level if merkle_root else None,
            segments=segments,
            leaf_hashes=leaf_hashes,
            c2pa_manifest_url=request.c2pa_manifest_url,
            c2pa_manifest_hash=request.c2pa_manifest_hash,
            license_info=license_info,
            expires_at=request.expires_at,
            action=request.action,
            previous_instance_id=request.previous_instance_id,
            custom_assertions=validated_assertions,  # Pass validated custom assertions
            digital_source_type=request.digital_source_type,  # Pass digital source type
            processing_metadata=processing_metadata,
            # === API Feature Augmentation (TEAM_044) ===
            manifest_mode=request.manifest_mode,
            ecc=request.ecc,
            legacy_safe=request.legacy_safe,
            embed_c2pa=request.embed_c2pa,
            embedding_strategy=request.embedding_strategy,
            distribution_target=request.distribution_target,
            add_dual_binding=request.add_dual_binding,
            disable_c2pa=request.disable_c2pa,
            store_c2pa_manifest=request.store_c2pa_manifest,
            organization_name=organization.get("publisher_identity_base") or organization.get("organization_name"),
            original_text=document_text,  # Preserve inter-segment whitespace (e.g. \n\n before headings)
        )

        # Step 4: Convert embeddings to response format
        embedding_infos = []
        for emb in embeddings:
            info = EmbeddingInfo(
                leaf_index=emb.leaf_index,
                text=emb.embedded_text if request.embedding_options.include_text else None,
                ref_id=None,  # No visible ref_id with invisible embeddings
                signature=None,  # No visible signature with invisible embeddings
                embedding=None,  # No visible embedding string
                verification_url=None,  # Verification is done by extracting from text
                leaf_hash=emb.leaf_hash,
            )
            embedding_infos.append(info)

        # Step 5: embedded_content already contains the full document
        # with minimal embeddings per sentence + ONE C2PA wrapper at the end

        # Extract instance_id from the embedded C2PA manifest
        instance_id = None
        extracted_manifest = None
        try:
            from encypher.core.unicode_metadata import UnicodeMetadata

            extracted = UnicodeMetadata.extract_metadata(embedded_content)
            if extracted:
                extracted_manifest = extracted
                if "instance_id" in extracted:
                    instance_id = extracted["instance_id"]
                    logger.info(f"Extracted instance_id from manifest: {instance_id}")
        except Exception as e:
            logger.warning(f"Could not extract instance_id from manifest: {e}")

        processing_time_ms = (time.time() - start_time) * 1000

        logger.info(f"Successfully encoded document {request.document_id} with {len(embeddings)} invisible embeddings in {processing_time_ms:.2f}ms")

        # Build Merkle tree info (None for free tier)
        merkle_tree_info = None
        if merkle_root:
            merkle_tree_info = MerkleTreeInfo(root_hash=merkle_root.root_hash, total_leaves=merkle_root.leaf_count, tree_depth=merkle_root.tree_depth)

        # Build metadata response
        if extracted_manifest:
            response_metadata = extracted_manifest
        else:
            response_metadata = {"instance_id": instance_id, "action": request.action, "previous_instance_id": request.previous_instance_id}

        return EncodeWithEmbeddingsResponse(
            success=True,
            document_id=request.document_id,
            merkle_tree=merkle_tree_info,
            merkle_trees=merkle_trees,
            embeddings=embedding_infos,
            embedded_content=embedded_content,
            statistics={
                "total_sentences": len(segments),
                "embeddings_created": len(embeddings),
                "processing_time_ms": round(processing_time_ms, 2),
                "uses_invisible_embeddings": True,
                "segmentation_level": request.segmentation_level,
                "tier": "free" if request.segmentation_level == "document" else "enterprise",
            },
            metadata=response_metadata,
        )

    except ValueError as e:
        logger.error(f"Validation error encoding document: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid document encoding parameters")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error encoding document with embeddings: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to encode document with embeddings")
