import os
import sys
from pathlib import Path

import pytest
from httpx import ASGITransport

from encypher_enterprise import AsyncEncypherClient
from encypher_enterprise.exceptions import AuthenticationError

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///placeholder-tests.sqlite")
os.environ.setdefault("KEY_ENCRYPTION_KEY", "0" * 64)
os.environ.setdefault("ENCRYPTION_NONCE", "0" * 24)
os.environ.setdefault("SSL_COM_API_KEY", "test-key")

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "enterprise_api"))

from app.main import app  # type: ignore  # noqa: E402
from app.database import get_db  # type: ignore  # noqa: E402


@pytest.fixture(autouse=True)
def override_db_dependency():
    class _FakeResult:
        def fetchone(self):
            return None

    class _FakeSession:
        async def execute(self, *args, **kwargs):
            return _FakeResult()

    async def _override():
        yield _FakeSession()

    app.dependency_overrides[get_db] = _override
    yield
    app.dependency_overrides.pop(get_db, None)


@pytest.mark.asyncio
async def test_sign_requires_authentication():
    transport = ASGITransport(app=app)
    client = AsyncEncypherClient(
        api_key="invalid",
        base_url="http://test",
        transport=transport,
    )

    with pytest.raises(AuthenticationError):
        await client.sign("Enterprise API integration smoke test")

    await client.close()


@pytest.mark.asyncio
async def test_verify_public_endpoint():
    transport = ASGITransport(app=app)
    client = AsyncEncypherClient(
        api_key="unused",
        base_url="http://test",
        transport=transport,
    )

    response = await client.verify("Unsigned content for integration test")
    await client.close()

    assert response.success is True
    assert response.is_valid is False
