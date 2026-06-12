"""Bot translation engine — JSON locale files loaded into RAM.

Mirrors the frontend's ``vue-i18n`` setup. English is the default and the
fallback for any missing key. Only user-facing strings live here; logs and the
logger stay English.

Public API::

    from bot.i18n import t, get_locale, resolve_group_locale

    await update.message.reply_text(t("start.ready", get_locale(update, context)))
"""

from __future__ import annotations

import json
import os
from typing import Any

from utils.languages import (
    DEFAULT_LANGUAGE,
    SUPPORTED_LANGUAGES,
    normalize_language,
)

_LOCALES_DIR = os.path.join(os.path.dirname(__file__), "locales")


def _load() -> dict[str, dict[str, Any]]:
    data: dict[str, dict[str, Any]] = {}
    for lang in SUPPORTED_LANGUAGES:
        path = os.path.join(_LOCALES_DIR, f"{lang}.json")
        try:
            with open(path, encoding="utf-8") as fh:
                data[lang] = json.load(fh)
        except (OSError, json.JSONDecodeError):
            data[lang] = {}
    return data


_TRANSLATIONS = _load()


def _lookup(lang: str, key: str) -> str | None:
    """Resolve a dotted ``key`` (e.g. ``"in.added_self"``) in ``lang``'s tree."""
    node: Any = _TRANSLATIONS.get(lang)
    for part in key.split("."):
        if isinstance(node, dict) and part in node:
            node = node[part]
        else:
            return None
    return node if isinstance(node, str) else None


def t(key: str, locale: str | None = None, /, **kwargs: Any) -> str:
    """Translate ``key`` into ``locale``, formatting with ``kwargs``.

    Falls back ``locale -> English -> the key itself``. If interpolation fails
    (a stray placeholder), the raw template is returned rather than raising.

    :param key: dotted translation key.
    :param locale: target language code (regional variants are normalized).
    :param kwargs: ``str.format`` interpolation values.
    :returns: the translated, interpolated string.
    """
    lang = normalize_language(locale)
    template = _lookup(lang, key)
    if template is None and lang != DEFAULT_LANGUAGE:
        template = _lookup(DEFAULT_LANGUAGE, key)
    if template is None:
        return key
    if not kwargs:
        return template
    try:
        return template.format(**kwargs)
    except (KeyError, IndexError, ValueError):
        return template


def get_locale(update: Any, context: Any = None) -> str:
    """Resolve the language to reply in for the current update.

    Priority: the per-update locale cached by ``activity_middleware`` in
    ``context.chat_data["locale"]`` -> the Telegram user's client language ->
    :data:`~utils.languages.DEFAULT_LANGUAGE`. Never raises.
    """
    if context is not None:
        chat_data = getattr(context, "chat_data", None)
        if isinstance(chat_data, dict):
            cached = chat_data.get("locale")
            if cached in SUPPORTED_LANGUAGES:
                return cached
    user = getattr(update, "effective_user", None)
    lang_code = getattr(user, "language_code", None) if user is not None else None
    return normalize_language(lang_code)


def resolve_group_locale(group: Any) -> str:
    """:returns: the configured language for ``group`` (via ``group.settings``),
    or the default when settings/language are missing."""
    try:
        settings = getattr(group, "settings", None)
        if settings is not None and getattr(settings, "language", None):
            return normalize_language(settings.language)
    except Exception:
        pass
    return DEFAULT_LANGUAGE
