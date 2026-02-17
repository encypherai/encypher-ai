"""
Unified signing service that handles both basic and advanced signing.

This service consolidates the logic from signing_executor.py and embedding_executor.py
into a single unified flow that uses tier-gated options.
"""

import logging
import time
from typing import Any, Dict, List, Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.schemas.api_response import (
    ErrorCode,
    build_error_response,
    build_tier_error,
    get_available_features,
    get_gated_features,
)
from app.schemas.sign_schemas import (
    SignDocument,
    SignedDocumentResult,
    SignOptions,
    SignResponseData,
    UnifiedSignRequest,
    validate_sign_options_for_tier,
)
from app.services.embedding_plan import build_embedding_plan

logger = logging.getLogger(__name__)


async def execute_unified_signing(
    *,
    request: UnifiedSignRequest,
    organization: Dict[str, Any],
    core_db: AsyncSession,
    content_db: AsyncSession,
    correlation_id: str,
) -> Dict[str, Any]:
    """
    Execute unified signing with tier-gated options.
    
    This function:
    1. Validates options against tier requirements
    2. Routes to basic or advanced signing based on options
    3. Returns standardized response with tier metadata
    
    Args:
        request: Unified sign request
        organization: Authenticated organization data
        core_db: Core database session
        content_db: Content database session
        correlation_id: Request correlation ID
        
    Returns:
        Standardized API response dict
    """
    start_time = time.time()
    
    tier = (organization.get("tier") or "free").lower().replace("-", "_")
    org_id = organization["organization_id"]
    is_nma_member = organization.get("nma_member", False)
    
    # Get documents to process
    documents = request.get_documents()
    batch_size = len(documents)
    
    logger.info(
        "Unified signing request from org %s (tier=%s, batch_size=%d)",
        org_id,
        tier,
        batch_size,
    )
    
    # Validate options against tier
    validation = validate_sign_options_for_tier(
        options=request.options,
        tier=tier,
        batch_size=batch_size,
        is_nma_member=is_nma_member,
    )
    
    if not validation.valid:
        # Return tier error with details about denied features
        denied = validation.features_denied[0]  # First denied feature
        return build_error_response(
            code=ErrorCode.E_TIER_REQUIRED,
            message=f"{denied['display_name']} requires {denied['required_tier'].title()} tier or higher",
            correlation_id=correlation_id,
            tier=tier,
            hint=f"Upgrade your plan at https://encypherai.com/pricing to access {denied['display_name']}",
            details={
                "features_denied": validation.features_denied,
                "current_tier": tier,
            },
            category="signing",
        )
    
    # Determine if we need advanced signing (any non-default options)
    needs_advanced = _needs_advanced_signing(request.options)
    
    # Process documents
    results: List[SignedDocumentResult] = []
    total_segments = 0
    
    for doc in documents:
        try:
            if needs_advanced:
                result = await _execute_advanced_signing(
                    document=doc,
                    options=request.options,
                    organization=organization,
                    core_db=core_db,
                    content_db=content_db,
                )
            else:
                result = await _execute_basic_signing(
                    document=doc,
                    options=request.options,
                    organization=organization,
                    db=core_db,
                )

            if request.options.return_embedding_plan and result.signed_text:
                result.embedding_plan = build_embedding_plan(
                    visible_text=doc.text,
                    signed_text=result.signed_text,
                )
            
            results.append(result)
            total_segments += result.total_segments
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error signing document {doc.document_id}: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "code": ErrorCode.E_INTERNAL,
                    "message": f"Failed to sign document: {str(e)}",
                },
            )
    
    processing_time_ms = int((time.time() - start_time) * 1000)
    
    # Build response data
    if batch_size == 1:
        response_data = SignResponseData(
            document=results[0],
            documents=None,
            total_documents=1,
            total_segments=total_segments,
            processing_time_ms=processing_time_ms,
        )
    else:
        response_data = SignResponseData(
            document=None,
            documents=results,
            total_documents=batch_size,
            total_segments=total_segments,
            processing_time_ms=processing_time_ms,
        )
    
    # Build standardized response
    from app.schemas.api_response import ResponseMeta
    
    meta = ResponseMeta(
        tier=tier,
        features_used=validation.features_used,
        features_available=get_available_features(tier, "signing"),
        features_gated=get_gated_features(tier, "signing"),
        processing_time_ms=processing_time_ms,
        correlation_id=correlation_id,
    )
    
    return {
        "success": True,
        "data": response_data.model_dump(),
        "error": None,
        "correlation_id": correlation_id,
        "meta": meta.model_dump(),
    }


def _needs_advanced_signing(options: SignOptions) -> bool:
    """Check if options require advanced signing flow."""
    # Advanced signing is needed for any non-default options
    return (
        options.segmentation_level != "document"
        or options.manifest_mode != "full"
        or options.embedding_strategy != "single_point"
        or options.index_for_attribution
        or options.custom_assertions is not None
        or options.template_id is not None
        or options.rights is not None
        or options.add_dual_binding
        or options.include_fingerprint
        or options.segmentation_levels is not None
    )


async def _execute_basic_signing(
    *,
    document: SignDocument,
    options: SignOptions,
    organization: Dict[str, Any],
    db: AsyncSession,
) -> SignedDocumentResult:
    """
    Execute basic document-level signing.
    
    This is the simpler flow for free/starter tier users who just want
    basic C2PA signing without advanced features.
    """
    from app.models.request_models import SignRequest
    from app.services.signing_executor import execute_signing
    
    # Convert to legacy SignRequest format
    legacy_request = SignRequest(
        text=document.text,
        document_id=document.document_id,
        document_title=document.document_title,
        document_url=document.document_url,
        document_type=options.document_type,
        claim_generator=options.claim_generator,
        actions=options.actions,
        custom_assertions=options.custom_assertions,
        template_id=options.template_id,
        validate_assertions=options.validate_assertions,
        rights=options.rights,
    )
    
    # Execute signing
    result = await execute_signing(
        request=legacy_request,
        organization=organization,
        db=db,
        document_id=document.document_id,
    )
    
    return SignedDocumentResult(
        document_id=result.document_id,
        signed_text=result.signed_text,
        verification_url=result.verification_url,
        total_segments=result.total_sentences,
        merkle_root=None,
        instance_id=None,
        metadata=document.metadata,
        publisher_attribution=result.publisher_attribution,
    )


async def _execute_advanced_signing(
    *,
    document: SignDocument,
    options: SignOptions,
    organization: Dict[str, Any],
    core_db: AsyncSession,
    content_db: AsyncSession,
) -> SignedDocumentResult:
    """
    Execute advanced signing with segmentation, Merkle trees, etc.
    
    This is the full-featured flow for Professional+ users.
    """
    from app.schemas.embeddings import (
        EmbeddingOptions as LegacyEmbeddingOptions,
        EncodeWithEmbeddingsRequest,
        LicenseInfo as LegacyLicenseInfo,
        RightsMetadata as LegacyRightsMetadata,
    )
    from app.services.embedding_executor import encode_document_with_embeddings
    
    # Convert options to legacy format
    legacy_embedding_options = LegacyEmbeddingOptions(
        format=options.embedding_options.format,
        method="data-attribute" if options.embedding_options.method == "invisible" else options.embedding_options.method,
        include_text=options.embedding_options.include_text,
    )
    
    # Convert rights if present
    legacy_rights = None
    if options.rights:
        legacy_rights = LegacyRightsMetadata(
            copyright_holder=options.rights.copyright_holder,
            license_url=options.rights.license_url,
            usage_terms=options.rights.usage_terms,
            syndication_allowed=options.rights.syndication_allowed,
            embargo_until=options.rights.embargo_until,
            contact_email=options.rights.contact_email,
        )
    
    # Convert license if present
    legacy_license = None
    if options.license:
        legacy_license = LegacyLicenseInfo(
            type=options.license.type,
            url=options.license.url,
            contact_email=options.license.contact_email,
        )
    
    # Build legacy request
    legacy_request = EncodeWithEmbeddingsRequest(
        document_id=document.document_id or f"doc_{int(time.time() * 1000)}",
        text=document.text,
        segmentation_level=options.segmentation_level,
        segmentation_levels=options.segmentation_levels,
        index_for_attribution=options.index_for_attribution,
        action=options.action,
        manifest_mode=options.manifest_mode,
        ecc=options.ecc,
        embed_c2pa=options.embed_c2pa,
        embedding_strategy=options.embedding_strategy,
        distribution_target=options.distribution_target,
        add_dual_binding=options.add_dual_binding,
        disable_c2pa=options.disable_c2pa,
        store_c2pa_manifest=options.store_c2pa_manifest,
        previous_instance_id=options.previous_instance_id,
        metadata=document.metadata or {
            "title": document.document_title,
            "url": document.document_url,
        },
        custom_assertions=options.custom_assertions,
        template_id=options.template_id,
        validate_assertions=options.validate_assertions,
        digital_source_type=options.digital_source_type,
        license=legacy_license,
        rights=legacy_rights,
        embedding_options=legacy_embedding_options,
        expires_at=options.expires_at,
    )
    
    # Execute advanced signing
    result = await encode_document_with_embeddings(
        request=legacy_request,
        organization=organization,
        core_db=core_db,
        content_db=content_db,
    )
    
    # Extract merkle root if available
    merkle_root = None
    if result.merkle_tree:
        merkle_root = result.merkle_tree.root_hash
    elif result.merkle_trees:
        # Use the first available merkle tree
        for level, tree_info in result.merkle_trees.items():
            merkle_root = tree_info.root_hash
            break
    
    # Extract instance_id from metadata
    instance_id = None
    if result.metadata and isinstance(result.metadata, dict):
        instance_id = result.metadata.get("instance_id")
    
    return SignedDocumentResult(
        document_id=result.document_id,
        signed_text=result.embedded_content or document.text,
        verification_url=f"https://verify.{settings.infrastructure_domain}/{result.document_id}",
        total_segments=len(result.embeddings),
        merkle_root=merkle_root,
        instance_id=instance_id,
        metadata=result.metadata,
        publisher_attribution=organization.get("publisher_attribution"),
    )
