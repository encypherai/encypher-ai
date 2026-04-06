"""CDN Edge Provenance Worker signing service.

Handles the server-side flow for the Cloudflare Edge Provenance Worker:
  1. Resolve domain -> org (auto-provision if new, cross-channel resolution)
  2. Content dedup by (domain, content_hash)
  3. Quota enforcement (1,000 unique signs/month, free tier)
  4. Sign text content via execute_unified_signing with return_embedding_plan
  5. Store embedding plan + manifest in cdn_content_records
  6. Return embedding plan for the worker to apply at the edge
"""

import hashlib
import logging
import secrets
import uuid as uuid_mod
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple
from urllib.parse import urlparse

from fastapi import HTTPException
from sqlalchemy import select, text, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.cdn_content_record import CdnContentRecord
from app.models.organization import Organization, OrganizationCertificateStatus, OrganizationTier
from app.schemas.sign_schemas import SignOptions, UnifiedSignRequest
from app.services.unified_signing_service import execute_unified_signing

logger = logging.getLogger(__name__)

FREE_TIER_MONTHLY_QUOTA = 1000


# ---------------------------------------------------------------------------
# Domain / hash utilities (shared patterns with prebid_signing_service)
# ---------------------------------------------------------------------------


def extract_domain(url: str) -> str:
    """Extract eTLD+1 domain from a URL, stripping www prefix."""
    parsed = urlparse(url)
    hostname = parsed.hostname or ""
    if hostname.startswith("www."):
        hostname = hostname[4:]
    return hostname.lower()


def hash_content(text_content: str) -> str:
    """SHA-256 hash of text content, prefixed with 'sha256:'."""
    digest = hashlib.sha256(text_content.encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


# ---------------------------------------------------------------------------
# Cross-channel org resolution
# ---------------------------------------------------------------------------


def _generate_cdn_org_id(domain: str) -> str:
    """Generate deterministic org ID for a CDN-provisioned domain.

    Namespace: org_cdn_{sha256(domain)[:12]}
    """
    domain_hash = hashlib.sha256(domain.encode("utf-8")).hexdigest()[:12]
    return f"org_cdn_{domain_hash}"


def _generate_prebid_org_id(domain: str) -> str:
    """Generate deterministic org ID for a Prebid domain (for cross-channel lookup)."""
    domain_hash = hashlib.sha256(domain.encode("utf-8")).hexdigest()[:12]
    return f"org_prebid_{domain_hash}"


async def resolve_publisher_org(
    db: AsyncSession,
    domain: str,
) -> Tuple[str, bool]:
    """Resolve an organization for a publisher domain across all channels.

    Check order:
      1. CDN-provisioned org (org_cdn_{hash})
      2. Prebid-provisioned org (org_prebid_{hash})
      3. Dashboard-claimed org (domain match on organizations table)
      4. Create new CDN org if none found

    Returns (org_id, is_new).
    """
    # Check CDN org
    cdn_org_id = _generate_cdn_org_id(domain)
    result = await db.execute(select(Organization.id).where(Organization.id == cdn_org_id))
    if result.scalar_one_or_none():
        return cdn_org_id, False

    # Check Prebid org
    prebid_org_id = _generate_prebid_org_id(domain)
    result = await db.execute(select(Organization.id).where(Organization.id == prebid_org_id))
    if result.scalar_one_or_none():
        return prebid_org_id, False

    # Check dashboard-claimed org by domain (email domain match)
    result = await db.execute(select(Organization.id).where(Organization.email.ilike(f"%@{domain}")).limit(1))
    dashboard_org = result.scalar_one_or_none()
    if dashboard_org:
        return dashboard_org, False

    # Create new CDN org
    now = datetime.utcnow()
    await db.execute(
        text("""
            INSERT INTO organizations (
                id, name, email, tier, status,
                monthly_quota, documents_signed,
                api_calls_this_month,
                merkle_encoding_calls_this_month,
                merkle_attribution_calls_this_month,
                merkle_plagiarism_calls_this_month,
                fuzzy_index_calls_this_month,
                fuzzy_search_calls_this_month,
                sentences_tracked_this_month,
                batch_operations_this_month,
                cdn_image_registrations_this_month,
                certificate_status,
                coalition_member,
                created_at, updated_at
            ) VALUES (
                :id, :name, :email, :tier, 'active',
                :quota, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0,
                :cert_status,
                true,
                :now, :now
            ) ON CONFLICT (id) DO NOTHING
        """),
        {
            "id": cdn_org_id,
            "name": f"CDN Publisher ({domain})",
            "email": f"cdn-auto@{domain}",
            "tier": OrganizationTier.FREE.value,
            "quota": FREE_TIER_MONTHLY_QUOTA,
            "cert_status": OrganizationCertificateStatus.NONE.value,
            "now": now,
        },
    )
    await db.commit()

    logger.info("Auto-provisioned CDN org %s for domain %s", cdn_org_id, domain)
    return cdn_org_id, True


# ---------------------------------------------------------------------------
# Provisioning
# ---------------------------------------------------------------------------


async def provision_domain(
    db: AsyncSession,
    domain: str,
    worker_version: Optional[str] = None,
) -> Dict[str, Any]:
    """Provision (or resolve) an organization for a CDN domain.

    Returns org_id, domain_token, dashboard_url, and claim_url.
    """
    domain = domain.lower().strip()
    if not domain or "." not in domain:
        return {"success": False, "error": "invalid_domain"}

    org_id, is_new = await resolve_publisher_org(db, domain)

    # Generate a domain token (deterministic per org for idempotency)
    domain_token = f"dtk_{hashlib.sha256(f'{org_id}:{domain}'.encode()).hexdigest()[:24]}"

    base_url = settings.marketing_site_url.rstrip("/") if hasattr(settings, "marketing_site_url") else "https://encypher.com"

    return {
        "success": True,
        "org_id": org_id,
        "domain_token": domain_token,
        "dashboard_url": f"{base_url}/cdn/{domain}",
        "claim_url": f"{base_url}/claim/{org_id}",
    }


# ---------------------------------------------------------------------------
# Quota
# ---------------------------------------------------------------------------


async def _check_cdn_quota(
    db: AsyncSession,
    org_id: str,
) -> Tuple[bool, int]:
    """Check if the org has remaining CDN signing quota.

    Returns (allowed, documents_signed_this_period).
    """
    result = await db.execute(select(Organization.documents_signed, Organization.monthly_quota).where(Organization.id == org_id))
    row = result.one_or_none()
    if not row:
        return False, 0

    signed, quota = row
    if quota == -1:
        return True, signed
    return signed < quota, signed


async def _increment_quota(db: AsyncSession, org_id: str) -> None:
    """Increment the documents_signed counter for the org."""
    await db.execute(update(Organization).where(Organization.id == org_id).values(documents_signed=Organization.documents_signed + 1))


# ---------------------------------------------------------------------------
# Org-tier-aware signing options
# ---------------------------------------------------------------------------


def _build_sign_options_for_org(
    db_org: Optional[Organization],
) -> SignOptions:
    """Build signing options based on the org's tier.

    Free tier: micro + ECC + C2PA, sentence-level segmentation.
    Enterprise tier: adds fingerprinting, dual binding, etc.
    """
    opts = SignOptions(
        manifest_mode="micro",
        ecc=True,
        embed_c2pa=True,
        segmentation_level="sentence",
        claim_generator="Encypher CDN Provenance/1.0",
    )

    if db_org and db_org.tier == OrganizationTier.ENTERPRISE.value:
        opts.include_fingerprint = True
        opts.add_dual_binding = True

    return opts


# ---------------------------------------------------------------------------
# Main signing flow
# ---------------------------------------------------------------------------


async def sign_or_retrieve(
    *,
    db: AsyncSession,
    text_content: str,
    page_url: str,
    org_id: Optional[str] = None,
    document_title: Optional[str] = None,
    boundary_selector: Optional[str] = None,
) -> Dict[str, Any]:
    """Main entry point for CDN content signing.

    1. Extract domain from page_url
    2. Hash content
    3. Check dedup (domain + content_hash)
    4. If hit: return existing embedding plan (cached=True, no quota charge)
    5. If miss: resolve org, check quota, sign with embedding plan, store, return
    """
    domain = extract_domain(page_url)
    if not domain:
        return {"success": False, "error": "invalid_url"}

    content_hash = hash_content(text_content)

    # Dedup: check for existing record
    result = await db.execute(
        select(CdnContentRecord).where(
            CdnContentRecord.domain == domain,
            CdnContentRecord.content_hash == content_hash,
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        return {
            "success": True,
            "embedding_plan": existing.embedding_plan,
            "document_id": (existing.manifest_store or {}).get("document_id"),
            "verification_url": (existing.manifest_store or {}).get("verification_url"),
            "content_hash": existing.content_hash,
            "org_id": existing.organization_id,
            "signer_tier": existing.signer_tier,
            "signed_at": existing.signed_at.isoformat() if existing.signed_at else None,
            "cached": True,
        }

    # Resolve org (cross-channel)
    if not org_id:
        org_id, _ = await resolve_publisher_org(db, domain)
    else:
        # Verify provided org_id exists, fall back to resolution
        check = await db.execute(select(Organization.id).where(Organization.id == org_id))
        if not check.scalar_one_or_none():
            org_id, _ = await resolve_publisher_org(db, domain)

    # Check quota
    allowed, current_usage = await _check_cdn_quota(db, org_id)
    if not allowed:
        upgrade_url = f"https://encypher.com/enterprise?ref=cdn&domain={domain}"
        return {
            "success": False,
            "error": "quota_exceeded",
            "org_id": org_id,
            "upgrade_url": upgrade_url,
        }

    # Load org for tier-aware signing options
    org_result = await db.execute(select(Organization).where(Organization.id == org_id))
    db_org = org_result.scalar_one_or_none()
    sign_options = _build_sign_options_for_org(db_org)

    # Execute signing via unified signing service with return_embedding_plan
    now = datetime.now(timezone.utc)
    correlation_id = str(uuid_mod.uuid4())

    sign_request = UnifiedSignRequest(
        text=text_content,
        document_title=document_title,
        document_url=page_url,
        options=sign_options,
    )
    sign_request.options.return_embedding_plan = True

    org_dict = {
        "organization_id": org_id,
        "organization_name": f"CDN Publisher ({domain})",
        "tier": db_org.tier if db_org else "free",
        "is_demo": False,
        "signing_mode": "managed",
    }

    try:
        signing_result = await execute_unified_signing(
            request=sign_request,
            organization=org_dict,
            core_db=db,
            content_db=db,
            correlation_id=correlation_id,
        )
    except HTTPException as exc:
        logger.error(
            "C2PA signing failed for CDN domain=%s: status=%s detail=%s",
            domain,
            exc.status_code,
            exc.detail,
        )
        return {"success": False, "error": "signing_failed"}
    except Exception as exc:
        logger.error("Unexpected signing error for CDN domain=%s: %s", domain, exc, exc_info=True)
        return {"success": False, "error": "signing_failed"}

    if not signing_result.get("success"):
        logger.error(
            "C2PA signing returned failure for CDN domain=%s: %s",
            domain,
            signing_result.get("error"),
        )
        return {"success": False, "error": "signing_failed"}

    # Extract signed document result
    result_data = signing_result["data"]
    doc_result = result_data["document"]

    # Extract embedding plan from the signing result
    embedding_plan_data = doc_result.get("embedding_plan")

    signer_tier = "encypher_free"
    if db_org and db_org.tier == OrganizationTier.ENTERPRISE.value:
        signer_tier = "enterprise"

    api_base = settings.api_base_url.rstrip("/")
    record = CdnContentRecord(
        organization_id=org_id,
        domain=domain,
        canonical_url=page_url,
        content_hash=content_hash,
        embedding_plan=embedding_plan_data,
        page_title=document_title,
        signer_tier=signer_tier,
        boundary_selector=boundary_selector,
        signed_at=now,
    )

    record.manifest_store = {
        "claim_generator": "Encypher CDN Provenance/1.0",
        "document_id": doc_result["document_id"],
        "verification_url": doc_result["verification_url"],
        "total_segments": doc_result["total_segments"],
        "signer_tier": signer_tier,
        "action": "c2pa.created",
        "source_domain": domain,
        "canonical_url": page_url,
        "content_hash": content_hash,
        "signed_at": now.isoformat(),
        "document_title": document_title,
    }

    db.add(record)
    await db.flush()

    # Set manifest_url now that we have the record ID
    record.manifest_url = f"{api_base}/api/v1/public/cdn/manifest/{record.id}"

    await _increment_quota(db, org_id)
    await db.commit()
    await db.refresh(record)

    logger.info(
        "CDN C2PA signed: domain=%s org=%s hash=%s doc_id=%s",
        domain,
        org_id,
        content_hash[:20],
        doc_result["document_id"],
    )

    return {
        "success": True,
        "embedding_plan": embedding_plan_data,
        "document_id": doc_result["document_id"],
        "verification_url": doc_result["verification_url"],
        "content_hash": content_hash,
        "org_id": org_id,
        "signer_tier": signer_tier,
        "signed_at": now.isoformat(),
        "cached": False,
    }
