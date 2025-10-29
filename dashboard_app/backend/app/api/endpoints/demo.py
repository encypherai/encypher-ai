"""
Demo corpus generation endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status

from app.models.user import User
from app.schemas.demo import DemoGenerateRequest, DemoGenerateResponse
from app.services.demo_generator import generate_demo_corpus
from app.services.user import get_current_active_superuser

router = APIRouter()


@router.post(
    "/generate",
    response_model=DemoGenerateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate a sample directory corpus for demos.",
)
async def generate_demo_endpoint(
    payload: DemoGenerateRequest,
    current_user: User = Depends(get_current_active_superuser),
) -> DemoGenerateResponse:
    """
    Create a demo file structure with subdirectories by topic and randomized
    example articles, suitable for driving signing/scanning demos.
    """
    try:
        result = generate_demo_corpus(payload)
        return result
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc
