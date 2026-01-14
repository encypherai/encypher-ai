from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class EncodeRequest(BaseModel):
    original_text: str
    target: str = "first_letter"
    custom_metadata: dict[str, str] | None = None
    metadata_format: str | None = None
    ai_info: dict[str, str] | None = None

class EncodeResponse(BaseModel):
    encoded_text: str
    metadata: dict[str, Any] | None = None

class DecodeRequest(BaseModel):
    encoded_text: str

class DecodeResponse(BaseModel):
    metadata: dict[str, Any] | None = None
    verification_status: str
    error: str | None = None
    raw_hidden_data: dict[str, Any] | None = None

# Docker service name for enterprise-api
ENTERPRISE_API_URL = "http://encypher-enterprise-api:8000"
# Matching the key set in docker-compose.dev.yml
DEMO_API_KEY = "demo-key-123"

@router.post("/encode", response_model=EncodeResponse, include_in_schema=False)
async def encode_text(request: EncodeRequest):
    _ = request
    raise HTTPException(status_code=410, detail="Deprecated endpoint. Use /api/v1/sign instead.")

@router.post("/decode", response_model=DecodeResponse, include_in_schema=False)
async def decode_text(request: DecodeRequest):
    _ = request
    raise HTTPException(status_code=410, detail="Deprecated endpoint. Use /api/v1/verify instead.")
