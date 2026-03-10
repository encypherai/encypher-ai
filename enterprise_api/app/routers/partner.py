"""Partner router for platform partner bulk publisher provisioning (TEAM_222).

Platform partners (e.g. Freestar) with strategic_partner tier can use this
endpoint to onboard hundreds of publishers at once, setting up rights profiles
and sending partner-branded claim emails.
"""

from __future__ import annotations

import html
import logging
from typing import Any, Dict, List, Optional

import httpx
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.rights_templates import get_template
from app.database import get_db
from app.dependencies import require_sign_permission
from app.schemas.api_response import ErrorCode
from app.services.auth_service_client import auth_service_client
from app.services.rights_service import rights_service

logger = logging.getLogger(__name__)
router = APIRouter()


# =============================================================================
# Schemas
# =============================================================================


class PartnerPublisherSpec(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    contact_email: EmailStr
    domain: Optional[str] = None
    template: str = "news_publisher_default"
    notice_status: str = "active"


class PartnerBulkProvisionRequest(BaseModel):
    publishers: List[PartnerPublisherSpec] = Field(min_length=1, max_length=1000)
    partner_name: str
    default_template: str = "news_publisher_default"
    coalition_member: bool = True
    send_claim_email: bool = True


# =============================================================================
# Partner claim email
# =============================================================================


async def _send_partner_claim_email(
    *,
    authorization: str,
    recipient_email: str,
    publisher_name: str,
    partner_name: str,
    invitation_token: str,
    domain: Optional[str] = None,
) -> None:
    """Send partner-branded account claim email to a newly provisioned publisher."""
    dashboard_url = settings.dashboard_url.rstrip("/")
    claim_url = f"{dashboard_url}/invite/{invitation_token}"

    safe_partner = html.escape(partner_name, quote=True)
    safe_publisher = html.escape(publisher_name, quote=True)
    safe_claim_url = html.escape(claim_url, quote=True)

    subject = f"{partner_name} has enabled content provenance for {publisher_name}"

    html_content = (
        f"<p>{safe_partner} has set up cryptographic content provenance for "
        f"<strong>{safe_publisher}</strong> through Encypher.</p>"
        f"<p>Every article published through {safe_partner}'s platform now carries a "
        "tamper-evident C2PA signature that protects your intellectual property rights.</p>"
        f'<p><a href="{safe_claim_url}">Claim your account and view your rights settings</a></p>'
        "<p>If you don't click anything, your content is still protected.</p>"
        "<hr />"
        '<p style="font-size:12px;color:#888">Powered by Encypher. '
        "If you believe this email was sent in error, you may safely ignore it.</p>"
    )

    plain_content = (
        f"{partner_name} has set up cryptographic content provenance for {publisher_name} through Encypher.\n\n"
        f"Every article published through {partner_name}'s platform now carries a "
        "tamper-evident C2PA signature that protects your intellectual property rights.\n\n"
        f"Claim your account and view your rights settings:\n  {claim_url}\n\n"
        "If you don't click anything, your content is still protected.\n\n"
        "Powered by Encypher."
    )

    payload = {
        "notification_type": "email",
        "recipient": recipient_email,
        "subject": subject,
        "content": html_content,
        "metadata": {
            "plain_content": plain_content,
            "publisher_name": publisher_name,
            "partner_name": partner_name,
            "claim_url": claim_url,
        },
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{settings.notification_service_url}/api/v1/notifications/send",
                json=payload,
                headers={"Authorization": authorization},
            )
            if response.status_code >= 400:
                logger.warning(
                    "partner_claim_email_failed status=%s response=%s",
                    response.status_code,
                    response.text,
                )
    except httpx.RequestError as exc:
        logger.warning("partner_claim_email_request_failed error=%s", str(exc))
    except Exception as exc:
        logger.exception("partner_claim_email_unexpected_error error=%s", str(exc))


# =============================================================================
# Bulk provisioning endpoint
# =============================================================================


@router.post(
    "/partner/publishers/provision",
    summary="Bulk-provision publisher organizations",
    description=(
        "Platform partners (strategic_partner tier) can provision up to 1000 publisher "
        "organizations in a single call. Each publisher gets a free-tier org, a rights "
        "profile using the specified template, and a partner-branded claim email."
    ),
    tags=["Partner"],
)
async def bulk_provision_publishers(
    payload: PartnerBulkProvisionRequest,
    http_request: Request,
    organization: dict = Depends(require_sign_permission),
    core_db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    """Bulk-provision publisher organizations for a platform partner."""
    tier = (organization.get("tier") or "free").lower().replace("-", "_")
    org_id = organization["organization_id"]
    partner_name = payload.partner_name

    if tier != "strategic_partner":
        return JSONResponse(
            status_code=403,
            content={
                "success": False,
                "data": None,
                "error": {
                    "code": ErrorCode.E_TIER_REQUIRED,
                    "message": "bulk publisher provisioning requires strategic_partner tier",
                },
            },
        )

    # Build publisher list for auth-service
    publishers_for_auth = [
        {
            "name": pub.name,
            "contact_email": str(pub.contact_email),
            "domain": pub.domain,
            "display_name": pub.name,
        }
        for pub in payload.publishers
    ]

    # Step 1: Create orgs + invitations via auth-service
    try:
        auth_result = await auth_service_client.bulk_provision_publishers(
            publishers=publishers_for_auth,
            partner_org_id=org_id,
            partner_name=partner_name,
            send_claim_email=False,  # enterprise_api sends partner-branded email
        )
    except Exception as exc:
        logger.error("bulk_provision_auth_service_error error=%s", str(exc))
        return JSONResponse(
            status_code=502,
            content={
                "success": False,
                "data": None,
                "error": {
                    "code": "E_AUTH_SERVICE_ERROR",
                    "message": f"Auth service provisioning failed: {exc}",
                },
            },
        )

    auth_data = auth_result.get("data", {})
    provisioned_auth = auth_data.get("provisioned", [])
    failed_auth = auth_data.get("failed", [])

    # Build a lookup from org_name -> publisher spec for rights profile
    spec_by_name: Dict[str, PartnerPublisherSpec] = {pub.name: pub for pub in payload.publishers}

    provisioned_results: List[Dict[str, Any]] = []
    failed_results: List[Dict[str, Any]] = list(failed_auth)

    dashboard_url = settings.dashboard_url.rstrip("/")
    authorization = http_request.headers.get("Authorization", "")

    for prov in provisioned_auth:
        pub_org_id = prov.get("org_id")
        org_name = prov.get("org_name", "")
        contact_email = prov.get("contact_email", "")
        invitation_token = prov.get("invitation_token")
        domain = prov.get("domain")

        if not pub_org_id:
            failed_results.append(
                {
                    "org_name": org_name,
                    "contact_email": contact_email,
                    "error": "No org_id returned from auth service",
                }
            )
            continue

        # Step 2: Create rights profile for this publisher
        spec = spec_by_name.get(org_name)
        template_id = (spec.template if spec else None) or payload.default_template

        try:
            template = get_template(template_id) or {}
            profile_data = {
                **template,
                "publisher_name": org_name,
                "notice_status": "active",
                "coalition_member": payload.coalition_member,
            }
            profile = await rights_service.create_or_update_profile(
                db=core_db,
                organization_id=pub_org_id,
                profile_data=profile_data,
            )
            rights_profile_version = profile.profile_version if profile else 1
        except Exception as exc:
            logger.warning(
                "bulk_provision_rights_profile_failed org_id=%s error=%s",
                pub_org_id,
                str(exc),
            )
            rights_profile_version = None

        # Step 3: Send partner claim email
        if payload.send_claim_email and invitation_token:
            await _send_partner_claim_email(
                authorization=authorization,
                recipient_email=contact_email,
                publisher_name=org_name,
                partner_name=partner_name,
                invitation_token=invitation_token,
                domain=domain,
            )

        claim_url = f"{dashboard_url}/invite/{invitation_token}" if invitation_token else None
        provisioned_results.append(
            {
                "org_id": pub_org_id,
                "org_name": org_name,
                "claim_url": claim_url,
                "rights_profile_version": rights_profile_version,
                "domain": domain,
            }
        )

    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "data": {
                "provisioned": provisioned_results,
                "failed": failed_results,
                "total": len(payload.publishers),
                "success_count": len(provisioned_results),
                "failure_count": len(failed_results),
            },
        },
    )
