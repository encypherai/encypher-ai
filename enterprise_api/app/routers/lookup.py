"""
Lookup router for sentence provenance tracking.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import logging

from app.database import get_db
from app.models.request_models import LookupRequest
from app.models.response_models import LookupResponse
from app.utils.sentence_parser import compute_sentence_hash

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/lookup", response_model=LookupResponse)
async def lookup_sentence(
    request: LookupRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Look up sentence provenance by hash.

    This endpoint allows anyone to paste a sentence and find which document
    it originally came from, along with metadata about the publisher.

    Use case: User pastes a sentence, we find which document it came from.

    Note: This endpoint does NOT require authentication (public lookup).

    Args:
        request: LookupRequest containing sentence text
        db: Database session

    Returns:
        LookupResponse with document and organization details if found
    """
    logger.info(f"Lookup request for sentence: {request.sentence_text[:50]}...")

    # Compute hash of the sentence
    sentence_hash = compute_sentence_hash(request.sentence_text)
    logger.debug(f"Computed sentence hash: {sentence_hash}")

    # Query database for sentence
    result = await db.execute(
        text("""
            SELECT
                sr.sentence_index,
                d.title AS document_title,
                d.url AS document_url,
                d.publication_date,
                o.organization_name
            FROM sentence_records sr
            JOIN documents d ON sr.document_id = d.document_id
            JOIN organizations o ON sr.organization_id = o.organization_id
            WHERE sr.sentence_hash = :hash
            LIMIT 1
        """),
        {"hash": sentence_hash}
    )

    row = result.fetchone()

    if not row:
        logger.info(f"Sentence not found in database (hash: {sentence_hash})")
        return LookupResponse(
            success=True,
            found=False
        )

    logger.info(
        f"Sentence found: document='{row.document_title}', "
        f"org='{row.organization_name}', index={row.sentence_index}"
    )

    return LookupResponse(
        success=True,
        found=True,
        document_title=row.document_title,
        document_url=row.document_url,
        organization_name=row.organization_name,
        publication_date=row.publication_date,
        sentence_index=row.sentence_index
    )
