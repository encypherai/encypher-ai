from fastapi import APIRouter

from app.api.v1.endpoints import analytics_events, demo_requests, tools

api_router = APIRouter()
api_router.include_router(demo_requests.router, prefix="/demo-requests", tags=["demo-requests"])
api_router.include_router(analytics_events.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(tools.router, prefix="/tools", tags=["tools"])
