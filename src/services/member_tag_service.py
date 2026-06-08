"""Resolve the per-member Telegram tag (``ChatMemberMember.tag``).

Telegram owns the tag string assigned by group admins to members of supergroups
(field added in Bot API 9.x / PTB 22.7). This service reads it via
``Bot.get_chat_member`` and caches the result aggressively so the mention
hot-path never pays the API cost more than once every
``CACHE_MEMBER_TAG_TTL`` seconds per user.

Tag values are stored lowercased so all comparisons against
:class:`ListTagRule` are case-insensitive.
"""

from __future__ import annotations

import asyncio
from collections.abc import Iterable

from telegram import Bot, Update

from services.base_service import BaseService
from services.cache_service import CacheService
from services.log_service import LogService
from utils.config import settings
from utils.logger_base import logger

_NULL_TAG_SENTINEL = "__none__"


class MemberTagService(BaseService):
    """Read and cache Telegram member tag strings."""

    MEMBER_TAG_KEY = "tg_member_tag:{chat_id}:{user_id}"
    KNOWN_TAGS_KEY = "tg_group_tags:{chat_id}"

    def __init__(
        self,
        cache: CacheService | None = None,
        log_service: LogService | None = None,
    ) -> None:
        """:param cache: optional :class:`CacheService`. Falls back to the singleton.
        :param log_service: optional audit logger (rarely used by this service).
        """
        super().__init__(session=None, log_service=log_service, cache=cache)  # type: ignore[arg-type]

    @staticmethod
    def _normalize(tag: str | None) -> str | None:
        """Lowercase and strip a tag. Returns ``None`` for empty input.

        :param tag: raw tag string straight from Telegram.
        :returns: normalized tag or ``None``.
        """
        if tag is None:
            return None
        value = tag.strip().lower()
        return value or None

    @staticmethod
    def _extract_tag(member: object) -> str | None:
        """Pull the ``tag`` attribute from a :class:`telegram.ChatMember` subtype.

        :param member: any PTB ``ChatMember`` instance.
        :returns: normalized tag string or ``None`` when absent.
        """
        return MemberTagService._normalize(getattr(member, "tag", None))

    async def _cache_get(self, chat_id: int, user_id: int) -> str | None | object:
        """Return the cached tag for a member, distinguishing miss from null.

        :param chat_id: Telegram chat ID.
        :param user_id: Telegram user ID.
        :returns: cached tag, the sentinel for cached-null, or ``None`` on miss.
        """
        key = self.MEMBER_TAG_KEY.format(chat_id=chat_id, user_id=user_id)
        cached = await self.cache.get(key)
        return cached

    async def _cache_set(
        self, chat_id: int, user_id: int, tag: str | None
    ) -> None:
        """Persist a resolved tag (or null sentinel) under the per-member key.

        :param chat_id: Telegram chat ID.
        :param user_id: Telegram user ID.
        :param tag: normalized tag string or ``None``.
        """
        key = self.MEMBER_TAG_KEY.format(chat_id=chat_id, user_id=user_id)
        payload = tag if tag is not None else _NULL_TAG_SENTINEL
        await self.cache.set(key, payload, ttl=settings.CACHE_MEMBER_TAG_TTL)

    async def invalidate(self, chat_id: int, user_id: int) -> None:
        """Drop a single member's cached tag.

        :param chat_id: Telegram chat ID.
        :param user_id: Telegram user ID.
        """
        await self._invalidate(
            self.MEMBER_TAG_KEY.format(chat_id=chat_id, user_id=user_id)
        )

    async def record_observed_tag(self, chat_id: int, tag: str | None) -> None:
        """Append a freshly observed tag to the group's known-tag list.

        Stored as a JSON list (we keep last 200 distinct values). Used by the
        WebApp rule editor for autocomplete.

        :param chat_id: Telegram chat ID.
        :param tag: normalized tag string. ``None`` is ignored.
        """
        if not tag:
            return
        key = self.KNOWN_TAGS_KEY.format(chat_id=chat_id)
        current = await self.cache.get(key) or []
        if not isinstance(current, list):
            current = []
        if tag in current:
            return
        current.append(tag)
        if len(current) > 200:
            current = current[-200:]
        await self.cache.set(key, current, ttl=settings.CACHE_KNOWN_TAGS_TTL)

    async def get_known_tags(self, chat_id: int) -> list[str]:
        """Return the cached list of distinct tag values observed in a group.

        :param chat_id: Telegram chat ID.
        :returns: sorted list of lowercased tag strings (possibly empty).
        """
        key = self.KNOWN_TAGS_KEY.format(chat_id=chat_id)
        current = await self.cache.get(key) or []
        if not isinstance(current, list):
            return []
        return sorted({str(t) for t in current if t})

    async def get_tag(
        self,
        bot: Bot,
        chat_id: int,
        user_id: int,
        update: Update | None = None,
    ) -> str | None:
        """Resolve a single member's tag, using cache + Telegram API.

        :param bot: PTB ``Bot`` used when no cache entry exists.
        :param chat_id: Telegram chat ID of the group.
        :param user_id: Telegram user ID.
        :param update: optional :class:`telegram.Update` whose ``message.chat``
            can be reused to save one HTTP round-trip (mirrors
            :meth:`MentionService.fetch_user_live`).
        :returns: lowercased tag, or ``None``.
        """
        cached = await self._cache_get(chat_id, user_id)
        if cached == _NULL_TAG_SENTINEL:
            return None
        if isinstance(cached, str):
            return cached

        try:
            if update is not None and update.message is not None:
                member = await update.message.chat.get_member(user_id)
            else:
                member = await bot.get_chat_member(chat_id, user_id)
        except Exception as exc:
            logger.debug(
                f"MemberTagService.get_tag({chat_id},{user_id}) failed: {exc}"
            )
            return None

        tag = self._extract_tag(member)
        await self._cache_set(chat_id, user_id, tag)
        await self.record_observed_tag(chat_id, tag)
        return tag

    async def get_tags_bulk(
        self,
        bot: Bot,
        chat_id: int,
        user_ids: Iterable[int],
        update: Update | None = None,
    ) -> dict[int, str | None]:
        """Bulk variant of :meth:`get_tag` with bounded concurrency.

        :param bot: PTB ``Bot`` used on cache misses.
        :param chat_id: Telegram chat ID of the group.
        :param user_ids: iterable of Telegram user IDs to resolve.
        :param update: optional :class:`Update` to short-circuit lookups.
        :returns: mapping ``user_id -> tag or None`` for every input ID.
        """
        ids = list({int(uid) for uid in user_ids})
        if not ids:
            return {}

        result: dict[int, str | None] = {}
        pending: list[int] = []
        for uid in ids:
            cached = await self._cache_get(chat_id, uid)
            if cached == _NULL_TAG_SENTINEL:
                result[uid] = None
            elif isinstance(cached, str):
                result[uid] = cached
            else:
                pending.append(uid)

        if pending:
            semaphore = asyncio.Semaphore(10)

            async def _fetch(lookup_uid: int) -> tuple[int, str | None]:
                async with semaphore:
                    try:
                        if update is not None and update.message is not None:
                            member = await update.message.chat.get_member(lookup_uid)
                        else:
                            member = await bot.get_chat_member(chat_id, lookup_uid)
                        tag = self._extract_tag(member)
                    except Exception as exc:
                        logger.debug(
                            f"MemberTagService.get_tags_bulk lookup failed for {lookup_uid}: {exc}"
                        )
                        tag = None
                    return lookup_uid, tag

            fetched = await asyncio.gather(*(_fetch(uid) for uid in pending))
            for uid, tag in fetched:
                result[uid] = tag
                await self._cache_set(chat_id, uid, tag)
                if tag:
                    await self.record_observed_tag(chat_id, tag)

        return result
