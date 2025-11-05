"""
Signing router for content signing with C2PA manifests.
"""
from datetime import datetime, timezone
import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

# NOTE: This import assumes the preview encypher-ai package with C2PA support
# After C2PA spec publication, this will use the public PyPI package
try:
    from encypher import UnicodeMetadata
except ImportError:
    raise ImportError(
        "encypher-ai package not found. "
        "Please install the preview version with C2PA support."
    )

from app.config import settings
from app.database import get_db
from app.dependencies import require_sign_permission
from app.models.request_models import SignRequest
from app.models.response_models import SignResponse
from app.utils.crypto_utils import load_organization_private_key, get_demo_private_key
from app.utils.sentence_parser import (
    compute_sentence_hash,
    compute_text_hash,
    parse_sentences,
)
from app.utils.coalition_client import CoalitionClient

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize coalition client
coalition_client = CoalitionClient(settings.coalition_service_url)


@router.post("/sign", response_model=SignResponse)
async def sign_content(
    request: SignRequest,
    organization: dict = Depends(require_sign_permission),
    db: AsyncSession = Depends(get_db),
):
    """
    Sign content with C2PA manifest using encypher-ai library.

    This endpoint:
    1. Loads the organization's private key
    2. Uses encypher-ai's UnicodeMetadata.embed_metadata() with metadata_format="c2pa"
    3. Parses sentences for granular tracking
    4. Stores signed text and sentence records in database
    5. Returns signed text with verification URL

    Args:
        request: SignRequest containing text and metadata
        organization: Organization details from authentication
        db: Database session

    Returns:
        SignResponse with signed text and document ID

    Raises:
        HTTPException: If signing fails or organization has no private key
    """
    logger.info(
        f"Signing request from organization {organization['organization_id']}: "
        f"{len(request.text)} characters, {request.document_type}"
    )

    is_demo_org = organization.get("is_demo", False)

    # 1. Load organization's private key
    try:
        if is_demo_org:
            private_key = get_demo_private_key()
        else:
            private_key = await load_organization_private_key(
                organization["organization_id"], db
            )
    except ValueError as e:
        logger.error(f"Failed to load private key: {e}")
        raise HTTPException(
            status_code=400,
            detail={
                "code": "NO_PRIVATE_KEY",
                "message": "Organization has no private key configured. "
                "Please complete certificate onboarding first.",
                "details": str(e),
            },
        )

    # 2. Generate document ID
    document_id = f"doc_{uuid.uuid4().hex[:16]}"

    # 3. Use encypher-ai library to embed C2PA manifest
    try:
        logger.debug(f"Embedding C2PA manifest for document {document_id}")
        signed_text = UnicodeMetadata.embed_metadata(
            text=request.text,
            private_key=private_key,
            signer_id=organization["organization_id"],
            metadata_format="c2pa",  # Triggers C2PA mode in encypher-ai
            claim_generator=request.claim_generator,
            actions=request.actions,
        )
        logger.info(f"Successfully embedded C2PA manifest in document {document_id}")
    except Exception as e:
        logger.error(f"C2PA embedding failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "code": "C2PA_EMBEDDING_FAILED",
                "message": "Failed to embed C2PA manifest",
                "details": str(e) if settings.is_development else None,
            },
        )

    # 4. Parse sentences for granular tracking
    sentences = parse_sentences(request.text)
    logger.debug(f"Parsed {len(sentences)} sentences from document {document_id}")

    # 5. Compute text hash for tamper detection
    text_hash = compute_text_hash(request.text)
    current_time = datetime.now(timezone.utc)

    # 6. Store document record (skipped for demo organizations)
    if not is_demo_org:
        try:
            await db.execute(
                text(
                    """
                    INSERT INTO documents
                    (document_id, organization_id, title, url, document_type,
                     total_sentences, signed_text, text_hash, publication_date)
                    VALUES (:doc_id, :org_id, :title, :url, :doc_type, :total, :signed, :hash, :publication_date)
                """
                ),
                {
                    "doc_id": document_id,
                    "org_id": organization["organization_id"],
                    "title": request.document_title,
                    "url": request.document_url,
                    "doc_type": request.document_type,
                    "total": len(sentences),
                    "signed": signed_text,
                    "hash": text_hash,
                    "publication_date": current_time,
                },
            )

            # 7. Store sentence records for lookup
            for idx, sentence in enumerate(sentences):
                sentence_id = f"sent_{uuid.uuid4().hex[:16]}"
                sentence_hash = compute_sentence_hash(sentence)

                await db.execute(
                    text(
                        """
                        INSERT INTO sentence_records
                        (sentence_id, document_id, organization_id, sentence_text,
                         sentence_hash, sentence_index, embedded_in_manifest)
                        VALUES (:sent_id, :doc_id, :org_id, :text, :hash, :idx, TRUE)
                    """
                    ),
                    {
                        "sent_id": sentence_id,
                        "doc_id": document_id,
                        "org_id": organization["organization_id"],
                        "text": sentence,
                        "hash": sentence_hash,
                        "idx": idx,
                    },
                )

            # 8. Update organization usage stats
            await db.execute(
                text(
                    """
                    UPDATE organizations
                    SET documents_signed = documents_signed + 1,
                        sentences_signed = sentences_signed + :count,
                        api_calls_this_month = api_calls_this_month + 1,
                        updated_at = :updated_at
                    WHERE organization_id = :org_id
                """
                ),
                {
                    "org_id": organization["organization_id"],
                    "count": len(sentences),
                    "updated_at": current_time,
                },
            )

            await db.commit()
            logger.info(
                f"Document {document_id} stored with {len(sentences)} sentences "
                f"for organization {organization['organization_id']}"
            )

            # 9. Coalition content indexing (non-blocking)
            try:
                # Look up organization's user_id
                org_result = await db.execute(
                    text("SELECT user_id FROM organizations WHERE organization_id = :org_id"),
                    {"org_id": organization["organization_id"]},
                )
                org_row = org_result.fetchone()

                if org_row and org_row.user_id:
                    # Check if user is a coalition member
                    member = await coalition_client.get_member_by_user_id(str(org_row.user_id))

                    if member and member.get("status") == "active":
                        # Calculate word count
                        word_count = len(request.text.split())

                        # Index content in coalition
                        indexed = await coalition_client.index_content(
                            member_id=member.get("member_id"),
                            document_id=document_id,
                            content_hash=text_hash,
                            content_type=request.document_type,
                            word_count=word_count,
                            signed_at=current_time,
                        )

                        if indexed:
                            logger.info(
                                f"Document {document_id} indexed in coalition for "
                                f"member {member.get('member_id')}"
                            )
                        else:
                            logger.warning(
                                f"Failed to index document {document_id} in coalition"
                            )
                    else:
                        logger.debug(
                            f"User {org_row.user_id} is not an active coalition member, "
                            f"skipping content indexing"
                        )
                else:
                    logger.debug(
                        f"Organization {organization['organization_id']} has no user_id, "
                        f"skipping coalition indexing"
                    )
            except Exception as coalition_error:
                # Don't fail the signing request if coalition indexing fails
                logger.warning(
                    f"Coalition indexing failed for document {document_id}: {coalition_error}",
                    exc_info=True,
                )

        except Exception as e:
            await db.rollback()
            logger.error(f"Database error while storing document: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail={
                    "code": "DATABASE_ERROR",
                    "message": "Failed to store signed document",
                    "details": str(e) if settings.is_development else None,
                },
            )

    # 10. Generate verification URL
    if settings.is_development:
        # In development, use localhost for verification
        verification_url = f"http://localhost:9000/api/v1/verify/{document_id}"
    elif is_demo_org:
        verification_url = f"https://verify.{settings.infrastructure_domain}/demo/{document_id}"
    else:
        verification_url = f"https://verify.{settings.infrastructure_domain}/{document_id}"

    return SignResponse(
        success=True,
        document_id=document_id,
        signed_text=signed_text,
        total_sentences=len(sentences),
        verification_url=verification_url,
    )
