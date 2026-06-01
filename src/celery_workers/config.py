import os

# Use the environment variables with default values
env_broker_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1")
env_result_backend = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")

# Configuration of Celery
broker_url = env_broker_url
result_backend = env_result_backend

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
