"""
Rights Management API Router — Publisher-Facing Endpoints.

Provides CRUD for publisher rights profiles, document/collection/content-type
overrides, bulk updates, and template initialization. All routes require
authentication as an organization member or admin.
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_organization_dep

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/rights", tags=["Rights Management"])


# ─────────────────────────────────────────────────────────────────────────────
# Lazy imports to avoid circular dependency at module load time.
# Models and schemas are imported inside each route handler.
# ─────────────────────────────────────────────────────────────────────────────


def _get_rights_service():
    from app.services.rights_service import rights_service

    return rights_service


def _get_templates():
    from app.core.rights_templates import get_template, list_templates

    return list_templates, get_template


# ─────────────────────────────────────────────────────────────────────────────
# Publisher Rights Profile
# ─────────────────────────────────────────────────────────────────────────────


@router.put(
    "/profile",
    status_code=status.HTTP_200_OK,
    summary="Set or update default rights profile",
    description="""
Set or update the default rights profile for the authenticated organization.

Each call creates a new immutable version (append-only). The previous profile
version is preserved for audit and legal evidence purposes.

Requires: Organization admin role.
    """,
)
async def upsert_rights_profile(
    request: Request,
    profile_data: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    org_context: Dict = Depends(get_current_organization_dep),
) -> Dict[str, Any]:
    """Create or update the publisher rights profile."""
    org_id: str = org_context["organization_id"]
    svc = _get_rights_service()

    try:
        profile = await svc.create_or_update_profile(
            db=db,
            organization_id=org_id,
            profile_data=profile_data,
            performed_by=None,
        )
        return _profile_to_dict(profile)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
    except Exception:
        logger.exception("Failed to upsert rights profile for org %s", org_id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to save rights profile")


@router.get(
    "/profile",
    status_code=status.HTTP_200_OK,
    summary="Get current rights profile",
    description="Retrieve the current (latest version) rights profile for the authenticated organization.",
)
async def get_rights_profile(
    db: AsyncSession = Depends(get_db),
    org_context: Dict = Depends(get_current_organization_dep),
) -> Dict[str, Any]:
    org_id: str = org_context["organization_id"]
    svc = _get_rights_service()

    profile = await svc.get_current_profile(db=db, organization_id=org_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No rights profile found for this organization. Use PUT /rights/profile to create one.",
        )
    return _profile_to_dict(profile)


@router.get(
    "/profile/history",
    status_code=status.HTTP_200_OK,
    summary="Rights profile version history",
    description="Retrieve the full version history of the organization's rights profile (immutable audit trail).",
)
async def get_rights_profile_history(
    db: AsyncSession = Depends(get_db),
    org_context: Dict = Depends(get_current_organization_dep),
) -> List[Dict[str, Any]]:
    org_id: str = org_context["organization_id"]
    svc = _get_rights_service()

    profiles = await svc.get_profile_history(db=db, organization_id=org_id)
    return [_profile_to_dict(p) for p in profiles]


# ─────────────────────────────────────────────────────────────────────────────
# Document-Level Overrides
# ─────────────────────────────────────────────────────────────────────────────


@router.put(
    "/documents/{document_id}",
    status_code=status.HTTP_200_OK,
    summary="Set rights override for a specific document",
    description="Override bronze/silver/gold tier terms for a single document. The override is merged on top of the publisher default profile using the priority cascade.",
)
async def set_document_rights_override(
    document_id: str = Path(..., description="Document ID (as stored in content_references.document_id)"),
    override_data: Dict[str, Any] = ...,
    db: AsyncSession = Depends(get_db),
    org_context: Dict = Depends(get_current_organization_dep),
) -> Dict[str, Any]:
    org_id: str = org_context["organization_id"]
    svc = _get_rights_service()

    try:
        override = await svc.create_document_override(
            db=db,
            organization_id=org_id,
            document_id=document_id,
            override_data={**override_data, "override_type": "document"},
        )
        return _override_to_dict(override)
    except Exception:
        logger.exception("Failed to set document override")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to set document override")


@router.put(
    "/collections/{collection_id}",
    status_code=status.HTTP_200_OK,
    summary="Set rights override for a collection of documents",
    description="Override bronze/silver/gold tier terms for all documents in a named collection. Applied after the publisher default but before any document-level override.",
)
async def set_collection_rights_override(
    collection_id: str = Path(..., description="Collection ID"),
    override_data: Dict[str, Any] = ...,
    db: AsyncSession = Depends(get_db),
    org_context: Dict = Depends(get_current_organization_dep),
) -> Dict[str, Any]:
    org_id: str = org_context["organization_id"]
    svc = _get_rights_service()

    try:
        override = await svc.create_collection_override(
            db=db,
            organization_id=org_id,
            collection_id=collection_id,
            override_data={**override_data, "override_type": "collection"},
        )
        return _override_to_dict(override)
    except Exception:
        logger.exception("Failed to set collection override")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to set collection override")


@router.put(
    "/content-types/{content_type}",
    status_code=status.HTTP_200_OK,
    summary="Set rights override for a content type",
    description="Apply rights overrides to all content of a given type (e.g., 'opinion', 'archive', 'news').",
)
async def set_content_type_rights_override(
    content_type: str = Path(..., description="Content type identifier (e.g., 'opinion', 'archive', 'news')"),
    override_data: Dict[str, Any] = ...,
    db: AsyncSession = Depends(get_db),
    org_context: Dict = Depends(get_current_organization_dep),
) -> Dict[str, Any]:
    org_id: str = org_context["organization_id"]
    svc = _get_rights_service()

    try:
        override = await svc.create_content_type_override(
            db=db,
            organization_id=org_id,
            content_type=content_type,
            override_data={**override_data, "override_type": "content_type", "content_type_filter": content_type},
        )
        return _override_to_dict(override)
    except Exception:
        logger.exception("Failed to set content-type override")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to set content-type override")


# ─────────────────────────────────────────────────────────────────────────────
# Bulk Operations
# ─────────────────────────────────────────────────────────────────────────────


@router.post(
    "/bulk-update",
    status_code=status.HTTP_200_OK,
    summary="Bulk update rights for multiple documents/collections",
)
async def bulk_update_rights(
    updates: List[Dict[str, Any]],
    db: AsyncSession = Depends(get_db),
    org_context: Dict = Depends(get_current_organization_dep),
) -> Dict[str, Any]:
    """
    Apply rights overrides to multiple documents or collections in a single call.

    Returns applied_count, skipped_count, and any errors.
    """
    org_id: str = org_context["organization_id"]
    svc = _get_rights_service()

    applied = 0
    skipped = 0
    errors: List[Dict[str, Any]] = []

    for i, update in enumerate(updates):
        try:
            await svc.create_document_override(
                db=db,
                organization_id=org_id,
                document_id=update.get("document_id"),
                override_data=update,
            )
            applied += 1
        except Exception as exc:
            errors.append({"index": i, "error": str(exc)})
            skipped += 1

    return {"applied_count": applied, "skipped_count": skipped, "errors": errors}


# ─────────────────────────────────────────────────────────────────────────────
# Rights Templates
# ─────────────────────────────────────────────────────────────────────────────


@router.get(
    "/templates",
    status_code=status.HTTP_200_OK,
    summary="List available rights profile templates",
    description="Public reference endpoint — no authentication required. Returns pre-built templates for common publisher types.",
    # Note: this route has no auth requirement (public reference)
    include_in_schema=True,
)
async def list_rights_templates() -> List[Dict[str, Any]]:
    list_templates, _ = _get_templates()
    return list_templates()


@router.post(
    "/profile/from-template/{template_id}",
    status_code=status.HTTP_200_OK,
    summary="Initialize rights profile from a template",
    description="Populate a rights profile from one of the pre-built templates. Can be customized after initialization.",
)
async def init_profile_from_template(
    request: Request,
    template_id: str = Path(..., description="Template ID (e.g., 'news_publisher_default')"),
    overrides: Optional[Dict[str, Any]] = None,
    db: AsyncSession = Depends(get_db),
    org_context: Dict = Depends(get_current_organization_dep),
) -> Dict[str, Any]:
    org_id: str = org_context["organization_id"]
    list_templates, get_template = _get_templates()
    svc = _get_rights_service()

    template = get_template(template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template '{template_id}' not found. Available: {[t['id'] for t in list_templates()]}",
        )

    # Merge overrides on top of template
    profile_data = dict(template)
    if overrides:
        profile_data.update(overrides)

    try:
        profile = await svc.create_or_update_profile(
            db=db,
            organization_id=org_id,
            profile_data=profile_data,
        )
        return _profile_to_dict(profile)
    except Exception:
        logger.exception("Failed to initialize profile from template %s", template_id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to initialize profile from template")


# ─────────────────────────────────────────────────────────────────────────────
# Platform Partner Delegated Setup
# ─────────────────────────────────────────────────────────────────────────────


@router.post(
    "/profile/delegated-setup",
    status_code=status.HTTP_201_CREATED,
    summary="Platform partner: onboard publisher with rights profile",
    description="""
Allows a strategic_partner-tier API key to set up a rights profile for a
publisher organization in a single call. The publisher's rights profile governs
all signing done on their behalf.

Requires: strategic_partner tier.
    """,
)
async def delegated_publisher_setup(
    request: Request,
    setup_data: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    org_context: Dict = Depends(get_current_organization_dep),
) -> Dict[str, Any]:
    org_id: str = org_context["organization_id"]

    # Verify this is a strategic partner
    if org_context.get("tier") not in ("strategic_partner",):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Delegated setup requires strategic_partner tier.",
        )

    publisher_org_id = setup_data.get("publisher_organization_id")
    if not publisher_org_id:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="publisher_organization_id is required")

    list_templates, get_template = _get_templates()
    svc = _get_rights_service()

    template_id = setup_data.get("template", "news_publisher_default")
    template = get_template(template_id) or {}

    profile_data = {
        **template,
        "publisher_name": setup_data.get("publisher_name", ""),
        "publisher_url": setup_data.get("publisher_url"),
        "contact_email": setup_data.get("contact_email", ""),
        **setup_data.get("overrides", {}),
    }

    try:
        profile = await svc.create_or_update_profile(
            db=db,
            organization_id=publisher_org_id,
            profile_data=profile_data,
        )
        return {
            "publisher_organization_id": publisher_org_id,
            "partner_organization_id": org_id,
            "profile": _profile_to_dict(profile),
            "delegation": setup_data.get("delegation", {}),
        }
    except Exception:
        logger.exception("Failed delegated setup for publisher %s", publisher_org_id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed delegated setup")


# ─────────────────────────────────────────────────────────────────────────────
# RSL Import
# ─────────────────────────────────────────────────────────────────────────────


@router.post(
    "/rsl/import",
    status_code=status.HTTP_200_OK,
    summary="Import existing RSL document as rights profile",
    description="""
Import an existing RSL 1.0 XML document and create a rights profile from it.
For publishers who already have RSL set up — Encypher ingests their terms
and enhances them with provenance layer.

Mapping:
- RSL crawl terms → Bronze tier
- RSL retrieval terms → Silver tier
- RSL training terms → Gold tier
    """,
)
async def import_rsl_document(
    request: Request,
    rsl_data: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    org_context: Dict = Depends(get_current_organization_dep),
) -> Dict[str, Any]:
    org_id: str = org_context["organization_id"]
    svc = _get_rights_service()

    rsl_xml = rsl_data.get("rsl_xml") or rsl_data.get("xml")
    if not rsl_xml:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="rsl_xml field required")

    try:
        profile = await svc.import_rsl_profile(db=db, organization_id=org_id, rsl_xml=rsl_xml)
        return {"imported": True, "profile": _profile_to_dict(profile)}
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
    except Exception:
        logger.exception("Failed to import RSL for org %s", org_id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to import RSL document")


# ─────────────────────────────────────────────────────────────────────────────
# Rights Analytics
# ─────────────────────────────────────────────────────────────────────────────


@router.get(
    "/analytics/detections",
    status_code=status.HTTP_200_OK,
    summary="Get content detection analytics",
    description="Returns detection events for the org's signed content — grouped by source, domain, and date.",
)
async def get_detection_analytics(
    days: int = Query(30, ge=1, le=365, description="Number of days to include"),
    db: AsyncSession = Depends(get_db),
    org_context: Dict = Depends(get_current_organization_dep),
) -> Dict[str, Any]:
    org_id: str = org_context["organization_id"]
    svc = _get_rights_service()

    return await svc.get_detection_summary(db=db, organization_id=org_id, days=days)


@router.get(
    "/analytics/crawlers",
    status_code=status.HTTP_200_OK,
    summary="Get AI crawler activity for org content",
    description="Retrieve known AI crawler activity summary for the organization's content, including crawler identity, rights lookup rate, and licensed vs. unlicensed access breakdown.",
)
async def get_crawler_analytics(
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    org_context: Dict = Depends(get_current_organization_dep),
) -> Dict[str, Any]:
    org_id: str = org_context["organization_id"]
    svc = _get_rights_service()

    return await svc.get_crawler_summary(db=db, organization_id=org_id, days=days)


@router.get(
    "/analytics/crawlers/timeseries",
    status_code=status.HTTP_200_OK,
    summary="Get AI crawler activity timeseries",
    description="Daily crawler activity grouped by bot type for the specified period.",
)
async def get_crawler_timeseries(
    days: int = Query(30, ge=1, le=90),
    db: AsyncSession = Depends(get_db),
    org_context: Dict = Depends(get_current_organization_dep),
) -> Dict[str, Any]:
    org_id: str = org_context["organization_id"]
    svc = _get_rights_service()
    return await svc.get_crawler_timeseries(db=db, organization_id=org_id, days=days)


@router.get(
    "/analytics/content-spread",
    status_code=status.HTTP_200_OK,
    summary="Content spread analytics",
    description=(
        "Returns external domain detections for the org's signed content. "
        "Requires Enterprise tier or Attribution Analytics add-on. "
        "Shows which external domains your signed content has been detected on."
    ),
)
async def get_content_spread(
    days: int = Query(30, ge=1, le=365, description="Number of days to include"),
    db: AsyncSession = Depends(get_db),
    org_context: Dict = Depends(get_current_organization_dep),
) -> Dict[str, Any]:
    from datetime import datetime, timedelta, timezone

    from sqlalchemy import and_, func, select

    org_id: str = org_context["organization_id"]
    tier: str = (org_context.get("tier") or "free").lower()
    add_ons: dict = org_context.get("add_ons") or {}

    # Gate: Enterprise or attribution_analytics add-on
    allowed = tier in ("enterprise", "strategic_partner", "demo") or bool(add_ons.get("attribution_analytics"))
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FEATURE_NOT_AVAILABLE",
                "message": "Content Spread analytics requires Enterprise tier or the Attribution Analytics add-on.",
                "required_tier": "enterprise",
            },
        )

    from app.models.rights import ContentDetectionEvent

    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    base_filter = and_(
        ContentDetectionEvent.organization_id == org_id,
        ContentDetectionEvent.created_at >= cutoff,
        ContentDetectionEvent.detected_on_domain.isnot(None),
    )

    # Unique external domains + detection count per domain
    domain_result = await db.execute(
        select(
            ContentDetectionEvent.detected_on_domain,
            func.count(ContentDetectionEvent.id).label("detection_count"),
            func.count(func.distinct(ContentDetectionEvent.document_id)).label("unique_documents"),
            func.max(ContentDetectionEvent.created_at).label("last_detected"),
        )
        .where(base_filter)
        .group_by(ContentDetectionEvent.detected_on_domain)
        .order_by(func.count(ContentDetectionEvent.id).desc())
        .limit(100)
    )
    domain_rows = domain_result.all()

    # Total unique domains
    total_domains_result = await db.execute(select(func.count(func.distinct(ContentDetectionEvent.detected_on_domain))).where(base_filter))
    total_unique_domains: int = total_domains_result.scalar_one() or 0

    # Total detections
    total_events_result = await db.execute(select(func.count(ContentDetectionEvent.id)).where(base_filter))
    total_events: int = total_events_result.scalar_one() or 0

    # Per-document breakdown (top 50 documents by external detections)
    doc_result = await db.execute(
        select(
            ContentDetectionEvent.document_id,
            func.count(ContentDetectionEvent.id).label("detection_count"),
            func.count(func.distinct(ContentDetectionEvent.detected_on_domain)).label("unique_domains"),
            func.max(ContentDetectionEvent.created_at).label("last_detected"),
        )
        .where(and_(base_filter, ContentDetectionEvent.document_id.isnot(None)))
        .group_by(ContentDetectionEvent.document_id)
        .order_by(func.count(ContentDetectionEvent.id).desc())
        .limit(50)
    )
    doc_rows = doc_result.all()

    return {
        "organization_id": org_id,
        "period_days": days,
        "total_external_detections": total_events,
        "unique_external_domains": total_unique_domains,
        "domains": [
            {
                "domain": row.detected_on_domain,
                "detection_count": row.detection_count,
                "unique_documents": row.unique_documents,
                "last_detected": row.last_detected.isoformat() if row.last_detected else None,
            }
            for row in domain_rows
        ],
        "documents": [
            {
                "document_id": str(row.document_id) if row.document_id else None,
                "detection_count": row.detection_count,
                "unique_domains": row.unique_domains,
                "last_detected": row.last_detected.isoformat() if row.last_detected else None,
            }
            for row in doc_rows
        ],
    }


# ─────────────────────────────────────────────────────────────────────────────
# Helper serializers
# ─────────────────────────────────────────────────────────────────────────────


def _profile_to_dict(profile) -> Dict[str, Any]:
    return {
        "id": str(profile.id),
        "organization_id": profile.organization_id,
        "profile_version": profile.profile_version,
        "effective_date": profile.effective_date.isoformat() if profile.effective_date else None,
        "created_at": profile.created_at.isoformat() if profile.created_at else None,
        "publisher_name": profile.publisher_name,
        "publisher_url": profile.publisher_url,
        "contact_email": profile.contact_email,
        "contact_url": profile.contact_url,
        "legal_entity": profile.legal_entity,
        "jurisdiction": profile.jurisdiction,
        "default_license_type": profile.default_license_type,
        "bronze_tier": profile.bronze_tier,
        "silver_tier": profile.silver_tier,
        "gold_tier": profile.gold_tier,
        "notice_status": profile.notice_status,
        "notice_effective_date": profile.notice_effective_date.isoformat() if profile.notice_effective_date else None,
        "notice_text": profile.notice_text,
        "notice_hash": profile.notice_hash,
        "coalition_member": profile.coalition_member,
        "coalition_joined_at": profile.coalition_joined_at.isoformat() if profile.coalition_joined_at else None,
        "licensing_track": profile.licensing_track,
    }


def _override_to_dict(override) -> Dict[str, Any]:
    return {
        "id": str(override.id),
        "organization_id": override.organization_id,
        "document_id": str(override.document_id) if override.document_id else None,
        "override_version": override.override_version,
        "override_type": override.override_type,
        "collection_id": str(override.collection_id) if override.collection_id else None,
        "content_type_filter": override.content_type_filter,
        "bronze_tier_override": override.bronze_tier_override,
        "silver_tier_override": override.silver_tier_override,
        "gold_tier_override": override.gold_tier_override,
        "do_not_license": override.do_not_license,
        "premium_content": override.premium_content,
        "embargo_until": override.embargo_until.isoformat() if override.embargo_until else None,
        "created_at": override.created_at.isoformat() if override.created_at else None,
    }
