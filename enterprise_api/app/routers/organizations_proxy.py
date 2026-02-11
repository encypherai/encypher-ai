"""
Organizations Proxy Router

Proxies /organizations requests to the auth-service.
In production, Traefik handles this routing directly. This proxy ensures
the enterprise API can serve these requests locally (no gateway) and acts
as a fallback on Railway.
"""

import logging

import httpx
from fastapi import APIRouter, Request, Response

from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/organizations", tags=["organizations-proxy"])

_AUTH_BASE = settings.auth_service_url.rstrip("/")


@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
async def proxy_organizations(path: str, request: Request) -> Response:
    """Forward any /organizations/* request to the auth service."""
    target_url = f"{_AUTH_BASE}/api/v1/organizations/{path}"
    return await _proxy(target_url, request)


@router.api_route("", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
async def proxy_organizations_root(request: Request) -> Response:
    """Forward GET /organizations (list orgs) to the auth service."""
    target_url = f"{_AUTH_BASE}/api/v1/organizations"
    return await _proxy(target_url, request)


async def _proxy(target_url: str, request: Request) -> Response:
    """Proxy a request to the auth service and return the response."""
    headers = dict(request.headers)
    # Remove hop-by-hop headers
    for h in ("host", "content-length", "transfer-encoding"):
        headers.pop(h, None)

    body = await request.body()

    # Preserve query string
    if request.url.query:
        target_url = f"{target_url}?{request.url.query}"

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=body if body else None,
            )

        # Forward response headers (skip hop-by-hop)
        resp_headers = {
            k: v for k, v in resp.headers.items()
            if k.lower() not in ("transfer-encoding", "content-encoding", "content-length")
        }

        return Response(
            content=resp.content,
            status_code=resp.status_code,
            headers=resp_headers,
            media_type=resp.headers.get("content-type"),
        )
    except httpx.ConnectError:
        logger.warning("Auth service unreachable at %s", _AUTH_BASE)
        return Response(
            content='{"detail":"Auth service unavailable"}',
            status_code=502,
            media_type="application/json",
        )
    except Exception as e:
        logger.error("Organizations proxy error: %s", e)
        return Response(
            content='{"detail":"Proxy error"}',
            status_code=502,
            media_type="application/json",
        )
