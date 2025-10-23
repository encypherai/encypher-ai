"""
Integration tests for signing workflow.
"""
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import get_db


@pytest.fixture(autouse=True)
def override_db_dependency():
    class _FakeResult:
        def fetchone(self):
            return None

    class _FakeSession:
        async def execute(self, *args, **kwargs):
            return _FakeResult()

    async def _override_get_db():
        yield _FakeSession()

    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.pop(get_db, None)


@pytest.mark.asyncio
async def test_health_check():
    """Test health check endpoint."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_root_endpoint():
    """Test root endpoint."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Encypher Enterprise API"


@pytest.mark.asyncio
async def test_sign_without_auth():
    """Test signing endpoint without authentication."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/sign",
            json={
                "text": "Test content.",
                "document_title": "Test Document"
            }
        )
        # Should return 403 (no credentials) or 401 (invalid credentials)
        assert response.status_code in [401, 403]


@pytest.mark.asyncio
async def test_verify_endpoint():
    """Test verification endpoint (public, no auth required)."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/verify",
            json={
                "text": "Some text without a manifest"
            }
        )
        # Should return 200 even for invalid content
        assert response.status_code == 200
        data = response.json()
        assert "is_valid" in data
        assert data["is_valid"] is False  # No manifest, so invalid


@pytest.mark.asyncio
async def test_lookup_endpoint():
    """Test lookup endpoint (public, no auth required)."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/lookup",
            json={
                "sentence_text": "This sentence doesn't exist."
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["found"] is False


# TODO: Add integration tests with actual database and API key
# These would require:
# 1. Test database setup
# 2. Test organization with API key
# 3. Test keypair generation
# 4. Full signing -> verification -> lookup flow
