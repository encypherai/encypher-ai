"""
API v1 router configuration.

Combines all v1 endpoints into a single router.
"""
from fastapi import APIRouter

from app.api.v1.endpoints import merkle, provisioning

api_router = APIRouter()

# Include Merkle tree endpoints
api_router.include_router(merkle.router)

# Include provisioning endpoints
api_router.include_router(provisioning.router)

# TODO: Add other endpoint routers as they are created
# api_router.include_router(signing.router)
# api_router.include_router(verification.router)
