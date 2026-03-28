"""Alert Service - Main Application."""

import logging
from contextlib import asynccontextmanager

from encypher_commercial_shared.db import ensure_database_ready
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.v1.endpoints import router as v1_router
from .core.config import settings
from .core.logging_config import setup_logging
from .middleware.logging import RequestLoggingMiddleware
from .monitoring.metrics import setup_metrics

setup_logging(settings.LOG_LEVEL)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting %s", settings.SERVICE_NAME)

    ensure_database_ready(
        database_url=settings.DATABASE_URL,
        service_name=settings.SERVICE_NAME,
        alembic_config_path="alembic.ini",
        run_migrations=True,
        exit_on_failure=True,
    )

    # Start Redis Stream consumer
    stream_consumer = None
    if settings.REDIS_URL:
        try:
            from .services.stream_consumer import start_alert_consumer

            stream_consumer = await start_alert_consumer(redis_url=settings.REDIS_URL)
            logger.info("Alert stream consumer started")
        except Exception as e:
            logger.warning("Failed to start alert stream consumer: %s", e)

    # Start background pattern detector
    pattern_task = None
    try:
        from .services.pattern_detector import start_pattern_detector, stop_pattern_detector

        await start_pattern_detector()
        pattern_task = True
        logger.info("Pattern detector started")
    except Exception as e:
        logger.warning("Failed to start pattern detector: %s", e)

    # Start Discord bot
    discord_bot_running = False
    if settings.DISCORD_BOT_TOKEN:
        try:
            from .services.discord_bot import start_discord_bot, stop_discord_bot

            await start_discord_bot()
            discord_bot_running = True
        except Exception as e:
            logger.warning("Failed to start Discord bot: %s", e)

    yield

    # Shutdown
    if stream_consumer:
        try:
            from .services.stream_consumer import stop_alert_consumer

            await stop_alert_consumer()
        except Exception as e:
            logger.error("Error stopping stream consumer: %s", e)

    if pattern_task:
        try:
            from .services.pattern_detector import stop_pattern_detector

            await stop_pattern_detector()
        except Exception as e:
            logger.error("Error stopping pattern detector: %s", e)

    if discord_bot_running:
        try:
            from .services.discord_bot import stop_discord_bot

            await stop_discord_bot()
        except Exception as e:
            logger.error("Error stopping Discord bot: %s", e)

    logger.info("Shutting down %s", settings.SERVICE_NAME)


app = FastAPI(
    title="Encypher Alert Service",
    description="Alerting and incident management for Encypher platform",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestLoggingMiddleware)
setup_metrics(app)

app.include_router(v1_router, prefix="/api/v1/alerts", tags=["alerts"])


@app.get("/")
async def root():
    return {
        "service": settings.SERVICE_NAME,
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    return {"status": "healthy", "service": settings.SERVICE_NAME}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host=settings.SERVICE_HOST, port=settings.SERVICE_PORT, reload=True)
