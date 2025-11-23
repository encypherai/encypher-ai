"""Verification service business logic"""
import time
from typing import Optional, Tuple, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func
import httpx

from ..db.models import VerificationResult, VerificationLog
from ..models.schemas import SignatureVerify, DocumentVerify
from ..core.crypto import verify_signature, verify_content_hash, check_tampering
from ..core.config import settings


class VerificationService:
    """Document verification service"""
    
    @staticmethod
    async def get_document_from_encoding_service(document_id: str) -> Optional[Dict[str, Any]]:
        """Fetch document from Encoding Service"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{settings.ENCODING_SERVICE_URL}/api/v1/encode/documents/{document_id}",
                    timeout=5.0
                )
                if response.status_code == 200:
                    return response.json()
                return None
        except Exception:
            return None
    
    @staticmethod
    def verify_signature_only(
        db: Session,
        user_id: Optional[str],
        verify_data: SignatureVerify,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Tuple[VerificationResult, float]:
        """Verify signature only"""
        start_time = time.time()
        
        # Verify signature
        is_valid, error_msg = verify_signature(
            verify_data.content,
            verify_data.signature,
            verify_data.public_key_pem
        )
        
        # Verify content hash
        content_hash = verify_content_hash(verify_data.content, verify_data.signature[:64])
        
        # Calculate confidence
        confidence = 1.0 if is_valid and content_hash else 0.0
        
        processing_time = (time.time() - start_time) * 1000
        
        # Create result
        result = VerificationResult(
            document_id="signature_only",
            user_id=user_id,
            is_valid=is_valid,
            is_tampered=not is_valid,
            signature_valid=is_valid,
            hash_valid=content_hash,
            confidence_score=confidence,
            content_hash=verify_data.signature[:64],
            signature=verify_data.signature,
            error_message=error_msg if not is_valid else None,
            verification_time_ms=int(processing_time),
            ip_address=ip_address,
            user_agent=user_agent,
        )
        
        db.add(result)
        db.commit()
        db.refresh(result)
        
        # Log operation
        VerificationService._log_verification(
            db=db,
            document_id="signature_only",
            user_id=user_id,
            operation_type="verify_signature",
            status="success",
            result="valid" if is_valid else "invalid",
            processing_time_ms=int(processing_time),
            ip_address=ip_address,
            user_agent=user_agent,
        )
        
        return result, processing_time
    
    @staticmethod
    async def verify_document_complete(
        db: Session,
        user_id: Optional[str],
        verify_data: DocumentVerify,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Tuple[VerificationResult, float]:
        """Complete document verification"""
        start_time = time.time()
        
        # Get document from encoding service
        doc = await VerificationService.get_document_from_encoding_service(verify_data.document_id)
        
        if not doc:
            processing_time = (time.time() - start_time) * 1000
            result = VerificationResult(
                document_id=verify_data.document_id,
                user_id=user_id,
                is_valid=False,
                is_tampered=True,
                signature_valid=False,
                hash_valid=False,
                confidence_score=0.0,
                content_hash="",
                signature="",
                error_message="Document not found",
                verification_time_ms=int(processing_time),
                ip_address=ip_address,
                user_agent=user_agent,
            )
            db.add(result)
            db.commit()
            db.refresh(result)
            return result, processing_time
        
        # Verify content hash
        hash_valid = verify_content_hash(verify_data.content, doc["content_hash"])
        
        # Check tampering
        is_tampered, similarity = check_tampering(doc["original_content"], verify_data.content)
        
        # Verify signature (simplified - would need public key)
        signature_valid = hash_valid and not is_tampered
        
        # Calculate confidence
        confidence = similarity if not is_tampered else 0.0
        
        # Collect warnings
        warnings = []
        if is_tampered:
            warnings.append("Content has been modified")
        if not hash_valid:
            warnings.append("Content hash mismatch")
        
        processing_time = (time.time() - start_time) * 1000
        
        # Create result
        result = VerificationResult(
            document_id=verify_data.document_id,
            user_id=user_id,
            is_valid=signature_valid and hash_valid and not is_tampered,
            is_tampered=is_tampered,
            signature_valid=signature_valid,
            hash_valid=hash_valid,
            confidence_score=confidence,
            similarity_score=similarity,
            content_hash=doc["content_hash"],
            signature=doc["signature"],
            signer_id=doc.get("signer_id"),
            warnings=warnings if warnings else None,
            verification_time_ms=int(processing_time),
            ip_address=ip_address,
            user_agent=user_agent,
        )
        
        db.add(result)
        db.commit()
        db.refresh(result)
        
        # Log operation
        VerificationService._log_verification(
            db=db,
            document_id=verify_data.document_id,
            user_id=user_id,
            operation_type="verify_document",
            status="success",
            result="valid" if result.is_valid else ("tampered" if is_tampered else "invalid"),
            processing_time_ms=int(processing_time),
            ip_address=ip_address,
            user_agent=user_agent,
        )
        
        return result, processing_time
    
    @staticmethod
    def get_verification_history(
        db: Session,
        document_id: str,
        limit: int = 100
    ) -> List[VerificationResult]:
        """Get verification history for a document"""
        return db.query(VerificationResult).filter(
            VerificationResult.document_id == document_id
        ).order_by(VerificationResult.created_at.desc()).limit(limit).all()
    
    @staticmethod
    def get_verification_stats(db: Session, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get verification statistics"""
        query = db.query(VerificationResult)
        if user_id:
            query = query.filter(VerificationResult.user_id == user_id)
        
        total = query.count()
        valid = query.filter(VerificationResult.is_valid == True).count()
        invalid = total - valid
        tampered = query.filter(VerificationResult.is_tampered == True).count()
        
        avg_confidence = query.with_entities(func.avg(VerificationResult.confidence_score)).scalar() or 0.0
        avg_time = query.with_entities(func.avg(VerificationResult.verification_time_ms)).scalar() or 0.0
        
        return {
            "total_verifications": total,
            "valid_verifications": valid,
            "invalid_verifications": invalid,
            "tampered_documents": tampered,
            "average_confidence_score": float(avg_confidence),
            "average_verification_time_ms": float(avg_time),
        }
    
    @staticmethod
    def _log_verification(
        db: Session,
        document_id: str,
        user_id: Optional[str],
        operation_type: str,
        status: str,
        result: str,
        processing_time_ms: int,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> VerificationLog:
        """Log verification operation"""
        log = VerificationLog(
            document_id=document_id,
            user_id=user_id,
            operation_type=operation_type,
            status=status,
            result=result,
            processing_time_ms=processing_time_ms,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return log
