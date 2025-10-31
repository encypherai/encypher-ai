"""
Encypher Enterprise API - Main Application

FastAPI application for C2PA-compliant content signing and verification.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from sqlalchemy import text

from app.config import settings
from app.routers import signing, verification, lookup, onboarding, streaming, kafka, chat
from app.api.v1.api import api_router as api_v1_router
from app.database import engine
from app.services.session_service import session_service

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.is_production else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler replacing deprecated on_event startup/shutdown."""
    logger.info("Encypher Enterprise API starting up...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(
        f"Database: {settings.database_url.split('@')[1] if '@' in settings.database_url else 'Not configured'}"
    )
    logger.info(f"SSL.com API: {settings.ssl_com_api_url}")
    
    # Initialize Redis connection for session management
    try:
        await session_service.connect()
    except Exception as e:
        logger.warning(f"Failed to connect to Redis: {e}. Running without session persistence.")
    
    # Initialize database schema on startup
    try:
        logger.info("Initializing database schema...")
        # Look for schema file in scripts directory
        schema_file = Path(__file__).parent.parent / "scripts" / "init_db.sql"
        if schema_file.exists():
            async with engine.begin() as conn:
                schema_sql = schema_file.read_text()
                # Split by semicolon and execute each statement
                for statement in schema_sql.split(';'):
                    statement = statement.strip()
                    if statement:
                        await conn.execute(text(statement))
            logger.info("Database schema initialized successfully")
        else:
            logger.warning(f"Schema file not found at {schema_file}")
            logger.info("Skipping schema initialization - database may already be initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database schema: {e}", exc_info=True)
        logger.info("Continuing startup - database may already be initialized")
    
    try:
        yield
    finally:
        logger.info("Encypher Enterprise API shutting down...")
        # Cleanup Redis connection
        try:
            await session_service.disconnect()
        except Exception as e:
            logger.error(f"Error disconnecting from Redis: {e}")

# Create FastAPI app
app = FastAPI(
    title="Encypher Enterprise API",
    description="C2PA-compliant content signing and verification infrastructure for publishers, legal/finance firms, AI labs, and enterprises",
    version="1.0.0-preview",
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
    openapi_url="/openapi.json" if not settings.is_production else None,
    lifespan=lifespan,
)

# CORS middleware (configure allowed origins)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        f"https://{settings.marketing_domain}",
        f"https://{settings.infrastructure_domain}",
        f"https://api.{settings.infrastructure_domain}",
        f"https://verify.{settings.infrastructure_domain}",
        f"https://dashboard.{settings.infrastructure_domain}",
        "http://localhost:3000",  # For local development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests and add processing time header."""
    start_time = time.time()

    # Log request
    logger.info(f"{request.method} {request.url.path} - Client: {request.client.host}")

    # Process request
    response = await call_next(request)

    # Calculate processing time
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)

    # Log response
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.4f}s"
    )

    return response


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring.

    Returns:
        dict: Status and environment information
    """
    return {
        "status": "healthy",
        "environment": settings.environment,
        "version": "1.0.0-preview"
    }


# Root endpoint
@app.get("/", tags=["Info"])
async def root():
    """
    API root endpoint with basic information.

    Returns:
        dict: API information
    """
    return {
        "name": "Encypher Enterprise API",
        "version": "1.0.0-preview",
        "description": "C2PA-compliant content signing and verification",
        "docs": f"{settings.api_base_url}/docs" if not settings.is_production else None,
        "status": "preview"  # Will change to "production" after C2PA spec publication
    }


# Include routers
app.include_router(signing.router, prefix="/api/v1", tags=["Signing"])
app.include_router(verification.router, prefix="/api/v1", tags=["Verification"])
app.include_router(lookup.router, prefix="/api/v1", tags=["Lookup"])
app.include_router(onboarding.router, prefix="/api/v1/onboarding", tags=["Onboarding"])
app.include_router(streaming.router, prefix="/api/v1", tags=["Streaming"])
app.include_router(kafka.router, prefix="/api/v1", tags=["Kafka"])
app.include_router(chat.router, prefix="/api/v1", tags=["Chat"])

# Include v1 API router (Merkle tree endpoints)
app.include_router(api_v1_router, prefix="/api/v1")


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled errors.

    Args:
        request: The incoming request
        exc: The exception that was raised

    Returns:
        JSONResponse with error details
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "details": str(exc) if settings.is_development else None
            }
        }
    )


 
