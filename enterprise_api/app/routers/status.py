"""
Status router for document revocation management.

TEAM_002: Implements per-document revocation via W3C StatusList2021.
Provides endpoints for:
- Revoking documents
- Reinstating documents
- Serving status lists (public, CDN-cacheable)
- Querying document status
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_organization
from app.models.status_list import RevocationReason, StatusListEntry, StatusListMetadata
from app.services.status_service import status_service

router = APIRouter(prefix="/status", tags=["Status & Revocation"])
logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Request/Response Models
# -----------------------------------------------------------------------------


class RevokeRequest(BaseModel):
    """Request to revoke a document."""

    reason: RevocationReason = Field(..., description="Revocation reason code")
    reason_detail: Optional[str] = Field(None, description="Detailed explanation")


class ReinstateRequest(BaseModel):
    """Request to reinstate a revoked document."""

    pass  # No additional fields needed


class DocumentStatusResponse(BaseModel):
    """Response for document status query."""

    document_id: str
    organization_id: str
    revoked: bool
    revoked_at: Optional[str] = None
    revoked_reason: Optional[str] = None
    revoked_reason_detail: Optional[str] = None
    reinstated_at: Optional[str] = None
    status_list_url: Optional[str] = None
    status_list_index: Optional[int] = None
    status_bit_index: Optional[int] = None


class RevocationResponse(BaseModel):
    """Response for revocation/reinstatement actions."""

    success: bool
    document_id: str
    action: str  # "revoked" or "reinstated"
    timestamp: str
    message: str


# -----------------------------------------------------------------------------
# Document Revocation Endpoints
# -----------------------------------------------------------------------------


@router.post("/documents/{document_id}/revoke", response_model=RevocationResponse)
async def revoke_document(
    document_id: str,
    request: RevokeRequest,
    db: AsyncSession = Depends(get_db),
    org: dict = Depends(get_current_organization),
):
    """
    Revoke a document's authenticity.

    The document will fail verification within 5 minutes (CDN cache TTL).
    This action is reversible via the reinstate endpoint.

    **Revocation Reasons:**
    - `factual_error`: Content contains factual errors
    - `legal_takedown`: Legal request (DMCA, court order)
    - `copyright_claim`: Copyright infringement claim
    - `privacy_request`: Privacy/GDPR request
    - `publisher_request`: Publisher-initiated takedown
    - `security_concern`: Security vulnerability in content
    - `content_policy`: Violates content policy
    - `other`: Other reason (specify in reason_detail)
    """
    organization_id = org.get("organization_id") or org.get("id")
    if not organization_id:
        raise HTTPException(status_code=400, detail="Organization ID missing")
    user_id = org.get("user_id", "api")

    try:
        entry = await status_service.revoke_document(
            db=db,
            organization_id=organization_id,
            document_id=document_id,
            reason=request.reason,
            reason_detail=request.reason_detail,
            revoked_by=user_id,
        )
        await db.commit()

        return RevocationResponse(
            success=True,
            document_id=document_id,
            action="revoked",
            timestamp=entry.revoked_at.isoformat() if entry.revoked_at else "",
            message=f"Document {document_id} has been revoked. Verification will fail within 5 minutes.",
        )

    except ValueError as e:
        logger.warning(f"Revocation validation error for document {document_id}: {e}")
        raise HTTPException(status_code=404, detail="Document not found or already revoked")
    except Exception as e:
        logger.error(f"Failed to revoke document {document_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to revoke document")


@router.post("/documents/{document_id}/reinstate", response_model=RevocationResponse)
async def reinstate_document(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    org: dict = Depends(get_current_organization),
):
    """
    Reinstate a previously revoked document.

    The document will pass verification again within 5 minutes (CDN cache TTL).
    """
    organization_id = org.get("organization_id") or org.get("id")
    if not organization_id:
        raise HTTPException(status_code=400, detail="Organization ID missing")
    user_id = org.get("user_id", "api")

    try:
        entry = await status_service.reinstate_document(
            db=db,
            organization_id=organization_id,
            document_id=document_id,
            reinstated_by=user_id,
        )
        await db.commit()

        return RevocationResponse(
            success=True,
            document_id=document_id,
            action="reinstated",
            timestamp=entry.reinstated_at.isoformat() if entry.reinstated_at else "",
            message=f"Document {document_id} has been reinstated. Verification will pass within 5 minutes.",
        )

    except ValueError as e:
        logger.warning(f"Reinstatement validation error for document {document_id}: {e}")
        raise HTTPException(status_code=404, detail="Document not found or not revoked")
    except Exception as e:
        logger.error(f"Failed to reinstate document {document_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to reinstate document")


@router.get("/documents/{document_id}", response_model=DocumentStatusResponse)
async def get_document_status(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    org: dict = Depends(get_current_organization),
):
    """
    Get the revocation status of a document.
    """
    organization_id = org.get("organization_id") or org.get("id")
    if not organization_id:
        raise HTTPException(status_code=400, detail="Organization ID missing")

    from sqlalchemy import select

    result = await db.execute(
        select(StatusListEntry).where(
            StatusListEntry.organization_id == organization_id,
            StatusListEntry.document_id == document_id,
        )
    )
    entry = result.scalar_one_or_none()

    if not entry:
        raise HTTPException(status_code=404, detail=f"Document {document_id} not found in status list")

    status_list_url = status_service._build_status_list_url(organization_id, int(entry.list_index))

    return DocumentStatusResponse(
        document_id=document_id,
        organization_id=organization_id,
        revoked=entry.revoked,
        revoked_at=entry.revoked_at.isoformat() if entry.revoked_at else None,
        revoked_reason=entry.revoked_reason,
        revoked_reason_detail=entry.revoked_reason_detail,
        reinstated_at=entry.reinstated_at.isoformat() if entry.reinstated_at else None,
        status_list_url=status_list_url,
        status_list_index=entry.list_index,
        status_bit_index=entry.bit_index,
    )


# -----------------------------------------------------------------------------
# Public Status List Endpoint (CDN-cacheable)
# -----------------------------------------------------------------------------


@router.get(
    "/list/{organization_id}/{list_index}",
    response_class=JSONResponse,
    include_in_schema=True,
)
async def get_status_list(
    organization_id: str,
    list_index: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Get a status list credential (public, no auth required).

    This endpoint serves W3C StatusList2021 credentials for verification.
    Responses are designed to be cached by CDN with 5-minute TTL.

    **Response Format:** W3C StatusList2021Credential (JSON-LD)
    """
    from sqlalchemy import select

    # Check if list exists
    result = await db.execute(
        select(StatusListMetadata).where(
            StatusListMetadata.organization_id == organization_id,
            StatusListMetadata.list_index == list_index,
        )
    )
    metadata = result.scalar_one_or_none()

    if not metadata:
        raise HTTPException(status_code=404, detail=f"Status list {organization_id}/{list_index} not found")

    # Generate the status list credential
    credential = await status_service.generate_status_list(
        db=db,
        organization_id=organization_id,
        list_index=list_index,
    )
    await db.commit()

    # Return with cache headers
    return JSONResponse(
        content=credential,
        headers={
            "Cache-Control": "public, max-age=300",  # 5 minutes
            "Content-Type": "application/json",
            "ETag": f'"{metadata.cdn_etag}"' if metadata.cdn_etag else "",
        },
    )


# -----------------------------------------------------------------------------
# Admin/Reporting Endpoints
# -----------------------------------------------------------------------------


@router.get("/stats")
async def get_status_stats(
    db: AsyncSession = Depends(get_db),
    org: dict = Depends(get_current_organization),
):
    """
    Get status list statistics for the organization.
    """
    organization_id = org.get("organization_id") or org.get("id")

    from sqlalchemy import select

    # Get list metadata
    result = await db.execute(
        select(StatusListMetadata).where(StatusListMetadata.organization_id == organization_id).order_by(StatusListMetadata.list_index)
    )
    lists = result.scalars().all()

    # Calculate totals
    total_documents = sum(m.total_documents for m in lists)
    total_revoked = sum(m.revoked_count for m in lists)
    total_lists = len(lists)

    return {
        "organization_id": organization_id,
        "total_documents": total_documents,
        "total_revoked": total_revoked,
        "revocation_rate": (total_revoked / total_documents * 100) if total_documents > 0 else 0,
        "total_lists": total_lists,
        "lists": [
            {
                "list_index": m.list_index,
                "total_documents": m.total_documents,
                "revoked_count": m.revoked_count,
                "capacity_remaining": m.capacity_remaining,
                "utilization_percent": round(m.utilization_percent, 2),
                "last_generated_at": m.last_generated_at.isoformat() if m.last_generated_at else None,
                "current_version": m.current_version,
            }
            for m in lists
        ],
    }
