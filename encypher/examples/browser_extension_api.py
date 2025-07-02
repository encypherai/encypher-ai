"""Browser Extension Verification API Example.

Run with:
    uvicorn encypher.examples.browser_extension_api:app --reload
"""
from typing import Any, Dict, Optional

from fastapi import FastAPI
from pydantic import BaseModel
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from encypher.core.unicode_metadata import UnicodeMetadata

PUBLIC_KEY_PATH = "public_key.pem"
SIGNER_ID = "demo-signer"

with open(PUBLIC_KEY_PATH, "rb") as f:
    PUBLIC_KEY: Ed25519PublicKey = serialization.load_pem_public_key(f.read())

def public_key_provider(signer_id: str) -> Optional[Ed25519PublicKey]:
    return PUBLIC_KEY if signer_id == SIGNER_ID else None

app = FastAPI(title="EncypherAI Browser Extension API")

class VerifyRequest(BaseModel):
    text: str

@app.post("/verify")
async def verify(request: VerifyRequest) -> Dict[str, Any]:
    is_valid, signer_id, payload = UnicodeMetadata.verify_metadata(
        text=request.text,
        public_key_provider=public_key_provider,
    )
    return {
        "is_valid": is_valid,
        "signer_id": signer_id,
        "payload": payload.to_dict() if payload else None,
    }
