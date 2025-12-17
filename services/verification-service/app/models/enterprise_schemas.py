from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class VerifyRequest(BaseModel):
    text: str = Field(..., min_length=1)


class ErrorDetail(BaseModel):
    code: str
    message: str
    hint: Optional[str] = None


class VerifyVerdict(BaseModel):
    valid: bool
    tampered: bool
    reason_code: str
    signer_id: Optional[str] = None
    signer_name: Optional[str] = None
    timestamp: Optional[datetime] = None
    details: Dict[str, Any] = Field(default_factory=dict)


class VerifyResponse(BaseModel):
    success: bool
    data: Optional[VerifyVerdict] = None
    error: Optional[ErrorDetail] = None
    correlation_id: str
