"""
Onboarding router for SSL.com certificate requests and lifecycle management.
"""

import logging
import uuid

import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
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
