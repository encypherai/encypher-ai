from fastapi import APIRouter, Request
from app.schemas.watermark_schemas import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health(request: Request) -> HealthResponse:
    svc = getattr(request.app.state, "trustmark_service", None)
    return HealthResponse(
        status="ok",
        model_loaded=svc.is_available if svc is not None else False,
    )
