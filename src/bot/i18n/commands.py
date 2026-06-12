"""Canonical user-facing command list for ``setMyCommands`` localization.

Pure data + helpers (only depends on :mod:`bot.i18n`, no telegram imports) so
the API process can build the localized payload when a group's language changes.
The bot wraps :func:`command_dicts` output into ``telegram.BotCommand``.
"""

from __future__ import annotations

from bot.i18n import t

# (command, description translation key) — list order is the menu order.
COMMAND_KEYS: list[tuple[str, str]] = [
    ("in", "commands.in.description"),
    ("out", "commands.out.description"),
    ("list", "commands.list.description"),
    ("everyone", "commands.everyone.description"),
    ("createlist", "commands.createlist.description"),
    ("deletelist", "commands.deletelist.description"),
    ("clearlist", "commands.clearlist.description"),
    ("settings", "commands.settings.description"),
    ("help", "commands.help.description"),
    ("status", "commands.status.description"),
]


def command_dicts(locale: str | None = None) -> list[dict[str, str]]:
    """:returns: ``[{"command", "description"}]`` localized to ``locale`` —
    the exact payload shape expected by Telegram's ``setMyCommands``."""
    return [
        {"command": cmd, "description": t(key, locale)} for cmd, key in COMMAND_KEYS
    ]
