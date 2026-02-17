from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

from app.middleware.metrics_middleware import MetricsMiddleware


class _CapturingMetricsService:
    def __init__(self) -> None:
        self.events: list[dict[str, Any]] = []

    async def emit(self, **kwargs: Any) -> bool:
        self.events.append(kwargs)
        return True


def test_metrics_middleware_emits_request_and_error_metadata(monkeypatch) -> None:
    metrics_service = _CapturingMetricsService()

    monkeypatch.setattr(
        "app.middleware.metrics_middleware.get_metrics_service",
        lambda: metrics_service,
    )

    app = FastAPI()
    app.add_middleware(MetricsMiddleware)

    @app.get("/api/v1/verify")
    async def verify_route(request: Request) -> JSONResponse:
        request.state.organization_id = "org_demo"
        request.state.user_id = "user_demo"
        request.state.api_key_id = "key_123"
        request.state.api_key_prefix = "ency_abc123"
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": {
                    "code": "E_VERIFY",
                    "message": "Verification failed",
                    "details": "Manifest parsing error",
                },
            },
        )

    client = TestClient(app)
    response = client.get("/api/v1/verify", headers={"x-request-id": "req_123"})

    assert response.status_code == 500
    assert len(metrics_service.events) == 1

    event = metrics_service.events[0]
    assert event["organization_id"] == "org_demo"
    assert event["status_code"] == 500
    assert event["metadata"]["request_id"] == "req_123"
    assert event["metadata"]["api_key_prefix"] == "ency_abc123"
    assert event["metadata"]["method"] == "GET"
    assert event["metadata"]["error_code"] == "E_VERIFY"
    assert event["metadata"]["error_message"] == "Verification failed"
    assert event["metadata"]["error_details"] == "Manifest parsing error"


def test_metrics_middleware_emits_traceback_for_unhandled_exception(monkeypatch) -> None:
    metrics_service = _CapturingMetricsService()

    monkeypatch.setattr(
        "app.middleware.metrics_middleware.get_metrics_service",
        lambda: metrics_service,
    )

    app = FastAPI()
    app.add_middleware(MetricsMiddleware)

    @app.get("/api/v1/sign")
    async def sign_route(request: Request) -> JSONResponse:
        request.state.organization_id = "org_demo"
        request.state.user_id = "user_demo"
        request.state.api_key_id = "key_123"
        request.state.api_key_prefix = "ency_abc123"
        raise RuntimeError("signing pipeline exploded")

    client = TestClient(app, raise_server_exceptions=False)
    response = client.get("/api/v1/sign", headers={"x-request-id": "req_trace_1"})

    assert response.status_code == 500
    assert len(metrics_service.events) == 1

    event = metrics_service.events[0]
    assert event["organization_id"] == "org_demo"
    assert event["status_code"] == 500
    assert event["metadata"]["request_id"] == "req_trace_1"
    assert event["metadata"]["api_key_prefix"] == "ency_abc123"
    assert event["metadata"]["error_code"] == "E_UNHANDLED"
    assert event["metadata"]["error_message"] == "signing pipeline exploded"
    assert "RuntimeError: signing pipeline exploded" in event["metadata"]["error_stack"]
