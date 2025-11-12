"""
API Gateway - Minimal FastAPI gateway that proxies selected routes to downstream services
"""
from contextlib import asynccontextmanager
import uuid
import logging
from typing import Dict, Iterable, Tuple

import httpx
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from prometheus_fastapi_instrumentator import Instrumentator

from .core.config import settings
from .core.logging_config import setup_logging


# Initialize logging
logger = setup_logging(settings.LOG_LEVEL)


HOP_BY_HOP_HEADERS = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "transfer-encoding",
    "upgrade",
}


def _filter_response_headers(headers: Iterable[Tuple[str, str]]) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for k, v in headers:
        lk = k.lower()
        if lk in HOP_BY_HOP_HEADERS:
            continue
        # Prevent overriding CORS from the gateway
        if lk.startswith("access-control-"):
            continue
        out[k] = v
    return out


async def _forward(request: Request, target_base: str, target_path: str) -> Response:
    # Preserve method, query, headers, and body
    method = request.method
    query_string = request.url.query

    # Build target URL
    if target_path and not target_path.startswith("/"):
        target_path = "/" + target_path
    target_url = f"{target_base}{target_path}"
    if query_string:
        target_url = f"{target_url}?{query_string}"

    # Headers: forward except host; ensure X-Request-ID
    headers = dict(request.headers)
    headers.pop("host", None)
    request_id = headers.get("x-request-id") or str(uuid.uuid4())
    headers["x-request-id"] = request_id

    # Body
    body = await request.body()

    timeout = httpx.Timeout(
        connect=settings.PROXY_CONNECT_TIMEOUT,
        read=settings.PROXY_READ_TIMEOUT,
        write=settings.PROXY_WRITE_TIMEOUT,
        pool=None,
    )

    try:
        async with httpx.AsyncClient(timeout=timeout, verify=True) as client:
            resp = await client.request(method, target_url, content=body, headers=headers)
    except httpx.TimeoutException:
        logger.warning(f"Gateway timeout: {method} {target_url}")
        return JSONResponse(
            status_code=504,
            content={
                "success": False,
                "data": None,
                "error": {"code": "GATEWAY_TIMEOUT", "message": "Upstream timeout", "details": None},
            },
        )
    except httpx.RequestError as e:
        logger.error(f"Upstream request error: {method} {target_url} - {e}")
        return JSONResponse(
            status_code=503,
            content={
                "success": False,
                "data": None,
                "error": {"code": "UPSTREAM_UNAVAILABLE", "message": "Upstream service unavailable", "details": None},
            },
        )

    filtered_headers = _filter_response_headers(resp.headers.items())
    return Response(content=resp.content, status_code=resp.status_code, headers=filtered_headers)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting api-gateway")
    yield
    logger.info("Shutting down api-gateway")


app = FastAPI(
    title="Encypher API Gateway",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Metrics
Instrumentator().instrument(app).expose(app)


# Correlation ID and security headers
@app.middleware("http")
async def add_correlation_and_security_headers(request: Request, call_next):
    request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
    response = await call_next(request)
    # Correlation
    response.headers["X-Request-ID"] = request_id
    # Security headers
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "no-referrer")
    # Minimal CSP - refine per requirements
    response.headers.setdefault("Content-Security-Policy", "default-src 'none'")
    return response


# Health
@app.get("/health")
async def health():
    return {"status": "healthy", "service": settings.SERVICE_NAME, "version": "0.1.0"}


# ---- Proxy Routes ----
# Auth
@app.api_route("/api/v1/auth/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
async def proxy_auth(path: str, request: Request):
    return await _forward(request, settings.AUTH_SERVICE_URL, f"/api/v1/auth/{path}")

@app.api_route("/api/v1/auth", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
async def proxy_auth_root(request: Request):
    return await _forward(request, settings.AUTH_SERVICE_URL, "/api/v1/auth")

# Analytics
@app.api_route("/api/v1/analytics/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
async def proxy_analytics(path: str, request: Request):
    return await _forward(request, settings.ANALYTICS_SERVICE_URL, f"/api/v1/analytics/{path}")

@app.api_route("/api/v1/analytics", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
async def proxy_analytics_root(request: Request):
    return await _forward(request, settings.ANALYTICS_SERVICE_URL, "/api/v1/analytics")

# Verification (public)
@app.api_route("/api/v1/verify/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
async def proxy_verify(path: str, request: Request):
    return await _forward(request, settings.ENTERPRISE_API_URL, f"/api/v1/verify/{path}")

@app.api_route("/api/v1/verify", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
async def proxy_verify_root(request: Request):
    return await _forward(request, settings.ENTERPRISE_API_URL, "/api/v1/verify")

# Also support public/verify path if FE uses it
@app.api_route("/api/v1/public/verify/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
async def proxy_public_verify(path: str, request: Request):
    return await _forward(request, settings.ENTERPRISE_API_URL, f"/api/v1/public/verify/{path}")

@app.api_route("/api/v1/public/verify", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
async def proxy_public_verify_root(request: Request):
    return await _forward(request, settings.ENTERPRISE_API_URL, "/api/v1/public/verify")
