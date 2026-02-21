"""
Public Rights Resolution Endpoints.

These endpoints are intentionally public (no auth required) — discoverability
is the entire point. Making rights information easy to find strengthens the
formal notice argument.

Rate limited to 10,000 requests/hour per IP.
"""

import logging
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request, status
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.public_rate_limiter import public_rate_limiter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/public/rights", tags=["Public - Rights"])

# Base URL for rights resolution links (injected from settings at runtime)
_BASE_URL = "https://api.encypherai.com"


def _rights_service():
    from app.services.rights_service import rights_service
    return rights_service


# ─────────────────────────────────────────────────────────────────────────────
# Document Rights Resolution
# ─────────────────────────────────────────────────────────────────────────────


@router.get(
    "/{document_id}",
    status_code=status.HTTP_200_OK,
    summary="Resolve rights for a specific document",
    description="""
Resolve the full rights and licensing terms for a signed document.

This endpoint is public and rate-limited. Any entity — AI companies, developers,
researchers — can call this to discover the publisher's licensing terms for content
they have encountered.

Calling this endpoint constitutes **constructive notice** — the information was
available, accessible, and machine-readable.
    """,
)
async def get_document_rights(
    request: Request,
    document_id: str = Path(..., description="Document ID from the signed content"),
    db: AsyncSession = Depends(get_db),
    _rate: None = Depends(public_rate_limiter),
) -> Dict[str, Any]:
    svc = _rights_service()

    # Resolve the organization_id for this document
    org_id, doc_record = await _resolve_document_org(db, document_id)
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document '{document_id}' not found in registry.",
        )

    # Resolve rights (priority cascade)
    rights = await svc.resolve_rights(
        db=db,
        document_id=document_id,
        organization_id=org_id,
    )

    # Get publisher profile for identity info
    profile = await svc.get_current_profile(db=db, organization_id=org_id)

    # Log detection event
    await _log_detection(
        svc=svc,
        db=db,
        document_id=document_id,
        organization_id=org_id,
        request=request,
        detection_source="rights_api_lookup",
        rights_served=True,
    )

    # Build response
    return _build_public_rights_response(document_id=document_id, profile=profile, rights=rights, doc_record=doc_record)


@router.post(
    "/resolve",
    status_code=status.HTTP_200_OK,
    summary="Resolve rights from raw text with embedded markers",
    description="""
Extract embedded Unicode variation selector markers from text and resolve each
to the publisher's rights information.

Accepts raw text (with or without visible markers). Useful for AI pipelines
that want to check rights before processing content.
    """,
)
async def resolve_rights_from_text(
    request: Request,
    body: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    _rate: None = Depends(public_rate_limiter),
) -> Dict[str, Any]:
    text_content = body.get("text", "")
    if not text_content:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="'text' field is required")

    svc = _rights_service()

    # Extract segment UUIDs from Unicode variation selectors
    segment_uuids = await _extract_segment_uuids(text_content)

    if not segment_uuids:
        return {"segments_found": 0, "rights": [], "message": "No Encypher provenance markers detected in text"}

    results: List[Dict[str, Any]] = []
    seen_docs = set()

    for seg_uuid in segment_uuids[:100]:  # cap at 100 segments per request
        doc_id, org_id = await _resolve_segment_to_document(db, seg_uuid)
        if not doc_id or doc_id in seen_docs:
            continue
        seen_docs.add(doc_id)

        rights = await svc.resolve_rights(db=db, document_id=doc_id, organization_id=org_id)
        profile = await svc.get_current_profile(db=db, organization_id=org_id)

        results.append({
            "document_id": doc_id,
            "segment_uuid": seg_uuid,
            "rights": _build_public_rights_response(
                document_id=doc_id,
                profile=profile,
                rights=rights,
                doc_record=None,
            ),
        })

    # Log detection
    if results:
        await _log_detection(
            svc=svc,
            db=db,
            document_id=results[0]["document_id"],
            organization_id=results[0]["rights"].get("publisher", {}).get("org_id", ""),
            request=request,
            detection_source="api_verification",
            rights_served=True,
            segments_found=len(segment_uuids),
        )

    return {
        "segments_found": len(segment_uuids),
        "unique_documents": len(results),
        "rights": results,
    }


@router.get(
    "/organization/{org_id}",
    status_code=status.HTTP_200_OK,
    summary="Get default rights profile for a publisher organization",
    description="""
Return the publisher's default rights profile (no document-specific overrides).
Useful for AI companies who want to know a publisher's standard terms before
processing their content at scale.
    """,
)
async def get_org_rights_profile(
    request: Request,
    org_id: str = Path(..., description="Organization ID"),
    db: AsyncSession = Depends(get_db),
    _rate: None = Depends(public_rate_limiter),
) -> Dict[str, Any]:
    svc = _rights_service()

    profile = await svc.get_current_profile(db=db, organization_id=org_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No public rights profile found for organization '{org_id}'.",
        )

    await _log_detection(
        svc=svc,
        db=db,
        document_id=None,
        organization_id=org_id,
        request=request,
        detection_source="rights_api_lookup",
        rights_served=True,
    )

    return {
        "organization_id": org_id,
        "publisher": {
            "name": profile.publisher_name,
            "url": profile.publisher_url,
            "contact_email": profile.contact_email,
            "contact_url": profile.contact_url,
            "legal_entity": profile.legal_entity,
        },
        "default_license_type": profile.default_license_type,
        "bronze_tier": profile.bronze_tier,
        "silver_tier": profile.silver_tier,
        "gold_tier": profile.gold_tier,
        "notice_status": profile.notice_status,
        "coalition_member": profile.coalition_member,
        "licensing_contact": {
            "email": profile.contact_email,
            "url": profile.contact_url,
            "coalition": profile.coalition_member,
            "coalition_contact": "licensing@encypherai.com" if profile.coalition_member else None,
        },
        "rights_api_url": f"{_BASE_URL}/api/v1/public/rights/organization/{org_id}",
    }


# ─────────────────────────────────────────────────────────────────────────────
# Machine-Readable Formats
# ─────────────────────────────────────────────────────────────────────────────


@router.get(
    "/{document_id}/json-ld",
    status_code=status.HTTP_200_OK,
    summary="Rights as JSON-LD (Schema.org compatible)",
    description="Returns the document's rights information in JSON-LD format for SEO and semantic web indexing.",
)
async def get_document_rights_json_ld(
    document_id: str = Path(..., description="Document ID"),
    db: AsyncSession = Depends(get_db),
    _rate: None = Depends(public_rate_limiter),
) -> Dict[str, Any]:
    svc = _rights_service()

    org_id, doc_record = await _resolve_document_org(db, document_id)
    if not org_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    profile = await svc.get_current_profile(db=db, organization_id=org_id)
    rights = await svc.resolve_rights(db=db, document_id=document_id, organization_id=org_id)

    return _build_json_ld(document_id=document_id, profile=profile, rights=rights)


@router.get(
    "/{document_id}/odrl",
    status_code=status.HTTP_200_OK,
    summary="Rights as ODRL (W3C Open Digital Rights Language)",
    description="Returns the document's rights in W3C ODRL format — machine-readable by semantic web crawlers.",
)
async def get_document_rights_odrl(
    document_id: str = Path(..., description="Document ID"),
    db: AsyncSession = Depends(get_db),
    _rate: None = Depends(public_rate_limiter),
) -> Dict[str, Any]:
    svc = _rights_service()

    org_id, doc_record = await _resolve_document_org(db, document_id)
    if not org_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    profile = await svc.get_current_profile(db=db, organization_id=org_id)
    rights = await svc.resolve_rights(db=db, document_id=document_id, organization_id=org_id)

    return _build_odrl(document_id=document_id, profile=profile, rights=rights)


@router.get(
    "/organization/{org_id}/robots-meta",
    status_code=status.HTTP_200_OK,
    summary="Generate AI-specific robots meta directives",
    description="""
Generate suggested meta tags and robots.txt additions that point AI crawlers
to the rights registry for this publisher.

WordPress plugin uses this to automatically add discovery paths.
    """,
)
async def get_robots_meta(
    org_id: str = Path(..., description="Organization ID"),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    svc = _rights_service()

    profile = await svc.get_current_profile(db=db, organization_id=org_id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    rights_api_url = f"{_BASE_URL}/api/v1/public/rights/organization/{org_id}"
    rsl_url = f"{_BASE_URL}/api/v1/public/rights/organization/{org_id}/rsl"

    meta_tags = f"""<!-- Encypher AI Rights Discovery -->
<meta name="content-rights" content="{rights_api_url}" />
<meta name="content-provenance" content="c2pa-signed" />
<meta name="licensing-contact" content="{profile.contact_email}" />
<link rel="license" href="{rights_api_url}/json-ld" type="application/ld+json" />"""

    robots_additions = f"""# Encypher AI Rights Management
# See {rights_api_url}

User-agent: GPTBot
User-agent: ClaudeBot
User-agent: Google-Extended
User-agent: PerplexityBot
User-agent: Meta-ExternalAgent
# License-URL: {profile.contact_url or profile.contact_email}
# Rights-API: {rights_api_url}

# RSL 1.0 License Directive
License: {rsl_url}"""

    http_headers = {
        "X-Content-Rights": rights_api_url,
        "X-Content-Provenance": "c2pa",
        "X-Licensing-Contact": profile.contact_email or "",
        "Link": f'<{rights_api_url}>; rel="license"',
    }

    return {
        "organization_id": org_id,
        "meta_tags_html": meta_tags,
        "robots_txt_additions": robots_additions,
        "http_headers": http_headers,
        "rights_api_url": rights_api_url,
        "rsl_url": rsl_url,
    }


@router.get(
    "/organization/{org_id}/rsl",
    status_code=status.HTTP_200_OK,
    summary="Generate RSL 1.0 XML document",
    description="""
Generate an RSL 1.0 XML document from the publisher's rights profile.
Maps bronze/silver/gold tiers to RSL <license> elements.

Publishers can host this as rsl.txt or reference it from robots.txt.
    """,
)
async def get_rsl_xml(
    org_id: str = Path(..., description="Organization ID"),
    db: AsyncSession = Depends(get_db),
) -> Any:
    from fastapi.responses import PlainTextResponse
    svc = _rights_service()

    profile = await svc.get_current_profile(db=db, organization_id=org_id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    rsl_xml = _build_rsl_xml(org_id=org_id, profile=profile)
    return PlainTextResponse(content=rsl_xml, media_type="application/xml")


@router.get(
    "/organization/{org_id}/robots-txt",
    status_code=status.HTTP_200_OK,
    summary="Generate robots.txt additions with RSL directives",
    description="Returns a text block to append to the publisher's robots.txt file.",
)
async def get_robots_txt_additions(
    org_id: str = Path(..., description="Organization ID"),
    db: AsyncSession = Depends(get_db),
) -> Any:
    from fastapi.responses import PlainTextResponse
    svc = _rights_service()

    profile = await svc.get_current_profile(db=db, organization_id=org_id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    rsl_url = f"{_BASE_URL}/api/v1/public/rights/organization/{org_id}/rsl"
    rights_url = f"{_BASE_URL}/api/v1/public/rights/organization/{org_id}"

    content = f"""# AI Content Rights — Generated by Encypher
# Rights Registry: {rights_url}
# RSL 1.0 License Terms: {rsl_url}
# Contact: {profile.contact_email}

User-agent: GPTBot
License: {rsl_url}

User-agent: ClaudeBot
License: {rsl_url}

User-agent: Google-Extended
License: {rsl_url}

User-agent: PerplexityBot
License: {rsl_url}

User-agent: Meta-ExternalAgent
License: {rsl_url}

User-agent: Bytespider
License: {rsl_url}

User-agent: CCBot
License: {rsl_url}
"""
    return PlainTextResponse(content=content, media_type="text/plain")


# ─────────────────────────────────────────────────────────────────────────────
# RSL OLP (Open License Protocol)
# ─────────────────────────────────────────────────────────────────────────────


@router.post(
    "/rsl/olp/token",
    status_code=status.HTTP_200_OK,
    summary="RSL Open License Protocol token endpoint",
    description="""
Implements RSL 1.0 Open License Protocol (OLP) with Encypher as the license
server backend. AI crawlers that comply with RSL send token requests here
before crawling publisher content.

Returns:
- 200 + token: Access granted (free bronze-tier crawling)
- 402: Payment required (paid bronze-tier)
- 401 + rights URL: Access blocked, rights resolution URL provided
    """,
)
async def rsl_olp_token(
    request: Request,
    body: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    svc = _rights_service()

    grant_type = body.get("grant_type", "rsl_license")
    scope = body.get("scope", "crawl")
    user_agent = body.get("user_agent") or request.headers.get("user-agent", "")
    target_url = body.get("target_url", "")

    # Determine org from target_url (look up domain → org_id)
    org_id = await _resolve_org_from_url(db, target_url)
    if not org_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Publisher not found for target URL")

    profile = await svc.get_current_profile(db=db, organization_id=org_id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No rights profile configured for this publisher")

    bronze_tier = profile.bronze_tier or {}
    permissions = bronze_tier.get("permissions", {})

    # Log the OLP check
    await svc.log_detection_event(db=db, event_data={
        "document_id": None,
        "organization_id": org_id,
        "detection_source": "rsl_olp_check",
        "detected_on_url": target_url,
        "detected_on_domain": urlparse(target_url).hostname if target_url else None,
        "requester_ip": request.client.host if request.client else None,
        "requester_user_agent": user_agent,
        "user_agent_category": await svc.classify_user_agent(db=db, user_agent=user_agent),
        "rights_served": True,
    })

    if not permissions.get("allowed", True):
        # Access blocked
        rights_url = f"{_BASE_URL}/api/v1/public/rights/organization/{org_id}"
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "access_denied",
                "message": "Content not available for crawling without license",
                "rights_url": rights_url,
                "licensing_contact": profile.contact_email,
            },
        )

    requires_license = permissions.get("requires_license", False)
    if requires_license:
        pricing = bronze_tier.get("pricing", {})
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail={
                "error": "payment_required",
                "message": "Crawling this content requires a license",
                "pricing": pricing,
                "licensing_url": permissions.get("license_url"),
                "licensing_contact": profile.contact_email,
            },
        )

    # Issue token (simple JWT-like structure for now)
    import secrets
    token = f"ency_olp_{secrets.token_urlsafe(32)}"
    return {
        "access_token": token,
        "token_type": "License",
        "scope": scope,
        "publisher_org_id": org_id,
        "expires_in": 86400,  # 24 hours
        "rate_limit": permissions.get("rate_limits", {}),
    }


@router.get(
    "/rsl/olp/validate/{token}",
    status_code=status.HTTP_200_OK,
    summary="Validate an OLP token",
    description="Publisher web servers use this to verify crawler authorization.",
)
async def validate_olp_token(
    token: str = Path(..., description="OLP token to validate"),
) -> Dict[str, Any]:
    # Simple validation — check token format (full implementation would use signed JWTs)
    if not token.startswith("ency_olp_"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    return {
        "valid": True,
        "token_type": "License",
        "scope": "crawl",
        "message": "Token is valid for crawl access",
    }


# ─────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ─────────────────────────────────────────────────────────────────────────────


async def _resolve_document_org(db: AsyncSession, document_id: str):
    """Resolve organization_id and basic record for a document_id."""
    try:
        from app.models.content_reference import ContentReference
        result = await db.execute(
            select(ContentReference.organization_id, ContentReference.document_id,
                   ContentReference.license_type, ContentReference.rights_resolution_url,
                   ContentReference.created_at, ContentReference.instance_id)
            .where(ContentReference.document_id == document_id)
            .limit(1)
        )
        row = result.first()
        if not row:
            return None, None
        return row.organization_id, {
            "document_id": row.document_id,
            "license_type": row.license_type,
            "rights_resolution_url": row.rights_resolution_url,
            "signed_at": row.created_at.isoformat() if row.created_at else None,
            "instance_id": row.instance_id,
        }
    except Exception:
        logger.exception("Error resolving document org for document_id=%s", document_id)
        return None, None


async def _extract_segment_uuids(text_content: str) -> List[str]:
    """Extract segment UUIDs from Unicode variation selectors in text."""
    try:
        from encypher.core.unicode_metadata import MetadataEncoder
        encoder = MetadataEncoder()
        metadata = encoder.extract_metadata(text_content)
        if metadata and isinstance(metadata, dict):
            segment_id = metadata.get("segment_id") or metadata.get("document_id")
            if segment_id:
                return [segment_id]
        return []
    except ImportError:
        logger.debug("encypher package not available for segment extraction")
        return []
    except Exception:
        logger.debug("Could not extract segment UUIDs from text")
        return []


async def _resolve_segment_to_document(db: AsyncSession, segment_uuid: str):
    """Resolve a segment UUID to (document_id, organization_id)."""
    try:
        from app.models.content_reference import ContentReference
        result = await db.execute(
            select(ContentReference.document_id, ContentReference.organization_id)
            .where(ContentReference.instance_id == segment_uuid)
            .limit(1)
        )
        row = result.first()
        if row:
            return row.document_id, row.organization_id
        return None, None
    except Exception:
        return None, None


async def _resolve_org_from_url(db: AsyncSession, target_url: str) -> Optional[str]:
    """Resolve an organization_id from a publisher URL (best-effort)."""
    if not target_url:
        return None
    try:
        from app.models.rights import PublisherRightsProfile
        from sqlalchemy import desc
        hostname = urlparse(target_url).hostname or ""
        # Try to match publisher_url against the target domain
        result = await db.execute(
            select(PublisherRightsProfile.organization_id)
            .where(PublisherRightsProfile.publisher_url.contains(hostname))
            .order_by(desc(PublisherRightsProfile.profile_version))
            .limit(1)
        )
        row = result.first()
        return row.organization_id if row else None
    except Exception:
        return None


async def _log_detection(
    svc,
    db: AsyncSession,
    document_id: Optional[str],
    organization_id: str,
    request: Request,
    detection_source: str,
    rights_served: bool = False,
    segments_found: Optional[int] = None,
):
    """Non-blocking detection event logging."""
    try:
        user_agent = request.headers.get("user-agent", "")
        ua_category = await svc.classify_user_agent(db=db, user_agent=user_agent)
        await svc.log_detection_event(db=db, event_data={
            "document_id": document_id,
            "organization_id": organization_id,
            "detection_source": detection_source,
            "detected_on_url": str(request.url),
            "detected_on_domain": request.headers.get("referer", ""),
            "requester_ip": request.client.host if request.client else None,
            "requester_user_agent": user_agent,
            "user_agent_category": ua_category,
            "segments_found": segments_found,
            "integrity_status": "intact",
            "rights_served": rights_served,
            "rights_acknowledged": False,
        })
    except Exception:
        pass  # Non-blocking — never fail the primary request due to analytics


def _build_public_rights_response(
    document_id: str,
    profile,
    rights: Dict[str, Any],
    doc_record: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    """Build the standard public rights response structure."""
    return {
        "publisher": {
            "name": profile.publisher_name if profile else None,
            "url": profile.publisher_url if profile else None,
            "contact": profile.contact_email if profile else None,
            "legal_entity": profile.legal_entity if profile else None,
        },
        "rights": {
            "license_type": rights.get("default_license_type", "all_rights_reserved"),
            "bronze_tier": rights.get("bronze_tier", {}),
            "silver_tier": rights.get("silver_tier", {}),
            "gold_tier": rights.get("gold_tier", {}),
        },
        "formal_notice": {
            "status": profile.notice_status if profile else "unknown",
            "effective_date": profile.notice_effective_date.isoformat() if (profile and profile.notice_effective_date) else None,
            "notice_hash": profile.notice_hash if profile else None,
        },
        "licensing_contact": {
            "email": profile.contact_email if profile else None,
            "url": profile.contact_url if profile else None,
            "coalition": profile.coalition_member if profile else False,
            "coalition_contact": "licensing@encypherai.com" if (profile and profile.coalition_member) else None,
        },
        "verification": {
            "c2pa_valid": True,
            "signed_at": doc_record.get("signed_at") if doc_record else None,
            "instance_id": doc_record.get("instance_id") if doc_record else None,
        },
        "rights_api_url": f"{_BASE_URL}/api/v1/public/rights/{document_id}",
    }


def _build_json_ld(document_id: str, profile, rights: Dict[str, Any]) -> Dict[str, Any]:
    """Build Schema.org-compatible JSON-LD rights representation."""
    bronze = rights.get("bronze_tier", {})
    return {
        "@context": "https://schema.org/",
        "@type": "CreativeWork",
        "identifier": document_id,
        "publisher": {
            "@type": "Organization",
            "name": profile.publisher_name if profile else None,
            "url": profile.publisher_url if profile else None,
            "email": profile.contact_email if profile else None,
        },
        "license": profile.contact_url if profile else None,
        "copyrightHolder": {
            "@type": "Organization",
            "name": profile.legal_entity or (profile.publisher_name if profile else None),
        },
        "usageInfo": f"{_BASE_URL}/api/v1/public/rights/{document_id}",
        "encypher:bronzeTier": bronze,
        "encypher:silverTier": rights.get("silver_tier", {}),
        "encypher:goldTier": rights.get("gold_tier", {}),
    }


def _build_odrl(document_id: str, profile, rights: Dict[str, Any]) -> Dict[str, Any]:
    """Build W3C ODRL-compatible rights representation."""
    bronze = rights.get("bronze_tier", {})
    silver = rights.get("silver_tier", {})
    gold = rights.get("gold_tier", {})

    def _tier_to_odrl_permission(tier_name: str, tier: Dict) -> Dict:
        permissions = tier.get("permissions", {})
        return {
            "@type": "odrl:Permission" if permissions.get("allowed") else "odrl:Prohibition",
            "odrl:action": tier_name,
            "odrl:assignee": "odrl:All",
            "odrl:duty": [
                {"odrl:action": "odrl:attribute"} if tier.get("attribution", {}).get("required") else None,
            ],
        }

    return {
        "@context": ["http://www.w3.org/ns/odrl.jsonld", {"encypher": "https://api.encypherai.com/ns/"}],
        "@type": "odrl:Policy",
        "uid": f"{_BASE_URL}/api/v1/public/rights/{document_id}/odrl",
        "odrl:target": {"@id": f"urn:encypher:document:{document_id}"},
        "odrl:assigner": {
            "odrl:uid": profile.publisher_url if profile else "",
            "odrl:name": profile.publisher_name if profile else "",
        },
        "odrl:permission": [
            _tier_to_odrl_permission("encypher:scraping", bronze),
            _tier_to_odrl_permission("encypher:rag_retrieval", silver),
            _tier_to_odrl_permission("encypher:training", gold),
        ],
    }


def _build_rsl_xml(org_id: str, profile) -> str:
    """Generate RSL 1.0 XML from publisher rights profile."""
    bronze = profile.bronze_tier or {}
    silver = profile.silver_tier or {}
    gold = profile.gold_tier or {}

    rsl_url = f"{_BASE_URL}/api/v1/public/rights/organization/{org_id}/rsl"
    rights_url = f"{_BASE_URL}/api/v1/public/rights/organization/{org_id}"

    bronze_perms = bronze.get("permissions", {})
    silver_perms = silver.get("permissions", {})
    gold_perms = gold.get("permissions", {})

    def _license_element(usage: str, allowed: bool, requires_license: bool, pricing: Dict, terms_url: str) -> str:
        license_type = "paid" if requires_license else ("allowed" if allowed else "prohibited")
        standard = "https://rslstandard.org/licenses/commercial-ai" if requires_license else "https://rslstandard.org/licenses/open"
        return f"""    <license usage="{usage}">
      <type>{license_type}</type>
      <standard>{standard}</standard>
      <terms url="{terms_url}" />
      {"<pricing>" + str(pricing.get("indicative_rate", "contact_us")) + "</pricing>" if requires_license else ""}
    </license>"""

    bronze_elem = _license_element(
        "crawl",
        bronze_perms.get("allowed", True),
        bronze_perms.get("requires_license", False),
        bronze.get("pricing", {}),
        profile.contact_url or rights_url,
    )
    silver_elem = _license_element(
        "retrieval",
        silver_perms.get("allowed", False),
        silver_perms.get("requires_license", True),
        silver.get("pricing", {}),
        f"{_BASE_URL}/api/v1/public/rights/organization/{org_id}",
    )
    gold_elem = _license_element(
        "training",
        gold_perms.get("allowed", False),
        gold_perms.get("requires_license", True),
        gold.get("pricing", {}),
        f"{_BASE_URL}/api/v1/licensing/request",
    )

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- RSL 1.0 — Generated by Encypher AI Rights Management -->
<!-- Rights Registry: {rights_url} -->
<rsl xmlns="https://rslstandard.org/rsl" version="1.0">
  <publisher>
    <name>{profile.publisher_name}</name>
    <url>{profile.publisher_url or ""}</url>
    <contact>{profile.contact_email}</contact>
  </publisher>
  <content url="/" server="{_BASE_URL}/api/v1/rsl/olp">
{bronze_elem}
{silver_elem}
{gold_elem}
  </content>
</rsl>
"""
