from datetime import datetime, timedelta
import base64
from typing import Optional
from urllib.parse import quote_plus, urlparse

from fastapi import APIRouter, Depends, Form, HTTPException, Query, status
from fastapi.responses import RedirectResponse, Response
from sqlalchemy.orm import Session
import jwt

from ...core.config import settings
from ...db.session import get_db

router = APIRouter(prefix="/saml")


def _is_allowed_return_to(return_to: str) -> bool:
    if return_to.startswith("//"):
        return False
    if return_to.startswith("/"):
        return True

    parsed = urlparse(return_to)
    if parsed.scheme not in {"http", "https"}:
        return False
    if not parsed.netloc:
        return False

    dashboard_origin = urlparse(settings.DASHBOARD_URL)
    marketing_origin = urlparse(settings.MARKETING_SITE_URL)
    allowed = {
        (dashboard_origin.scheme, dashboard_origin.netloc),
        (marketing_origin.scheme, marketing_origin.netloc),
    }
    return (parsed.scheme, parsed.netloc) in allowed


@router.get("/metadata")
async def saml_metadata(org_id: str = Query(...)):
    entity_id = f"urn:encypher:auth:{org_id}"
    acs_url = f"{settings.API_URL}/api/v1/auth/saml/acs"

    xml = (
        "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
        "<EntityDescriptor xmlns=\"urn:oasis:names:tc:SAML:2.0:metadata\" "
        f"entityID=\"{entity_id}\">"
        "<SPSSODescriptor protocolSupportEnumeration=\"urn:oasis:names:tc:SAML:2.0:protocol\">"
        f"<AssertionConsumerService Binding=\"urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST\" Location=\"{acs_url}\" index=\"0\"/>"
        "</SPSSODescriptor>"
        "</EntityDescriptor>"
    )

    return Response(content=xml, media_type="application/xml")


@router.get("/login")
async def saml_login(org_id: str = Query(...), return_to: str = Query("")):
    if return_to and not _is_allowed_return_to(return_to):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid return_to")

    relay_payload = {
        "org_id": org_id,
        "return_to": return_to,
        "type": "relay",
        "exp": datetime.utcnow() + timedelta(minutes=5),
    }
    relay_state = jwt.encode(relay_payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    saml_request = base64.b64encode(f"dummy-saml-request:{org_id}".encode("utf-8")).decode("ascii")

    redirect_url = (
        f"{settings.DASHBOARD_URL}/sso/saml?SAMLRequest={quote_plus(saml_request)}&RelayState={quote_plus(relay_state)}"
    )

    return RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)


@router.post("/acs")
async def saml_acs(
    SAMLResponse: str = Form(...),
    RelayState: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    _ = (RelayState, db)

    if not SAMLResponse:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid SAMLResponse")

    try:
        base64.b64decode(SAMLResponse, validate=True)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid SAMLResponse") from exc

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="SAML assertion validation not implemented",
    )
