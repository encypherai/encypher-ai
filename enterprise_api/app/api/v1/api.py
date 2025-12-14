"""
API v1 router configuration.

Combines all v1 endpoints into a single router.
"""
from fastapi import APIRouter

from app.api.v1.endpoints import embeddings, merkle, provisioning
from app.api.v1.enterprise import c2pa
from app.api.v1.public import c2pa as public_c2pa
from app.api.v1.public import verify

api_router = APIRouter()

# Include Merkle tree endpoints
api_router.include_router(merkle.router)

# Include provisioning endpoints
api_router.include_router(provisioning.router)

# Include embedding endpoints (enterprise)
api_router.include_router(embeddings.router)

# Include C2PA custom assertions endpoints (enterprise)
api_router.include_router(c2pa.router, prefix="/enterprise/c2pa", tags=["C2PA Custom Assertions"])

# Include public verification endpoints (no auth)
api_router.include_router(verify.router)

# Include public C2PA endpoints (no auth)
api_router.include_router(public_c2pa.router)
