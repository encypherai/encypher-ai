"""
Shared signing logic reused by HTTP endpoints and batch workers.

Two-Database Architecture:
- Content DB: Stores documents and sentence_records
- Core DB: Stores organization usage counters
"""
from __future__ import annotations

from datetime import datetime, timezone
import logging
import uuid
from typing import Optional

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

try:
    from encypher import UnicodeMetadata
except ImportError as exc:  # pragma: no cover - import guard
    raise ImportError(
        "encypher-ai package not found. "
        "Please install the preview version with C2PA support."
    ) from exc

from app.config import settings
from app.database import content_session_factory, core_session_factory
from app.models.request_models import SignRequest
from app.models.response_models import SignResponse
from app.utils.coalition_client import CoalitionClient
from app.utils.crypto_utils import get_demo_private_key, load_organization_private_key
from app.utils.sentence_parser import compute_sentence_hash, compute_text_hash, parse_sentences

logger = logging.getLogger(__name__)
coalition_client = CoalitionClient(settings.coalition_service_url)


async def execute_signing(
    *,
    request: SignRequest,
    organization: dict,
    db: AsyncSession,
    document_id: Optional[str] = None,
) -> SignResponse:
    """
    Perform signing, persistence, and coalition indexing.

    Args:
        request: Sign request payload.
        organization: Authenticated organization data.
        db: Database session.
        document_id: Optional document identifier override.
    """

    logger.info(
        "Signing request from organization %s (%s chars, type=%s)",
        organization["organization_id"],
        len(request.text),
        request.document_type,
    )

    is_demo_org = organization.get("is_demo", False)

    # Load organization's private key
    try:
        if is_demo_org:
            private_key = get_demo_private_key()
        else:
            private_key = await load_organization_private_key(organization["organization_id"], db)
    except ValueError as exc:
        logger.error("Failed to load private key: %s", exc)
        raise HTTPException(
            status_code=400,
            detail={
                "code": "NO_PRIVATE_KEY",
                "message": "Organization has no private key configured. Please complete certificate onboarding first.",
                "details": str(exc),
            },
        )

    document_id = document_id or f"doc_{uuid.uuid4().hex[:16]}"

    # Embed manifest
    try:
        logger.debug("Embedding C2PA manifest for document %s", document_id)
        signed_text = UnicodeMetadata.embed_metadata(
            text=request.text,
            private_key=private_key,
            signer_id=organization["organization_id"],
            metadata_format="c2pa",
            claim_generator=request.claim_generator,
            actions=request.actions,
        )
    except Exception as exc:  # pragma: no cover - defensive
        logger.error("C2PA embedding failed: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "code": "C2PA_EMBEDDING_FAILED",
                "message": "Failed to embed C2PA manifest",
                "details": str(exc) if settings.is_development else None,
            },
        )

    sentences = parse_sentences(request.text)
    text_hash = compute_text_hash(request.text)
    current_time = datetime.now(timezone.utc)

    # Two-Database Architecture:
    # 1. Store document/sentences in CONTENT database
    # 2. Update usage counters in CORE database
    
    try:
        # Write to CONTENT database (documents, sentences)
        async with content_session_factory() as content_db:
            await content_db.execute(
                text(
                    """
                    INSERT INTO documents (
                        id, organization_id, title, url, document_type,
                        total_sentences, signed_text, text_hash, publication_date, created_at
                    )
                    VALUES (
                        :doc_id, :org_id, :title, :url, :doc_type,
                        :total, :signed, :hash, :pub_date, :created_at
                    )
                    """
                ),
                {
                    "doc_id": document_id,
                    "org_id": organization["organization_id"],
                    "title": request.document_title or "Untitled Document",
                    "url": request.document_url,
                    "doc_type": request.document_type,
                    "total": len(sentences),
                    "signed": signed_text,
                    "hash": text_hash,
                    "pub_date": current_time,
                    "created_at": current_time,
                },
            )

            sentence_records = []
            for idx, sentence in enumerate(sentences):
                sentence_id = f"sent_{uuid.uuid4().hex[:20]}"
                sentence_hash = compute_sentence_hash(sentence)
                sentence_records.append({
                    "sent_id": sentence_id,
                    "doc_id": document_id,
                    "org_id": organization["organization_id"],
                    "text": sentence,
                    "hash": sentence_hash,
                    "idx": idx,
                })

            if sentence_records:
                await content_db.execute(
                    text(
                        """
                        INSERT INTO sentence_records (
                            id, document_id, organization_id,
                            sentence_text, sentence_hash, sentence_index, embedded_in_manifest
                        )
                        VALUES (:sent_id, :doc_id, :org_id, :text, :hash, :idx, TRUE)
                        """
                    ),
                    sentence_records
                )
            
            await content_db.commit()

        # Write to CORE database (usage counters)
        async with core_session_factory() as core_db:
            await core_db.execute(
                text(
                    """
                    UPDATE organizations
                    SET monthly_api_usage = monthly_api_usage + 1,
                        updated_at = :updated_at
                    WHERE id = :org_id
                    """
                ),
                {
                    "org_id": organization["organization_id"],
                    "updated_at": current_time,
                },
            )
            await core_db.commit()

    except Exception as exc:
        logger.error("Database error while storing document: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "code": "DATABASE_ERROR",
                "message": "Failed to store signed document",
                "details": str(exc) if settings.is_development else None,
            },
        )

    # Best-effort coalition indexing - don't fail signing if this fails
    try:
        await _index_in_coalition(
            document_id=document_id,
            organization=organization,
            request=request,
            text_hash=text_hash,
            current_time=current_time,
            db=db,
        )
    except Exception as exc:
        logger.warning("Coalition indexing failed (non-critical): %s", exc)

    verification_url = _build_verification_url(document_id=document_id, is_demo_org=is_demo_org)

    return SignResponse(
        success=True,
        document_id=document_id,
        signed_text=signed_text,
        total_sentences=len(sentences),
        verification_url=verification_url,
    )


def _build_verification_url(*, document_id: str, is_demo_org: bool) -> str:
    if settings.is_development:
        return f"http://localhost:9000/api/v1/verify/{document_id}"
    if is_demo_org:
        return f"https://verify.{settings.infrastructure_domain}/demo/{document_id}"
    return f"https://verify.{settings.infrastructure_domain}/{document_id}"


async def _index_in_coalition(
    *,
    document_id: str,
    organization: dict,
    request: SignRequest,
    text_hash: str,
    current_time: datetime,
    db: AsyncSession,
) -> None:
    """Best-effort coalition indexing."""

    try:
        # Get the owner user_id from organization_members
        org_result = await db.execute(
            text("SELECT user_id FROM organization_members WHERE organization_id = :org_id AND role = 'owner' LIMIT 1"),
            {"org_id": organization["organization_id"]},
        )
        org_row = org_result.fetchone()
        if not org_row or not org_row.user_id:
            return

        member = await coalition_client.get_member_by_user_id(str(org_row.user_id))
        if not member or member.get("status") != "active":
            return

        word_count = len(request.text.split())
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
                "Document %s indexed in coalition for member %s",
                document_id,
                member.get("member_id"),
            )
    except Exception as exc:  # pragma: no cover - external dependency
        logger.warning("Coalition indexing failed for %s: %s", document_id, exc, exc_info=True)

