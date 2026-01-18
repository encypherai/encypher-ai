from fastapi import APIRouter

from app.api.v1.endpoints import (
    ai_demo,
    analytics_events,
    demo_requests,
    publisher_demo,
    sales,
    tools,
)

api_router = APIRouter()

# Legacy generic endpoints (kept for backwards compatibility)
api_router.include_router(demo_requests.router, prefix="/demo-requests", tags=["demo-requests"])
api_router.include_router(analytics_events.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(tools.router, prefix="/tools", tags=["tools"])

# Context-specific demo endpoints (migrated from old backend)
api_router.include_router(ai_demo.router, prefix="/ai-demo", tags=["AI Demo"])
api_router.include_router(publisher_demo.router, prefix="/publisher-demo", tags=["Publisher Demo"])
api_router.include_router(sales.router, prefix="/sales", tags=["Sales Contact"])
