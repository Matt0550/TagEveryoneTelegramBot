"""
Celery task for processing announce batches.
Sends an announcement message to a batch of Telegram groups,
tracking delivery status in the database.
"""

from datetime import UTC, datetime

import httpx
from sqlmodel import select

from celery_workers.celery_app import celery_app
from celery_workers.celery_logger_base import logger
from celery_workers.tasks.send_telegram_message import (
    TelegramAPIError,
    TelegramRateLimitError,
    _get_api_url,
)
from models_all.announce_job_group import AnnounceGroupStatus, AnnounceJobGroup
from models_all.async_job import AsyncJob, JobStatus
from utils.session_manager import Session, engine


def _update_job_progress(session: Session, job_id: int) -> None:
    """
    Recalculate and update the async job's completed/failed counts
    from the announce_job_groups table.

    Also marks the job as completed/failed if all groups have been processed.
    """
    job = session.get(AsyncJob, job_id)
    if not job:
        return

    # Count sent and failed groups
    sent_statement = select(AnnounceJobGroup).where(
        AnnounceJobGroup.job_id == job_id,
        AnnounceJobGroup.status == AnnounceGroupStatus.SENT,
    )
    sent_count = len(session.exec(sent_statement).all())

    failed_statement = select(AnnounceJobGroup).where(
        AnnounceJobGroup.job_id == job_id,
        AnnounceJobGroup.status == AnnounceGroupStatus.FAILED,
    )
    failed_count = len(session.exec(failed_statement).all())

    job.completed_items = sent_count
    job.failed_items = failed_count

    # Check if all groups have been processed
    processed = sent_count + failed_count
    if processed >= job.total_items:
        if failed_count == job.total_items:
            job.status = JobStatus.FAILED
        else:
            job.status = JobStatus.COMPLETED
        job.completed_at = datetime.now(UTC)
        logger.info(
            f"[send_announce_batch] Job {job_id} completed: "
            f"sent={sent_count}, failed={failed_count}"
        )

    session.add(job)
    session.commit()


@celery_app.task(
    bind=True,
    name="send_announce_batch",
    max_retries=3,
    default_retry_delay=10,
)
def send_announce_batch(
    self,
    job_id: int,
    group_ids: list[int],
    message: str,
) -> dict:
    """
    Send an announcement message to a batch of Telegram groups.

    For each group in the batch:
    - Send the message via Telegram HTTP API
    - Update the announce_job_groups row with the result
    - Update the parent async_job's progress counters

    :param job_id: The ID of the parent AsyncJob.
    :param group_ids: List of AnnounceJobGroup IDs to process in this batch.
    :param message: The announcement message text.

    :return: A dict with batch processing statistics.
    """
    task_id = self.request.id
    logger.info(
        f"[send_announce_batch] task_id={task_id} job_id={job_id} "
        f"batch_size={len(group_ids)}"
    )

    stats = {
        "task_id": task_id,
        "job_id": job_id,
        "sent": 0,
        "failed": 0,
        "rate_limited": False,
    }

    session = Session(engine)
    try:
        # Mark parent job as in_progress if still pending
        job = session.get(AsyncJob, job_id)
        if job and job.status == JobStatus.PENDING:
            job.status = JobStatus.IN_PROGRESS
            session.add(job)
            session.commit()

        for ajg_id in group_ids:
            ajg = session.get(AnnounceJobGroup, ajg_id)
            if not ajg or ajg.status != AnnounceGroupStatus.PENDING:
                continue

            try:
                _send_message_to_group(ajg.group_telegram_id, message)

                # Mark as sent
                ajg.status = AnnounceGroupStatus.SENT
                ajg.sent_at = datetime.now(UTC)
                ajg.error_message = None
                session.add(ajg)
                session.commit()
                stats["sent"] += 1

                logger.info(
                    f"[send_announce_batch] Sent to group "
                    f"{ajg.group_telegram_id} (job={job_id})"
                )

            except TelegramRateLimitError as e:
                # On rate limit, retry the entire batch with the specified delay
                session.rollback()
                stats["rate_limited"] = True
                logger.warning(
                    f"[send_announce_batch] Rate limited, retrying batch "
                    f"in {e.retry_after}s"
                )
                raise self.retry(exc=e, countdown=e.retry_after)

            except TelegramAPIError as e:
                # Non-retryable error for this specific group
                ajg.status = AnnounceGroupStatus.FAILED
                ajg.error_message = e.description
                session.add(ajg)
                session.commit()
                stats["failed"] += 1

                logger.warning(
                    f"[send_announce_batch] Failed for group "
                    f"{ajg.group_telegram_id}: {e.description}"
                )

                # If bot was kicked/blocked (403), delete the group from DB
                if e.status_code == 403:
                    _handle_removed_group(session, ajg.group_telegram_id)

            except Exception as e:
                ajg.status = AnnounceGroupStatus.FAILED
                ajg.error_message = str(e)
                session.add(ajg)
                session.commit()
                stats["failed"] += 1

                logger.error(
                    f"[send_announce_batch] Unexpected error for group "
                    f"{ajg.group_telegram_id}: {e}",
                    exc_info=True,
                )

        # Update parent job progress
        _update_job_progress(session, job_id)

        logger.info(f"[send_announce_batch] Batch complete: {stats}")
        return stats

    except Exception as e:
        session.rollback()
        logger.error(
            f"[send_announce_batch] Fatal error in batch for job {job_id}: {e}",
            exc_info=True,
        )
        raise

    finally:
        session.close()


def _send_message_to_group(chat_id: int, text: str) -> dict:
    """
    Send a message to a Telegram chat via the HTTP API (synchronous).
    Raises TelegramRateLimitError on 429, TelegramAPIError on other errors.
    """
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }

    with httpx.Client(timeout=30.0) as client:
        response = client.post(_get_api_url("sendMessage"), json=payload)

    response_data = response.json()

    if response.status_code == 200 and response_data.get("ok"):
        return response_data

    if response.status_code == 429:
        retry_after = response_data.get("parameters", {}).get("retry_after", 30)
        raise TelegramRateLimitError(retry_after=retry_after)

    description = response_data.get("description", "Unknown error")
    raise TelegramAPIError(status_code=response.status_code, description=description)


def _handle_removed_group(session: Session, group_telegram_id: int) -> None:
    """
    Handle a group where the bot was kicked/blocked.
    Soft-deletes the group from the database.
    """
    from repositories.group_repository import GroupRepository

    repo = GroupRepository()
    group = repo.get_by_telegram_id(session, group_telegram_id)
    if group:
        group.active = False
        group.deleted_at = datetime.now(UTC)
        session.add(group)
        session.commit()
        logger.info(
            f"[send_announce_batch] Soft-deleted group {group_telegram_id} "
            f"(bot was kicked/blocked)"
        )
