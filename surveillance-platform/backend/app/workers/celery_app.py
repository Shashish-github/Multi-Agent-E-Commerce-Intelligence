"""Celery application for background video processing."""
from celery import Celery

from backend.app.core.config import settings

celery_app = Celery(
    "surveillance",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,
    task_soft_time_limit=250,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,
)

celery_app.autodiscover_tasks(["backend.app.workers"])
