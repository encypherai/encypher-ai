"""
API v1 router configuration.

Combines all v1 endpoints into a single router.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import merkle, provisioning
from app.api.v1.endpoints import streaming_merkle, evidence, fingerprint, multi_source
from app.api.v1.enterprise import c2pa
from app.api.v1.enterprise import image_attribution
from app.api.v1.image_verify import router as image_verify_router
from app.api.v1.public import c2pa as public_c2pa
from app.api.v1.public import rights as public_rights
from app.api.v1.public import verify

api_router = APIRouter()

# Include Merkle tree endpoints
api_router.include_router(merkle.router)

# Include provisioning endpoints
api_router.include_router(provisioning.router)

# Include C2PA custom assertions endpoints (enterprise)
api_router.include_router(c2pa.router, prefix="/enterprise/c2pa", tags=["C2PA Custom Assertions"])

# === API Feature Augmentation (TEAM_044) ===
# Include streaming Merkle tree endpoints (Professional+)
api_router.include_router(streaming_merkle.router, prefix="/enterprise")

# Include evidence generation endpoints (Enterprise)
api_router.include_router(evidence.router, prefix="/enterprise")

# Include fingerprint endpoints (Enterprise)
api_router.include_router(fingerprint.router, prefix="/enterprise")

# Include multi-source lookup endpoints (Business+)
api_router.include_router(multi_source.router, prefix="/enterprise")

# Include image attribution endpoint (Enterprise: cross-org pHash search)
api_router.include_router(image_attribution.router, prefix="", tags=["Image Attribution"])

# Include image verification endpoints (no auth -- public)
api_router.include_router(image_verify_router, tags=["Image Verification"])

# Include public verification endpoints (no auth)
api_router.include_router(verify.router)

# Include public C2PA endpoints (no auth)
api_router.include_router(public_c2pa.router)

# === Rights Management System (TEAM_215) ===
# Include public rights resolution endpoints (no auth — discoverability is the point)
api_router.include_router(public_rights.router)
