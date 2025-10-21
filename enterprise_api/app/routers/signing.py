"""
Signing router for content signing with C2PA manifests.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import uuid
import logging

# NOTE: This import assumes the preview encypher-ai package with C2PA support
# After C2PA spec publication, this will use the public PyPI package
try:
    from encypher import UnicodeMetadata
except ImportError:
    raise ImportError(
        "encypher-ai package not found. "
        "Please install the preview version with C2PA support."
    )

from app.database import get_db
from app.models.request_models import SignRequest
from app.models.response_models import SignResponse
from app.dependencies import require_sign_permission
from app.utils.crypto_utils import load_organization_private_key
from app.utils.sentence_parser import parse_sentences, compute_sentence_hash, compute_text_hash
from app.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/sign", response_model=SignResponse)
async def sign_content(
    request: SignRequest,
    organization: dict = Depends(require_sign_permission),
    db: AsyncSession = Depends(get_db)
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

    # 1. Load organization's private key
    try:
        private_key = await load_organization_private_key(
            organization['organization_id'],
            db
        )
    except ValueError as e:
        logger.error(f"Failed to load private key: {e}")
        raise HTTPException(
            status_code=400,
            detail={
                "code": "NO_PRIVATE_KEY",
                "message": "Organization has no private key configured. "
                          "Please complete certificate onboarding first.",
                "details": str(e)
            }
        )

    # 2. Generate document ID
    document_id = f"doc_{uuid.uuid4().hex[:16]}"

    # 3. Use encypher-ai library to embed C2PA manifest
    try:
        logger.debug(f"Embedding C2PA manifest for document {document_id}")
        signed_text = UnicodeMetadata.embed_metadata(
            text=request.text,
            private_key=private_key,
            signer=organization['organization_id'],
            metadata_format="c2pa"  # Triggers C2PA mode in encypher-ai
        )
        logger.info(f"Successfully embedded C2PA manifest in document {document_id}")
    except Exception as e:
        logger.error(f"C2PA embedding failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "code": "C2PA_EMBEDDING_FAILED",
                "message": "Failed to embed C2PA manifest",
                "details": str(e) if settings.is_development else None
            }
        )

    # 4. Parse sentences for granular tracking
    sentences = parse_sentences(request.text)
    logger.debug(f"Parsed {len(sentences)} sentences from document {document_id}")

    # 5. Compute text hash for tamper detection
    text_hash = compute_text_hash(request.text)

    # 6. Store document record
    try:
        await db.execute(
            text("""
                INSERT INTO documents
                (document_id, organization_id, title, url, document_type,
                 total_sentences, signed_text, text_hash, publication_date)
                VALUES (:doc_id, :org_id, :title, :url, :doc_type, :total, :signed, :hash, NOW())
            """),
            {
                "doc_id": document_id,
                "org_id": organization['organization_id'],
                "title": request.document_title,
                "url": request.document_url,
                "doc_type": request.document_type,
                "total": len(sentences),
                "signed": signed_text,
                "hash": text_hash
            }
        )

        # 7. Store sentence records for lookup
        for idx, sentence in enumerate(sentences):
            sentence_id = f"sent_{uuid.uuid4().hex[:16]}"
            sentence_hash = compute_sentence_hash(sentence)

            await db.execute(
                text("""
                    INSERT INTO sentence_records
                    (sentence_id, document_id, organization_id, sentence_text,
                     sentence_hash, sentence_index, embedded_in_manifest)
                    VALUES (:sent_id, :doc_id, :org_id, :text, :hash, :idx, TRUE)
                """),
                {
                    "sent_id": sentence_id,
                    "doc_id": document_id,
                    "org_id": organization['organization_id'],
                    "text": sentence,
                    "hash": sentence_hash,
                    "idx": idx
                }
            )

        # 8. Update organization usage stats
        await db.execute(
            text("""
                UPDATE organizations
                SET documents_signed = documents_signed + 1,
                    sentences_signed = sentences_signed + :count,
                    api_calls_this_month = api_calls_this_month + 1,
                    updated_at = NOW()
                WHERE organization_id = :org_id
            """),
            {"org_id": organization['organization_id'], "count": len(sentences)}
        )

        await db.commit()
        logger.info(
            f"Document {document_id} stored with {len(sentences)} sentences "
            f"for organization {organization['organization_id']}"
        )

    except Exception as e:
        await db.rollback()
        logger.error(f"Database error while storing document: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "code": "DATABASE_ERROR",
                "message": "Failed to store signed document",
                "details": str(e) if settings.is_development else None
            }
        )

    # 9. Generate verification URL
    verification_url = f"https://verify.{settings.infrastructure_domain}/{document_id}"

    return SignResponse(
        success=True,
        document_id=document_id,
        signed_text=signed_text,
        total_sentences=len(sentences),
        verification_url=verification_url
    )
