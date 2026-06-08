"""Common base class for every service.

Mirrors :class:`repositories.base_repository.BaseRepository`: provides shared
session handling, audit logging through :class:`LogService`, and cache helpers
backed by :class:`CacheService`. Concrete services should call ``self._log``,
``self._cached``, and ``self._invalidate`` instead of touching the session or
cache backend directly.
"""

from __future__ import annotations

import uuid
from collections.abc import Awaitable, Callable
from typing import Any

from sqlmodel import Session

from services.cache_service import CacheService, get_cache
from services.log_service import LogService
from utils.logger_base import logger


class BaseService:
    """Shared building blocks for every service in ``src/services``."""

    def __init__(
        self,
        session: Session,
        log_service: LogService | None = None,
        cache: CacheService | None = None,
    ) -> None:
        """:param session: active SQLModel session bound to the request/command.
        :param log_service: optional :class:`LogService` injected for audit logging.
            When omitted, ``_log`` falls back to :meth:`LogService.add_log`.
        :param cache: optional :class:`CacheService`. When omitted the process
            singleton is used.
        """
        self.session = session
        self.log_service = log_service
        self.cache = cache or get_cache()
        self.logger = logger

    def _log(
        self,
        user_id: int,
        group_id: uuid.UUID | int | str | None,
        action: str,
        description: str | None = None,
    ) -> None:
        """Write an audit log entry through :class:`LogService`.

        :param user_id: telegram user id of the actor.
        :param group_id: internal UUID or telegram id of the affected group.
        :param action: short, uppercase action identifier (e.g. ``CREATE_LIST``).
        :param description: optional human-readable description.
        """
        try:
            if self.log_service is not None:
                LogService.add_log(
                    self.session, user_id, group_id, action, description
                )
            else:
                LogService.add_log(
                    self.session, user_id, group_id, action, description
                )
        except Exception as exc:
            self.logger.warning(f"Failed to write audit log {action}: {exc}")

    async def _cached(
        self,
        key: str,
        ttl: int | None,
        loader: Callable[[], Awaitable[Any]],
    ) -> Any:
        """Return ``key`` from cache, otherwise call ``loader`` and store it.

        :param key: cache key (without prefix).
        :param ttl: time-to-live in seconds.
        :param loader: zero-arg async callable returning the fresh value.
        :returns: the cached or freshly-loaded value.
        """
        return await self.cache.get_or_set(key, ttl, loader)

    async def _invalidate(self, *keys: str) -> None:
        """Drop the given cache keys.

        :param keys: keys to delete (without prefix).
        """
        if keys:
            await self.cache.delete(*keys)

    async def _invalidate_pattern(self, pattern: str) -> None:
        """Drop every cache key matching ``pattern``.

        :param pattern: glob-style pattern (without prefix).
        """
        await self.cache.delete_pattern(pattern)
