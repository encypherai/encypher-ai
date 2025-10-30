"""
Encoding service business logic
"""
import time
from datetime import datetime
from typing import Optional, Tuple, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
import httpx

from ..db.models import EncodedDocument, SigningOperation
from ..models.schemas import DocumentSign, DocumentEmbed
from ..core.crypto import (
    generate_document_id,
    hash_content,
    sign_content,
    create_manifest,
)
from ..core.config import settings


class EncodingService:
    """Document encoding and signing service"""
    
    @staticmethod
    async def verify_api_key(api_key: str) -> Optional[Dict[str, Any]]:
        """
        Verify API key with Key Service
        
        Returns:
            Key information if valid, None otherwise
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{settings.KEY_SERVICE_URL}/api/v1/keys/verify",
                    json={"key": api_key},
                    timeout=5.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("valid"):
                        return data
                return None
        except Exception:
            return None
    
    @staticmethod
    def sign_document(
        db: Session,
        user_id: str,
        document_data: DocumentSign,
        private_key_pem: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Tuple[EncodedDocument, float]:
        """
        Sign a document with cryptographic signature
        
        Returns:
            (EncodedDocument, processing_time_ms)
        """
        start_time = time.time()
        
        try:
            # Generate document ID
            document_id = generate_document_id()
            
            # Hash content
            content_hash = hash_content(document_data.content)
            
            # Sign content
            signature = sign_content(document_data.content, private_key_pem)
            
            # Create manifest
            manifest = create_manifest(
                document_id=document_id,
                content_hash=content_hash,
                signature=signature,
                metadata=document_data.metadata or {}
            )
            
            # For now, encoded content is same as original
            # In production, this would use Unicode steganography
            encoded_content = document_data.content
            
            # Create database record
            db_document = EncodedDocument(
                user_id=user_id,
                document_id=document_id,
                original_content=document_data.content,
                encoded_content=encoded_content,
                content_hash=content_hash,
                signature=signature,
                signer_id=user_id,
                manifest=manifest,
                metadata=document_data.metadata,
                format=document_data.format,
                encoding_method=settings.DEFAULT_ENCODING,
            )
            
            db.add(db_document)
            db.commit()
            db.refresh(db_document)
            
            # Calculate processing time
            processing_time = (time.time() - start_time) * 1000
            
            # Log operation
            EncodingService._log_operation(
                db=db,
                document_id=document_id,
                user_id=user_id,
                operation_type="sign",
                status="success",
                processing_time_ms=int(processing_time),
                content_size_bytes=len(document_data.content),
                ip_address=ip_address,
                user_agent=user_agent,
            )
            
            return db_document, processing_time
            
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            
            # Log failed operation
            EncodingService._log_operation(
                db=db,
                document_id=document_id if 'document_id' in locals() else "unknown",
                user_id=user_id,
                operation_type="sign",
                status="failed",
                error_message=str(e),
                processing_time_ms=int(processing_time),
                content_size_bytes=len(document_data.content),
                ip_address=ip_address,
                user_agent=user_agent,
            )
            
            raise
    
    @staticmethod
    def embed_metadata(
        db: Session,
        user_id: str,
        document_data: DocumentEmbed,
    ) -> EncodedDocument:
        """
        Embed metadata into document without signing
        """
        # Generate document ID
        document_id = generate_document_id()
        
        # Hash content
        content_hash = hash_content(document_data.content)
        
        # For now, encoded content is same as original
        # In production, this would use Unicode steganography
        encoded_content = document_data.content
        
        # Create simple manifest without signature
        manifest = {
            "manifest_id": document_id,
            "version": "2.0",
            "content_hash": content_hash,
            "metadata": document_data.metadata,
        }
        
        # Create database record
        db_document = EncodedDocument(
            user_id=user_id,
            document_id=document_id,
            original_content=document_data.content,
            encoded_content=encoded_content,
            content_hash=content_hash,
            signature="",  # No signature for embed-only
            signer_id=user_id,
            manifest=manifest,
            metadata=document_data.metadata,
            format=document_data.format,
            encoding_method=settings.DEFAULT_ENCODING,
        )
        
        db.add(db_document)
        db.commit()
        db.refresh(db_document)
        
        return db_document
    
    @staticmethod
    def get_document(db: Session, document_id: str, user_id: str) -> Optional[EncodedDocument]:
        """Get a document by ID"""
        return db.query(EncodedDocument).filter(
            EncodedDocument.document_id == document_id,
            EncodedDocument.user_id == user_id
        ).first()
    
    @staticmethod
    def get_user_documents(db: Session, user_id: str, limit: int = 100) -> list[EncodedDocument]:
        """Get all documents for a user"""
        return db.query(EncodedDocument).filter(
            EncodedDocument.user_id == user_id
        ).order_by(EncodedDocument.created_at.desc()).limit(limit).all()
    
    @staticmethod
    def get_operation_stats(db: Session, user_id: str) -> Dict[str, Any]:
        """Get operation statistics for a user"""
        # Total operations
        total = db.query(SigningOperation).filter(
            SigningOperation.user_id == user_id
        ).count()
        
        # Successful operations
        successful = db.query(SigningOperation).filter(
            SigningOperation.user_id == user_id,
            SigningOperation.status == "success"
        ).count()
        
        # Failed operations
        failed = total - successful
        
        # Average processing time
        avg_time = db.query(func.avg(SigningOperation.processing_time_ms)).filter(
            SigningOperation.user_id == user_id,
            SigningOperation.status == "success"
        ).scalar() or 0.0
        
        # Total content size
        total_size = db.query(func.sum(SigningOperation.content_size_bytes)).filter(
            SigningOperation.user_id == user_id
        ).scalar() or 0
        
        return {
            "total_operations": total,
            "successful_operations": successful,
            "failed_operations": failed,
            "average_processing_time_ms": float(avg_time),
            "total_content_size_bytes": int(total_size),
        }
    
    @staticmethod
    def _log_operation(
        db: Session,
        document_id: str,
        user_id: str,
        operation_type: str,
        status: str,
        processing_time_ms: Optional[int] = None,
        content_size_bytes: Optional[int] = None,
        error_message: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> SigningOperation:
        """Log a signing operation"""
        operation = SigningOperation(
            document_id=document_id,
            user_id=user_id,
            operation_type=operation_type,
            status=status,
            error_message=error_message,
            processing_time_ms=processing_time_ms,
            content_size_bytes=content_size_bytes,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        
        db.add(operation)
        db.commit()
        db.refresh(operation)
        
        return operation
