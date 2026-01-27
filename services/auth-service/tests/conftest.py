"""
Pytest configuration for auth-service tests
"""

import os
import sys
import types
from dataclasses import dataclass
from pathlib import Path

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key")

# Add the auth-service root to the path so we can import app modules
auth_service_root = Path(__file__).parent.parent
sys.path.insert(0, str(auth_service_root))

shared_libs_root = auth_service_root / "shared_libs" / "src"
sys.path.insert(0, str(shared_libs_root))

shared_module = types.ModuleType("encypher_commercial_shared")
shared_email_module = types.ModuleType("encypher_commercial_shared.email")


@dataclass
class _EmailConfig:
    smtp_host: str = ""
    smtp_port: int = 0
    smtp_user: str = ""
    smtp_pass: str = ""
    smtp_tls: bool = True
    email_from: str = ""
    email_from_name: str = ""
    frontend_url: str = ""
    dashboard_url: str = ""
    support_email: str = ""


def _build_invitation_email(*_args, **_kwargs):
    return "Subject", "<p>HTML</p>", "Plain"


def _generate_token(*_args, **_kwargs):
    return "token"


def _send_email_stub(*_args, **_kwargs):
    return True


def _render_template_stub(*_args, **_kwargs):
    return "<p>HTML</p>"


shared_email_module.EmailConfig = _EmailConfig
shared_email_module.render_template = _render_template_stub
shared_email_module.generate_token = _generate_token
shared_email_module.send_verification_email = _send_email_stub
shared_email_module.send_welcome_email = _send_email_stub
shared_email_module.send_password_reset_email = _send_email_stub
shared_email_module.send_new_signup_admin_email = _send_email_stub
shared_email_module.send_api_access_request_admin_email = _send_email_stub
shared_email_module.send_api_access_approved_email = _send_email_stub
shared_email_module.send_api_access_denied_email = _send_email_stub

sys.modules.setdefault("encypher_commercial_shared", shared_module)
sys.modules.setdefault("encypher_commercial_shared.email", shared_email_module)

encypher_module = types.ModuleType("encypher")
encypher_core_module = types.ModuleType("encypher.core")
encypher_keys_module = types.ModuleType("encypher.core.keys")
encypher_unicode_module = types.ModuleType("encypher.core.unicode_metadata")


def _stub_key_loader(*_args, **_kwargs):
    return None


encypher_keys_module.load_private_key_from_data = _stub_key_loader
encypher_keys_module.load_public_key_from_data = _stub_key_loader
encypher_unicode_module.MetadataTarget = type("MetadataTarget", (), {})
encypher_unicode_module.UnicodeMetadata = type("UnicodeMetadata", (), {})

sys.modules.setdefault("encypher", encypher_module)
sys.modules.setdefault("encypher.core", encypher_core_module)
sys.modules.setdefault("encypher.core.keys", encypher_keys_module)
sys.modules.setdefault("encypher.core.unicode_metadata", encypher_unicode_module)

jwt_module = types.ModuleType("jwt")
jwt_module.ExpiredSignatureError = type("ExpiredSignatureError", (Exception,), {})
jwt_module.InvalidTokenError = type("InvalidTokenError", (Exception,), {})
jwt_module.DecodeError = type("DecodeError", (Exception,), {})


def _jwt_encode_stub(*_args, **_kwargs):
    return "stub.jwt.token"


def _jwt_decode_stub(*_args, **_kwargs):
    return {}


jwt_module.encode = _jwt_encode_stub
jwt_module.decode = _jwt_decode_stub
sys.modules.setdefault("jwt", jwt_module)

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from sqlalchemy.orm import Session

from app.db.session import get_db


@pytest.fixture
def mock_db():
    """Create a mock database session"""
    return MagicMock(spec=Session)


@pytest.fixture
def test_app(mock_db):
    app = FastAPI()

    try:
        from app.api.v1.saml import router as saml_router

        app.include_router(saml_router, prefix="/api/v1/auth")
    except ImportError:
        pass

    try:
        from app.api.scim import router as scim_router

        app.include_router(scim_router)
    except ImportError:
        pass

    app.dependency_overrides[get_db] = lambda: mock_db
    return app


@pytest.fixture
def client(test_app):
    return TestClient(test_app)
