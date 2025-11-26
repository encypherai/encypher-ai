"""API endpoints for Verification Service v1"""
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import List, Optional
import httpx

from ...db.session import get_db
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
