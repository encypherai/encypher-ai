"""
Integration tests for signing workflow.

Uses PostgreSQL via Docker for full compatibility.
"""
import os
import unicodedata
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Set test environment variables (PostgreSQL is configured via conftest.py)
os.environ.setdefault("KEY_ENCRYPTION_KEY", "0" * 64)
os.environ.setdefault("ENCRYPTION_NONCE", "0" * 24)
os.environ.setdefault("SSL_COM_API_KEY", "test-key")

import pytest
import pytest_asyncio
from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.x509.oid import NameOID
from encypher.interop.c2pa import text_wrapper
from encypher.streaming.handlers import StreamingHandler
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

import app.database as db_module
from app.config import settings
from app.database import get_db
from app.main import app
from app.utils.crypto_utils import encrypt_private_key, generate_ed25519_keypair
from app.utils.sentence_parser import parse_sentences


@pytest.fixture(autouse=True)
def override_db_dependency(request):
    if request.node.get_closest_marker("real_db"):
        yield
        return

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
        assert response.status_code == 410
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "ENDPOINT_DEPRECATED"


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


INIT_SQL_PATH = Path(__file__).resolve().parents[2] / "scripts" / "init_db.sql"


def _create_self_signed_certificate(private_key, public_key, common_name: str) -> str:
    now = datetime.now(timezone.utc)

    subject = issuer = x509.Name(
        [
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, common_name),
            x509.NameAttribute(NameOID.COMMON_NAME, f"{common_name}.example"),
        ]
    )

    certificate = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(public_key)
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(days=1))
        .not_valid_after(now + timedelta(days=30))
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
        .sign(private_key, algorithm=None)
    )

    return certificate.public_bytes(serialization.Encoding.PEM).decode("utf-8")


async def _truncate_all_tables(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    """Truncate test tables in PostgreSQL."""
    async with session_factory() as session:
        # Use PostgreSQL TRUNCATE with CASCADE
        truncate_sql = (
            "TRUNCATE TABLE audit_logs, sentence_records, documents, "
            "api_keys, organizations RESTART IDENTITY CASCADE"
        )
        try:
            await session.execute(text(truncate_sql))
            await session.commit()
        except Exception:
            # Tables may not exist in test environment
            await session.rollback()


async def _prepare_organization_with_api_key(
    session_factory: async_sessionmaker[AsyncSession],
    organization_name: str,
) -> dict:
    """Create a test organization with API key using unified schema."""
    private_key, public_key = generate_ed25519_keypair()
    encrypted_private_key = encrypt_private_key(private_key)
    certificate_pem = _create_self_signed_certificate(private_key, public_key, organization_name)
    organization_id = f"org_{uuid.uuid4().hex[:12]}"
    api_key = f"test_{uuid.uuid4().hex}"
    timestamp = datetime.now(timezone.utc)

    async with session_factory() as session:
        # Insert organization using unified schema
        await session.execute(
            text(
                """
                INSERT INTO organizations (
                    id,
                    name,
                    email,
                    tier,
                    private_key_encrypted,
                    certificate_pem,
                    features,
                    created_at,
                    updated_at
                )
                VALUES (
                    :id,
                    :name,
                    :email,
                    :tier,
                    :private_key_encrypted,
                    :certificate_pem,
                    :features,
                    :created_at,
                    :updated_at
                )
                ON CONFLICT (id) DO NOTHING
                """
            ),
            {
                "id": organization_id,
                "name": organization_name,
                "email": f"test-{organization_id}@example.com",
                "tier": "enterprise",
                "private_key_encrypted": encrypted_private_key,
                "certificate_pem": certificate_pem,
                "features": '{"can_sign": true, "can_verify": true, "monthly_quota": 1000000}',
                "created_at": timestamp,
                "updated_at": timestamp,
            },
        )

        # Insert API key using unified schema
        await session.execute(
            text(
                """
                INSERT INTO api_keys (
                    id,
                    key_hash,
                    key_prefix,
                    organization_id,
                    name,
                    scopes,
                    created_at,
                    is_active
                )
                VALUES (
                    :id,
                    :key_hash,
                    :key_prefix,
                    :organization_id,
                    :name,
                    :scopes,
                    :created_at,
                    TRUE
                )
                ON CONFLICT (id) DO NOTHING
                """
            ),
            {
                "id": f"key_{uuid.uuid4().hex[:12]}",
                "key_hash": api_key,  # In tests, we use the key directly as hash
                "key_prefix": api_key[:8],  # First 8 chars as prefix
                "organization_id": organization_id,
                "name": "Integration Test Key",
                "scopes": '["sign", "verify", "lookup"]',
                "created_at": timestamp,
            },
        )

        await session.commit()

    return {
        "organization_id": organization_id,
        "organization_name": organization_name,
        "api_key": api_key,
        "private_key": private_key,
        "public_key": public_key,
        "certificate_pem": certificate_pem,
    }


async def _assert_document_persistence(
    session_factory: async_sessionmaker[AsyncSession],
    organization_id: str,
    document_id: str,
    expected_sentence_count: int,
) -> None:
    async with session_factory() as session:
        document_row = await session.execute(
            text(
                """
                SELECT total_sentences
                FROM documents
                WHERE document_id = :document_id
                """
            ),
            {"document_id": document_id},
        )
        document_record = document_row.one()
        assert document_record.total_sentences == expected_sentence_count

        sentences_count = await session.execute(
            text(
                """
                SELECT COUNT(*) AS sentence_count
                FROM sentence_records
                WHERE document_id = :document_id
                """
            ),
            {"document_id": document_id},
        )
        assert sentences_count.scalar_one() == expected_sentence_count

        organization_stats = await session.execute(
            text(
                """
                SELECT documents_signed, sentences_signed, api_calls_this_month
                FROM organizations
                WHERE organization_id = :organization_id
                """
            ),
            {"organization_id": organization_id},
        )
        stats = organization_stats.one()
        assert stats.documents_signed == 1
        assert stats.sentences_signed == expected_sentence_count
        assert stats.api_calls_this_month == 1

        api_key_last_used = await session.execute(
            text(
                """
                SELECT last_used_at
                FROM api_keys
                WHERE organization_id = :organization_id
                """
            ),
            {"organization_id": organization_id},
        )
        assert api_key_last_used.scalar_one() is not None


async def _perform_sign_verify_lookup(
    session_factory: async_sessionmaker[AsyncSession],
    *,
    organization_name: str,
    document_text: str,
    document_title: str,
    document_url: str,
    document_type: str,
    lookup_sentence_index: int = 0,
) -> dict:
    await _truncate_all_tables(session_factory)
    organization = await _prepare_organization_with_api_key(session_factory, organization_name)

    sentences = parse_sentences(document_text)
    assert sentences, "Document must yield at least one sentence for lookup assertions"
    if lookup_sentence_index >= len(sentences):
        raise AssertionError("Lookup sentence index out of range for parsed sentences")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        sign_response = await client.post(
            "/api/v1/sign",
            headers={"Authorization": f"Bearer {organization['api_key']}"},
            json={
                "text": document_text,
                "document_title": document_title,
                "document_url": document_url,
                "document_type": document_type,
            },
        )
        assert sign_response.status_code == 200
        sign_data = sign_response.json()
        assert sign_data["success"] is True
        assert sign_data["total_sentences"] == len(sentences)
        signed_text = sign_data["signed_text"]
        document_id = sign_data["document_id"]

        verify_response = await client.post(
            "/api/v1/verify",
            json={"text": signed_text},
        )
        assert verify_response.status_code == 410
        verify_data = verify_response.json()
        assert verify_data["success"] is False
        assert verify_data["error"]["code"] == "ENDPOINT_DEPRECATED"

        lookup_response = await client.post(
            "/api/v1/lookup",
            json={"sentence_text": sentences[lookup_sentence_index]},
        )
        assert lookup_response.status_code == 200
        lookup_data = lookup_response.json()
        assert lookup_data["success"] is True
        assert lookup_data["found"] is True
        assert lookup_data["organization_name"] == organization_name
        assert lookup_data["document_title"] == document_title
        assert lookup_data["sentence_index"] == lookup_sentence_index
        assert lookup_data["document_url"] == document_url

    manifest_bytes, normalized_text, span = text_wrapper.find_and_decode(signed_text)
    assert manifest_bytes is not None
    assert span is not None
    assert signed_text.count("\ufeff") == 1
    assert signed_text[span[0]] == "\ufeff"
    assert span[1] == len(signed_text)
    assert normalized_text == unicodedata.normalize("NFC", document_text)

    await _assert_document_persistence(
        session_factory,
        organization_id=organization["organization_id"],
        document_id=document_id,
        expected_sentence_count=len(sentences),
    )

    return {
        **organization,
        "document_id": document_id,
        "signed_text": signed_text,
        "sentences": sentences,
        "manifest_bytes": manifest_bytes,
        "wrapper_span": span,
    }


@pytest_asyncio.fixture
async def real_db_session_factory():
    """
    Create a PostgreSQL session factory for integration tests.
    Uses the Docker PostgreSQL instance for full compatibility.
    
    Note: Uses core database for organization/key data.
    Content data (documents, sentences) goes to content database.
    """
    # Use PostgreSQL from Docker - Core database for org/key data
    db_url = os.getenv(
        "CORE_DATABASE_URL",
        "postgresql+asyncpg://encypher:encypher_dev_password@postgres-core:5432/encypher_core"
    )

    engine = create_async_engine(
        db_url,
        future=True,
        pool_pre_ping=True,
    )
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    old_engine = db_module.engine
    old_session_factory = db_module.async_session_factory
    old_db_url = getattr(settings, "database_url", None)
    old_key = getattr(settings, "key_encryption_key", None)
    old_nonce = getattr(settings, "encryption_nonce", None)

    db_module.engine = engine
    db_module.async_session_factory = session_factory
    settings.database_url = db_url
    # Always use valid hex keys for integration tests
    settings.key_encryption_key = "0" * 64
    settings.encryption_nonce = "0" * 24

    try:
        yield session_factory
    finally:
        # Don't truncate - let tests clean up after themselves or use transactions
        db_module.engine = old_engine
        db_module.async_session_factory = old_session_factory
        if old_db_url is not None:
            settings.database_url = old_db_url
        if old_key is not None:
            settings.key_encryption_key = old_key
        if old_nonce is not None:
            settings.encryption_nonce = old_nonce

        await engine.dispose()


@pytest.mark.skip(reason="Requires full microservices stack (key-service) - run with docker-compose.full-stack.yml")
@pytest.mark.real_db
@pytest.mark.asyncio
async def test_sign_verify_lookup_flow_with_real_database(real_db_session_factory):
    session_factory = real_db_session_factory

    document_text = (
        "This integration test signs content using the enterprise API. "
        "It then verifies the resulting manifest for validity. "
        "Finally, it performs a lookup on one of the sentences."
    )

    result = await _perform_sign_verify_lookup(
        session_factory,
        organization_name="Integration Test Org",
        document_text=document_text,
        document_title="Integration Test Document",
        document_url="https://example.com/integration-test",
        document_type="article",
    )

    assert result["document_id"].startswith("doc_")
    assert len(result["sentences"]) == 3
    assert result["sentences"][0].startswith("This integration test")


@pytest.mark.skip(reason="Requires full microservices stack (key-service) - run with docker-compose.full-stack.yml")
@pytest.mark.real_db
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "content_type, document_text, document_type",
    [
        (
            "plain_text",
            "Plain text example validates signing for prose content. "
            "Metadata persists across multiple sentences.",
            "article",
        ),
        (
            "xml",
            "<note><to>Integration</to><from>Tester</from>"
            "<body>XML payload metadata works. Verification succeeds.</body></note>",
            "article",
        ),
        (
            "html",
            "<html><body><p>HTML document includes metadata embedding.</p>"
            "<p>Lookup should resolve correctly.</p></body></html>",
            "article",
        ),
        (
            "json",
            '{ "title": "Integration example.", "description": "Metadata validated." }',
            "ai_output",
        ),
        (
            "tsx",
            'import React from "react";\n'
            "export const IntegrationComponent = () => (\n"
            '  <div>Metadata test for TSX content.</div>\n'
            ");",
            "ai_output",
        ),
        (
            "js",
            'export function integrationExample() {\n'
            '  console.log("Metadata embedding succeeds.");\n'
            "  return true;\n"
            "}",
            "ai_output",
        ),
    ],
)
async def test_sign_verify_lookup_flow_various_content_types(
    real_db_session_factory,
    content_type,
    document_text,
    document_type,
):
    session_factory = real_db_session_factory
    document_title = f"Integration Test {content_type.title()} Document"
    document_url = f"https://example.com/{content_type}-{uuid.uuid4().hex[:8]}"

    result = await _perform_sign_verify_lookup(
        session_factory,
        organization_name=f"{content_type.title()} Org",
        document_text=document_text,
        document_title=document_title,
        document_url=document_url,
        document_type=document_type,
    )

    assert result["organization_name"] == f"{content_type.title()} Org"
    assert result["document_id"].startswith("doc_")
    assert result["sentences"]


@pytest.mark.skip(reason="Requires full microservices stack (key-service) - run with docker-compose.full-stack.yml")
@pytest.mark.real_db
@pytest.mark.asyncio
async def test_streaming_text_verification(real_db_session_factory):
    session_factory = real_db_session_factory

    await _truncate_all_tables(session_factory)
    organization = await _prepare_organization_with_api_key(session_factory, "Streaming Test Org")

    handler = StreamingHandler(
        private_key=organization["private_key"],
        signer_id=organization["organization_id"],
        custom_metadata={"mode": "streaming-integration"},
    )
    stream_chunks = [
        "Streaming integration chunk one checks metadata. ",
        "Chunk two continues the signing process. ",
        "Final chunk closes the streaming session.",
    ]

    encoded_chunks = [handler.process_chunk(chunk) for chunk in stream_chunks]
    final_chunk = handler.finalize()
    if final_chunk:
        encoded_chunks.append(final_chunk)

    streamed_text = "".join(encoded_chunks)
    assert streamed_text

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        verify_response = await client.post("/api/v1/verify", json={"text": streamed_text})
        assert verify_response.status_code == 410
        verify_data = verify_response.json()
        assert verify_data["success"] is False
        assert verify_data["error"]["code"] == "ENDPOINT_DEPRECATED"

    return
