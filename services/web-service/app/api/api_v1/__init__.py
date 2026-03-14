"""
API v1 router registration.

Route groups:
- /demo-requests  : Admin CRUD for all demo request records (requires X-Internal-Token)
- /marketing-analytics : Analytics event ingestion and session lookup
- /tools          : Legacy encode/decode endpoints (deprecated, returns 410)
- /ai-demo        : Public POST for AI Demo landing page submissions
- /publisher-demo : Public POST for Publisher Demo landing page submissions
- /sales          : Public POST for enterprise and general sales contact forms
- /newsletter     : Newsletter subscribe/unsubscribe, broadcast, and subscriber admin

Note: /ai-demo/demo-requests and /publisher-demo/demo-requests are kept as separate
routes for backward compatibility. They share the same underlying DemoRequest model
and differ only in their default `source` label. A future consolidation into a single
/demo-requests POST with a required `source` field is tracked in TODO.md.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    ai_demo,
    analytics_events,
    demo_requests,
    newsletter,
    publisher_demo,
    sales,
    tools,
)

api_router = APIRouter()

# Admin-facing endpoints (require X-Internal-Token)
api_router.include_router(demo_requests.router, prefix="/demo-requests", tags=["demo-requests"])

# Public analytics ingestion
api_router.include_router(analytics_events.router, prefix="/marketing-analytics", tags=["analytics"])

# Legacy tool endpoints (deprecated, returns 410 Gone)
api_router.include_router(tools.router, prefix="/tools", tags=["tools"])

# Context-specific public demo-request endpoints
api_router.include_router(ai_demo.router, prefix="/ai-demo", tags=["AI Demo"])
api_router.include_router(publisher_demo.router, prefix="/publisher-demo", tags=["Publisher Demo"])
api_router.include_router(sales.router, prefix="/sales", tags=["Sales Contact"])
api_router.include_router(newsletter.router, prefix="/newsletter", tags=["Newsletter"])
