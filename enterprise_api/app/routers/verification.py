"""
Verification router for C2PA manifest verification.

Provides both HTML-friendly verification pages and JSON APIs used by SDKs.
"""
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.models.request_models import VerifyRequest

router = APIRouter()


@router.get("/verify/{document_id}", include_in_schema=False)
async def verify_by_document_id_deprecated(document_id: str):
    return JSONResponse(
        status_code=410,
        content={
            "success": False,
            "error": {
                "code": "ENDPOINT_DEPRECATED",
                "message": "This endpoint has been moved to the verification-service for independent scaling.",
                "hint": f"Use GET https://api.encypherai.com/api/v1/verify/{document_id} instead.",
            },
        },
    )


@router.post("/verify", include_in_schema=False)
async def verify_content_deprecated(verify_request: VerifyRequest):
    _ = verify_request
    return JSONResponse(
        status_code=410,
        content={
            "success": False,
            "error": {
                "code": "ENDPOINT_DEPRECATED",
                "message": "This endpoint has been moved to the verification-service for independent scaling.",
                "hint": "Use POST https://api.encypherai.com/api/v1/verify with the same request body.",
            },
        },
    )
