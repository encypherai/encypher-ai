"""Prebid auto-provenance signing service.

Handles the server-side flow for the encypherRtdProvider Path C:
  1. Resolve domain -> org (auto-provision if new)
  2. Content dedup by (domain, content_hash)
  3. Quota enforcement (1,000 unique signs/month, free tier)
  4. Sign text content via execute_unified_signing (real C2PA JUMBF,
     managed signer key - Encypher acts as notary)
  5. Store manifest reference in prebid_content_records; the signing
     executor persists the full signed document in the documents table
  6. Return manifest_url + metadata
"""

import hashlib
import logging
import uuid as uuid_mod
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple
from urllib.parse import urlparse

from fastapi import HTTPException
from sqlalchemy import select, text, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.organization import Organization, OrganizationCertificateStatus, OrganizationTier
from app.models.prebid_content_record import PrebidContentRecord
from app.schemas.sign_schemas import SignOptions, UnifiedSignRequest
from app.services.unified_signing_service import execute_unified_signing

logger = logging.getLogger(__name__)

FREE_TIER_MONTHLY_QUOTA = 1000


def extract_domain(url: str) -> str:
    """Extract eTLD+1 domain from a URL, stripping www prefix."""
    parsed = urlparse(url)
    hostname = parsed.hostname or ""
    if hostname.startswith("www."):
        hostname = hostname[4:]
    return hostname.lower()


def hash_content(text: str) -> str:
    """SHA-256 hash of text content, prefixed with 'sha256:'."""
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


def _generate_prebid_org_id(domain: str) -> str:
    """Generate deterministic org ID for a Prebid domain.

    Namespace: org_prebid_{sha256(domain)[:12]}
    """
    domain_hash = hashlib.sha256(domain.encode("utf-8")).hexdigest()[:12]
    return f"org_prebid_{domain_hash}"


async def _ensure_prebid_org(
    db: AsyncSession,
    domain: str,
) -> Tuple[str, bool]:
    """Look up or create a Prebid-provisioned organization for a domain.

    Returns (org_id, is_new).
    """
    org_id = _generate_prebid_org_id(domain)

    result = await db.execute(select(Organization).where(Organization.id == org_id))
    existing = result.scalar_one_or_none()

    if existing:
        return org_id, False

    # Create new org. Use ON CONFLICT DO NOTHING via raw SQL
    # to handle concurrent first-requests for the same domain.
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
            "id": org_id,
            "name": f"Prebid Publisher ({domain})",
            "email": f"prebid-auto@{domain}",
            "tier": OrganizationTier.FREE.value,
            "quota": FREE_TIER_MONTHLY_QUOTA,
            "cert_status": OrganizationCertificateStatus.NONE.value,
            "now": now,
        },
    )
    await db.commit()

    logger.info("Auto-provisioned Prebid org %s for domain %s", org_id, domain)
    return org_id, True


async def _check_prebid_quota(
    db: AsyncSession,
    org_id: str,
) -> Tuple[bool, int]:
    """Check if the org has remaining Prebid signing quota.

    Returns (allowed, documents_signed_this_period).
    Uses the existing documents_signed counter on the organizations table.
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


async def sign_or_retrieve(
    *,
    db: AsyncSession,
    page_url: str,
    text_content: str,
    document_title: Optional[str] = None,
) -> Dict[str, Any]:
    """Main entry point for Prebid signing.

    1. Extract domain from page_url
    2. Hash content
    3. Check dedup (domain + content_hash)
    4. If hit: return existing manifest (cached=True, no quota charge)
    5. If miss: ensure org, check quota, sign, store, return
    """
    domain = extract_domain(page_url)
    if not domain:
        return {"success": False, "error": "invalid_url"}

    content_hash = hash_content(text_content)

    # Dedup: check for existing record
    result = await db.execute(
        select(PrebidContentRecord).where(
            PrebidContentRecord.domain == domain,
            PrebidContentRecord.content_hash == content_hash,
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        return {
            "success": True,
            "manifest_url": existing.manifest_url,
            "signer_tier": existing.signer_tier,
            "signed_at": existing.signed_at.isoformat() if existing.signed_at else None,
            "content_hash": existing.content_hash,
            "org_id": existing.organization_id,
            "cached": True,
        }

    # New content: provision org and check quota
    org_id, _ = await _ensure_prebid_org(db, domain)

    allowed, current_usage = await _check_prebid_quota(db, org_id)
    if not allowed:
        upgrade_url = f"https://encypher.com/enterprise?ref=prebid&domain={domain}"
        return {
            "success": False,
            "error": "quota_exceeded",
            "org_id": org_id,
            "upgrade_url": upgrade_url,
        }

    # Execute real C2PA signing via unified signing service (managed signer)
    now = datetime.now(timezone.utc)
    correlation_id = str(uuid_mod.uuid4())

    sign_request = UnifiedSignRequest(
        text=text_content,
        document_title=document_title,
        document_url=page_url,
        options=SignOptions(claim_generator="Encypher Prebid Provenance/1.0"),
    )

    org_dict = {
        "organization_id": org_id,
        "organization_name": f"Prebid Publisher ({domain})",
        "tier": "free",
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
            "C2PA signing failed for domain=%s: status=%s detail=%s",
            domain,
            exc.status_code,
            exc.detail,
        )
        return {"success": False, "error": "signing_failed"}
    except Exception as exc:
        logger.error("Unexpected signing error for domain=%s: %s", domain, exc, exc_info=True)
        return {"success": False, "error": "signing_failed"}

    if not signing_result.get("success"):
        logger.error(
            "C2PA signing returned failure for domain=%s: %s",
            domain,
            signing_result.get("error"),
        )
        return {"success": False, "error": "signing_failed"}

    # Extract signed document result
    result_data = signing_result["data"]
    doc_result = result_data["document"]

    api_base = settings.api_base_url.rstrip("/")
    record = PrebidContentRecord(
        organization_id=org_id,
        domain=domain,
        canonical_url=page_url,
        content_hash=content_hash,
        page_title=document_title,
        signer_tier="encypher_free",
        signed_at=now,
    )

    record.manifest_store = {
        "claim_generator": "Encypher Prebid Provenance/1.0",
        "document_id": doc_result["document_id"],
        "verification_url": doc_result["verification_url"],
        "total_segments": doc_result["total_segments"],
        "signer_tier": "encypher_free",
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
    record.manifest_url = f"{api_base}/api/v1/public/prebid/manifest/{record.id}"

    await _increment_quota(db, org_id)
    await db.commit()
    await db.refresh(record)

    logger.info(
        "Prebid C2PA signed: domain=%s org=%s hash=%s doc_id=%s",
        domain,
        org_id,
        content_hash[:20],
        doc_result["document_id"],
    )

    return {
        "success": True,
        "manifest_url": record.manifest_url,
        "signer_tier": record.signer_tier,
        "signed_at": now.isoformat(),
        "content_hash": content_hash,
        "org_id": org_id,
        "cached": False,
    }
