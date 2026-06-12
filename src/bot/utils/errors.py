"""Shared error-reporting helpers for the bot.

All command handlers should use these helpers instead of echoing the raw
exception back to the originating chat. This prevents internal details from
leaking and keeps error messaging consistent across commands.
"""

from __future__ import annotations

import html
import json
import traceback

from telegram import Bot, Update

from bot.i18n import get_locale, t
from utils.config import settings
from utils.logger_base import logger


async def reply_generic_error(update: Update | None, context=None) -> None:
    """Reply to the user with a generic, non-sensitive error message.

    :param update: the incoming :class:`telegram.Update`; safely handles ``None``.
    :param context: optional telegram-ext context, used to localize the reply to
        the group's configured language (falls back to English).
    """
    try:
        if update is None or update.effective_message is None:
            return
        await update.effective_message.reply_text(
            t("errors.generic", get_locale(update, context))
        )
    except Exception as exc:
        logger.warning(f"Failed to send generic error reply: {exc}")


async def notify_owner_of_error(
    bot: Bot,
    exc: BaseException,
    update: object | None = None,
    context_data: dict | None = None,
) -> None:
    """Send a detailed traceback to the bot owner DM (if enabled).

    Controlled by ``settings.REPORT_ERRORS_OWNER`` and
    ``settings.SEND_DETAILED_ERRORS_TO_OWNER``. If either flag is off, or
    ``OWNER_ID`` is missing, this is a no-op.

    :param bot: the shared :class:`telegram.Bot`.
    :param exc: the exception to report.
    :param update: optional originating update for additional context.
    :param context_data: optional dict of extra contextual data to include.
    """
    if not settings.REPORT_ERRORS_OWNER or not settings.OWNER_ID:
        return
    if not settings.SEND_DETAILED_ERRORS_TO_OWNER:
        return

    try:
        tb_string = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        max_tb_length = 2500
        if len(tb_string) > max_tb_length:
            tb_string = tb_string[:max_tb_length] + "\n... [TRUNCATED]"

        update_str: str | dict
        if isinstance(update, Update):
            try:
                update_str = update.to_dict()
            except Exception:
                update_str = str(update)
        else:
            update_str = str(update) if update is not None else ""

        update_repr = json.dumps(update_str, indent=2, ensure_ascii=False, default=str)
        if len(update_repr) > 1000:
            update_repr = update_repr[:1000] + "... [TRUNCATED]"

        extras = ""
        if context_data:
            try:
                extras = json.dumps(context_data, indent=2, ensure_ascii=False, default=str)
                if len(extras) > 800:
                    extras = extras[:800] + "... [TRUNCATED]"
                extras = f"\n<b>Context:</b>\n<pre>{html.escape(extras)}</pre>"
            except Exception:
                extras = ""

        message = (
            "🚨 <b>Bot Error</b>\n\n"
            f"<b>Type:</b> {type(exc).__name__}\n"
            f"<b>Message:</b> {html.escape(str(exc)[:500])}\n\n"
            f"<b>Update:</b>\n<pre>{html.escape(update_repr)}</pre>"
            f"{extras}\n"
            f"<b>Traceback:</b>\n<pre>{html.escape(tb_string)}</pre>"
        )

        if len(message) > 4000:
            message = message[:3900] + "\n... [TRUNCATED]</pre>"

        await bot.send_message(
            chat_id=settings.OWNER_ID, text=message, parse_mode="HTML"
        )
    except Exception as inner:
        logger.error(f"Failed to notify owner of error: {inner}")
