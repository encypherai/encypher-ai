import logging
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from app.config import settings

logger = logging.getLogger(__name__)


async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception: %s", exc, exc_info=True)
    correlation_id = getattr(request.state, "request_id", None) or request.headers.get("x-request-id") or f"req-{uuid4().hex}"
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "E_INTERNAL",
                "message": "An unexpected error occurred",
                "details": str(exc) if settings.is_development else None,
            },
            "correlation_id": correlation_id,
        },
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    correlation_id = getattr(request.state, "request_id", None) or request.headers.get("x-request-id") or f"req-{uuid4().hex}"
    detail = exc.detail
    if isinstance(detail, dict):
        error_payload = detail
        if "code" not in error_payload:
            error_payload["code"] = "E_HTTP"
        if "message" not in error_payload:
            error_payload["message"] = "Request failed"
    else:
        error_payload = {"code": "E_HTTP", "message": str(detail)}

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


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(Exception, global_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
