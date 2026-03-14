"""
Shared response envelope helpers.

All endpoints should use ok() or err() instead of hand-rolling dicts like
{"success": True, "data": ..., "error": None}
"""

from typing import Any, Optional

from fastapi.responses import JSONResponse


def ok(data: Any = None, status_code: int = 200) -> dict:
    """Return a standard success envelope."""
    return {"success": True, "data": data, "error": None}


def err(detail: str, status_code: int = 400) -> JSONResponse:
    """Return a standard error envelope as a JSONResponse."""
    return JSONResponse(
        status_code=status_code,
        content={"success": False, "data": None, "error": {"detail": detail}},
    )


def paginated(
    items: list,
    total: int,
    page: int,
    page_size: int,
    *,
    items_key: str = "items",
) -> dict:
    """Return a standard paginated success envelope."""
    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
    return ok(
        {
            items_key: items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        }
    )
