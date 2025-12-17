"""API endpoints for Verification Service v1"""
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import List, Optional
import httpx
from uuid import uuid4

from ...db.session import get_db
from ...models.enterprise_schemas import VerifyRequest, VerifyResponse, VerifyVerdict
from ...models.schemas import (
    SignatureVerify,
    DocumentVerify,
    VerificationResponse,
    VerificationHistory,
    VerificationStats,
)
from ...services.verification_service import VerificationService
from ...core.config import settings

router = APIRouter()


async def get_current_user(authorization: str = Header(None)) -> Optional[dict]:
    """Verify user token with auth service (optional)"""
    if not authorization:
        return None

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.AUTH_SERVICE_URL}/api/v1/auth/verify",
                headers={"Authorization": authorization}
            )
            if response.status_code == 200:
                return response.json()
            return None
    except Exception:
        return None


async def get_current_organization(authorization: str = Header(None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    api_key = authorization.split(" ", 1)[1].strip()
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.KEY_SERVICE_URL}/api/v1/keys/validate",
                json={"key": api_key},
                timeout=5.0,
            )
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Key service unavailable",
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = response.json()
    data = payload.get("data")
    if not payload.get("success") or not isinstance(data, dict):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return data


@router.post("", response_model=VerifyResponse)
async def verify_text(
    verify_request: VerifyRequest,
    organization: dict = Depends(get_current_organization),
):
    correlation_id = f"req-{uuid4().hex}"
    verdict = VerifyVerdict(
        valid=False,
        tampered=True,
        reason_code="NOT_IMPLEMENTED",
        signer_id=None,
        signer_name=None,
        timestamp=None,
        details={},
    )
    return VerifyResponse(success=True, data=verdict, error=None, correlation_id=correlation_id)


@router.post("/signature", response_model=VerificationResponse)
async def verify_signature(
    verify_data: SignatureVerify,
    x_forwarded_for: Optional[str] = Header(None),
    user_agent: Optional[str] = Header(None),
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user),
):
    """
    Verify a signature (public endpoint)
    
    - **content**: Original content
    - **signature**: Hex-encoded signature
    - **public_key_pem**: PEM-encoded public key
    """
    try:
        result, processing_time = VerificationService.verify_signature_only(
            db=db,
            user_id=current_user["id"] if current_user else None,
            verify_data=verify_data,
            ip_address=x_forwarded_for,
            user_agent=user_agent,
        )

        return VerificationResponse(
            is_valid=result.is_valid,
            is_tampered=result.is_tampered,
            signature_valid=result.signature_valid,
            hash_valid=result.hash_valid,
            confidence_score=result.confidence_score,
            similarity_score=result.similarity_score,
            signer_id=result.signer_id,
            warnings=result.warnings,
            verification_time_ms=result.verification_time_ms,
            created_at=result.created_at,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Verification failed: {str(e)}",
        )


@router.post("/document", response_model=VerificationResponse)
async def verify_document(
    verify_data: DocumentVerify,
    x_forwarded_for: Optional[str] = Header(None),
    user_agent: Optional[str] = Header(None),
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user),
):
    """
    Complete document verification (public endpoint)
    
    - **document_id**: Document ID from encoding service
    - **content**: Current content to verify
    """
    try:
        result, processing_time = await VerificationService.verify_document_complete(
            db=db,
            user_id=current_user["id"] if current_user else None,
            verify_data=verify_data,
            ip_address=x_forwarded_for,
            user_agent=user_agent,
        )

        return VerificationResponse(
            is_valid=result.is_valid,
            is_tampered=result.is_tampered,
            signature_valid=result.signature_valid,
            hash_valid=result.hash_valid,
            confidence_score=result.confidence_score,
            similarity_score=result.similarity_score,
            signer_id=result.signer_id,
            warnings=result.warnings,
            verification_time_ms=result.verification_time_ms,
            created_at=result.created_at,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Verification failed: {str(e)}",
        )


@router.get("/history/{document_id}", response_model=List[VerificationHistory])
async def get_verification_history(
    document_id: str,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """
    Get verification history for a document (public endpoint)
    
    - **document_id**: Document ID
    - **limit**: Maximum number of results
    """
    history = VerificationService.get_verification_history(db, document_id, limit)
    return history


@router.get("/stats", response_model=VerificationStats)
async def get_stats(
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user),
):
    """Get verification statistics"""
    user_id = current_user["id"] if current_user else None
    stats = VerificationService.get_verification_stats(db, user_id)
    return VerificationStats(**stats)


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "verification-service"}
