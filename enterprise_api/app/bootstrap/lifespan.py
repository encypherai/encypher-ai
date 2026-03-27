import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy import text as sa_text

from app.config import settings
from app.observability.tracing import setup_tracing, shutdown_tracing
from app.services.metrics_service import init_metrics_service, shutdown_metrics_service
from app.services.session_service import session_service
from app.utils.db_startup import ensure_database_ready

logger = logging.getLogger(__name__)


def validate_startup_config() -> None:
    errors: list[str] = []
    warnings: list[str] = []

    if not settings.core_database_url_resolved:
        errors.append("DATABASE_URL or CORE_DATABASE_URL is not set")

    if not settings.key_encryption_key:
        errors.append("KEY_ENCRYPTION_KEY is not set (required for private key encryption)")
    elif len(settings.key_encryption_key) != 64:
        errors.append(f"KEY_ENCRYPTION_KEY must be 64 hex chars, got {len(settings.key_encryption_key)}")

    if not settings.encryption_nonce:
        errors.append("ENCRYPTION_NONCE is not set (required for private key encryption)")
    elif len(settings.encryption_nonce) != 24:
        errors.append(f"ENCRYPTION_NONCE must be 24 hex chars, got {len(settings.encryption_nonce)}")

    if settings.is_production and "localhost" in settings.allowed_origins:
        warnings.append("ALLOWED_ORIGINS contains localhost in production mode")

    if not settings.is_development and settings.redis_url == "redis://localhost:6379/0":
        errors.append("REDIS_URL must be configured for non-development environments (not the default localhost)")

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


def _apply_content_database_schema_patches(primary_db_url: str) -> None:
    content_db_url = settings.content_database_url_resolved
    if not content_db_url or content_db_url == primary_db_url:
        return

    logger.info("Applying schema patches to content database...")
    try:
        sync_content_url = content_db_url.replace("+asyncpg", "").replace("+aiopg", "")
        content_engine = create_engine(sync_content_url, pool_pre_ping=True)
        with content_engine.connect() as conn:
            conn.execute(
                sa_text(
                    "ALTER TABLE content_references"
                    " ADD COLUMN IF NOT EXISTS rights_snapshot JSONB,"
                    " ADD COLUMN IF NOT EXISTS rights_resolution_url TEXT"
                )
            )
            # Ensure article_images table exists on content DB
            # (Alembic only runs against core DB)
            conn.execute(
                sa_text(
                    "CREATE TABLE IF NOT EXISTS article_images ("
                    "  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),"
                    "  organization_id VARCHAR(64) NOT NULL,"
                    "  document_id VARCHAR(64) NOT NULL,"
                    "  image_id VARCHAR(64) NOT NULL,"
                    "  position INTEGER NOT NULL DEFAULT 0,"
                    "  filename VARCHAR(500),"
                    "  mime_type VARCHAR(100) NOT NULL,"
                    "  alt_text TEXT,"
                    "  original_hash VARCHAR(128) NOT NULL,"
                    "  signed_hash VARCHAR(128) NOT NULL,"
                    "  size_bytes BIGINT NOT NULL,"
                    "  c2pa_instance_id VARCHAR(255),"
                    "  c2pa_manifest_hash VARCHAR(128),"
                    "  phash BIGINT,"
                    "  phash_algorithm VARCHAR(20) DEFAULT 'average_hash',"
                    "  trustmark_applied BOOLEAN NOT NULL DEFAULT false,"
                    "  trustmark_key VARCHAR(100),"
                    "  exif_metadata JSONB,"
                    "  image_metadata JSONB DEFAULT '{}',"
                    "  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),"
                    "  CONSTRAINT uq_article_images_image_id UNIQUE (image_id)"
                    ")"
                )
            )
            conn.execute(sa_text("CREATE INDEX IF NOT EXISTS idx_article_images_org_doc ON article_images (organization_id, document_id)"))
            conn.execute(sa_text("CREATE INDEX IF NOT EXISTS idx_article_images_image_id ON article_images (image_id)"))
            conn.execute(sa_text("CREATE INDEX IF NOT EXISTS idx_article_images_phash ON article_images (phash) WHERE phash IS NOT NULL"))
            conn.execute(sa_text("CREATE INDEX IF NOT EXISTS idx_article_images_signed_hash ON article_images (signed_hash)"))
            # Ensure composite_manifests table exists on content DB
            conn.execute(
                sa_text(
                    "CREATE TABLE IF NOT EXISTS composite_manifests ("
                    "  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),"
                    "  organization_id VARCHAR(64) NOT NULL,"
                    "  document_id VARCHAR(64) NOT NULL,"
                    "  instance_id VARCHAR(255) NOT NULL,"
                    "  manifest_data JSONB NOT NULL,"
                    "  manifest_hash VARCHAR(128) NOT NULL,"
                    "  text_merkle_root VARCHAR(128),"
                    "  ingredient_count INTEGER NOT NULL DEFAULT 0,"
                    "  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),"
                    "  CONSTRAINT uq_composite_manifests_document_id UNIQUE (document_id)"
                    ")"
                )
            )
            conn.execute(sa_text("CREATE INDEX IF NOT EXISTS idx_composite_manifests_org ON composite_manifests (organization_id)"))
            conn.execute(sa_text("CREATE INDEX IF NOT EXISTS idx_composite_manifests_doc ON composite_manifests (document_id)"))
            conn.execute(sa_text("CREATE INDEX IF NOT EXISTS idx_composite_manifests_instance ON composite_manifests (instance_id)"))
            conn.commit()
        content_engine.dispose()
        logger.info("Content database schema patches applied.")
    except Exception as exc:
        logger.error("Content database schema patch failed: %s", exc)
        sys.exit(1)


async def _load_trust_lists() -> None:
    from app.utils.c2pa_trust_list import (
        C2PA_TRUST_LIST_URL,
        C2PA_TSA_TRUST_LIST_URL,
        get_trust_list_metadata,
        get_tsa_trust_list_metadata,
        refresh_trust_list,
        refresh_tsa_trust_list,
        set_revocation_denylist,
        trust_list_needs_refresh,
        tsa_trust_list_needs_refresh,
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Encypher Enterprise API starting up...")
    logger.info("Environment: %s", settings.environment)

    validate_startup_config()
    db_url = settings.core_database_url_resolved or settings.database_url or ""
    logger.info("Database: %s", db_url.split("@")[1] if "@" in db_url else "Not configured")
    if settings.ssl_com_api_key:
        logger.info("SSL.com API: %s", settings.ssl_com_api_url)
    else:
        logger.info("SSL.com API: Not configured (optional for staging)")

    ensure_database_ready(
        database_url=db_url,
        service_name="enterprise-api",
        run_migrations=True,
        exit_on_failure=True,
    )
    _apply_content_database_schema_patches(db_url)

    try:
        await session_service.connect()
    except Exception as exc:
        logger.warning("Failed to connect to Redis: %s. Running without session persistence.", exc)

    # Wire Redis into the org cache and job queue when available
    from app.services.cache_service import org_cache
    from app.services.job_queue import job_queue

    if session_service.redis_client:
        await org_cache.connect(session_service.redis_client)
        await job_queue.connect(session_service.redis_client)
        logger.info("Redis-backed org cache and job queue connected")

    # Recover incomplete batch state from Redis
    from app.services.batch_service import batch_service

    if session_service.redis_client:
        recovered = await batch_service.recover_incomplete_batches(
            session_service.redis_client,
        )
        if recovered:
            logger.info("Recovered %d incomplete batch state entries from Redis", recovered)

    try:
        await init_metrics_service()
        logger.info("Metrics service initialized")
    except Exception as exc:
        logger.warning("Failed to initialize metrics service: %s. Running without metrics.", exc)

    setup_tracing(app)

    try:
        await _load_trust_lists()
    except Exception as exc:
        if settings.is_production:
            logger.error("Failed to load C2PA trust list: %s", exc)
            raise
        logger.warning("Failed to load C2PA trust list: %s. BYOK certificate validation may not work.", exc)

    # Start webhook retry background loop
    from app.services.webhook_dispatcher import webhook_dispatcher

    webhook_dispatcher.start_retry_loop()

    try:
        yield
    finally:
        logger.info("Encypher Enterprise API shutting down...")
        await webhook_dispatcher.close()
        shutdown_tracing()
        try:
            await shutdown_metrics_service()
        except Exception as exc:
            logger.error("Error shutting down metrics service: %s", exc)
        try:
            await session_service.disconnect()
        except Exception as exc:
            logger.error("Error disconnecting from Redis: %s", exc)
