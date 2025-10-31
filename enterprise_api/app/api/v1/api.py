"""
API v1 router configuration.

Combines all v1 endpoints into a single router.
"""
from fastapi import APIRouter

from app.api.v1.endpoints import merkle, provisioning, embeddings
from app.api.v1.public import verify

api_router = APIRouter()

# Include Merkle tree endpoints
api_router.include_router(merkle.router)

# Include provisioning endpoints
api_router.include_router(provisioning.router)

# Include embedding endpoints (enterprise)
api_router.include_router(embeddings.router)

# Include public verification endpoints (no auth)
api_router.include_router(verify.router)
