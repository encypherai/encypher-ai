"""
Formal Notice Management Router.

Formal notice is the legal mechanism that transforms innocent infringement
into willful infringement. These endpoints manage the notice lifecycle:
create → deliver → evidence package.

Once a notice is delivered, its content is cryptographically locked.
"""

import logging
from typing import Any, Dict, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_organization_dep

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/notices", tags=["Formal Notices"])


def _notice_service():
    from app.services.rights_service import rights_service
    return rights_service


# ─────────────────────────────────────────────────────────────────────────────
# Create Notice
# ─────────────────────────────────────────────────────────────────────────────


@router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    summary="Create a formal notice",
    description="""
Create a formal notice for an AI company or other entity.

The notice text is SHA-256 hashed on creation. Once delivered, the content is
cryptographically locked and cannot be changed. Every event in the notice
lifecycle is recorded in an append-only evidence chain.

**Notice types:**
- `licensing_notice` — Informational notice that content is registered
- `cease_and_desist` — Legal demand to stop using content without license
- `dmca_takedown` — DMCA formal takedown notice
- `formal_awareness` — Formal record that the entity is aware of rights

Requires: Organization admin.
    """,
)
async def create_formal_notice(
    request: Request,
    notice_data: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    org_context: Dict = Depends(get_current_organization_dep),
) -> Dict[str, Any]:
    org_id: str = org_context["organization_id"]
    svc = _notice_service()

    try:
        notice = await svc.create_notice(
            db=db,
            organization_id=org_id,
            notice_data=notice_data,
            created_by=None,
        )
        return _notice_to_dict(notice)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
    except Exception:
        logger.exception("Failed to create formal notice for org %s", org_id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create formal notice")


# ─────────────────────────────────────────────────────────────────────────────
# Get Notice
# ─────────────────────────────────────────────────────────────────────────────


@router.get(
    "/{notice_id}",
    status_code=status.HTTP_200_OK,
    summary="Get notice details and delivery status",
    description="""
Retrieve a formal notice with its full cryptographic proof, delivery confirmations,
and response history.
    """,
)
async def get_formal_notice(
    notice_id: str = Path(..., description="Notice UUID"),
    db: AsyncSession = Depends(get_db),
    org_context: Dict = Depends(get_current_organization_dep),
) -> Dict[str, Any]:
    org_id: str = org_context["organization_id"]
    svc = _notice_service()

    notice = await svc.get_notice(db=db, notice_id=notice_id)
    if not notice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notice not found")

    # Scope check — only the owning org can see the notice
    if notice.organization_id != org_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return _notice_to_dict(notice, include_evidence=True)


# ─────────────────────────────────────────────────────────────────────────────
# List Notices
# ─────────────────────────────────────────────────────────────────────────────


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="List formal notices for the organization",
)
async def list_notices(
    db: AsyncSession = Depends(get_db),
    org_context: Dict = Depends(get_current_organization_dep),
) -> List[Dict[str, Any]]:
    org_id: str = org_context["organization_id"]
    svc = _notice_service()

    notices = await svc.list_notices(db=db, organization_id=org_id)
    return [_notice_to_dict(n) for n in notices]


# ─────────────────────────────────────────────────────────────────────────────
# Deliver Notice
# ─────────────────────────────────────────────────────────────────────────────


@router.post(
    "/{notice_id}/deliver",
    status_code=status.HTTP_200_OK,
    summary="Deliver a formal notice",
    description="""
Deliver the formal notice via available channels (email, API, registered mail).

**Once a notice is delivered:**
1. Its content is cryptographically locked (notice_text and notice_hash cannot change)
2. A delivery receipt is generated with timestamp and cryptographic proof
3. The delivery event is appended to the evidence chain

Delivery methods:
- `email` — Send via Encypher notification service
- `api` — Record as API-delivered (recipient must acknowledge via API)
- `registered_mail` — Record manual registered mail delivery

Returns delivery receipt with timestamp and cryptographic proof.
    """,
)
async def deliver_notice(
    request: Request,
    notice_id: str = Path(..., description="Notice UUID"),
    delivery_data: Dict[str, Any] = ...,
    db: AsyncSession = Depends(get_db),
    org_context: Dict = Depends(get_current_organization_dep),
) -> Dict[str, Any]:
    org_id: str = org_context["organization_id"]
    svc = _notice_service()

    notice = await svc.get_notice(db=db, notice_id=notice_id)
    if not notice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notice not found")

    if notice.organization_id != org_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    if notice.status == "delivered":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Notice has already been delivered. Notice content is now locked.",
        )

    delivery_method = delivery_data.get("delivery_method", "api")

    try:
        notice = await svc.deliver_notice(
            db=db,
            notice_id=notice_id,
            delivery_method=delivery_method,
            delivery_info={
                **delivery_data,
                "requester_ip": request.client.host if request.client else None,
            },
        )
        return {
            "notice_id": str(notice.id),
            "status": notice.status,
            "delivered_at": notice.delivered_at.isoformat() if notice.delivered_at else None,
            "delivery_method": notice.delivery_method,
            "delivery_receipt": notice.delivery_receipt,
            "delivery_receipt_hash": notice.delivery_receipt_hash,
            "message": "Notice delivered and content locked. The notice is now admissible as evidence.",
        }
    except Exception:
        logger.exception("Failed to deliver notice %s", notice_id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to deliver notice")


# ─────────────────────────────────────────────────────────────────────────────
# Evidence Package
# ─────────────────────────────────────────────────────────────────────────────


@router.get(
    "/{notice_id}/evidence",
    status_code=status.HTTP_200_OK,
    summary="Generate court-ready evidence package",
    description="""
Generate a court-ready evidence package proving:
1. Content was cryptographically signed (original signed content with Merkle proofs)
2. Formal notice was created with specific content (notice hash)
3. Notice was delivered with confirmed receipt (delivery chain)
4. Rights terms were in effect at time of signing (rights snapshot)
5. Complete chain-of-custody documentation

The evidence package includes:
- Original signed content with C2PA manifest references
- Formal notice with SHA-256 hash
- Full evidence chain with each event's hash (tamper-evident linked list)
- Delivery confirmation with timestamp
- Rights terms at time of signing
    """,
)
async def get_evidence_package(
    notice_id: str = Path(..., description="Notice UUID"),
    db: AsyncSession = Depends(get_db),
    org_context: Dict = Depends(get_current_organization_dep),
) -> Dict[str, Any]:
    org_id: str = org_context["organization_id"]
    svc = _notice_service()

    notice = await svc.get_notice(db=db, notice_id=notice_id)
    if not notice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notice not found")

    if notice.organization_id != org_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    try:
        package = await svc.generate_evidence_package(db=db, notice_id=notice_id)
        return package
    except Exception:
        logger.exception("Failed to generate evidence package for notice %s", notice_id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to generate evidence package")


# ─────────────────────────────────────────────────────────────────────────────
# Serializers
# ─────────────────────────────────────────────────────────────────────────────


def _notice_to_dict(notice, include_evidence: bool = False) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "id": str(notice.id),
        "organization_id": notice.organization_id,
        "created_at": notice.created_at.isoformat() if notice.created_at else None,
        "target_entity_name": notice.target_entity_name,
        "target_entity_domain": notice.target_entity_domain,
        "target_contact_email": notice.target_contact_email,
        "target_entity_type": notice.target_entity_type,
        "scope_type": notice.scope_type,
        "scope_document_ids": [str(d) for d in (notice.scope_document_ids or [])],
        "notice_type": notice.notice_type,
        "notice_hash": notice.notice_hash,
        "demands": notice.demands,
        "status": notice.status,
        "delivered_at": notice.delivered_at.isoformat() if notice.delivered_at else None,
        "delivery_method": notice.delivery_method,
        "delivery_receipt_hash": notice.delivery_receipt_hash,
        "acknowledged_at": notice.acknowledged_at.isoformat() if notice.acknowledged_at else None,
    }

    if include_evidence:
        result["notice_text"] = notice.notice_text
        result["delivery_receipt"] = notice.delivery_receipt
        result["response"] = notice.response
        if notice.evidence_chain:
            result["evidence_chain"] = [
                {
                    "id": str(e.id),
                    "event_type": e.event_type,
                    "event_data": e.event_data,
                    "event_hash": e.event_hash,
                    "previous_hash": e.previous_hash,
                    "created_at": e.created_at.isoformat() if e.created_at else None,
                }
                for e in notice.evidence_chain
            ]

    return result
