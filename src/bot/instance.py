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


async def _post_init(application: Application) -> None:
    """Register the localized slash-command menus once the bot is initialized.

    Sets English as the global default scope and a Spanish menu keyed on the
    Telegram client ``language_code``. Per-group (chat-scoped) menus that follow
    a group's configured language are synced separately on change (see
    :func:`bot.utils.commands_sync.set_chat_commands`). Best-effort.
    """
    from telegram import BotCommand

    from bot.i18n.commands import command_dicts
    from utils.logger_base import logger

    try:
        bot = application.bot
        await bot.set_my_commands([BotCommand(**c) for c in command_dicts("en")])
        await bot.set_my_commands(
            [BotCommand(**c) for c in command_dicts("es")], language_code="es"
        )
        logger.info("Registered localized bot command menus (en default, es)")
    except Exception as exc:
        logger.warning(f"Failed to register bot command menus: {exc}")


def build_application() -> Application:
    """Build the python-telegram-bot ``Application`` around the shared ``Bot``.

    :returns: a fully configured ``Application`` ready to register handlers on.
    """
    bot = get_bot()
    return ApplicationBuilder().bot(bot).post_init(_post_init).build()


def reset_bot() -> None:
    """Drop the cached ``Bot`` instance. Intended for tests only."""
    global _bot
    with _bot_lock:
        _bot = None
