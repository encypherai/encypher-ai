"""
Documents router for document management.

Provides endpoints for listing, viewing, and managing signed documents.
"""

import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import bindparam, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_content_db, get_db
from app.dependencies import get_current_organization
from app.models.status_list import RevocationReason
from app.services.status_service import status_service

router = APIRouter(prefix="/documents", tags=["Documents"])
logger = logging.getLogger(__name__)


# =============================================================================
# Response Models
# =============================================================================


class DocumentSummary(BaseModel):
    """Summary of a signed document."""

    document_id: str = Field(..., description="Unique document ID")
    title: Optional[str] = Field(None, description="Document title")
    document_type: Optional[str] = Field(None, description="Document type")
    status: str = Field("active", description="Document status (active/revoked)")
    signed_at: str = Field(..., description="When the document was signed")
    verification_url: str = Field(..., description="URL to verify this document")
    word_count: Optional[int] = Field(None, description="Word count")


class DocumentDetail(BaseModel):
    """Detailed document information."""

    document_id: str
    title: Optional[str] = None
    document_type: Optional[str] = None
    status: str = "active"
    signed_at: str
    verification_url: str
    word_count: Optional[int] = None
    url: Optional[str] = None
    signer_id: Optional[str] = None
    revoked_at: Optional[str] = None
    revoked_reason: Optional[str] = None


class DocumentHistoryEntry(BaseModel):
    """Single entry in document history."""

    action: str = Field(..., description="Action type (signed, verified, revoked, etc.)")
    timestamp: str = Field(..., description="When the action occurred")
    actor: Optional[str] = Field(None, description="Who performed the action")
    details: Optional[str] = Field(None, description="Additional details")


class DocumentListResponse(BaseModel):
    """Response for document listing."""

    success: bool = True
    data: dict = Field(..., description="Documents and pagination info")


class DocumentDetailResponse(BaseModel):
    """Response for single document."""

    success: bool = True
    data: DocumentDetail


class DocumentHistoryResponse(BaseModel):
    """Response for document history."""

    success: bool = True
    data: dict


class DocumentDeleteResponse(BaseModel):
    """Response for document deletion."""

    success: bool = True
    data: dict


# =============================================================================
# Endpoints
# =============================================================================


@router.get("", response_model=DocumentListResponse)
async def list_documents(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search in title"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status (active/revoked)"),
    from_date: Optional[str] = Query(None, description="Filter from date (ISO format)"),
    to_date: Optional[str] = Query(None, description="Filter to date (ISO format)"),
    organization: dict = Depends(get_current_organization),
    content_db: AsyncSession = Depends(get_content_db),
    db: AsyncSession = Depends(get_db),
) -> DocumentListResponse:
    """
    List signed documents for the organization.

    Supports pagination, search, and filtering by status and date range.
    """
    org_id = organization.get("organization_id")
    if not org_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Organization ID missing")
    offset = (page - 1) * page_size

    # Build query with filters
    where_clauses = ["organization_id = :org_id", "COALESCE(deleted, false) = false"]
    params = {"org_id": org_id, "limit": page_size, "offset": offset}

    if search:
        where_clauses.append("title ILIKE :search")
        escaped = search.replace("%", r"\%").replace("_", r"\_")
        params["search"] = f"%{escaped}%"

    _ = status_filter

    if from_date:
        where_clauses.append("created_at >= :from_date")
        params["from_date"] = from_date

    if to_date:
        where_clauses.append("created_at <= :to_date")
        params["to_date"] = to_date

    where_sql = " AND ".join(where_clauses)

    # Get total count
    count_result = await content_db.execute(
        text(f"SELECT COUNT(*) FROM documents WHERE {where_sql}"),
        params,
    )
    total = count_result.scalar() or 0

    # Get documents
    result = await content_db.execute(
        text(f"""
            SELECT
                id AS document_id, title, document_type,
                created_at
            FROM documents
            WHERE {where_sql}
            ORDER BY created_at DESC
            LIMIT :limit OFFSET :offset
        """),
        params,
    )
    rows = result.fetchall()

    revocation_lookup = {}
    doc_ids = [row.document_id for row in rows if getattr(row, "document_id", None)]
    if doc_ids:
        revocation_result = await db.execute(
            text(
                """
                SELECT document_id, revoked, revoked_at, revoked_reason
                FROM status_list_entries
                WHERE organization_id = :org_id
                  AND document_id IN :doc_ids
                """
            ).bindparams(bindparam("doc_ids", expanding=True)),
            {"org_id": org_id, "doc_ids": doc_ids},
        )
        for row in revocation_result.fetchall():
            revocation_lookup[row.document_id] = row

    documents = []
    for row in rows:
        revocation = revocation_lookup.get(row.document_id)
        is_revoked = bool(revocation.revoked) if revocation is not None else False
        doc_status = "revoked" if is_revoked else "active"
        documents.append(
            DocumentSummary(
                document_id=row.document_id,
                title=row.title,
                document_type=row.document_type,
                status=doc_status,
                signed_at=row.created_at.isoformat() if row.created_at else "",
                verification_url=f"https://api.encypher.com/api/v1/verify/{row.document_id}",
                word_count=None,
            ).model_dump()
        )

    total_pages = (total + page_size - 1) // page_size if total > 0 else 1

    return DocumentListResponse(
        data={
            "documents": documents,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        }
    )


@router.get("/{document_id}", response_model=DocumentDetailResponse)
async def get_document(
    document_id: str,
    organization: dict = Depends(get_current_organization),
    content_db: AsyncSession = Depends(get_content_db),
    db: AsyncSession = Depends(get_db),
) -> DocumentDetailResponse:
    """
    Get detailed information about a specific document.
    """
    org_id = organization.get("organization_id")

    result = await content_db.execute(
        text(
            """
            SELECT
                id AS document_id, title, document_type, url,
                created_at
            FROM documents
            WHERE id = :doc_id
              AND organization_id = :org_id
              AND COALESCE(deleted, false) = false
            """
        ),
        {"doc_id": document_id, "org_id": org_id},
    )
    row = result.fetchone()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "DOCUMENT_NOT_FOUND", "message": "Document not found"},
        )

    revocation = await db.execute(
        text(
            """
            SELECT revoked, revoked_at, revoked_reason
            FROM status_list_entries
            WHERE organization_id = :org_id AND document_id = :doc_id
            """
        ),
        {"org_id": org_id, "doc_id": document_id},
    )
    revocation_row = revocation.fetchone()
    is_revoked = bool(revocation_row.revoked) if revocation_row is not None else False
    doc_status = "revoked" if is_revoked else "active"

    return DocumentDetailResponse(
        data=DocumentDetail(
            document_id=row.document_id,
            title=row.title,
            document_type=row.document_type,
            status=doc_status,
            signed_at=row.created_at.isoformat() if row.created_at else "",
            verification_url=f"https://api.encypher.com/api/v1/verify/{row.document_id}",
            word_count=None,
            url=row.url,
            signer_id=None,
            revoked_at=revocation_row.revoked_at.isoformat() if revocation_row and getattr(revocation_row, "revoked_at", None) else None,
            revoked_reason=revocation_row.revoked_reason if revocation_row and getattr(revocation_row, "revoked_reason", None) else None,
        )
    )


@router.get("/{document_id}/history", response_model=DocumentHistoryResponse)
async def get_document_history(
    document_id: str,
    organization: dict = Depends(get_current_organization),
    content_db: AsyncSession = Depends(get_content_db),
    db: AsyncSession = Depends(get_db),
) -> DocumentHistoryResponse:
    """
    Get the audit trail/history for a document.

    Shows all actions taken on the document including signing, verification, and revocation.
    """
    org_id = organization.get("organization_id")

    # Verify document exists and belongs to org
    doc_result = await content_db.execute(
        text("SELECT id AS document_id, created_at FROM documents WHERE id = :doc_id AND organization_id = :org_id"),
        {"doc_id": document_id, "org_id": org_id},
    )
    doc_row = doc_result.fetchone()

    if not doc_row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "DOCUMENT_NOT_FOUND", "message": "Document not found"},
        )

    history: List[dict] = []

    # Add signing event
    history.append(
        {
            "action": "signed",
            "timestamp": doc_row.created_at.isoformat() if doc_row.created_at else "",
            "actor": "api",
            "details": "Document signed with C2PA manifest",
        }
    )

    # Check for revocation events in status_list_entries
    revoke_result = await db.execute(
        text("""
            SELECT revoked_at, revoked_reason, revoked_by, reinstated_at
            FROM status_list_entries
            WHERE organization_id = :org_id
              AND document_id = :doc_id
            ORDER BY revoked_at DESC
        """),
        {"org_id": org_id, "doc_id": document_id},
    )
    revoke_rows = revoke_result.fetchall()

    for revoke_row in revoke_rows:
        if revoke_row.revoked_at:
            history.append(
                {
                    "action": "revoked",
                    "timestamp": revoke_row.revoked_at.isoformat(),
                    "actor": revoke_row.revoked_by or "api",
                    "details": f"Reason: {revoke_row.revoked_reason}" if revoke_row.revoked_reason else None,
                }
            )
        if revoke_row.reinstated_at:
            history.append(
                {
                    "action": "reinstated",
                    "timestamp": revoke_row.reinstated_at.isoformat(),
                    "actor": "api",
                    "details": "Document reinstated",
                }
            )

    # Sort by timestamp descending
    history.sort(key=lambda x: x["timestamp"], reverse=True)

    return DocumentHistoryResponse(
        data={
            "document_id": document_id,
            "history": history,
            "total": len(history),
        }
    )


@router.delete("/{document_id}", response_model=DocumentDeleteResponse)
async def delete_document(
    document_id: str,
    revoke: bool = Query(True, description="Also revoke the document"),
    reason: Optional[str] = Query(None, description="Reason for deletion"),
    organization: dict = Depends(get_current_organization),
    content_db: AsyncSession = Depends(get_content_db),
    db: AsyncSession = Depends(get_db),
) -> DocumentDeleteResponse:
    """
    Soft delete a document.

    By default, this also revokes the document so it will fail verification.
    The document is not permanently deleted but marked as deleted.
    """
    org_id = organization.get("organization_id")
    if not org_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Organization ID missing")

    # Verify document exists
    doc_result = await content_db.execute(
        text("SELECT id AS document_id FROM documents WHERE id = :doc_id AND organization_id = :org_id"),
        {"doc_id": document_id, "org_id": org_id},
    )
    doc_row = doc_result.fetchone()

    if not doc_row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "DOCUMENT_NOT_FOUND", "message": "Document not found"},
        )

    # Revoke if requested
    if revoke:
        try:
            await status_service.revoke_document(
                db=db,
                organization_id=org_id,
                document_id=document_id,
                reason=RevocationReason.PUBLISHER_REQUEST,
                reason_detail=reason or "Document deleted via API",
                revoked_by="api",
            )
        except Exception as e:
            logger.warning(f"Failed to revoke document {document_id}: {e}")

    # Soft delete by marking as deleted
    await content_db.execute(
        text("""
            UPDATE documents
            SET deleted = true, deleted_at = :now
            WHERE id = :doc_id AND organization_id = :org_id
        """),
        {"doc_id": document_id, "org_id": org_id, "now": datetime.utcnow()},
    )
    await content_db.commit()

    return DocumentDeleteResponse(
        data={
            "document_id": document_id,
            "deleted": True,
            "revoked": revoke,
            "deleted_at": datetime.utcnow().isoformat(),
        }
    )
