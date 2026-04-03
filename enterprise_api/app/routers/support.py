"""Support contact router for dashboard support form."""

import html
import logging
from datetime import datetime, timezone

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.config import settings
from app.dependencies import get_current_organization

router = APIRouter(prefix="/support", tags=["Support"])
logger = logging.getLogger(__name__)

VALID_CATEGORIES = {"general", "billing", "technical", "security", "feature_request", "bug_report"}


class SupportContactRequest(BaseModel):
    subject: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=10, max_length=5000)
    category: str = Field("general", max_length=50)


class SupportResponseData(BaseModel):
    message: str
    sent_at: str


class SupportContactResponse(BaseModel):
    success: bool = True
    data: SupportResponseData


def _escape(value: str) -> str:
    """HTML-escape a string."""
    return html.escape(value, quote=True)


@router.post("/contact", response_model=SupportContactResponse)
async def submit_support_contact(
    request: SupportContactRequest,
    organization: dict = Depends(get_current_organization),
) -> SupportContactResponse:
    """Submit a support contact request. Sends email to support team."""
    org_id = organization.get("organization_id", "unknown")
    org_name = organization.get("name", "Unknown Organization")
    user_email = organization.get("user_email", "")
    user_name = organization.get("user_name", "")
    tier = organization.get("tier", "free")

    category = request.category if request.category in VALID_CATEGORIES else "general"

    # Build email to support team
    subject = f"[Dashboard Support] [{category.replace('_', ' ').title()}] {request.subject}"

    html_content = (
        f"<h2>Support Request from Dashboard</h2>"
        f"<table style='border-collapse:collapse;'>"
        f"<tr><td style='padding:4px 12px 4px 0;font-weight:bold;'>From:</td>"
        f"<td>{_escape(user_name)} ({_escape(user_email)})</td></tr>"
        f"<tr><td style='padding:4px 12px 4px 0;font-weight:bold;'>Organization:</td>"
        f"<td>{_escape(org_name)} ({_escape(org_id)})</td></tr>"
        f"<tr><td style='padding:4px 12px 4px 0;font-weight:bold;'>Tier:</td>"
        f"<td>{_escape(tier)}</td></tr>"
        f"<tr><td style='padding:4px 12px 4px 0;font-weight:bold;'>Category:</td>"
        f"<td>{_escape(category.replace('_', ' ').title())}</td></tr>"
        f"<tr><td style='padding:4px 12px 4px 0;font-weight:bold;'>Subject:</td>"
        f"<td>{_escape(request.subject)}</td></tr>"
        f"</table>"
        f"<hr/>"
        f"<h3>Message</h3>"
        f"<p style='white-space:pre-wrap;'>{_escape(request.message)}</p>"
        f"<hr/>"
        f'<p style="font-size:12px;color:#888;">'
        f"Reply to this email to respond directly to the user at {_escape(user_email)}</p>"
    )

    plain_content = (
        f"Support Request from Dashboard\n\n"
        f"From: {user_name} ({user_email})\n"
        f"Organization: {org_name} ({org_id})\n"
        f"Tier: {tier}\n"
        f"Category: {category.replace('_', ' ').title()}\n"
        f"Subject: {request.subject}\n\n"
        f"Message:\n{request.message}\n\n"
        f"Reply to this email to respond directly to the user."
    )

    payload = {
        "notification_type": "email",
        "recipient": "support@encypher.com",
        "subject": subject,
        "content": html_content,
        "metadata": {
            "plain_content": plain_content,
            "reply_to": user_email,
            "category": category,
            "org_id": org_id,
            "user_email": user_email,
        },
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{settings.notification_service_url}/api/v1/notifications/send",
                json=payload,
                headers=({"Authorization": f"Bearer {settings.internal_service_token}"} if settings.internal_service_token else {}),
            )
            if response.status_code >= 400:
                logger.warning(
                    "support_contact_email_failed status=%s response=%s",
                    response.status_code,
                    response.text,
                )
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail={
                        "code": "EMAIL_SEND_FAILED",
                        "message": "Failed to send support message. Please try again.",
                    },
                )
    except httpx.RequestError as exc:
        logger.error("support_contact_email_error: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={
                "code": "EMAIL_SEND_FAILED",
                "message": "Failed to send support message. Please try again.",
            },
        )

    logger.info("support_contact_sent org=%s user=%s category=%s", org_id, user_email, category)

    return SupportContactResponse(
        data=SupportResponseData(
            message="Support request sent successfully",
            sent_at=datetime.now(timezone.utc).isoformat(),
        )
    )
