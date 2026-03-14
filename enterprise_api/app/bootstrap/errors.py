"""Centralized exception handlers.

Ensures every error response follows the ApiResponse envelope and includes
navigation hints (Unix Agent Design criterion 1) so that consumers -- human
or agent -- always know what to do next.
"""

import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.config import settings
from app.middleware.request_id_middleware import get_correlation_id
from app.schemas.api_response import get_error_navigation

logger = logging.getLogger(__name__)


def _enrich_with_navigation(error_payload: dict) -> None:
    """Mutate *error_payload* in place, adding navigation hints if missing."""
    code = error_payload.get("code", "")
    nav = get_error_navigation(code)
    if nav:
        error_payload.setdefault("next_action", nav.get("next_action"))
        if "docs_url" in nav:
            error_payload.setdefault("docs_url", nav["docs_url"])


async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception: %s", exc, exc_info=True)
    correlation_id = get_correlation_id(request)
    error_payload = {
        "code": "E_INTERNAL",
        "message": "An unexpected error occurred",
        "details": str(exc) if settings.is_development else None,
        "next_action": "Retry the request. If the problem persists, contact support with the correlation_id.",
    }
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": error_payload,
            "correlation_id": correlation_id,
        },
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    correlation_id = get_correlation_id(request)
    detail = exc.detail
    if isinstance(detail, dict):
        error_payload = dict(detail)  # copy to avoid mutating shared instances
        if "code" not in error_payload:
            error_payload["code"] = "E_HTTP"
        if "message" not in error_payload:
            error_payload["message"] = "Request failed"
    else:
        error_payload = {"code": "E_HTTP", "message": str(detail)}

    # Promote generic E_HTTP to a specific code based on status so that
    # navigation hints can match (many auth dependencies raise plain strings).
    if error_payload["code"] == "E_HTTP":
        _STATUS_TO_CODE = {401: "E_UNAUTHORIZED", 403: "E_FORBIDDEN", 404: "E_NOT_FOUND", 429: "E_RATE_LIMIT"}
        specific = _STATUS_TO_CODE.get(exc.status_code)
        if specific:
            error_payload["code"] = specific

    _enrich_with_navigation(error_payload)

    payload = {
        "success": False,
        "error": error_payload,
        "correlation_id": correlation_id,
    }
    return JSONResponse(
        status_code=exc.status_code,
        content=payload,
        headers=exc.headers,
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Custom handler for Pydantic / FastAPI validation errors.

    Groups errors by field and provides a human-readable summary with
    documentation links (Unix Agent Design criterion 5 -- progressive help L1).
    """
    correlation_id = get_correlation_id(request)

    # Group errors by field location
    field_errors: dict[str, list[str]] = {}
    for err in exc.errors():
        loc_parts = [str(p) for p in err.get("loc", [])]
        # Skip the leading "body" segment for cleaner field names
        if loc_parts and loc_parts[0] == "body":
            loc_parts = loc_parts[1:]
        field = ".".join(loc_parts) if loc_parts else "_root"
        msg = err.get("msg", "invalid")
        field_errors.setdefault(field, []).append(msg)

    # Build a human-readable summary
    summary_parts = []
    for field, msgs in field_errors.items():
        summary_parts.append(f"  {field}: {'; '.join(msgs)}")
    summary = "\n".join(summary_parts)

    error_payload = {
        "code": "E_VALIDATION",
        "message": f"Request validation failed:\n{summary}",
        "next_action": "Check the request body against the endpoint schema.",
        "docs_url": "/docs",
        "details": {"field_errors": field_errors},
    }

    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": error_payload,
            "correlation_id": correlation_id,
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(Exception, global_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
