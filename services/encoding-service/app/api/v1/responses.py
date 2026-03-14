"""
Shared response helpers for Encoding Service API v1.

Separates presentation logic (HTTP error detail, hints, request IDs) from
business logic in endpoints.py.
"""

from fastapi import Request
from fastapi.responses import JSONResponse
from typing import Optional


def _get_request_id(request: Optional[Request]) -> Optional[str]:
    """Extract request ID from request state or headers."""
    if request is None:
        return None
    # Try state (set by logging middleware) then fall back to header
    rid = getattr(request.state, "request_id", None)
    if rid:
        return str(rid)
    return request.headers.get("X-Request-ID")


def make_error(
    status_code: int,
    detail: str,
    hint: Optional[str] = None,
    request: Optional[Request] = None,
) -> JSONResponse:
    """
    Build a consistent JSON error response.

    Args:
        status_code: HTTP status code.
        detail: Human-readable error message.
        hint: Optional navigation hint for the caller.
        request: FastAPI Request object used to extract the request ID.

    Returns:
        JSONResponse with detail, hint, and request_id fields.
    """
    body: dict = {"detail": detail}
    if hint:
        body["hint"] = hint
    request_id = _get_request_id(request)
    if request_id:
        body["request_id"] = request_id
    return JSONResponse(status_code=status_code, content=body)


def make_success(data: dict, processing_time_ms: Optional[float] = None) -> dict:
    """
    Wrap a success payload with optional metadata.

    Args:
        data: The response payload dict.
        processing_time_ms: Optional processing duration.

    Returns:
        The data dict, optionally augmented with processing_time_ms.
    """
    if processing_time_ms is not None:
        data["processing_time_ms"] = processing_time_ms
    return data
