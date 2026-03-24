"""
Encypher Enterprise API - Main Application

FastAPI application for C2PA-compliant content signing and verification.
"""

import logging

from fastapi import FastAPI

from app.bootstrap import (
    lifespan,
    register_application_routers,
    register_docs_routes,
    register_exception_handlers,
    register_middleware,
    register_probe_routes,
)
from app.bootstrap.docs import build_public_openapi as _build_public_openapi
from app.bootstrap.logging_setup import configure_logging
from app.dependencies import require_super_admin_dep

configure_logging()
logger = logging.getLogger(__name__)


# Create FastAPI app
app = FastAPI(
    title="Encypher Enterprise API",
    description="C2PA-compliant content signing and verification infrastructure for publishers, legal/finance firms, AI labs, and enterprises",
    version="2.0.0",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
    lifespan=lifespan,
)


register_middleware(app)
register_probe_routes(app)
register_docs_routes(app, require_super_admin_dep)
register_application_routers(app)
register_exception_handlers(app)


def build_public_openapi():
    return _build_public_openapi(app)
