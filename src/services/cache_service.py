"""Generic, reusable cache layer backed by Redis.

The rest of the codebase interacts with cache through :class:`CacheService`
without knowing (or caring) whether Redis is actually enabled. When
``settings.CACHE_ENABLED`` is ``False`` a :class:`NullCacheBackend` is used:
every read misses, every write is a no-op, so callers can keep the same code
path in both modes.

Typical usage::

    cache = get_cache()
    value = await cache.get_or_set(
        key=f"user:{tg_id}:username",
        ttl=settings.CACHE_USERNAME_TTL,
        loader=lambda: fetch_username_from_telegram(tg_id),
    )

Keys are automatically prefixed with ``settings.CACHE_KEY_PREFIX`` so cache
contents are isolated from other applications sharing the same Redis instance.
"""

from __future__ import annotations

import json
from collections.abc import Awaitable, Callable, Iterable
from threading import Lock
from typing import Any

import redis.asyncio as redis_asyncio

from utils.config import settings
from utils.logger_base import logger


class CacheBackend:
    """Abstract async cache backend."""

    async def get(self, key: str) -> str | None:
        raise NotImplementedError

    async def set(self, key: str, value: str, ttl: int | None) -> None:
        raise NotImplementedError

    async def delete(self, keys: Iterable[str]) -> None:
        raise NotImplementedError

    async def delete_pattern(self, pattern: str) -> None:
        raise NotImplementedError

    async def close(self) -> None:
        pass


class NullCacheBackend(CacheBackend):
    """No-op backend used when caching is disabled."""

    async def get(self, key: str) -> str | None:
        return None

    async def set(self, key: str, value: str, ttl: int | None) -> None:
        return None

    async def delete(self, keys: Iterable[str]) -> None:
        return None

    async def delete_pattern(self, pattern: str) -> None:
        return None


class RedisCacheBackend(CacheBackend):
    """Async Redis backend built on top of ``redis.asyncio``."""

    def __init__(self, url: str) -> None:
        """:param url: redis connection URL (e.g. ``redis://host:6379/1``)."""
        self._client: redis_asyncio.Redis = redis_asyncio.from_url(
            url, encoding="utf-8", decode_responses=True
        )

    async def get(self, key: str) -> str | None:
        try:
            return await self._client.get(key)
        except Exception as exc:
            logger.warning(f"Cache GET failed for {key}: {exc}")
            return None

    async def set(self, key: str, value: str, ttl: int | None) -> None:
        try:
            if ttl and ttl > 0:
                await self._client.set(key, value, ex=ttl)
            else:
                await self._client.set(key, value)
        except Exception as exc:
            logger.warning(f"Cache SET failed for {key}: {exc}")

    async def delete(self, keys: Iterable[str]) -> None:
        keys_list = list(keys)
        if not keys_list:
            return
        try:
            await self._client.delete(*keys_list)
        except Exception as exc:
            logger.warning(f"Cache DEL failed for {keys_list}: {exc}")

    async def delete_pattern(self, pattern: str) -> None:
        try:
            cursor = 0
            while True:
                cursor, keys = await self._client.scan(
                    cursor=cursor, match=pattern, count=500
                )
                if keys:
                    await self._client.delete(*keys)
                if cursor == 0:
                    break
        except Exception as exc:
            logger.warning(f"Cache SCAN/DEL failed for pattern {pattern}: {exc}")

    async def close(self) -> None:
        try:
            await self._client.aclose()
        except Exception as exc:
            logger.warning(f"Cache close failed: {exc}")


class CacheService:
    """High-level cache façade used by the rest of the codebase."""

    def __init__(self, backend: CacheBackend, prefix: str = "tetb") -> None:
        """:param backend: concrete :class:`CacheBackend` implementation.
        :param prefix: namespace prepended to every key.
        """
        self._backend = backend
        self._prefix = prefix.rstrip(":")

    def _k(self, key: str) -> str:
        """:returns: ``key`` prefixed with the namespace separator."""
        return f"{self._prefix}:{key}"

    async def get(self, key: str) -> Any | None:
        """:param key: cache key (without prefix).
        :returns: deserialized value, or ``None`` on miss / error.
        """
        raw = await self._backend.get(self._k(key))
        if raw is None:
            return None
        try:
            return json.loads(raw)
        except (TypeError, ValueError):
            return raw

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Store ``value`` under ``key`` with optional TTL (seconds).

        :param key: cache key (without prefix).
        :param value: any JSON-serializable value.
        :param ttl: time-to-live in seconds; ``None`` uses ``CACHE_DEFAULT_TTL``.
        """
        ttl = ttl if ttl is not None else settings.CACHE_DEFAULT_TTL
        try:
            payload = json.dumps(value, default=str)
        except (TypeError, ValueError) as exc:
            logger.warning(f"Cache SET serialization failed for {key}: {exc}")
            return
        await self._backend.set(self._k(key), payload, ttl)

    async def delete(self, *keys: str) -> None:
        """Invalidate one or more keys.

        :param keys: cache keys (without prefix).
        """
        await self._backend.delete([self._k(k) for k in keys])

    async def delete_pattern(self, pattern: str) -> None:
        """Invalidate every key matching ``pattern`` (uses Redis ``SCAN``).

        :param pattern: glob-style pattern (without prefix).
        """
        await self._backend.delete_pattern(self._k(pattern))

    async def get_or_set(
        self,
        key: str,
        ttl: int | None,
        loader: Callable[[], Awaitable[Any]],
    ) -> Any:
        """Return the cached value or compute, store, and return it.

        :param key: cache key (without prefix).
        :param ttl: time-to-live in seconds.
        :param loader: zero-arg async callable producing the fresh value on miss.
        :returns: the cached or freshly-loaded value.
        """
        cached = await self.get(key)
        if cached is not None:
            return cached
        value = await loader()
        if value is not None:
            await self.set(key, value, ttl)
        return value

    async def close(self) -> None:
        await self._backend.close()


_cache: CacheService | None = None
_cache_lock = Lock()


def get_cache() -> CacheService:
    """Return the process-wide :class:`CacheService` singleton.

    The backend is chosen at first call based on ``settings.CACHE_ENABLED``.
    Safe to call from sync and async contexts.

    :returns: a ready-to-use :class:`CacheService`.
    """
    global _cache
    if _cache is None:
        with _cache_lock:
            if _cache is None:
                backend: CacheBackend
                if settings.CACHE_ENABLED:
                    try:
                        backend = RedisCacheBackend(settings.REDIS_CACHE_URL)
                        logger.info(
                            f"Cache enabled (Redis at {settings.REDIS_CACHE_URL})"
                        )
                    except Exception as exc:
                        logger.warning(
                            f"Cache enabled but Redis init failed ({exc}); falling back to NullCacheBackend"
                        )
                        backend = NullCacheBackend()
                else:
                    backend = NullCacheBackend()
                    logger.info("Cache disabled (NullCacheBackend)")
                _cache = CacheService(backend, prefix=settings.CACHE_KEY_PREFIX)
    return _cache


async def close_cache() -> None:
    """Close the cache singleton's backend. Call on application shutdown."""
    global _cache
    if _cache is not None:
        await _cache.close()
        _cache = None
