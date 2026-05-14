import time
import json
from typing import Optional, Any
from app.core.config import settings

try:
    import redis.asyncio as aioredis

    _redis: Optional[aioredis.Redis] = None

    def get_redis() -> Optional[aioredis.Redis]:
        global _redis
        if _redis is None and settings.REDIS_URL:
            _redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
        return _redis

except ImportError:
    get_redis = lambda: None  # type: ignore


class MemoryCache:
    def __init__(self, ttl: int = 300):
        self._store: dict[str, tuple[Any, float]] = {}
        self._ttl = ttl

    def get(self, key: str) -> Optional[Any]:
        data = self._store.get(key)
        if not data:
            return None
        value, expires = data
        if time.time() > expires:
            del self._store[key]
            return None
        return value

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        self._store[key] = (value, time.time() + (ttl or self._ttl))

    def delete(self, key: str) -> None:
        self._store.pop(key, None)

    def clear(self) -> None:
        self._store.clear()


memory_cache = MemoryCache()


class Cache:
    def __init__(self):
        self._redis = get_redis()
        self._memory = memory_cache

    async def get(self, key: str) -> Optional[Any]:
        if self._redis:
            try:
                data = await self._redis.get(key)
                if data:
                    return json.loads(data)
            except Exception:
                pass
        return self._memory.get(key)

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        if self._redis:
            try:
                await self._redis.set(key, json.dumps(value), ex=ttl)
            except Exception:
                pass
        self._memory.set(key, value, ttl)

    async def delete(self, key: str) -> None:
        if self._redis:
            try:
                await self._redis.delete(key)
            except Exception:
                pass
        self._memory.delete(key)

    async def clear(self) -> None:
        if self._redis:
            try:
                await self._redis.flushdb()
            except Exception:
                pass
        self._memory.clear()


cache = Cache()
