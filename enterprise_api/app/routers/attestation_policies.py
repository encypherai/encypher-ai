"""Attestation policy management -- enterprise-gated CRUD."""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_organization_dep

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Attestation Policies"])


def _require_enterprise(org_context: Dict) -> str:
    """Gate access to enterprise/strategic_partner/demo tiers only."""
    tier = (org_context.get("tier") or "free").lower()
    if tier not in ("enterprise", "strategic_partner", "demo"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FEATURE_NOT_AVAILABLE",
                "message": "Attestation policies require Enterprise plan.",
                "required_tier": "enterprise",
            },
        )
    return org_context["organization_id"]


# -- Request / response schemas ------------------------------------------------


class PolicyRule(BaseModel):
    field: str = Field(..., description="Field to check: model_provider, confidence_score, reviewer_role, human_reviewed")
    operator: str = Field(..., description="Comparison: eq, gte, lte, in, contains")
    value: Any
    action: str = Field(..., description="Action: warn, block, require_review")


class CreatePolicyRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    enforcement: str = Field(default="warn", description="warn, block, or audit")
    scope: Optional[str] = None
    rules: List[PolicyRule] = Field(default_factory=list)


class UpdatePolicyRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    enforcement: Optional[str] = None
    scope: Optional[str] = None
    rules: Optional[List[PolicyRule]] = None
    active: Optional[bool] = None


# -- Helpers -------------------------------------------------------------------


def _policy_to_dict(p: Any) -> Dict[str, Any]:
    return {
        "id": str(p.id),
        "name": p.name,
        "description": getattr(p, "description", None),
        "enforcement": p.enforcement,
        "scope": p.scope,
        "rules": p.rules or [],
        "active": p.active,
        "created_at": p.created_at.isoformat() if p.created_at else None,
        "updated_at": p.updated_at.isoformat() if p.updated_at else None,
    }


def _attestation_to_dict(a: Any) -> Dict[str, Any]:
    return {
        "id": str(a.id),
        "document_id": a.document_id,
        "policy_id": str(getattr(a, "policy_id", None)) if getattr(a, "policy_id", None) else None,
        "reviewer": getattr(a, "reviewer_identity", None),
        "model_provider": getattr(a, "model_provider", None),
        "verdict": getattr(a, "status", None),
        "confidence_score": None,
        "created_at": a.created_at.isoformat() if a.created_at else None,
    }


# -- Policy CRUD routes -------------------------------------------------------


@router.get(
    "/attestation-policies/",
    summary="List attestation policies",
    description="List all attestation policies for the authenticated enterprise organization.",
)
async def list_policies(
    active: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db),
    org_context: Dict = Depends(get_current_organization_dep),
) -> Dict[str, Any]:
    org_id = _require_enterprise(org_context)
    from app.models.attestation import AttestationPolicy

    stmt = select(AttestationPolicy).where(AttestationPolicy.organization_id == org_id)
    if active is not None:
        stmt = stmt.where(AttestationPolicy.active == active)
    stmt = stmt.order_by(AttestationPolicy.created_at.desc())
    result = await db.execute(stmt)
    policies = result.scalars().all()
    return {
        "policies": [_policy_to_dict(p) for p in policies],
        "total": len(policies),
    }


@router.post(
    "/attestation-policies/",
    status_code=status.HTTP_201_CREATED,
    summary="Create attestation policy",
    description="Create a new attestation policy defining rules and enforcement mode for content attestation.",
)
async def create_policy(
    body: CreatePolicyRequest,
    db: AsyncSession = Depends(get_db),
    org_context: Dict = Depends(get_current_organization_dep),
) -> Dict[str, Any]:
    org_id = _require_enterprise(org_context)
    from app.models.attestation import AttestationPolicy

    now = datetime.now(timezone.utc)
    policy = AttestationPolicy(
        id=uuid.uuid4(),
        organization_id=org_id,
        name=body.name,
        enforcement=body.enforcement,
        scope=body.scope or "all",
        rules=[r.model_dump() for r in body.rules],
        active=True,
        created_at=now,
        updated_at=now,
    )
    db.add(policy)
    await db.commit()
    await db.refresh(policy)
    return _policy_to_dict(policy)


@router.get("/attestation-policies/{policy_id}", summary="Get attestation policy", description="Retrieve a specific attestation policy by ID.")
async def get_policy(
    policy_id: str = Path(...),
    db: AsyncSession = Depends(get_db),
    org_context: Dict = Depends(get_current_organization_dep),
) -> Dict[str, Any]:
    org_id = _require_enterprise(org_context)
    from app.models.attestation import AttestationPolicy

    stmt = select(AttestationPolicy).where(
        AttestationPolicy.id == policy_id,
        AttestationPolicy.organization_id == org_id,
    )
    result = await db.execute(stmt)
    policy = result.scalar_one_or_none()
    if not policy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Policy not found")
    return _policy_to_dict(policy)


@router.put(
    "/attestation-policies/{policy_id}",
    summary="Update attestation policy",
    description="Update an existing attestation policy's name, enforcement mode, scope, rules, or active state.",
)
async def update_policy(
    body: UpdatePolicyRequest,
    policy_id: str = Path(...),
    db: AsyncSession = Depends(get_db),
    org_context: Dict = Depends(get_current_organization_dep),
) -> Dict[str, Any]:
    org_id = _require_enterprise(org_context)
    from app.models.attestation import AttestationPolicy

    stmt = select(AttestationPolicy).where(
        AttestationPolicy.id == policy_id,
        AttestationPolicy.organization_id == org_id,
    )
    result = await db.execute(stmt)
    policy = result.scalar_one_or_none()
    if not policy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Policy not found")

    if body.name is not None:
        policy.name = body.name
    if body.description is not None:
        # description is not in the DB schema; store in rules metadata if needed
        pass
    if body.enforcement is not None:
        policy.enforcement = body.enforcement
    if body.scope is not None:
        policy.scope = body.scope
    if body.rules is not None:
        policy.rules = [r.model_dump() for r in body.rules]
    if body.active is not None:
        policy.active = body.active

    policy.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(policy)
    return _policy_to_dict(policy)


@router.delete(
    "/attestation-policies/{policy_id}",
    summary="Delete attestation policy",
    description="Deactivate an attestation policy. The policy is marked inactive rather than permanently deleted.",
)
async def delete_policy(
    policy_id: str = Path(...),
    db: AsyncSession = Depends(get_db),
    org_context: Dict = Depends(get_current_organization_dep),
) -> Dict[str, Any]:
    org_id = _require_enterprise(org_context)
    from app.models.attestation import AttestationPolicy

    stmt = select(AttestationPolicy).where(
        AttestationPolicy.id == policy_id,
        AttestationPolicy.organization_id == org_id,
    )
    result = await db.execute(stmt)
    policy = result.scalar_one_or_none()
    if not policy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Policy not found")

    policy.active = False
    policy.updated_at = datetime.now(timezone.utc)
    await db.commit()
    return {"success": True, "message": "Policy deactivated"}


# -- Attestation list route ----------------------------------------------------


@router.get("/attestations/", summary="List attestations", description="List attestation records for the authenticated enterprise organization.")
async def list_attestations(
    document_id: Optional[str] = Query(None),
    verdict: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    org_context: Dict = Depends(get_current_organization_dep),
) -> Dict[str, Any]:
    org_id = _require_enterprise(org_context)
    from app.models.attestation import Attestation

    stmt = select(Attestation).where(Attestation.organization_id == org_id)
    count_stmt = select(func.count(Attestation.id)).where(Attestation.organization_id == org_id)

    if document_id:
        stmt = stmt.where(Attestation.document_id == document_id)
        count_stmt = count_stmt.where(Attestation.document_id == document_id)
    if verdict:
        stmt = stmt.where(Attestation.status == verdict)
        count_stmt = count_stmt.where(Attestation.status == verdict)

    stmt = stmt.order_by(Attestation.created_at.desc()).offset(offset).limit(limit)
    result = await db.execute(stmt)
    attestations = result.scalars().all()

    total = (await db.execute(count_stmt)).scalar() or 0

    return {
        "attestations": [_attestation_to_dict(a) for a in attestations],
        "total": total,
    }
