# pyright: reportUnusedImport=false
from celery import Celery
from celery.signals import task_failure, task_retry, worker_shutdown

from celery_workers.celery_logger_base import logger


def create_celery_app() -> Celery:
    app = Celery("tag_everyonebot")

    app.config_from_object("celery_workers.config")

    app.autodiscover_tasks(["celery_workers.tasks"])

    return app


celery_app = create_celery_app()


@task_failure.connect
def handle_task_failure(
    sender=None,
    task_id=None,
    exception=None,
    args=None,
    kwargs=None,
    **_,
):
    task_name = sender.name if sender else "Unknown"

    error_context = {
        "task_name": task_name,
        "task_id": task_id,
        "task_args": args,
        "task_kwargs": kwargs,
    }

    error_message = f"Celery Task Failed: {task_name} - {exception}"
    logger.error(error_message, exc_info=True, extra=error_context)


@task_retry.connect
def handle_task_retry(sender=None, request=None, reason=None, **_):
    task_name = sender.name if sender else "Unknown"
    retries = request.retries if request else 0
    max_retries = sender.max_retries if sender else 0

    logger.warning(
        f"Task {task_name} is being retried. Attempt {retries}/{max_retries}. Reason: {reason}",
    )


@worker_shutdown.connect
def handle_worker_shutdown(sender=None, **_):
    logger.info(f"Worker {sender} is shutting down. Cleaning up resources...")


# Explicitly import the task modules to ensure they are registered
import celery_workers.tasks.send_telegram_message  # noqa: E402, I001
import celery_workers.tasks.send_announce_batch  # noqa: E402, F401, I001
