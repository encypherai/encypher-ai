"""
API v1 router configuration.

Combines all v1 endpoints into a single router.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import evidence, fingerprint, internal_usage, merkle, multi_source, provisioning, streaming_merkle
from app.api.v1.enterprise import audio_attribution, c2pa, image_attribution, video_attribution, video_stream_attribution
from app.api.v1.audio_verify import router as audio_verify_router
from app.api.v1.image_verify import router as image_verify_router
from app.api.v1.video_verify import router as video_verify_router
from app.api.v1.public import c2pa as public_c2pa
from app.api.v1.public import cdn_signing as public_cdn_signing
from app.api.v1.public import prebid as public_prebid
from app.api.v1.public import rights as public_rights
from app.api.v1.public import verify

api_router = APIRouter()

# Include Merkle tree endpoints
api_router.include_router(merkle.router)

# Include provisioning endpoints
api_router.include_router(provisioning.router)

# Include internal usage/overage billing endpoints
api_router.include_router(internal_usage.router)

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

# Include audio C2PA signing and verification endpoints
api_router.include_router(audio_attribution.router, prefix="", tags=["Audio Attribution"])

# Include video C2PA signing and verification endpoints
api_router.include_router(video_attribution.router, prefix="", tags=["Video Attribution"])

# Include video stream C2PA signing endpoints (C2PA 2.3 Section 19)
api_router.include_router(video_stream_attribution.router, prefix="", tags=["Video Stream Attribution"])

# Include image verification endpoints (no auth -- public)
api_router.include_router(image_verify_router, tags=["Image Verification"])

# Include audio verification endpoint (no auth -- public)
api_router.include_router(audio_verify_router, tags=["Audio Verification"])

# Include video verification endpoint (no auth -- public)
api_router.include_router(video_verify_router, tags=["Video Verification"])

# Include public verification endpoints (no auth)
api_router.include_router(verify.router)

# Include public C2PA endpoints (no auth)
api_router.include_router(public_c2pa.router)

# === Rights Management System (TEAM_215) ===
# Include public rights resolution endpoints (no auth — discoverability is the point)
api_router.include_router(public_rights.router)

# === Prebid Auto-Provenance (TEAM_283) ===
# Include public Prebid RTD signing endpoints (no auth — rate limited by IP/domain)
api_router.include_router(public_prebid.router)

# === CDN Edge Provenance Worker (TEAM_298) ===
# Include public CDN signing endpoints (no auth — rate limited by IP/domain)
api_router.include_router(public_cdn_signing.router)
