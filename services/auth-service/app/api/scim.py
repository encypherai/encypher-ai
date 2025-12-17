from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Any, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, Header, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ..db.models import Organization, OrganizationMember, User
from ..db.session import get_db

SCIM_MEDIA_TYPE = "application/scim+json"
SCIM_LIST_RESPONSE_SCHEMA = "urn:ietf:params:scim:api:messages:2.0:ListResponse"
SCIM_ERROR_SCHEMA = "urn:ietf:params:scim:api:messages:2.0:Error"
SCIM_USER_SCHEMA = "urn:ietf:params:scim:schemas:core:2.0:User"

router = APIRouter(prefix="/scim/v2", tags=["scim"])


@dataclass(frozen=True)
class ScimAuthContext:
    organization: Organization
    token: str


def _scim_error(status_code: int, detail: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "schemas": [SCIM_ERROR_SCHEMA],
            "detail": detail,
            "status": str(status_code),
        },
        media_type=SCIM_MEDIA_TYPE,
    )


def _extract_bearer_token(authorization: Optional[str]) -> str:
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    parts = authorization.split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer" or not parts[1].strip():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    return parts[1].strip()


def _get_scim_org_id_from_token(token: str) -> str:
    parts = token.split(".")
    if len(parts) < 3 or parts[0] != "scim":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    return parts[1]


def _hash_scim_token(token: str) -> str:
    return sha256(token.encode("utf-8")).hexdigest()


def scim_auth(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> ScimAuthContext:
    token = _extract_bearer_token(authorization)
    org_id = _get_scim_org_id_from_token(token)

    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    features: Any = getattr(org, "features", None) or {}
    if not isinstance(features, dict):
        features = {}

    expected_hash = features.get("scim_bearer_token_hash")
    if not expected_hash or expected_hash != _hash_scim_token(token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    return ScimAuthContext(organization=org, token=token)


@router.get("/Users")
async def scim_list_users(
    auth: ScimAuthContext = Depends(scim_auth),
    db: Session = Depends(get_db),
):
    users = (
        db.query(User)
        .join(OrganizationMember, OrganizationMember.user_id == User.id)
        .filter(OrganizationMember.organization_id == auth.organization.id)
        .all()
    )

    resources = [
        {
            "schemas": [SCIM_USER_SCHEMA],
            "id": getattr(u, "id", None),
            "userName": getattr(u, "email", None),
            "displayName": getattr(u, "name", None),
            "active": getattr(u, "is_active", True),
        }
        for u in users
    ]

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "schemas": [SCIM_LIST_RESPONSE_SCHEMA],
            "totalResults": len(resources),
            "startIndex": 1,
            "itemsPerPage": len(resources),
            "Resources": resources,
        },
        media_type=SCIM_MEDIA_TYPE,
    )


@router.post("/Users")
async def scim_create_user(
    body: dict[str, Any],
    auth: ScimAuthContext = Depends(scim_auth),
    db: Session = Depends(get_db),
):
    schemas = body.get("schemas")
    if schemas != [SCIM_USER_SCHEMA]:
        return _scim_error(status.HTTP_400_BAD_REQUEST, "Invalid schemas")

    user_name = body.get("userName")
    if not isinstance(user_name, str) or not user_name.strip():
        return _scim_error(status.HTTP_400_BAD_REQUEST, "userName is required")

    display_name = body.get("displayName")
    active = bool(body.get("active", True))

    existing = db.query(User).filter(User.email == user_name).first()
    if existing:
        user = existing
        user.name = display_name or user.name
        user.is_active = active
    else:
        user = User(
            id=str(uuid4()),
            email=user_name,
            name=display_name,
            password_hash=None,
            email_verified=True,
            is_active=active,
        )
        db.add(user)

    existing_member = (
        db.query(OrganizationMember)
        .filter(OrganizationMember.organization_id == getattr(auth.organization, "id", None))
        .filter(OrganizationMember.user_id == getattr(user, "id", None))
        .first()
    )
    if not existing_member:
        member = OrganizationMember(
            organization_id=getattr(auth.organization, "id", None),
            user_id=getattr(user, "id", None),
            role="member",
            status="active",
        )
        db.add(member)

    db.commit()

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "schemas": [SCIM_USER_SCHEMA],
            "id": getattr(user, "id", None),
            "userName": user_name,
            "displayName": display_name,
            "active": active,
        },
        media_type=SCIM_MEDIA_TYPE,
    )


@router.get("/Users/{user_id}")
async def scim_get_user(
    user_id: str,
    auth: ScimAuthContext = Depends(scim_auth),
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .join(OrganizationMember, OrganizationMember.user_id == User.id)
        .filter(OrganizationMember.organization_id == auth.organization.id)
        .filter(User.id == user_id)
        .first()
    )
    if not user:
        return _scim_error(status.HTTP_404_NOT_FOUND, "User not found")

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "schemas": [SCIM_USER_SCHEMA],
            "id": getattr(user, "id", None),
            "userName": getattr(user, "email", None),
            "displayName": getattr(user, "name", None),
            "active": getattr(user, "is_active", True),
        },
        media_type=SCIM_MEDIA_TYPE,
    )
