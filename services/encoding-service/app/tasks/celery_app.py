"""
Celery application configuration for background tasks.
"""
from celery import Celery
import os

# Get Redis URL from environment
REDIS_CELERY_URL = os.getenv("REDIS_CELERY_URL", "redis://localhost:6380")

# Create Celery app
celery_app = Celery(
    "encypher-encoding",
    broker=REDIS_CELERY_URL,
    backend=REDIS_CELERY_URL
)

# Configure Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes max
    task_soft_time_limit=25 * 60,  # 25 minutes soft limit
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    result_expires=3600,  # Results expire after 1 hour
)

# Auto-discover tasks
celery_app.autodiscover_tasks(['app.tasks'])
