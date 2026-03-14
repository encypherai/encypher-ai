"""API Discovery endpoint.

Provides a public, unauthenticated index of available API endpoints so that
agents and new consumers can discover the API without needing access to the
Swagger docs (Unix Agent Design criterion 6 -- progressive help L0).

Routes tagged with internal doc tags (Admin, Provisioning, etc.) or marked
``include_in_schema=False`` are excluded to match the public docs visibility.
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.bootstrap.docs import _INTERNAL_DOC_TAGS

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Discovery"])

# Paths to exclude from the public discovery listing
_EXCLUDE_PREFIXES = (
    "/health",
    "/readyz",
    "/metrics",
    "/docs",
    "/openapi",
    "/favicon",
    "/internal",
)

_EXCLUDE_EXACT = frozenset({"/", ""})

# Cached after first request (routes are static after startup)
_cached_payload: Optional[Dict[str, Any]] = None


def _build_discovery_payload(app: Any) -> Dict[str, Any]:
    """Build the discovery payload by iterating app routes once."""
    endpoints: List[Dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()

    for route in app.routes:
        path = getattr(route, "path", None)
        if not path:
            continue

        if path in _EXCLUDE_EXACT:
            continue
        if any(path.startswith(p) for p in _EXCLUDE_PREFIXES):
            continue

        # Respect include_in_schema=False (same as public OpenAPI spec)
        if getattr(route, "include_in_schema", True) is False:
            continue

        methods = getattr(route, "methods", None)
        if not methods:
            continue

        tags = getattr(route, "tags", []) or []

        # Filter out routes with internal tags (mirrors _INTERNAL_DOC_TAGS
        # from bootstrap/docs.py used by the public OpenAPI filter)
        if any(tag in _INTERNAL_DOC_TAGS for tag in tags):
            continue

        summary = getattr(route, "summary", None) or ""
        description = getattr(route, "description", None) or ""
        if not summary and description:
            summary = description.split(".")[0].strip()

        for method in sorted(methods):
            if method in ("HEAD", "OPTIONS"):
                continue
            key = (method, path)
            if key in seen:
                continue
            seen.add(key)
            entry: Dict[str, Any] = {
                "method": method,
                "path": path,
                "summary": summary,
            }
            if tags:
                entry["tags"] = tags
            endpoints.append(entry)

    endpoints.sort(key=lambda e: (e["path"], e["method"]))

    return {
        "success": True,
        "data": {
            "endpoint_count": len(endpoints),
            "endpoints": endpoints,
        },
        "error": None,
        "meta": {
            "api_version": "v1",
            "docs_url": "/docs",
        },
    }


@router.get(
    "/api/v1/",
    summary="API Discovery",
    description="Returns an index of all available API endpoints with summaries.",
    include_in_schema=True,
)
async def api_discovery(request: Request) -> JSONResponse:
    """Return a listing of all API endpoints with their HTTP methods and summaries.

    This endpoint is public (no authentication required) and helps new
    consumers and AI agents discover available operations.
    """
    global _cached_payload
    if _cached_payload is None:
        _cached_payload = _build_discovery_payload(request.app)
    return JSONResponse(content=_cached_payload)
