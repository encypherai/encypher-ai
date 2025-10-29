"""
API endpoints for Enterprise API-backed signing workflows.
"""
from fastapi import APIRouter, Depends, HTTPException, status

from app.models.user import User
from app.schemas.signing import DirectorySigningRequest, DirectorySigningResponse
from app.services.directory_signing import sign_directory
from app.services.user import get_current_active_superuser

router = APIRouter()


@router.post(
    "/directory",
    response_model=DirectorySigningResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Sign all text files within a directory via Enterprise API.",
)
async def sign_directory_endpoint(
    payload: DirectorySigningRequest,
    current_user: User = Depends(get_current_active_superuser),
) -> DirectorySigningResponse:
    """
    Trigger signing for every file in the specified directory.

    Requires superuser privileges because the operation reads from the server filesystem.
    """
    try:
        return await sign_directory(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc
