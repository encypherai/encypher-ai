"""
Shared response helpers for Key Service.

Centralizes error and success response construction so all handlers
produce consistent shapes with navigation hints and request IDs.
"""

import uuid
from typing import Optional


# Navigation hint map: HTTP status code -> hint string
_HINTS: dict[int, str] = {
    400: "Check the request body against POST /api/v1/keys/generate docs.",
    401: "Provide a valid Bearer token via the Authorization header. Validate your key at POST /api/v1/keys/validate.",
    403: "Your key lacks the required permissions. See GET /api/v1/keys/{key_id} for current permissions.",
    404: "The resource does not exist or belongs to a different user/org. List available keys at GET /api/v1/keys.",
    500: "An internal error occurred. Retry with exponential back-off; contact support if the issue persists.",
}


def make_error_body(
    status_code: int,
    message: str,
    request_id: Optional[str] = None,
    hint: Optional[str] = None,
) -> dict:
    """
    Return a JSON-serialisable error body with a navigation hint and request_id.

    Args:
        status_code: HTTP status code for hint selection.
        message: Human-readable error message (passed through as ``detail``).
        request_id: Optional correlation ID. A new UUID is generated if omitted.
        hint: Optional override hint. Falls back to the status-code table.

    Returns:
        dict suitable for use as the ``detail`` value in HTTPException or
        as a direct JSON response body.
    """
    return {
        "detail": message,
        "hint": hint or _HINTS.get(status_code, "See /docs for endpoint reference."),
        "request_id": request_id or str(uuid.uuid4()),
    }


def make_success_body(data: object, request_id: Optional[str] = None) -> dict:
    """
    Wrap a successful payload in the standard envelope.

    Args:
        data: The response payload (dict, list, or scalar).
        request_id: Optional correlation ID.

    Returns:
        dict with ``success``, ``data``, and ``request_id`` keys.
    """
    return {
        "success": True,
        "data": data,
        "request_id": request_id or str(uuid.uuid4()),
    }
