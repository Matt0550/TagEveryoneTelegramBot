"""Shared python-telegram-bot ``Bot`` singleton.

Every layer that needs to talk to the Telegram Bot API (the bot itself, the
FastAPI layer, services, Celery workers) must obtain its ``Bot`` through
:func:`get_bot`. Constructing additional ``Bot`` instances throughout the
codebase wastes connections and makes mocking in tests harder.
"""

from __future__ import annotations

from threading import Lock

from telegram import Bot
from telegram.ext import Application, ApplicationBuilder

from utils.config import settings

_bot: Bot | None = None
_bot_lock = Lock()


def get_bot() -> Bot:
    """Return the process-wide :class:`telegram.Bot` singleton.

    :returns: a lazily-created ``Bot`` configured with ``settings.BOT_TOKEN``.
    """
    global _bot
    if _bot is None:
        with _bot_lock:
            if _bot is None:
                _bot = Bot(token=settings.BOT_TOKEN)
    return _bot


def build_application() -> Application:
    """Build the python-telegram-bot ``Application`` around the shared ``Bot``.

    :returns: a fully configured ``Application`` ready to register handlers on.
    """
    bot = get_bot()
    return ApplicationBuilder().bot(bot).build()


def reset_bot() -> None:
    """Drop the cached ``Bot`` instance. Intended for tests only."""
    global _bot
    with _bot_lock:
        _bot = None
