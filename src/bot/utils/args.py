"""Argument parsing helpers shared by command handlers."""

from __future__ import annotations


def parse_trigger_name(args: list[str] | None) -> str | None:
    """Extract the canonical trigger name from a command's positional args.

    Strips a leading ``@`` or ``/`` and lowercases the result. Returns ``None``
    when ``args`` is empty so the caller can decide how to respond.

    :param args: ``context.args`` from a telegram-ext handler.
    :returns: the normalized trigger name, or ``None`` if no args were given.
    """
    if not args:
        return None
    trigger = args[0].lower()
    if trigger.startswith("@") or trigger.startswith("/"):
        trigger = trigger[1:]
    return trigger
