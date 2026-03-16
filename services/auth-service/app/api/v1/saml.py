import logging
import uuid
import defusedxml.ElementTree as ET
from datetime import datetime, timedelta
import base64
from typing import Optional
from urllib.parse import quote_plus, urlparse

from fastapi import APIRouter, Body, Depends, Form, HTTPException, Query, Request, status
from fastapi.responses import RedirectResponse, Response
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
import jwt

from ...core.config import settings
from ...db.models import User
from ...db.saml_config import SamlConfig
from ...db.session import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/saml")


# ---------------------------------------------------------------------------
# Auth helper -- reuse get_current_user_id from organizations module
# ---------------------------------------------------------------------------


async def _require_authenticated_org_admin(
    request: Request,
    org_id: str,
    db: Session,
) -> str:
    """Validate caller is authenticated and is an admin/owner of the org.

    Returns the user_id on success. Raises HTTPException on failure.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header",
        )

    token = auth_header.split(" ", 1)[1]
    try:
        from ...core.auth import AuthService

        payload = AuthService.verify_access_token(token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    user_id = payload["sub"]

    # Verify user is a member of the org with admin/owner role
    from ...db.models import OrganizationMember

    member = (
        db.query(OrganizationMember)
        .filter(
            OrganizationMember.organization_id == org_id,
            OrganizationMember.user_id == user_id,
            OrganizationMember.status == "active",
        )
        .first()
    )
    if not member or member.role not in ("owner", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organization admin access required",
        )

    return user_id


# ---------------------------------------------------------------------------
# SAML signature verification
# ---------------------------------------------------------------------------


def _verify_saml_signature(saml_bytes: bytes, idp_certificate_pem: str) -> None:
    """Verify the XML signature on a SAMLResponse using the IdP certificate.

    Raises HTTPException if verification fails.
    """
    try:
        from lxml import etree
        from signxml import XMLVerifier
    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="SAML signature verification not available (missing signxml library)",
        )

    try:
        doc = etree.fromstring(saml_bytes)
    except etree.XMLSyntaxError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Malformed SAML XML",
        ) from exc

    # Find Signature elements in the document
    sig_ns = "http://www.w3.org/2000/09/xmldsig#"
    signatures = doc.findall(f".//{{{sig_ns}}}Signature")
    if not signatures:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="SAMLResponse has no XML signature -- unsigned assertions are not accepted",
        )

    # Parse the IdP certificate
    cert_pem = idp_certificate_pem.strip()
    if not cert_pem.startswith("-----BEGIN"):
        cert_pem = f"-----BEGIN CERTIFICATE-----\n{cert_pem}\n-----END CERTIFICATE-----"

    try:
        verifier = XMLVerifier()
        verifier.verify(doc, x509_cert=cert_pem)
    except Exception as exc:
        logger.warning("SAML signature verification failed for document: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="SAML signature verification failed -- the assertion signature is invalid or does not match the configured IdP certificate",
        ) from exc


# ---------------------------------------------------------------------------
# Public endpoints (no auth required)
# ---------------------------------------------------------------------------


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
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<EntityDescriptor xmlns="urn:oasis:names:tc:SAML:2.0:metadata" '
        f'entityID="{entity_id}">'
        '<SPSSODescriptor protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol">'
        f'<AssertionConsumerService Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST" Location="{acs_url}" index="0"/>'
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

    redirect_url = f"{settings.DASHBOARD_URL}/sso/saml?SAMLRequest={quote_plus(saml_request)}&RelayState={quote_plus(relay_state)}"

    return RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)


@router.post("/acs")
async def saml_acs(
    SAMLResponse: str = Form(...),
    RelayState: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    # --- Validate SAMLResponse encoding ---
    if not SAMLResponse:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid SAMLResponse")

    try:
        saml_bytes = base64.b64decode(SAMLResponse, validate=True)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid SAMLResponse") from exc

    # --- Decode RelayState JWT to get org_id and return_to ---
    if not RelayState:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing RelayState")

    try:
        relay = jwt.decode(RelayState, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="RelayState expired")
    except (jwt.InvalidTokenError, jwt.DecodeError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid RelayState")

    org_id = relay.get("org_id")
    return_to = relay.get("return_to", "")
    if not org_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing org_id in RelayState")

    # --- Look up SamlConfig for org_id ---
    saml_cfg = db.query(SamlConfig).filter(SamlConfig.organization_id == org_id).first()
    if not saml_cfg or not saml_cfg.enabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="SSO not configured for this organization")

    # --- CRITICAL: Verify SAML signature against IdP certificate ---
    if not saml_cfg.idp_certificate:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="IdP certificate not configured -- cannot verify SAML signature",
        )
    _verify_saml_signature(saml_bytes, saml_cfg.idp_certificate)

    # --- Parse XML and extract NameID (email) ---
    try:
        root = ET.fromstring(saml_bytes)
    except ET.ParseError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Malformed SAML XML") from exc

    ns = {
        "samlp": "urn:oasis:names:tc:SAML:2.0:protocol",
        "saml": "urn:oasis:names:tc:SAML:2.0:assertion",
    }

    name_id_el = root.find(".//saml:Assertion/saml:Subject/saml:NameID", ns)
    if name_id_el is None or not name_id_el.text:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="NameID not found in SAML assertion")

    email = name_id_el.text.strip().lower()

    # --- Use attribute mapping from SamlConfig ---
    attr_map = saml_cfg.attribute_mapping or {}
    name_attr_key = attr_map.get("name", "displayName")

    # Try to extract display name from SAML attributes
    display_name = None
    attr_stmt = root.find(".//saml:Assertion/saml:AttributeStatement", ns)
    if attr_stmt is not None:
        for attr_el in attr_stmt.findall("saml:Attribute", ns):
            if attr_el.get("Name") == name_attr_key:
                val_el = attr_el.find("saml:AttributeValue", ns)
                if val_el is not None and val_el.text:
                    display_name = val_el.text.strip()
                break
    if not display_name:
        display_name = email.split("@")[0]
        logger.debug("SAML attribute '%s' empty/missing for %s; using email prefix", name_attr_key, email)

    # --- Find or create user ---
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        user = User(
            id=str(uuid.uuid4()),
            email=email,
            name=display_name,
            email_verified=True,
            is_active=True,
        )
        try:
            db.add(user)
            db.commit()
            db.refresh(user)
        except IntegrityError:
            db.rollback()
            user = db.query(User).filter(User.email == email).first()
            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="User creation race condition",
                )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated",
        )

    # --- Issue JWT access token ---
    token_payload = {
        "sub": user.id,
        "email": user.email,
        "org_id": org_id,
        "type": "access",
        "exp": datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    access_token = jwt.encode(token_payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    # --- Redirect to dashboard with token ---
    dashboard_base = settings.DASHBOARD_URL.rstrip("/")
    redirect_path = return_to if return_to else "/dashboard"
    redirect_url = f"{dashboard_base}{redirect_path}?token={quote_plus(access_token)}"

    return RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)


# ============================================================
# SAML config CRUD endpoints (authenticated -- org admin only)
# ============================================================


@router.get("/config/{org_id}")
async def get_saml_config(
    org_id: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """Return the SAML config for an organization, or {configured: false}.

    Requires: authenticated org admin.
    """
    await _require_authenticated_org_admin(request, org_id, db)

    cfg = db.query(SamlConfig).filter(SamlConfig.organization_id == org_id).first()
    if cfg is None:
        return {"configured": False}

    return {
        "configured": True,
        "idp_entity_id": cfg.idp_entity_id,
        "idp_sso_url": cfg.idp_sso_url,
        "has_certificate": bool(cfg.idp_certificate),
        "attribute_mapping": cfg.attribute_mapping or {},
        "enabled": cfg.enabled,
    }


@router.put("/config/{org_id}")
async def update_saml_config(
    org_id: str,
    request: Request,
    payload: dict = Body(...),
    db: Session = Depends(get_db),
):
    """Create or update SAML config for an organization.

    Requires: authenticated org admin.
    """
    await _require_authenticated_org_admin(request, org_id, db)

    cfg = db.query(SamlConfig).filter(SamlConfig.organization_id == org_id).first()

    if cfg is None:
        cfg = SamlConfig(
            id=f"saml_{uuid.uuid4().hex[:16]}",
            organization_id=org_id,
            idp_entity_id=payload.get("idp_entity_id", ""),
            idp_sso_url=payload.get("idp_sso_url", ""),
            idp_certificate=payload.get("idp_certificate", ""),
            attribute_mapping=payload.get("attribute_mapping", {}),
            enabled=payload.get("enabled", False),
        )
        db.add(cfg)
    else:
        if "idp_entity_id" in payload:
            cfg.idp_entity_id = payload["idp_entity_id"]
        if "idp_sso_url" in payload:
            cfg.idp_sso_url = payload["idp_sso_url"]
        if "idp_certificate" in payload:
            cfg.idp_certificate = payload["idp_certificate"]
        if "attribute_mapping" in payload:
            cfg.attribute_mapping = payload["attribute_mapping"]
        if "enabled" in payload:
            cfg.enabled = payload["enabled"]
        cfg.updated_at = datetime.utcnow()

    db.commit()

    return {"success": True, "organization_id": org_id}
