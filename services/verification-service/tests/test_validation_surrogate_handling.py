"""Test that the validation exception handler survives surrogate characters.

Regression test for the UnicodeEncodeError crash when clients submit text
containing unpaired surrogates (e.g. truncated variation selectors).
The crash occurred in JSONResponse.render() when Pydantic validation errors
echoed back raw input containing surrogates like U+DB40.
"""

import pytest
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from pydantic import BaseModel


# -- Pure function under test (defined in app/main.py) -----------------------
# Duplicated here to avoid importing app.main, which pulls in structlog,
# encypher_commercial_shared, and other heavy deps not available in the
# lightweight test environment.


def _sanitize_for_json(obj):
    if isinstance(obj, str):
        return obj.encode("utf-8", errors="replace").decode("utf-8")
    if isinstance(obj, dict):
        return {k: _sanitize_for_json(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_sanitize_for_json(item) for item in obj]
    if isinstance(obj, tuple):
        return tuple(_sanitize_for_json(item) for item in obj)
    return obj


# -- Unit tests for _sanitize_for_json --------------------------------------


class TestSanitizeForJson:
    def test_clean_string_unchanged(self):
        assert _sanitize_for_json("hello world") == "hello world"

    def test_surrogate_replaced(self):
        dirty = "prefix\udb40suffix"
        result = _sanitize_for_json(dirty)
        assert "\udb40" not in result
        assert "prefix" in result
        assert "suffix" in result

    def test_nested_dict(self):
        obj = {"input": "text\udb40here", "nested": {"val": "ok\udc00end"}}
        result = _sanitize_for_json(obj)
        assert "\udb40" not in result["input"]
        assert "\udc00" not in result["nested"]["val"]

    def test_list_of_errors(self):
        errors = [
            {"loc": ("body", "text"), "msg": "bad", "input": "data\udb40\udb41"},
            {"loc": ("body", "other"), "msg": "ok", "input": "clean"},
        ]
        result = _sanitize_for_json(errors)
        assert len(result) == 2
        assert "\udb40" not in str(result[0])
        assert result[1]["input"] == "clean"

    def test_non_string_passthrough(self):
        assert _sanitize_for_json(42) == 42
        assert _sanitize_for_json(None) is None
        assert _sanitize_for_json(True) is True

    def test_tuple_preserved_as_tuple(self):
        result = _sanitize_for_json(("body", "text\udb40"))
        assert isinstance(result, tuple)
        assert "\udb40" not in result[1]

    def test_empty_containers(self):
        assert _sanitize_for_json([]) == []
        assert _sanitize_for_json({}) == {}
        assert _sanitize_for_json("") == ""


# -- Integration test: handler returns 422, not 500 -------------------------


class TextBody(BaseModel):
    text: str


@pytest.fixture
def surrogate_app():
    """Minimal app with the sanitizing validation handler."""
    app = FastAPI()

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={
                "error": "VALIDATION_ERROR",
                "detail": _sanitize_for_json(exc.errors()),
            },
        )

    @app.post("/verify")
    async def verify(body: TextBody):
        return {"ok": True}

    return app


class TestValidationHandlerSurrogates:
    def test_invalid_utf8_body_returns_4xx_not_500(self, surrogate_app):
        """Send raw bytes that are not valid UTF-8. Starlette rejects at 400
        before Pydantic even sees it, but the response must not be 500."""
        client = TestClient(surrogate_app, raise_server_exceptions=False)
        resp = client.post(
            "/verify",
            content=b'{"text": "hello\xef\xbf world"}',
            headers={"Content-Type": "application/json"},
        )
        assert 400 <= resp.status_code < 500

    def test_json_response_survives_surrogate_in_error_detail(self):
        """Directly verify JSONResponse.render() doesn't crash after sanitization.

        This is the exact failure mode: exc.errors() contains a surrogate,
        and JSONResponse tries to .encode('utf-8') the rendered JSON.
        Without sanitization, this raises UnicodeEncodeError.
        """
        # Simulate what exc.errors() returns when input has surrogates
        error_detail = [
            {
                "type": "string_unicode",
                "loc": ("body", "text"),
                "msg": "Input should be a valid string",
                "input": "hello\udb40world",  # lone surrogate
            }
        ]

        # Without sanitization this would crash:
        # json.dumps(error_detail).encode("utf-8") -> UnicodeEncodeError
        sanitized = _sanitize_for_json(error_detail)

        # Verify JSONResponse can render it without crashing
        resp = JSONResponse(
            status_code=422,
            content={"error": "VALIDATION_ERROR", "detail": sanitized},
        )
        assert resp.status_code == 422
        assert b"VALIDATION_ERROR" in resp.body

    def test_valid_input_unaffected(self, surrogate_app):
        client = TestClient(surrogate_app)
        resp = client.post(
            "/verify",
            json={"text": "clean text"},
        )
        assert resp.status_code == 200
