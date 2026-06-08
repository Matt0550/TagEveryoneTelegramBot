"""
Celery task for sending a single Telegram message via the HTTP API.
Handles rate limit errors (429) with automatic exponential backoff retry.
"""

import httpx

from celery_workers.celery_app import celery_app
from celery_workers.celery_logger_base import logger
from models_all.exceptions import TelegramAPIError, TelegramRateLimitError
from utils.config import _get_telegram_api_url


@celery_app.task(
    bind=True,
    name="send_telegram_message",
    autoretry_for=(TelegramRateLimitError,),
    retry_backoff=True,
    retry_backoff_max=300,
    max_retries=10,
    retry_jitter=True,
)
def send_telegram_message(
    self,
    chat_id: int | str,
    text: str,
    parse_mode: str = "HTML",
    disable_web_page_preview: bool = True,
    reply_to_message_id: int | None = None,
) -> dict:
    """
    Send a single message to a Telegram chat via the HTTP API.

    This task auto-retries on 429 (rate limit) errors with exponential backoff.
    Non-retryable errors (e.g., 403 bot was kicked, 400 bad request) raise
    TelegramAPIError immediately.

    :param chat_id: The target chat ID (group or user).
    :param text: The message text to send.
    :param parse_mode: Parse mode for the message (HTML, Markdown, MarkdownV2).
    :param disable_web_page_preview: Whether to disable link previews.
    :param reply_to_message_id: Optional message ID to reply to.

    :return: The Telegram API response as a dict on success.

    :raise TelegramRateLimitError: On 429 responses (auto-retried by Celery).
    :raise TelegramAPIError: On other non-2xx responses (not retried).
    """
    task_id = self.request.id
    logger.info(
        f"[send_telegram_message] task_id={task_id} chat_id={chat_id} "
        f"text_length={len(text)}"
    )

    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": disable_web_page_preview,
    }

    if reply_to_message_id is not None:
        payload["reply_to_message_id"] = reply_to_message_id

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(_get_telegram_api_url("sendMessage"), json=payload)

        response_data = response.json()

        if response.status_code == 200 and response_data.get("ok"):
            logger.info(
                f"[send_telegram_message] Message sent successfully to {chat_id}"
            )
            return response_data

        # Rate limit. Celery will auto-retry with backoff
        if response.status_code == 429:
            retry_after = response_data.get("parameters", {}).get("retry_after", 30)
            logger.warning(
                f"[send_telegram_message] Rate limited for chat {chat_id}, "
                f"retry_after={retry_after}s"
            )
            raise TelegramRateLimitError(retry_after=retry_after)

        # Non-retryable error
        description = response_data.get("description", "Unknown error")
        logger.error(
            f"[send_telegram_message] Failed for chat {chat_id}: "
            f"{response.status_code} - {description}"
        )
        raise TelegramAPIError(
            status_code=response.status_code, description=description
        )

    except httpx.RequestError as e:
        logger.error(
            f"[send_telegram_message] Network error for chat {chat_id}: {e}",
            exc_info=True,
        )
        # Retry on network errors by re-raising as a rate limit with short delay
        raise self.retry(exc=e, countdown=5, max_retries=5)
