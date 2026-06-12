"""Sync the localized slash-command menu for a single group (chat scope).

Used by the API/service layer when a group's language changes so the Telegram
command list shown inside that group follows its configured language. This is a
plain synchronous HTTP call (so it works from the sync service method) and is
strictly best-effort — failures are logged in English and never raised.
"""

from __future__ import annotations

import httpx

from bot.i18n.commands import command_dicts
from utils.config import _get_telegram_api_url
from utils.logger_base import logger


def set_chat_commands(telegram_id: int, locale: str) -> bool:
    """Set the localized command menu for the chat ``telegram_id``.

    :param telegram_id: the group's Telegram chat id.
    :param locale: language code to render the command descriptions in.
    :returns: ``True`` if Telegram acknowledged the update, ``False`` otherwise.
    """
    try:
        url = _get_telegram_api_url("setMyCommands")
        payload = {
            "commands": command_dicts(locale),
            "scope": {"type": "chat", "chat_id": telegram_id},
        }
        resp = httpx.post(url, json=payload, timeout=10)
        ok = resp.status_code == 200 and resp.json().get("ok", False)
        if not ok:
            logger.warning(
                f"setMyCommands(chat={telegram_id}, lang={locale}) failed: "
                f"{resp.text[:200]}"
            )
        return ok
    except Exception as exc:
        logger.warning(
            f"setMyCommands(chat={telegram_id}, lang={locale}) error: {exc}"
        )
        return False
