"""Supported bot languages — single source of truth.

Kept dependency-free (no telegram/bot imports) so both the API/service layer
and the bot translation engine can import it. English is the system default
and fallback language.
"""

from __future__ import annotations

DEFAULT_LANGUAGE = "en"

# ISO 639-1 codes the bot can reply in. English MUST stay first / default.
SUPPORTED_LANGUAGES: tuple[str, ...] = ("en", "es")

# Human-readable names (shown in the webapp language selector).
LANGUAGE_NAMES: dict[str, str] = {
    "en": "English",
    "es": "Español",
}


def normalize_language(value: str | None) -> str:
    """Coerce an arbitrary language code to a supported one.

    Maps regional variants (e.g. ``es-ES`` -> ``es``) and falls back to
    :data:`DEFAULT_LANGUAGE` for anything unsupported or missing.

    :param value: a language code (possibly ``None`` or regional).
    :returns: a code guaranteed to be in :data:`SUPPORTED_LANGUAGES`.
    """
    if not value:
        return DEFAULT_LANGUAGE
    base = str(value).strip().lower().replace("_", "-").split("-", 1)[0]
    return base if base in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE


def is_supported(value: str | None) -> bool:
    """:returns: ``True`` if ``value`` is exactly a supported language code."""
    return value in SUPPORTED_LANGUAGES
