"""
Onboarding router for SSL.com certificate requests and lifecycle management.
"""

import logging
import uuid
from datetime import datetime, timezone

import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import text, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from app.database import get_db, get_content_db
from app.dependencies import get_current_organization
from app.utils.ssl_com_client import SSLComClient

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/request-certificate")
async def request_certificate(organization: dict = Depends(get_current_organization), db: AsyncSession = Depends(get_db)):
    """
    Initiate SSL.com certificate request for organization.

    This endpoint:
    1. Checks if organization already has a pending/active certificate
    2. Creates SSL.com order via API
    3. Stores order tracking in certificate_lifecycle table
    4. Returns validation URL to organization

    Args:
        organization: Organization details from authentication
        db: Database session

    Returns:
        dict: Certificate request details including validation URL

    Raises:
        HTTPException: If organization already has certificate or SSL.com API fails
    """
    logger.info(f"Certificate request from organization {organization['organization_id']}")

    # Check if organization already has pending/active certificate
    existing = await db.execute(
        text("""
            SELECT cert_id, order_status
            FROM certificate_lifecycle
            WHERE organization_id = :org_id
              AND order_status IN ('pending_validation', 'issued')
            ORDER BY created_at DESC
            LIMIT 1
        """),
        {"org_id": organization["organization_id"]},
    )
    existing_cert = existing.fetchone()

    if existing_cert:
        logger.warning(f"Organization {organization['organization_id']} already has {existing_cert.order_status} certificate")
        return {
            "success": False,
            "error": {
                "code": "CERTIFICATE_EXISTS",
                "message": f"Organization already has {existing_cert.order_status} certificate",
                "cert_id": existing_cert.cert_id,
            },
        }

    # Create SSL.com order
    async with SSLComClient() as ssl_client:
        try:
            logger.debug("Creating SSL.com certificate order...")
            order = await ssl_client.create_code_signing_order(
                organization=organization["organization_name"],
                country=organization.get("country") or organization.get("billing_country") or "US",
                email=organization.get("email", "noreply@encypherai.com"),
                validity_years=2,
            )
            logger.info(f"SSL.com order created: {order.get('order_id')}")
        except httpx.HTTPStatusError as e:
            logger.error(f"SSL.com API error: {e}", exc_info=True)
            raise HTTPException(
                status_code=500, detail={"code": "SSL_COM_API_ERROR", "message": "Failed to create SSL.com certificate order", "details": str(e)}
            )

    # Store order tracking
    cert_id = f"cert_{uuid.uuid4().hex[:16]}"

    try:
        await db.execute(
            text("""
                INSERT INTO certificate_lifecycle
                (cert_id, organization_id, ssl_order_id, order_status,
                 validation_url, ordered_at)
                VALUES (:cert_id, :org_id, :order_id, 'pending_validation', :val_url, NOW())
            """),
            {
                "cert_id": cert_id,
                "org_id": organization["organization_id"],
                "order_id": order.get("order_id"),
                "val_url": order.get("validation_url"),
            },
        )

        await db.commit()
        logger.info(f"Certificate lifecycle tracking created: {cert_id}")

    except Exception as e:
        await db.rollback()
        logger.error(f"Database error while storing certificate lifecycle: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail={"code": "DATABASE_ERROR", "message": "Failed to store certificate request", "details": str(e)})

    return {
        "success": True,
        "cert_id": cert_id,
        "order_id": order.get("order_id"),
        "status": "pending_validation",
        "validation_url": order.get("validation_url"),
        "estimated_completion": "2-5 business days",
        "instructions": ("Please complete identity verification at the validation URL. You will receive an email when your certificate is issued."),
    }


@router.get("/certificate-status")
async def get_certificate_status(organization: dict = Depends(get_current_organization), db: AsyncSession = Depends(get_db)):
    """
    Get current certificate status for organization.

    Args:
        organization: Organization details from authentication
        db: Database session

    Returns:
        dict: Current certificate status
    """
    logger.info(f"Certificate status request from organization {organization['organization_id']}")

    result = await db.execute(
        text("""
            SELECT
                cert_id, ssl_order_id, order_status, validation_url,
                ordered_at, issued_at, expires_at
            FROM certificate_lifecycle
            WHERE organization_id = :org_id
            ORDER BY created_at DESC
            LIMIT 1
        """),
        {"org_id": organization["organization_id"]},
    )

    row = result.fetchone()

    if not row:
        return {"success": True, "has_certificate": False, "message": "No certificate request found. Please request a certificate first."}

    return {
        "success": True,
        "has_certificate": True,
        "cert_id": row.cert_id,
        "order_id": row.ssl_order_id,
        "status": row.order_status,
        "validation_url": row.validation_url,
        "ordered_at": row.ordered_at,
        "issued_at": row.issued_at,
        "expires_at": row.expires_at,
    }


# ---------------------------------------------------------------------------
# Formal Notice Progression Status (TEAM_225)
# ---------------------------------------------------------------------------

NOTICE_VERIFICATION_THRESHOLD = 500  # external verifications to qualify for Formal Notice


class ProgressionStage(BaseModel):
    """Single stage in the publisher value journey."""

    stage: int
    label: str
    description: str
    status: str  # "complete" | "in_progress" | "locked"
    metric_value: Optional[int] = None
    metric_label: Optional[str] = None
    metric_target: Optional[int] = None
    cta_label: Optional[str] = None
    cta_url: Optional[str] = None


class ProgressionStatusResponse(BaseModel):
    """Publisher progression status across the 6-stage value journey."""

    organization_id: str
    current_stage: int
    stages: List[ProgressionStage]
    notice_ready: bool
    notice_verification_threshold: int
    total_documents_signed: int
    total_external_verifications: int
    coalition_active: bool
    total_earnings_cents: int


@router.get(
    "/progression-status",
    response_model=ProgressionStatusResponse,
    summary="Get publisher value journey progression status",
    description=(
        "Returns the publisher's current stage in the 6-stage value journey: "
        "Sign -> Verify -> Spread -> Notice Ready -> Licensing -> Earnings. "
        "Used to power the progression component on the home page and analytics page."
    ),
)
async def get_progression_status(
    organization: dict = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db),
    content_db: AsyncSession = Depends(get_content_db),
) -> ProgressionStatusResponse:
    org_id: str = organization["organization_id"]

    # --- Stage 1: Documents signed (from content_db) ---
    doc_result = await content_db.execute(
        text("SELECT COUNT(*) FROM documents WHERE organization_id = :org_id"),
        {"org_id": org_id},
    )
    documents_signed: int = doc_result.scalar() or 0

    # --- Stage 2: External verifications (content detection events) ---
    try:
        cutoff_30d = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        cutoff_30d = cutoff_30d.replace(day=1)  # start of current month for a rolling window
        verification_result = await db.execute(
            text(
                """
                SELECT COUNT(*) FROM content_detection_events
                WHERE organization_id = :org_id
                """
            ),
            {"org_id": org_id},
        )
        total_verifications: int = verification_result.scalar() or 0
    except Exception:
        total_verifications = 0

    # --- Coalition membership check (from organizations table) ---
    coalition_result = await db.execute(
        text(
            """
            SELECT coalition_opted_in
            FROM organizations
            WHERE id = :org_id
            """
        ),
        {"org_id": org_id},
    )
    coalition_row = coalition_result.fetchone()
    coalition_active: bool = bool(coalition_row and getattr(coalition_row, "coalition_opted_in", False))

    # --- Total earnings (from coalition_revenue_entries if exists, else 0) ---
    total_earnings_cents: int = 0
    try:
        earnings_result = await db.execute(
            text(
                """
                SELECT COALESCE(SUM(publisher_earnings_cents), 0)
                FROM coalition_revenue_entries
                WHERE organization_id = :org_id AND status = 'paid'
                """
            ),
            {"org_id": org_id},
        )
        total_earnings_cents = earnings_result.scalar() or 0
    except Exception:
        total_earnings_cents = 0

    # --- Notice check ---
    notice_ready = total_verifications >= NOTICE_VERIFICATION_THRESHOLD

    # --- Build stage objects ---
    def _stage_status(condition: bool, prev_condition: bool = True) -> str:
        if not prev_condition:
            return "locked"
        return "complete" if condition else "in_progress"

    stages = [
        ProgressionStage(
            stage=1,
            label="Sign",
            description="Sign your articles with C2PA cryptographic provenance. Every signed article is enforcement evidence.",
            status="complete" if documents_signed > 0 else "in_progress",
            metric_value=documents_signed,
            metric_label="articles signed",
            cta_label="Sign content" if documents_signed == 0 else None,
            cta_url="/integrations" if documents_signed == 0 else None,
        ),
        ProgressionStage(
            stage=2,
            label="Accumulate",
            description="Reach 500 external provenance verifications. Each check documents that rights were seen before content was used.",
            status=_stage_status(notice_ready, documents_signed > 0),
            metric_value=total_verifications,
            metric_label="external verifications",
            metric_target=NOTICE_VERIFICATION_THRESHOLD,
        ),
        ProgressionStage(
            stage=3,
            label="Document",
            description="Your evidence package is building automatically with every verification logged.",
            status="complete" if notice_ready else ("in_progress" if total_verifications > 0 else "locked"),
        ),
        ProgressionStage(
            stage=4,
            label="Notice Ready",
            description="You qualify to serve Formal Notice to infringing entities. This converts them to willful infringement status ($150K/work max).",
            status="complete" if notice_ready else "locked",
            cta_label="Take Action" if notice_ready else None,
            cta_url="/rights" if notice_ready else None,
        ),
        ProgressionStage(
            stage=5,
            label="Negotiating",
            description="Formal Notice served. Encypher is negotiating coalition licensing terms on your behalf.",
            status="complete" if coalition_active and total_earnings_cents > 0 else ("in_progress" if coalition_active else "locked"),
        ),
        ProgressionStage(
            stage=6,
            label="Earnings",
            description="Coalition licensing revenue is distributed to your account.",
            status="complete" if total_earnings_cents > 0 else "locked",
            metric_value=total_earnings_cents,
            metric_label="cents earned",
        ),
    ]

    # Current stage = highest in_progress or complete stage
    current_stage = 1
    for s in stages:
        if s.status in ("complete", "in_progress"):
            current_stage = s.stage

    return ProgressionStatusResponse(
        organization_id=org_id,
        current_stage=current_stage,
        stages=stages,
        notice_ready=notice_ready,
        notice_verification_threshold=NOTICE_VERIFICATION_THRESHOLD,
        total_documents_signed=documents_signed,
        total_external_verifications=total_verifications,
        coalition_active=coalition_active,
        total_earnings_cents=total_earnings_cents,
    )
