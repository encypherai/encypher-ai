import logging
import time
from typing import cast

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from starlette.datastructures import Headers
from starlette.types import ASGIApp, Receive, Scope, Send

from app.config import settings
from app.middleware.request_id_middleware import RequestIDMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.utils.request_logging import should_log_request

logger = logging.getLogger(__name__)


def build_cors_settings() -> dict[str, object]:
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

    logger.info("CORS allowed origins: %s", origins)
    return {
        "allow_origins": origins,
        "allow_credentials": allow_credentials,
        "allow_methods": ["*"],
        "allow_headers": ["*"],
    }


def build_trusted_hosts() -> list[str]:
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


def register_middleware(app: FastAPI) -> None:
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

    from app.middleware.metrics_middleware import MetricsMiddleware

    app.add_middleware(MetricsMiddleware)
    app.add_middleware(RequestIDMiddleware)

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start_time = time.time()

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
