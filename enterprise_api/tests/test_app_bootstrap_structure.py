import json

from fastapi import FastAPI, HTTPException

from app.bootstrap.docs import build_public_openapi as bootstrap_build_public_openapi
from app.bootstrap.docs import register_docs_routes
from app.bootstrap.errors import global_exception_handler, http_exception_handler, register_exception_handlers
from app.bootstrap.lifespan import validate_startup_config as bootstrap_validate_startup_config
from app.bootstrap.middleware import EncypherTrustedHostMiddleware as BootstrapTrustedHostMiddleware
from app.bootstrap.middleware import build_cors_settings as bootstrap_build_cors_settings
from app.bootstrap.middleware import build_trusted_hosts as bootstrap_build_trusted_hosts
from app.bootstrap.middleware import register_middleware
from app.bootstrap.probes import register_probe_routes
from app.bootstrap.routers import ROUTER_SPECS, register_application_routers
from app.main import EncypherTrustedHostMiddleware, app, build_cors_settings, build_public_openapi, build_trusted_hosts, validate_startup_config


class _IncludeRouterRecorder:
    def __init__(self) -> None:
        self.calls: list[tuple[object, dict[str, object]]] = []

    def include_router(self, router, **kwargs) -> None:
        self.calls.append((router, kwargs))


def test_main_re_exports_bootstrap_helpers() -> None:
    assert build_cors_settings is bootstrap_build_cors_settings
    assert build_trusted_hosts is bootstrap_build_trusted_hosts
    assert validate_startup_config is bootstrap_validate_startup_config
    assert EncypherTrustedHostMiddleware is BootstrapTrustedHostMiddleware


def test_main_public_openapi_wrapper_delegates_to_bootstrap() -> None:
    main_payload = json.loads(build_public_openapi().body.decode("utf-8"))
    bootstrap_payload = json.loads(bootstrap_build_public_openapi(app).body.decode("utf-8"))

    assert main_payload == bootstrap_payload


def test_register_application_routers_applies_all_router_specs() -> None:
    recorder = _IncludeRouterRecorder()

    register_application_routers(recorder)

    assert len(recorder.calls) == len(ROUTER_SPECS)

    for call, spec in zip(recorder.calls, ROUTER_SPECS, strict=False):
        router, kwargs = call
        expected_router, expected_prefix, expected_tags = spec
        assert router is expected_router
        if expected_prefix is None:
            assert "prefix" not in kwargs
        else:
            assert kwargs["prefix"] == expected_prefix
        if expected_tags is None:
            assert "tags" not in kwargs
        else:
            assert kwargs["tags"] == expected_tags


def test_register_probe_and_docs_routes_expose_expected_paths() -> None:
    test_app = FastAPI()

    register_probe_routes(test_app)
    register_docs_routes(test_app, lambda: {"organization_id": "org_admin"})

    route_paths = {route.path for route in test_app.routes}

    assert {"/", "/health", "/readyz", "/metrics"}.issubset(route_paths)
    assert {
        "/docs",
        "/docs/openapi.json",
        "/docs/swagger",
        "/docs/assets/design-system.css",
        "/docs/assets/{filename:path}",
        "/internal/openapi.json",
        "/internal/docs",
    }.issubset(route_paths)


def test_register_exception_handlers_uses_bootstrap_handlers() -> None:
    test_app = FastAPI()

    register_exception_handlers(test_app)

    assert test_app.exception_handlers[Exception] is global_exception_handler
    assert test_app.exception_handlers[HTTPException] is http_exception_handler


def test_register_middleware_adds_expected_layers() -> None:
    test_app = FastAPI()

    register_middleware(test_app)

    middleware_classes = {middleware.cls.__name__ for middleware in test_app.user_middleware}

    assert "CORSMiddleware" in middleware_classes
    assert "EncypherTrustedHostMiddleware" in middleware_classes
    assert "SecurityHeadersMiddleware" in middleware_classes
    assert "MetricsMiddleware" in middleware_classes
    assert "RequestIDMiddleware" in middleware_classes
