import asyncio
import logging

from app.config import settings
from app.database import engine
from app.observability.metrics import render_prometheus
from app.services.session_service import session_service
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import PlainTextResponse
from sqlalchemy import text

logger = logging.getLogger(__name__)


def register_probe_routes(app: FastAPI) -> None:
    @app.get("/health", tags=["Health"])
    async def health_check():
        if not settings.expose_health_details:
            return {"status": "healthy"}
        return {
            "status": "healthy",
            "environment": settings.environment,
            "version": "1.0.0-preview",
        }

    @app.get("/readyz", tags=["Health"])
    async def readiness_check():
        import httpx as _httpx

        db_status = "ok"
        try:
            async with engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
        except Exception as exc:
            logger.warning("Readiness DB probe failed: %s", exc)
            db_status = "error"
        redis_status = "ok" if session_service.redis_client else "degraded"

        async def _probe(url: str) -> str:
            try:
                async with _httpx.AsyncClient(timeout=2.0) as client:
                    response = await client.get(url)
                return "ok" if response.status_code < 500 else "degraded"
            except Exception:
                return "degraded"

        key_service_status, auth_service_status = await asyncio.gather(
            _probe(f"{settings.key_service_url}/health"),
            _probe(f"{settings.auth_service_url}/health"),
        )

        all_ok = all(status_value == "ok" for status_value in (db_status, key_service_status, auth_service_status))
        status_text = "ready" if all_ok else "degraded"
        if not settings.expose_readiness_details:
            return {"status": status_text}
        return {
            "status": status_text,
            "database": db_status,
            "redis": redis_status,
            "key_service": key_service_status,
            "auth_service": auth_service_status,
            "version": "1.0.0-preview",
        }

    @app.get("/metrics", include_in_schema=False)
    async def metrics():
        if not settings.enable_public_metrics_endpoint:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
        return PlainTextResponse(render_prometheus(), media_type="text/plain; version=0.0.4")

    @app.get("/", tags=["Info"])
    async def root():
        return {
            "name": "Encypher Enterprise API",
            "version": "1.0.0-preview",
            "description": "C2PA-compliant content signing and verification",
            "docs": f"{settings.api_base_url}/docs" if settings.enable_public_api_docs else None,
            "status": "preview",
        }
