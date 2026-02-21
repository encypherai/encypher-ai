"""
Rights Licensing Request/Response Router.

Manages the publisher ↔ consumer licensing transaction flow.
Distinct from the existing licensing.py which covers Encypher-managed
AI company agreements.
"""

import logging
from typing import Any, Dict, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request, status
from sqlalchemy import select, desc, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_organization_dep

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/rights-licensing", tags=["Rights Licensing Transactions"])


def _svc():
    from app.services.rights_service import rights_service
    return rights_service


# ─────────────────────────────────────────────────────────────────────────────
# Licensing Requests
# ─────────────────────────────────────────────────────────────────────────────


@router.post(
    "/request",
    status_code=status.HTTP_201_CREATED,
    summary="Submit a licensing request",
    description="""
Submit a licensing request for publisher content.

**Requester** (AI company / consumer): Sends a request to a publisher for
rights to use their content at a specific tier (bronze, silver, or gold).

The publisher is notified and can approve, counter, or reject the request.
    """,
)
async def create_licensing_request(
    request: Request,
    request_data: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    org_context: Dict = Depends(get_current_organization_dep),
) -> Dict[str, Any]:
    requester_org_id: str = org_context["organization_id"]
    publisher_org_id = request_data.get("organization_id") or request_data.get("publisher_org_id")

    if not publisher_org_id:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="organization_id (publisher) is required")

    tier = request_data.get("tier")
    if tier not in ("bronze", "silver", "gold"):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="tier must be bronze, silver, or gold")

    try:
        from app.models.rights import RightsLicensingRequest
        from datetime import datetime, timezone
        import uuid as _uuid

        req = RightsLicensingRequest(
            id=_uuid.uuid4(),
            publisher_org_id=publisher_org_id,
            requester_org_id=requester_org_id,
            tier=tier,
            scope=request_data.get("scope", {}),
            proposed_terms=request_data.get("proposed_terms", {}),
            requester_info={
                **request_data.get("requester", {}),
                "requester_ip": request.client.host if request.client else None,
            },
            status="pending",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(req)
        await db.commit()
        await db.refresh(req)

        # Write audit log
        svc = _svc()
        await svc._write_audit_log(
            db=db,
            organization_id=publisher_org_id,
            action="licensing_request_submitted",
            resource_type="rights_licensing_request",
            resource_id=req.id,
            old_value=None,
            new_value={"tier": tier, "requester_org": requester_org_id},
        )

        return {
            "request_id": str(req.id),
            "status": req.status,
            "publisher_org_id": publisher_org_id,
            "requester_org_id": requester_org_id,
            "tier": tier,
            "created_at": req.created_at.isoformat(),
            "message": "Licensing request submitted. The publisher will be notified.",
            "estimated_response": "3-5 business days",
        }
    except HTTPException:
        raise
    except Exception:
        logger.exception("Failed to create licensing request")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to submit licensing request")


@router.get(
    "/requests",
    status_code=status.HTTP_200_OK,
    summary="List licensing requests",
    description="""
List licensing requests for the authenticated organization.

- **Publisher view**: incoming requests (where org is the publisher)
- **Consumer view**: outgoing requests (where org is the requester)
    """,
)
async def list_licensing_requests(
    view: str = Query("incoming", description="'incoming' (publisher) or 'outgoing' (consumer)"),
    status_filter: str = Query(None, alias="status", description="Filter by status: pending, approved, rejected, countered"),
    db: AsyncSession = Depends(get_db),
    org_context: Dict = Depends(get_current_organization_dep),
) -> List[Dict[str, Any]]:
    org_id: str = org_context["organization_id"]

    from app.models.rights import RightsLicensingRequest

    stmt = select(RightsLicensingRequest)
    if view == "incoming":
        stmt = stmt.where(RightsLicensingRequest.publisher_org_id == org_id)
    else:
        stmt = stmt.where(RightsLicensingRequest.requester_org_id == org_id)

    if status_filter:
        stmt = stmt.where(RightsLicensingRequest.status == status_filter)

    stmt = stmt.order_by(desc(RightsLicensingRequest.created_at)).limit(100)

    result = await db.execute(stmt)
    requests = result.scalars().all()

    return [_request_to_dict(r) for r in requests]


@router.put(
    "/requests/{request_id}/respond",
    status_code=status.HTTP_200_OK,
    summary="Publisher responds to a licensing request",
    description="""
Publisher approves, counters, or rejects a licensing request.

- `approve`: Creates a licensing agreement and notifies requester
- `counter`: Returns counter-proposal for negotiation
- `reject`: Declines the request with optional reason

Requires: Publisher org admin.
    """,
)
async def respond_to_licensing_request(
    request: Request,
    request_id: str = Path(..., description="Licensing request UUID"),
    response_data: Dict[str, Any] = ...,
    db: AsyncSession = Depends(get_db),
    org_context: Dict = Depends(get_current_organization_dep),
) -> Dict[str, Any]:
    org_id: str = org_context["organization_id"]

    from app.models.rights import RightsLicensingRequest, RightsLicensingAgreement
    from datetime import datetime, timezone
    import uuid as _uuid

    req = await db.get(RightsLicensingRequest, _uuid.UUID(request_id))
    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Licensing request not found")

    if req.publisher_org_id != org_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the publisher can respond to this request")

    if req.status not in ("pending", "countered"):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Cannot respond to request in status '{req.status}'")

    action = response_data.get("action")
    if action not in ("approve", "counter", "reject"):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="action must be: approve, counter, or reject")

    now = datetime.now(timezone.utc)
    req.response = {
        "action": action,
        "terms": response_data.get("terms", {}),
        "message": response_data.get("message", ""),
        "responded_at": now.isoformat(),
    }
    req.responded_at = now
    req.updated_at = now

    agreement = None
    if action == "approve":
        req.status = "approved"
        # Create licensing agreement
        final_terms = response_data.get("terms") or req.proposed_terms
        effective_date_str = final_terms.get("effective_date")
        effective_date = datetime.fromisoformat(effective_date_str) if effective_date_str else now

        agreement = RightsLicensingAgreement(
            id=_uuid.uuid4(),
            request_id=req.id,
            publisher_org_id=req.publisher_org_id,
            licensee_org_id=req.requester_org_id,
            tier=req.tier,
            scope=req.scope,
            terms=final_terms,
            effective_date=effective_date,
            status="active",
            usage_metrics={},
            created_at=now,
            updated_at=now,
        )
        db.add(agreement)
        req.agreement_id = agreement.id

    elif action == "counter":
        req.status = "countered"
    else:
        req.status = "rejected"

    await db.commit()
    if req.agreement_id:
        await db.refresh(req)

    result = _request_to_dict(req)
    if agreement:
        result["agreement"] = _agreement_to_dict(agreement)

    return result


# ─────────────────────────────────────────────────────────────────────────────
# Licensing Agreements
# ─────────────────────────────────────────────────────────────────────────────


@router.get(
    "/agreements",
    status_code=status.HTTP_200_OK,
    summary="List active licensing agreements",
    description="List all licensing agreements where the authenticated organization is either the publisher or the licensee, ordered by creation date.",
)
async def list_agreements(
    db: AsyncSession = Depends(get_db),
    org_context: Dict = Depends(get_current_organization_dep),
) -> List[Dict[str, Any]]:
    org_id: str = org_context["organization_id"]

    from app.models.rights import RightsLicensingAgreement

    stmt = (
        select(RightsLicensingAgreement)
        .where(
            or_(
                RightsLicensingAgreement.publisher_org_id == org_id,
                RightsLicensingAgreement.licensee_org_id == org_id,
            )
        )
        .order_by(desc(RightsLicensingAgreement.created_at))
        .limit(100)
    )

    result = await db.execute(stmt)
    agreements = result.scalars().all()

    return [_agreement_to_dict(a) for a in agreements]


@router.get(
    "/agreements/{agreement_id}",
    status_code=status.HTTP_200_OK,
    summary="Get specific agreement details",
    description="Retrieve the full terms, scope, and status for a specific licensing agreement. Only accessible to the publisher or licensee party to the agreement.",
)
async def get_agreement(
    agreement_id: str = Path(..., description="Agreement UUID"),
    db: AsyncSession = Depends(get_db),
    org_context: Dict = Depends(get_current_organization_dep),
) -> Dict[str, Any]:
    org_id: str = org_context["organization_id"]

    from app.models.rights import RightsLicensingAgreement
    import uuid as _uuid

    agr = await db.get(RightsLicensingAgreement, _uuid.UUID(agreement_id))
    if not agr:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agreement not found")

    if agr.publisher_org_id != org_id and agr.licensee_org_id != org_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied — not a party to this agreement")

    return _agreement_to_dict(agr)


@router.get(
    "/agreements/{agreement_id}/usage",
    status_code=status.HTTP_200_OK,
    summary="Get usage metrics for an active agreement",
    description="Retrieve usage metrics (articles accessed, retrievals, ingestion events) for a specific licensing agreement. Useful for compliance monitoring and billing reconciliation.",
)
async def get_agreement_usage(
    agreement_id: str = Path(..., description="Agreement UUID"),
    db: AsyncSession = Depends(get_db),
    org_context: Dict = Depends(get_current_organization_dep),
) -> Dict[str, Any]:
    org_id: str = org_context["organization_id"]

    from app.models.rights import RightsLicensingAgreement
    import uuid as _uuid

    agr = await db.get(RightsLicensingAgreement, _uuid.UUID(agreement_id))
    if not agr:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agreement not found")

    if agr.publisher_org_id != org_id and agr.licensee_org_id != org_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return {
        "agreement_id": agreement_id,
        "tier": agr.tier,
        "status": agr.status,
        "effective_date": agr.effective_date.isoformat() if agr.effective_date else None,
        "expiry_date": agr.expiry_date.isoformat() if agr.expiry_date else None,
        "usage_metrics": agr.usage_metrics or {},
        "compliance_status": "compliant" if agr.status == "active" else "non_compliant",
    }


# ─────────────────────────────────────────────────────────────────────────────
# Serializers
# ─────────────────────────────────────────────────────────────────────────────


def _request_to_dict(req) -> Dict[str, Any]:
    return {
        "id": str(req.id),
        "publisher_org_id": req.publisher_org_id,
        "requester_org_id": req.requester_org_id,
        "tier": req.tier,
        "scope": req.scope,
        "proposed_terms": req.proposed_terms,
        "requester_info": req.requester_info,
        "status": req.status,
        "response": req.response,
        "responded_at": req.responded_at.isoformat() if req.responded_at else None,
        "agreement_id": str(req.agreement_id) if req.agreement_id else None,
        "created_at": req.created_at.isoformat() if req.created_at else None,
        "updated_at": req.updated_at.isoformat() if req.updated_at else None,
    }


def _agreement_to_dict(agr) -> Dict[str, Any]:
    return {
        "id": str(agr.id),
        "request_id": str(agr.request_id) if agr.request_id else None,
        "publisher_org_id": agr.publisher_org_id,
        "licensee_org_id": agr.licensee_org_id,
        "licensee_name": agr.licensee_name,
        "tier": agr.tier,
        "scope": agr.scope,
        "terms": agr.terms,
        "effective_date": agr.effective_date.isoformat() if agr.effective_date else None,
        "expiry_date": agr.expiry_date.isoformat() if agr.expiry_date else None,
        "auto_renew": agr.auto_renew,
        "status": agr.status,
        "usage_metrics": agr.usage_metrics,
        "created_at": agr.created_at.isoformat() if agr.created_at else None,
    }
