"""
Encypher Enterprise API - Main Application

FastAPI application for C2PA-compliant content signing and verification.
"""

import logging
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import cast
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse, Response
from starlette.datastructures import Headers
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.types import ASGIApp, Receive, Scope, Send

from app.api.v1.api import api_router as api_v1_router
from app.config import settings
from app.database import engine, get_content_db, get_db
from app.observability.metrics import render_prometheus
from app.routers import (
    account,
    admin,
    audit,
    batch,
    byok,
    cdn_integrations,
    chat,
    coalition,
    documents,
    integrations,
    keys,
    licensing,
    lookup,
    notices,
    onboarding,
    organizations_proxy,
    partner,
    rights,
    rights_licensing,
    signing,
    status as status_router,
    streaming,
    team,
    tools,
    usage,
    verification,
    webhooks,
)
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.services.session_service import session_service
from app.services.metrics_service import init_metrics_service, shutdown_metrics_service, get_metrics_service
from app.utils.db_startup import ensure_database_ready
from app.utils.request_logging import should_log_request
from app.dependencies import require_super_admin_dep

from app.middleware.request_id_middleware import RequestIDFilter, RequestIDMiddleware

# Configure logging with request_id field from RequestIDMiddleware contextvars
logging.basicConfig(
    level=logging.INFO if settings.is_production else logging.DEBUG,
    format="%(asctime)s [%(request_id)s] %(name)s %(levelname)s - %(message)s",
)
logging.getLogger().addFilter(RequestIDFilter())
logger = logging.getLogger(__name__)


def validate_startup_config():
    """Validate critical configuration before app starts. Logs clear errors."""
    errors = []
    warnings = []

    # Check database URLs
    if not settings.core_database_url_resolved:
        errors.append("DATABASE_URL or CORE_DATABASE_URL is not set")

    # Check encryption keys (required for key storage)
    if not settings.key_encryption_key:
        errors.append("KEY_ENCRYPTION_KEY is not set (required for private key encryption)")
    elif len(settings.key_encryption_key) != 64:
        errors.append(f"KEY_ENCRYPTION_KEY must be 64 hex chars, got {len(settings.key_encryption_key)}")

    if not settings.encryption_nonce:
        errors.append("ENCRYPTION_NONCE is not set (required for private key encryption)")
    elif len(settings.encryption_nonce) != 24:
        errors.append(f"ENCRYPTION_NONCE must be 24 hex chars, got {len(settings.encryption_nonce)}")

    # Check CORS origins for production
    if settings.is_production and "localhost" in settings.allowed_origins:
        warnings.append("ALLOWED_ORIGINS contains localhost in production mode")

    # Log results
    if errors:
        logger.error("=" * 60)
        logger.error("STARTUP CONFIGURATION ERRORS:")
        for err in errors:
            logger.error(f"  ✗ {err}")
        logger.error("=" * 60)
        raise RuntimeError(f"Startup failed: {len(errors)} configuration error(s). Check logs above.")

    if warnings:
        logger.warning("Startup configuration warnings:")
        for warn in warnings:
            logger.warning(f"  ⚠ {warn}")

    logger.info("✓ Startup configuration validated")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler replacing deprecated on_event startup/shutdown."""
    logger.info("Encypher Enterprise API starting up...")
    logger.info(f"Environment: {settings.environment}")

    # Validate configuration before proceeding
    validate_startup_config()
    # Log database connection info (safely handle None)
    db_url = settings.core_database_url_resolved or settings.database_url or ""
    logger.info(f"Database: {db_url.split('@')[1] if '@' in db_url else 'Not configured'}")
    if settings.ssl_com_api_key:
        logger.info(f"SSL.com API: {settings.ssl_com_api_url}")
    else:
        logger.info("SSL.com API: Not configured (optional for staging)")

    # Ensure database is ready and run migrations (Alembic SSOT)
    ensure_database_ready(
        database_url=db_url,
        service_name="enterprise-api",
        run_migrations=True,
        exit_on_failure=True,
    )

    # Initialize Redis connection for session management
    try:
        await session_service.connect()
    except Exception as e:
        logger.warning(f"Failed to connect to Redis: {e}. Running without session persistence.")

    # Initialize metrics service for analytics
    try:
        await init_metrics_service()
        logger.info("Metrics service initialized")
    except Exception as e:
        logger.warning(f"Failed to initialize metrics service: {e}. Running without metrics.")

    # Load C2PA trust list for BYOK certificate validation
    try:
        from app.utils.c2pa_trust_list import (
            C2PA_TSA_TRUST_LIST_URL,
            C2PA_TRUST_LIST_URL,
            get_tsa_trust_list_metadata,
            get_trust_list_metadata,
            refresh_tsa_trust_list,
            refresh_trust_list,
            set_revocation_denylist,
            tsa_trust_list_needs_refresh,
            trust_list_needs_refresh,
        )

        trust_list_url = settings.c2pa_trust_list_url or C2PA_TRUST_LIST_URL
        tsa_trust_list_url = settings.c2pa_tsa_trust_list_url or C2PA_TSA_TRUST_LIST_URL

        set_revocation_denylist(
            serial_numbers=settings.c2pa_revoked_certificate_serials_set,
            fingerprints=settings.c2pa_revoked_certificate_fingerprints_set,
        )

        if trust_list_needs_refresh(settings.c2pa_trust_list_refresh_hours):
            count = await refresh_trust_list(
                url=trust_list_url,
                expected_sha256=settings.c2pa_trust_list_sha256,
            )
        else:
            metadata = get_trust_list_metadata()
            count = int(metadata.get("count") or 0)

        metadata = get_trust_list_metadata()
        logger.info(
            "C2PA trust list loaded: %s trust anchors (fingerprint=%s)",
            count,
            metadata.get("fingerprint"),
        )

        if tsa_trust_list_needs_refresh(settings.c2pa_tsa_trust_list_refresh_hours):
            tsa_count = await refresh_tsa_trust_list(
                url=tsa_trust_list_url,
                expected_sha256=settings.c2pa_tsa_trust_list_sha256,
            )
        else:
            tsa_metadata = get_tsa_trust_list_metadata()
            tsa_count = int(tsa_metadata.get("count") or 0)

        tsa_metadata = get_tsa_trust_list_metadata()
        logger.info(
            "C2PA TSA trust list loaded: %s trust anchors (fingerprint=%s)",
            tsa_count,
            tsa_metadata.get("fingerprint"),
        )
    except Exception as e:
        if settings.is_production:
            logger.error("Failed to load C2PA trust list: %s", e)
            raise
        logger.warning(f"Failed to load C2PA trust list: {e}. BYOK certificate validation may not work.")

    try:
        yield
    finally:
        logger.info("Encypher Enterprise API shutting down...")
        # Cleanup metrics service
        try:
            await shutdown_metrics_service()
        except Exception as e:
            logger.error(f"Error shutting down metrics service: {e}")
        # Cleanup Redis connection
        try:
            await session_service.disconnect()
        except Exception as e:
            logger.error(f"Error disconnecting from Redis: {e}")


# Create FastAPI app
app = FastAPI(
    title="Encypher Enterprise API",
    description="C2PA-compliant content signing and verification infrastructure for publishers, legal/finance firms, AI labs, and enterprises",
    version="1.0.2",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
    lifespan=lifespan,
)


def build_cors_settings() -> dict[str, object]:
    """Return CORS settings derived from configuration."""
    origins = [origin.strip() for origin in settings.allowed_origins.split(",") if origin.strip()]
    allow_credentials = True

    if not settings.is_production:
        localhost_origins = [
            "http://localhost:3000",
            "http://localhost:3001",
            "http://localhost:3050",
            "http://localhost:3051",
        ]
        for origin in localhost_origins:
            if origin not in origins:
                origins.append(origin)

    if "*" in origins:
        origins = ["*"]
        allow_credentials = False

    logger.info(f"CORS allowed origins: {origins}")
    return {
        "allow_origins": origins,
        "allow_credentials": allow_credentials,
        "allow_methods": ["*"],
        "allow_headers": ["*"],
    }


def build_trusted_hosts() -> list[str]:
    """Return trusted host list for TrustedHostMiddleware."""
    host_values = [host.strip() for host in settings.allowed_hosts.split(",") if host.strip()]
    extra_hosts = [settings.marketing_domain, settings.infrastructure_domain]
    for host in extra_hosts:
        if host and host not in host_values:
            host_values.append(host)
        if host and not host.startswith("www."):
            www_host = f"www.{host}"
            if www_host not in host_values:
                host_values.append(www_host)
        if host == settings.infrastructure_domain:
            for subdomain in ("api", "verify"):
                subdomain_host = f"{subdomain}.{host}"
                if subdomain_host not in host_values:
                    host_values.append(subdomain_host)

    if not settings.is_production:
        # TEAM_156: Include Docker service name for inter-container calls
        # TEAM_159: Add "traefik" — marketing-site container calls http://traefik:8000
        for host in (
            "localhost",
            "127.0.0.1",
            "host.docker.internal",
            "test",
            "testserver",
            "enterprise-api",
            "encypher-enterprise-api",
            "traefik",
        ):
            if host not in host_values:
                host_values.append(host)

    return host_values


class EncypherTrustedHostMiddleware:
    def __init__(
        self,
        app: ASGIApp,
        allowed_hosts: list[str],
        exempt_paths: set[str] | None = None,
    ) -> None:
        self.app = app
        self.allowed_hosts = allowed_hosts
        self.exempt_paths = exempt_paths or {"/health", "/readyz"}
        self._has_wildcard = "*" in allowed_hosts

    def _is_allowed(self, host: str) -> bool:
        if self._has_wildcard:
            return True
        for pattern in self.allowed_hosts:
            if pattern.startswith("*."):
                suffix = pattern[2:]
                if host == suffix or host.endswith(f".{suffix}"):
                    return True
                continue
            if host == pattern:
                return True
        return False

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = scope.get("path") or ""
        if path in self.exempt_paths:
            await self.app(scope, receive, send)
            return

        headers = Headers(scope=scope)
        raw_host = headers.get("host")
        if raw_host is None:
            await self.app(scope, receive, send)
            return

        host = raw_host.split(":", 1)[0]
        if self._is_allowed(host):
            await self.app(scope, receive, send)
            return

        logger.warning(
            "Rejected host header: host=%s raw_host=%s x_forwarded_host=%s allowed_hosts=%s path=%s",
            host,
            raw_host,
            headers.get("x-forwarded-host"),
            self.allowed_hosts,
            path,
        )
        response = PlainTextResponse("Invalid host header", status_code=400)
        await response(scope, receive, send)


cors_settings = build_cors_settings()
allow_origins = cast(list[str], cors_settings["allow_origins"])
allow_credentials = cast(bool, cors_settings["allow_credentials"])
allow_methods = cast(list[str], cors_settings["allow_methods"])
allow_headers = cast(list[str], cors_settings["allow_headers"])
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=allow_credentials,
    allow_methods=allow_methods,
    allow_headers=allow_headers,
)
app.add_middleware(EncypherTrustedHostMiddleware, allowed_hosts=build_trusted_hosts())
app.add_middleware(SecurityHeadersMiddleware)

# Add metrics middleware for analytics
from app.middleware.metrics_middleware import MetricsMiddleware

app.add_middleware(MetricsMiddleware)
# RequestIDMiddleware must be added AFTER MetricsMiddleware so it wraps outermost (runs first)
app.add_middleware(RequestIDMiddleware)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log request summaries with production-safe suppression defaults."""
    start_time = time.time()

    # Process request
    try:
        response = await call_next(request)
    except Exception:
        process_time_ms = int((time.time() - start_time) * 1000)
        if should_log_request(
            path=request.url.path,
            status_code=500,
            process_time_ms=process_time_ms,
            request_logging_enabled=settings.request_logging_enabled_effective,
            log_health_checks=settings.log_health_checks,
            slow_request_threshold_ms=settings.slow_request_threshold_ms,
        ):
            client_host = request.client.host if request.client else "unknown"
            logger.error(
                "%s %s - Status: 500 - Time: %.4fs - Client: %s",
                request.method,
                request.url.path,
                process_time_ms / 1000,
                client_host,
            )
        raise

    # Calculate processing time
    process_time = time.time() - start_time
    process_time_ms = int(process_time * 1000)
    response.headers["X-Process-Time"] = str(process_time)

    if should_log_request(
        path=request.url.path,
        status_code=response.status_code,
        process_time_ms=process_time_ms,
        request_logging_enabled=settings.request_logging_enabled_effective,
        log_health_checks=settings.log_health_checks,
        slow_request_threshold_ms=settings.slow_request_threshold_ms,
    ):
        client_host = request.client.host if request.client else "unknown"
        log_method = logger.warning if response.status_code >= 500 else logger.info
        log_method(
            "%s %s - Status: %s - Time: %.4fs - Client: %s",
            request.method,
            request.url.path,
            response.status_code,
            process_time,
            client_host,
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
    return {"status": "healthy", "environment": settings.environment, "version": "1.0.0-preview"}


@app.get("/readyz", tags=["Health"])
async def readiness_check():
    """Lightweight readiness probe."""

    db_status = "ok"
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception as exc:  # pragma: no cover
        logger.warning("Readiness DB probe failed: %s", exc)
        db_status = "error"
    redis_status = "ok" if session_service.redis_client else "degraded"
    status_text = "ready" if db_status == "ok" else "degraded"
    return {
        "status": status_text,
        "database": db_status,
        "redis": redis_status,
        "version": "1.0.0-preview",
    }


@app.get("/metrics", include_in_schema=False)
async def metrics():
    """Prometheus-compatible metrics endpoint."""

    return PlainTextResponse(render_prometheus(), media_type="text/plain; version=0.0.4")


_INTERNAL_DOC_TAGS = {
    "Admin",
    "Licensing",
    "Kafka",
    "Provisioning",
    "Audit",
    "Team Management",
}


def _collect_schema_refs(obj: object, out: set[str]) -> None:
    if isinstance(obj, dict):
        ref = obj.get("$ref")
        if isinstance(ref, str) and ref.startswith("#/components/schemas/"):
            out.add(ref.removeprefix("#/components/schemas/"))
        for value in obj.values():
            _collect_schema_refs(value, out)
    elif isinstance(obj, list):
        for item in obj:
            _collect_schema_refs(item, out)


def _prune_schemas(openapi: dict) -> dict:
    components = openapi.get("components")
    if not isinstance(components, dict):
        return openapi
    schemas = components.get("schemas")
    if not isinstance(schemas, dict):
        return openapi

    referenced: set[str] = set()
    _collect_schema_refs(openapi.get("paths", {}), referenced)

    kept: dict[str, object] = {}
    stack = list(referenced)
    while stack:
        name = stack.pop()
        if name in kept:
            continue
        schema = schemas.get(name)
        if schema is None:
            continue
        kept[name] = schema
        before = len(referenced)
        _collect_schema_refs(schema, referenced)
        if len(referenced) > before:
            for new_name in referenced:
                if new_name not in kept:
                    stack.append(new_name)

    components["schemas"] = kept
    return openapi


def _filter_openapi_for_public(openapi: dict) -> dict:
    paths = openapi.get("paths")
    if not isinstance(paths, dict):
        return openapi

    filtered_paths: dict[str, object] = {}
    for path, ops in paths.items():
        if not isinstance(ops, dict):
            continue
        kept_ops: dict[str, object] = {}
        for method, op in ops.items():
            if not isinstance(op, dict):
                continue
            tags = op.get("tags", [])
            if any(tag in _INTERNAL_DOC_TAGS for tag in (tags or [])):
                continue
            kept_ops[method] = op
        if kept_ops:
            filtered_paths[path] = kept_ops

    openapi["paths"] = filtered_paths

    tags = openapi.get("tags")
    if isinstance(tags, list):
        openapi["tags"] = [t for t in tags if isinstance(t, dict) and t.get("name") not in _INTERNAL_DOC_TAGS]

    return _prune_schemas(openapi)


@app.get("/docs/assets/design-system.css", include_in_schema=False)
async def docs_design_system_css() -> Response:
    repo_root = Path(__file__).resolve().parents[2]
    theme_path = repo_root / "packages" / "design-system" / "src" / "styles" / "theme.css"
    globals_path = repo_root / "packages" / "design-system" / "src" / "styles" / "globals.css"

    theme_css = theme_path.read_text(encoding="utf-8")
    globals_css = globals_path.read_text(encoding="utf-8")

    # globals.css imports theme.css; since we inline theme.css first, strip that import.
    globals_css = "\n".join(line for line in globals_css.splitlines() if "@import './theme.css'" not in line and '@import "./theme.css"' not in line)

    bundled = f"{theme_css}\n\n{globals_css}\n"
    return Response(content=bundled, media_type="text/css")


@app.get("/docs/assets/{filename:path}", include_in_schema=False)
async def docs_static_asset(filename: str) -> Response:
    """Serve static assets (logos, images) from marketing-site/public."""
    repo_root = Path(__file__).resolve().parents[2]
    asset_path = repo_root / "apps" / "marketing-site" / "public" / filename

    if not asset_path.exists() or not asset_path.is_file():
        raise HTTPException(status_code=404, detail="Asset not found")

    # Determine content type
    suffix = asset_path.suffix.lower()
    content_types = {
        ".svg": "image/svg+xml",
        ".png": "image/png",
        ".ico": "image/x-icon",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
    }
    content_type = content_types.get(suffix, "application/octet-stream")

    content = asset_path.read_bytes()
    return Response(content=content, media_type=content_type)


_DOCS_PAGE_HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Encypher Enterprise API</title>
  <link rel="icon" href="https://encypherai.com/favicon.ico" />
  <link rel="stylesheet" href="/docs/assets/design-system.css" />
  <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css" />
  <style>
    :root {
      --header-bg: #1b2f50;
      --accent: #2a87c4;
    }
    * { box-sizing: border-box; }
    body { margin: 0; font-family: var(--font-sans, "Roboto", system-ui, sans-serif); background: hsl(var(--background, 0 0% 100%)); color: hsl(var(--foreground, 222 47% 20%)); }
    .header { background: var(--header-bg); color: #fff; padding: 24px 32px; }
    .header-inner { max-width: 1400px; margin: 0 auto; display: flex; align-items: center; gap: 24px; flex-wrap: wrap; }
    .logo { height: 40px; width: auto; }
    .header h1 { margin: 0; font-size: 1.5rem; font-weight: 600; }
    .header-desc { margin: 0; opacity: 0.85; font-size: 0.95rem; flex-basis: 100%; }
    .intro { max-width: 1400px; margin: 0 auto; padding: 24px 32px; display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; }
    .intro-card { background: hsl(var(--card, 0 0% 100%)); border: 1px solid hsl(var(--border, 214 32% 91%)); border-radius: 12px; padding: 20px; }
    .intro-card h3 { margin: 0 0 8px; font-size: 1rem; color: var(--accent); }
    .intro-card p { margin: 0; font-size: 0.9rem; line-height: 1.5; color: hsl(var(--muted-foreground, 215 16% 47%)); }
    .swagger-container { max-width: 1400px; margin: 0 auto; padding: 0 32px 48px; }
    .swagger-ui .topbar { display: none; }
    .swagger-ui .info { margin: 20px 0 0; }
    .swagger-ui .info hgroup.main { margin: 0; }
    .swagger-ui .info .title { font-size: 1.25rem; }
  </style>
</head>
<body>
  <header class="header">
    <div class="header-inner">
      <img src="https://encypherai.com/encypher_full_logo_white.svg" alt="Encypher" class="logo" />
      <h1>Enterprise API</h1>
      <p class="header-desc">C2PA-compliant content signing and verification infrastructure for publishers, legal/finance firms, AI labs, and enterprises.</p>
    </div>
  </header>

  <section class="intro">
    <div class="intro-card">
      <h3>Public Endpoints</h3>
      <p>Verify signed content, validate manifests, and perform public C2PA verification workflows. No authentication required.</p>
    </div>
    <div class="intro-card">
      <h3>Publisher Endpoints</h3>
      <p>Sign content with C2PA manifests, batch processing, streaming signatures, and other authenticated operations.</p>
    </div>
    <div class="intro-card">
      <h3>Getting Started</h3>
      <p>Obtain an API key from <a href="https://dashboard.encypherai.com" style="color:var(--accent);">dashboard.encypherai.com</a>, then use the endpoints below.</p>
    </div>
    <div class="intro-card">
      <h3>Client SDKs</h3>
      <p>Auto-generated from this API spec: <a href="https://github.com/encypherai/sdk-python" style="color:var(--accent);">Python</a>, <a href="https://github.com/encypherai/sdk-typescript" style="color:var(--accent);">TypeScript</a>, <a href="https://github.com/encypherai/sdk-go" style="color:var(--accent);">Go</a>, <a href="https://github.com/encypherai/sdk-rust" style="color:var(--accent);">Rust</a>. Always in sync with the API.</p>
    </div>
    <div class="intro-card">
      <h3>Open-Source Package</h3>
      <p>Looking for the AGPL-licensed <code>encypher-ai</code> Python package? See <a href="https://docs.encypherai.com" style="color:var(--accent);">docs.encypherai.com</a>.</p>
    </div>
  </section>

  <div class="swagger-container">
    <div id="swagger-ui"></div>
  </div>

  <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
  <script>
    window.onload = () => {
      SwaggerUIBundle({
        url: "/docs/openapi.json",
        dom_id: "#swagger-ui",
        presets: [SwaggerUIBundle.presets.apis, SwaggerUIBundle.SwaggerUIStandalonePreset],
        layout: "BaseLayout",
        deepLinking: true,
        defaultModelsExpandDepth: 0,
      });
    };
  </script>
</body>
</html>
"""


def build_public_openapi() -> JSONResponse:
    """Build filtered OpenAPI response for public docs."""
    base = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    return JSONResponse(_filter_openapi_for_public(base))


def build_public_docs_html() -> HTMLResponse:
    """Build HTML for public docs landing page."""
    return HTMLResponse(_DOCS_PAGE_HTML, media_type="text/html")


@app.get("/docs", include_in_schema=False)
async def docs_landing(request: Request) -> HTMLResponse:
    if not settings.enable_public_api_docs:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return build_public_docs_html()


@app.get("/docs/openapi.json", include_in_schema=False)
async def public_openapi(request: Request) -> JSONResponse:
    if not settings.enable_public_api_docs:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return build_public_openapi()


@app.get("/docs/swagger", include_in_schema=False)
async def public_swagger_ui(request: Request) -> HTMLResponse:
    if not settings.enable_public_api_docs:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return get_swagger_ui_html(
        openapi_url="/docs/openapi.json",
        title="Encypher Enterprise API - Docs",
    )


@app.get("/internal/openapi.json", include_in_schema=False, dependencies=[Depends(require_super_admin_dep)])
async def internal_openapi() -> JSONResponse:
    base = get_openapi(
        title=f"{app.title} (Internal)",
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    return JSONResponse(base)


@app.get("/internal/docs", include_in_schema=False, dependencies=[Depends(require_super_admin_dep)])
async def internal_swagger_ui() -> HTMLResponse:
    return get_swagger_ui_html(
        openapi_url="/internal/openapi.json",
        title="Encypher Enterprise API - Internal Docs",
    )


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
        "docs": f"{settings.api_base_url}/docs" if settings.enable_public_api_docs else None,
        "status": "preview",  # Will change to "production" after C2PA spec publication
    }


# Include routers
app.include_router(account.router, prefix="/api/v1", tags=["Account"])
app.include_router(admin.router, prefix="/api/v1", tags=["Admin"])
app.include_router(byok.router, prefix="/api/v1", tags=["BYOK"])
app.include_router(documents.router, prefix="/api/v1", tags=["Documents"])
app.include_router(keys.router, prefix="/api/v1", tags=["API Keys"])
app.include_router(webhooks.router, prefix="/api/v1", tags=["Webhooks"])
app.include_router(signing.router, prefix="/api/v1", tags=["Signing"])
app.include_router(verification.router, prefix="/api/v1", tags=["Verification"])
app.include_router(lookup.router, prefix="/api/v1", tags=["Lookup"])
app.include_router(onboarding.router, prefix="/api/v1/onboarding", tags=["Onboarding"])
app.include_router(streaming.router, prefix="/api/v1", tags=["Streaming"])
app.include_router(chat.router, prefix="/api/v1", tags=["Chat"])
app.include_router(licensing.router, prefix="/api/v1", tags=["Licensing"])
app.include_router(usage.router, prefix="/api/v1", tags=["Usage"])
app.include_router(audit.router, prefix="/api/v1", tags=["Audit"])
app.include_router(team.router, prefix="/api/v1", tags=["Team Management"])
app.include_router(team.invite_router, prefix="/api/v1", tags=["Team Invites"])
app.include_router(coalition.router, prefix="/api/v1", tags=["Coalition"])
app.include_router(status_router.router, prefix="/api/v1", tags=["Status & Revocation"])
app.include_router(batch.router)
app.include_router(tools.router, prefix="/api/v1", tags=["Public Tools"])
app.include_router(organizations_proxy.router, prefix="/api/v1", tags=["Organizations Proxy"])
app.include_router(integrations.router, prefix="/api/v1", tags=["Integrations"])
app.include_router(cdn_integrations.router, prefix="/api/v1", tags=["CDN Integrations"])
app.include_router(rights.router, prefix="/api/v1", tags=["Rights Management"])
app.include_router(notices.router, prefix="/api/v1", tags=["Formal Notices"])
app.include_router(rights_licensing.router, prefix="/api/v1", tags=["Rights Licensing Transactions"])
app.include_router(partner.router, prefix="/api/v1", tags=["Partner"])

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
    correlation_id = getattr(request.state, "request_id", None) or request.headers.get("x-request-id") or f"req-{uuid4().hex}"
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {"code": "E_INTERNAL", "message": "An unexpected error occurred", "details": str(exc) if settings.is_development else None},
            "correlation_id": correlation_id,
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Return standardized error payloads for HTTP exceptions."""

    correlation_id = getattr(request.state, "request_id", None) or request.headers.get("x-request-id") or f"req-{uuid4().hex}"
    detail = exc.detail
    if isinstance(detail, dict):
        # Preserve full detail dictionary
        error_payload = detail
        if "code" not in error_payload:
            error_payload["code"] = "E_HTTP"
        if "message" not in error_payload:
            error_payload["message"] = "Request failed"
    else:
        error_payload = {"code": "E_HTTP", "message": str(detail)}

    payload = {
        "success": False,
        "error": error_payload,
        "correlation_id": correlation_id,
    }
    return JSONResponse(
        status_code=exc.status_code,
        content=payload,
        headers=exc.headers,
    )
