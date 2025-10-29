"""
API endpoints for Enterprise API-backed directory scanning workflows.
"""
from fastapi import APIRouter, Depends, HTTPException, status

from app.models.user import User
from app.schemas.scanning import DirectoryScanRequest, DirectoryScanResponse
from app.services.directory_scanner import scan_directory
from app.services.user import get_current_active_superuser

router = APIRouter()


@router.post(
    "/scan",
    response_model=DirectoryScanResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Scan a directory for signed/unsigned files. Optionally mark unmarked via Enterprise API.",
)
async def scan_directory_endpoint(
    payload: DirectoryScanRequest,
    current_user: User = Depends(get_current_active_superuser),
) -> DirectoryScanResponse:
    """
    Scan a directory tree for files that have C2PA text wrappers and optionally
    sign unmarked files using the Enterprise API.

    Requires superuser privileges because the operation reads from the server filesystem.
    """
    try:
        return await scan_directory(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc
