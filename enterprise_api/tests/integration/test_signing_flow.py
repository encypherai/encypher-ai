"""
Integration tests for signing workflow.
"""
import os
import unicodedata
import tempfile
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///placeholder-tests.sqlite")
os.environ.setdefault("KEY_ENCRYPTION_KEY", "0" * 64)
os.environ.setdefault("ENCRYPTION_NONCE", "0" * 24)
os.environ.setdefault("SSL_COM_API_KEY", "test-key")

import pytest
import pytest_asyncio
from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.x509.oid import NameOID
from httpx import AsyncClient, ASGITransport
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

import app.database as db_module
from app.config import settings
from app.database import get_db
from app.main import app
from app.utils.crypto_utils import encrypt_private_key, generate_ed25519_keypair
from app.utils.sentence_parser import parse_sentences
from encypher.streaming.handlers import StreamingHandler
from encypher.interop.c2pa import text_wrapper


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
        # Should return 200 even for invalid content
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["error"] is None
        assert data["data"]["valid"] is False  # No manifest, so invalid
        assert data["data"]["reason_code"] in {"SIGNATURE_INVALID", "SIGNER_UNKNOWN"}
        assert isinstance(data["correlation_id"], str) and data["correlation_id"]


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
TEST_DATABASE_IS_SQLITE = False


def _load_init_statements(*, use_sqlite: bool) -> list[str]:
    statements: list[str] = []
    buffer: list[str] = []

    for raw_line in INIT_SQL_PATH.read_text().splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("--"):
            continue

        buffer.append(raw_line)
        if stripped.endswith(";"):
            statements.append("\n".join(buffer))
            buffer.clear()

    if buffer:
        statements.append("\n".join(buffer))

    if not use_sqlite:
        return statements

    sqlite_statements: list[str] = []
    uuid_default = "lower(hex(randomblob(16)))"
    for stmt in statements:
        sqlite_stmt = stmt
        sqlite_stmt = sqlite_stmt.replace("BYTEA", "BLOB")
        sqlite_stmt = sqlite_stmt.replace("UUID", "TEXT")
        sqlite_stmt = sqlite_stmt.replace("JSONB", "TEXT")
        sqlite_stmt = sqlite_stmt.replace(
            "SERIAL PRIMARY KEY", "INTEGER PRIMARY KEY AUTOINCREMENT"
        )
        sqlite_stmt = sqlite_stmt.replace(
            "DEFAULT gen_random_uuid()", f"DEFAULT {uuid_default}"
        )
        sqlite_stmt = sqlite_stmt.replace("DEFAULT lower(hex(randomblob(16)))", "")
        sqlite_stmt = sqlite_stmt.replace("DEFAULT NOW()", "DEFAULT CURRENT_TIMESTAMP")
        sqlite_stmt = sqlite_stmt.replace("NOW()", "CURRENT_TIMESTAMP")
        sqlite_stmt = sqlite_stmt.replace(
            "CURRENT_TIMESTAMP + INTERVAL '24 hours'", "CURRENT_TIMESTAMP"
        )
        sqlite_stmt = sqlite_stmt.replace("CHECK (tree_depth >= 0)", "")
        sqlite_stmt = sqlite_stmt.replace("CHECK (total_leaves > 0)", "")
        sqlite_stmt = sqlite_stmt.replace(
            "CHECK (segmentation_level IN ('sentence', 'paragraph', 'section'))", ""
        )
        sqlite_statements.append(sqlite_stmt)

    return sqlite_statements


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


TABLE_TRUNCATE_ORDER = [
    "audit_log",
    "certificate_lifecycle",
    "sentence_records",
    "documents",
    "api_keys",
    "organizations",
]


async def _truncate_all_tables(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_factory() as session:
        if TEST_DATABASE_IS_SQLITE:
            for table in TABLE_TRUNCATE_ORDER:
                await session.execute(text(f"DELETE FROM {table}"))
            try:
                await session.execute(text("DELETE FROM sqlite_sequence"))
            except Exception:  # pragma: no cover - sqlite sequence may not exist yet
                pass
        else:
            truncate_sql = (
                "TRUNCATE TABLE audit_log, certificate_lifecycle, sentence_records, documents, "
                "api_keys, organizations RESTART IDENTITY CASCADE"
            )
            await session.execute(text(truncate_sql))
        await session.commit()


async def _prepare_organization_with_api_key(
    session_factory: async_sessionmaker[AsyncSession],
    organization_name: str,
) -> dict:
    private_key, public_key = generate_ed25519_keypair()
    encrypted_private_key = encrypt_private_key(private_key)
    certificate_pem = _create_self_signed_certificate(private_key, public_key, organization_name)
    organization_id = f"org_{uuid.uuid4().hex[:12]}"
    api_key = f"test_{uuid.uuid4().hex}"
    timestamp = datetime.now(timezone.utc)

    async with session_factory() as session:
        await session.execute(
            text(
                """
                INSERT INTO organizations (
                    organization_id,
                    organization_name,
                    organization_type,
                    email,
                    tier,
                    private_key_encrypted,
                    certificate_pem,
                    monthly_quota,
                    documents_signed,
                    sentences_signed,
                    api_calls_this_month,
                    created_at,
                    updated_at
                )
                VALUES (
                    :organization_id,
                    :organization_name,
                    :organization_type,
                    :email,
                    :tier,
                    :private_key_encrypted,
                    :certificate_pem,
                    :monthly_quota,
                    0,
                    0,
                    0,
                    :created_at,
                    :updated_at
                )
                """
            ),
            {
                "organization_id": organization_id,
                "organization_name": organization_name,
                "organization_type": "enterprise",
                "email": f"{organization_id}@example.com",
                "tier": "enterprise",
                "private_key_encrypted": encrypted_private_key,
                "certificate_pem": certificate_pem,
                "monthly_quota": 1_000_000,
                "created_at": timestamp,
                "updated_at": timestamp,
            },
        )

        await session.execute(
            text(
                """
                INSERT INTO api_keys (
                    api_key,
                    organization_id,
                    key_name,
                    can_sign,
                    can_verify,
                    can_lookup,
                    created_at,
                    revoked
                )
                VALUES (
                    :api_key,
                    :organization_id,
                    :key_name,
                    TRUE,
                    TRUE,
                    TRUE,
                    :created_at,
                    FALSE
                )
                """
            ),
            {
                "api_key": api_key,
                "organization_id": organization_id,
                "key_name": "Integration Test Key",
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
        assert verify_response.status_code == 200
        verify_payload = verify_response.json()
        assert verify_payload["success"] is True
        verdict = verify_payload["data"]
        assert verdict["valid"] is True
        assert verdict["tampered"] is False
        assert verdict["signer_id"] == organization["organization_id"]
        assert verdict["signer_name"] == organization_name

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
    global TEST_DATABASE_IS_SQLITE

    temp_db = tempfile.NamedTemporaryFile(prefix="encypher_test_db_", suffix=".sqlite", delete=False)
    temp_db_path = Path(temp_db.name)
    temp_db.close()

    db_uri_path = temp_db_path.as_posix()
    async_db_url = f"sqlite+aiosqlite:///{db_uri_path}"

    engine = create_async_engine(
        async_db_url,
        future=True,
        pool_pre_ping=True,
    )
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    statements = _load_init_statements(use_sqlite=True)
    async with engine.begin() as conn:
        await conn.exec_driver_sql("PRAGMA foreign_keys=ON")
        for statement in statements:
            await conn.exec_driver_sql(statement)

    old_engine = db_module.engine
    old_session_factory = db_module.async_session_factory
    old_db_url = getattr(settings, "database_url", None)
    old_key = getattr(settings, "key_encryption_key", None)
    old_nonce = getattr(settings, "encryption_nonce", None)
    previous_sqlite_flag = TEST_DATABASE_IS_SQLITE

    db_module.engine = engine
    db_module.async_session_factory = session_factory
    settings.database_url = async_db_url
    if not old_key:
        settings.key_encryption_key = "0" * 64
    if not old_nonce:
        settings.encryption_nonce = "0" * 24
    TEST_DATABASE_IS_SQLITE = True

    try:
        yield session_factory
    finally:
        await _truncate_all_tables(session_factory)

        db_module.engine = old_engine
        db_module.async_session_factory = old_session_factory
        if old_db_url is not None:
            settings.database_url = old_db_url
        if old_key is not None:
            settings.key_encryption_key = old_key
        if old_nonce is not None:
            settings.encryption_nonce = old_nonce
        TEST_DATABASE_IS_SQLITE = previous_sqlite_flag

        await engine.dispose()
        try:
            temp_db_path.unlink(missing_ok=True)
        except OSError:  # pragma: no cover - best effort cleanup
            pass


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
        assert verify_response.status_code == 200
        verify_data = verify_response.json()

    assert verify_data["success"] is True
    verdict = verify_data["data"]
    assert verdict["signer_id"] == organization["organization_id"]
    assert verdict["signer_name"] == organization["organization_name"]
    manifest = verdict["details"]["manifest"]
    assert isinstance(manifest, dict) and manifest
    assert manifest.get("claim_generator") == "encypher-ai/2.4.2"
    assertion_labels = {
        assertion.get("label")
        for assertion in manifest.get("assertions", [])
        if isinstance(assertion, dict)
    }
    assert "c2pa.actions.v1" in assertion_labels
    assert "c2pa.soft_binding.v1" in assertion_labels
    assert verdict["valid"] is False
    assert verdict["tampered"] is True
