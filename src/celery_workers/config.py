import os

from utils.config import settings

# Configuration of Celery
broker_url = settings.CELERY_BROKER_URL
result_backend = settings.CELERY_RESULT_BACKEND

task_serializer = "json"
accept_content = ["json"]
result_serializer = "json"
timezone = "UTC"
enable_utc = True

task_track_started = True
task_time_limit = 30 * 60
worker_prefetch_multiplier = 1

task_acks_late = True
task_reject_on_worker_lost = True
