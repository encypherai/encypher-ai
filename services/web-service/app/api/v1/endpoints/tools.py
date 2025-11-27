import httpx
import uuid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any

router = APIRouter()

class EncodeRequest(BaseModel):
    original_text: str
    target: str = "first_letter"
    custom_metadata: Optional[Dict[str, str]] = None
    metadata_format: Optional[str] = None
    ai_info: Optional[Dict[str, str]] = None

class EncodeResponse(BaseModel):
    encoded_text: str
    metadata: Optional[Dict[str, Any]] = None

class DecodeRequest(BaseModel):
    encoded_text: str

class DecodeResponse(BaseModel):
    metadata: Optional[Dict[str, Any]] = None
    verification_status: str
    error: Optional[str] = None
    raw_hidden_data: Optional[Dict[str, Any]] = None

# Docker service name for enterprise-api
ENTERPRISE_API_URL = "http://encypher-enterprise-api:8000"
# Matching the key set in docker-compose.dev.yml
DEMO_API_KEY = "demo-key-123"

@router.post("/encode", response_model=EncodeResponse)
async def encode_text(request: EncodeRequest):
    """
    Proxy to Enterprise API encode-with-embeddings endpoint.
    """
    doc_id = f"doc_{uuid.uuid4().hex}"
    
    # Combine custom_metadata and ai_info into metadata
    # This ensures both legacy KV pairs and C2PA info are preserved if sent
    metadata_payload = (request.custom_metadata or {}).copy()
    if request.ai_info:
        metadata_payload.update(request.ai_info)
    
    # Map to EncodeWithEmbeddingsRequest
    payload = {
        "document_id": doc_id,
        "text": request.original_text,
        "segmentation_level": "sentence",
        "action": "c2pa.created",
        "metadata": metadata_payload,
        "embedding_options": {
            "format": "plain",
            "method": "data-attribute", # Might be ignored for plain, but required by schema
            "include_text": True
        }
    }
    
    async with httpx.AsyncClient() as client:
        try:
            # Use longer timeout as generating keys/embeddings might take time
            response = await client.post(
                f"{ENTERPRISE_API_URL}/api/v1/enterprise/embeddings/encode-with-embeddings",
                json=payload,
                headers={"Authorization": f"Bearer {DEMO_API_KEY}"},
                timeout=30.0
            )
            
            if response.status_code != 201:
                error_detail = response.text
                try:
                    error_json = response.json()
                    if "detail" in error_json:
                        error_detail = error_json["detail"]
                except Exception:
                    pass
                raise HTTPException(status_code=response.status_code, detail=f"Enterprise API Error: {error_detail}")
            
            data = response.json()
            encoded = data.get("embedded_content")
            metadata = data.get("metadata")
            
            if not encoded:
                # Fallback if API returns empty content but success
                # This might happen if 'plain' format isn't fully supported for embedding injection in the version
                encoded = request.original_text
                
            return {"encoded_text": encoded, "metadata": metadata}
            
        except httpx.ConnectError:
            raise HTTPException(status_code=503, detail="Enterprise API not available")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

@router.post("/decode", response_model=DecodeResponse)
async def decode_text(request: DecodeRequest):
    """
    Proxy to Enterprise API verify endpoint.
    """
    payload = {"text": request.encoded_text}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{ENTERPRISE_API_URL}/api/v1/verify",
                json=payload,
                # Verify might be public, but passing auth doesn't hurt if it accepts it
                headers={"Authorization": f"Bearer {DEMO_API_KEY}"},
                timeout=30.0
            )
            
            if response.status_code != 200:
                 # Try to handle specific error codes
                raise HTTPException(status_code=response.status_code, detail=response.text)

            data = response.json()
            
            # VerifyResponse: { success: bool, data: Verdict, error: ... }
            success = data.get("success", False)
            verdict = data.get("data", {})
            
            # Verdict object uses 'valid' field
            is_valid = verdict.get("valid", False) if verdict else False
            
            verification_status = "Success" if (success and is_valid) else "Failure"
            
            # Extract metadata if available
            details = verdict.get("details", {})
            manifest = details.get("manifest", {})
            metadata = {
                "manifest": manifest
            }
            
            return {
                "metadata": metadata,
                "verification_status": verification_status,
                "raw_hidden_data": verdict
            }
            
        except httpx.ConnectError:
             raise HTTPException(status_code=503, detail="Enterprise API not available")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
