"""EU AI Act Compliance readiness endpoint.

Sales tool: shows what the org has done and what is missing
for EU AI Act compliance (deadline: August 2, 2026).
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_organization_dep

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/compliance", tags=["Compliance"])


@router.get("/readiness")
async def get_compliance_readiness(
    db: AsyncSession = Depends(get_db),
    org_context: Dict = Depends(get_current_organization_dep),
) -> Dict[str, Any]:
    """Return EU AI Act compliance readiness checklist for the organization."""
    org_id: str = org_context["organization_id"]
    tier: str = (org_context.get("tier") or "free").lower()
    features: dict = org_context.get("features") or {}

    items: List[Dict[str, Any]] = []

    # 1. Content signing active
    try:
        from app.models.merkle import MerkleRoot

        stmt = select(func.count(MerkleRoot.id)).where(MerkleRoot.organization_id == org_id)
        result = await db.execute(stmt)
        doc_count = result.scalar() or 0
        items.append(
            {
                "id": "content_signing",
                "label": "Content Signing Active",
                "description": "Organization has signed content with C2PA manifests",
                "status": "compliant" if doc_count > 0 else "action_needed",
                "eu_ai_act_article": "Article 50 - Transparency",
                "recommendation": ("Sign at least one document to establish content provenance" if doc_count == 0 else None),
                "action_href": "/playground",
                "category": "Content Provenance",
            }
        )
    except Exception:
        items.append(
            {
                "id": "content_signing",
                "label": "Content Signing Active",
                "description": "Organization has signed content with C2PA manifests",
                "status": "unknown",
                "eu_ai_act_article": "Article 50 - Transparency",
                "recommendation": "Unable to check signing status",
                "action_href": "/playground",
                "category": "Content Provenance",
            }
        )

    # 2. Rights profile configured
    try:
        from app.models.rights import PublisherRightsProfile

        stmt = select(func.count(PublisherRightsProfile.id)).where(PublisherRightsProfile.organization_id == org_id)
        result = await db.execute(stmt)
        profile_count = result.scalar() or 0
        items.append(
            {
                "id": "rights_profile",
                "label": "Rights Profile Configured",
                "description": ("Publisher rights profile defines how AI can use your content"),
                "status": "compliant" if profile_count > 0 else "action_needed",
                "eu_ai_act_article": "Article 53 - Provider obligations",
                "recommendation": ("Set up a rights profile to define AI usage terms" if profile_count == 0 else None),
                "action_href": "/rights",
                "category": "Rights Management",
            }
        )
    except Exception:
        items.append(
            {
                "id": "rights_profile",
                "label": "Rights Profile Configured",
                "description": ("Publisher rights profile defines how AI can use your content"),
                "status": "unknown",
                "eu_ai_act_article": "Article 53 - Provider obligations",
                "recommendation": "Unable to check rights profile",
                "action_href": "/rights",
                "category": "Rights Management",
            }
        )

    # 3. Coalition membership
    coalition_member = org_context.get("coalition_member", False)
    items.append(
        {
            "id": "coalition_member",
            "label": "Coalition Membership",
            "description": ("Part of the Encypher publisher coalition for collective enforcement"),
            "status": "compliant" if coalition_member else "action_needed",
            "eu_ai_act_article": "Article 53 - Provider obligations",
            "recommendation": ("Join the coalition for stronger collective enforcement" if not coalition_member else None),
            "action_href": "/settings",
            "category": "Rights Management",
        }
    )

    # 4. Formal notice capability
    from app.core.tier_config import is_enterprise_tier

    enterprise = is_enterprise_tier(tier)
    items.append(
        {
            "id": "formal_notice",
            "label": "Formal Notice Capability",
            "description": ("Ability to send legally binding formal notices to AI companies"),
            "status": "compliant" if enterprise else "action_needed",
            "eu_ai_act_article": "Article 53 - Provider obligations",
            "recommendation": ("Upgrade to Enterprise for formal notice capabilities" if not enterprise else None),
            "action_href": "/billing",
            "category": "Governance",
        }
    )

    # 5. Audit logs
    audit_enabled = features.get("audit_logs", False)
    items.append(
        {
            "id": "audit_logs",
            "label": "Audit Logs Enabled",
            "description": ("Complete audit trail of all content signing and verification events"),
            "status": "compliant" if audit_enabled else "action_needed",
            "eu_ai_act_article": "Article 17 - Quality management system",
            "recommendation": ("Enable audit logs for compliance documentation" if not audit_enabled else None),
            "action_href": "/audit-logs",
            "category": "Governance",
        }
    )

    # 6. Team management
    items.append(
        {
            "id": "team_management",
            "label": "Team Management Active",
            "description": ("Multiple team members with defined roles for oversight"),
            "status": "compliant" if enterprise else "action_needed",
            "eu_ai_act_article": "Article 17 - Quality management system",
            "recommendation": ("Upgrade to Enterprise for team management" if not enterprise else None),
            "action_href": "/team",
            "category": "Governance",
        }
    )

    # 7. SSO configured
    sso_enabled = features.get("sso", False)
    items.append(
        {
            "id": "sso_configured",
            "label": "SSO Configured",
            "description": "Single Sign-On for secure enterprise authentication",
            "status": "compliant" if sso_enabled else "action_needed",
            "eu_ai_act_article": "Article 15 - Accuracy, robustness and cybersecurity",
            "recommendation": ("Configure SSO for secure access control" if not sso_enabled else None),
            "action_href": "/settings",
            "category": "Governance",
        }
    )

    # Calculate readiness score
    compliant_count = sum(1 for item in items if item["status"] == "compliant")
    total_count = len(items)
    readiness_score = (compliant_count / total_count * 100) if total_count > 0 else 0

    return {
        "readiness_score": round(readiness_score, 1),
        "compliant_count": compliant_count,
        "total_count": total_count,
        "items": items,
        "eu_ai_act_deadline": "2026-08-02",
    }
