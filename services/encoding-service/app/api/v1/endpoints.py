"""
API endpoints for Encoding Service v1
"""
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import List, Optional
import httpx

from ...db.session import get_db
from ...models.schemas import (
    DocumentSign,
    DocumentEmbed,
    SignedDocumentResponse,
    DocumentInfo,
    ManifestResponse,
    MessageResponse,
    OperationStats,
)
from ...services.encoding_service import EncodingService
from ...core.config import settings

router = APIRouter()

# Temporary demo private key for development
DEMO_PRIVATE_KEY = """-----BEGIN PRIVATE KEY-----
MC4CAQAwBQYDK2VwBCIEIJ+DYvh6SEqVTm50DFtMDoQikTmiCqirVv9mWG9qfSnF
-----END PRIVATE KEY-----"""


async def get_current_user(authorization: str = Header(...)) -> dict:
    """
    Verify user token with auth service
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.AUTH_SERVICE_URL}/api/v1/auth/verify",
                headers={"Authorization": authorization}
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials",
                )
            
            return response.json()
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Auth service unavailable",
        )


@router.post("/sign", response_model=SignedDocumentResponse, status_code=status.HTTP_201_CREATED)
async def sign_document(
    document_data: DocumentSign,
    x_forwarded_for: Optional[str] = Header(None),
    user_agent: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    """
    Sign a document with cryptographic signature
    
    **Important:** Requires a valid API key
    
    - **content**: Document content to sign
    - **metadata**: Optional metadata to include
    - **format**: Document format (text, json, markdown)
    - **api_key**: Valid API key from Key Service
    """
    # Verify API key
    key_info = await EncodingService.verify_api_key(document_data.api_key)
    
    if not key_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
    
    # Check permissions
    if "sign" not in key_info.get("permissions", []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API key does not have 'sign' permission",
        )
    
    user_id = key_info["user_id"]
    
    # Check document size
    if len(document_data.content) > settings.MAX_DOCUMENT_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Document size exceeds maximum of {settings.MAX_DOCUMENT_SIZE} bytes",
        )
    
    # Check format
    if document_data.format not in settings.supported_formats_list:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported format. Supported: {settings.SUPPORTED_FORMATS}",
        )
    
    try:
        # Sign document
        db_document, processing_time = EncodingService.sign_document(
            db=db,
            user_id=user_id,
            document_data=document_data,
            private_key_pem=DEMO_PRIVATE_KEY,  # TODO: Get from secure storage
            ip_address=x_forwarded_for,
            user_agent=user_agent,
        )
        
        return SignedDocumentResponse(
            document_id=db_document.document_id,
            encoded_content=db_document.encoded_content,
            signature=db_document.signature,
            content_hash=db_document.content_hash,
            manifest=db_document.manifest,
            created_at=db_document.created_at,
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sign document: {str(e)}",
        )


@router.post("/embed", response_model=SignedDocumentResponse, status_code=status.HTTP_201_CREATED)
async def embed_metadata(
    document_data: DocumentEmbed,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Embed metadata into document without signing
    
    - **content**: Document content
    - **metadata**: Metadata to embed
    - **format**: Document format
    """
    # Check document size
    if len(document_data.content) > settings.MAX_DOCUMENT_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Document size exceeds maximum of {settings.MAX_DOCUMENT_SIZE} bytes",
        )
    
    try:
        db_document = EncodingService.embed_metadata(
            db=db,
            user_id=current_user["id"],
            document_data=document_data,
        )
        
        return SignedDocumentResponse(
            document_id=db_document.document_id,
            encoded_content=db_document.encoded_content,
            signature=db_document.signature,
            content_hash=db_document.content_hash,
            manifest=db_document.manifest,
            created_at=db_document.created_at,
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to embed metadata: {str(e)}",
        )


@router.get("/documents", response_model=List[DocumentInfo])
async def list_documents(
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    List all documents for the current user
    
    - **limit**: Maximum number of documents to return
    """
    documents = EncodingService.get_user_documents(db, current_user["id"], limit)
    return documents


@router.get("/documents/{document_id}", response_model=DocumentInfo)
async def get_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get details of a specific document
    
    - **document_id**: Document ID
    """
    document = EncodingService.get_document(db, document_id, current_user["id"])
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    
    return document


@router.get("/documents/{document_id}/manifest", response_model=ManifestResponse)
async def get_manifest(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get the manifest for a document
    
    - **document_id**: Document ID
    """
    document = EncodingService.get_document(db, document_id, current_user["id"])
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    
    return ManifestResponse(**document.manifest)


@router.get("/stats", response_model=OperationStats)
async def get_stats(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get operation statistics for the current user
    """
    stats = EncodingService.get_operation_stats(db, current_user["id"])
    return OperationStats(**stats)


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "encoding-service"}
