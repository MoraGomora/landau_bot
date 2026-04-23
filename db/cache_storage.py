from datetime import datetime, timedelta

from typing import Any, Dict, Optional

try:
    from redis.asyncio import Redis
except ImportError:
    pass


class CacheStorage:

    def __init__(self) -> None:
        self._memory: Dict[str, tuple[Any, datetime]] = {}

    async def get(self, key: str) -> Optional[Any]:
        entry = self._memory.get(key, None)
        if not entry:
            return None
        
        value, expires_at = entry
        if expires_at and datetime.now() > expires_at:
            del self._memory[key]
            return None
        
        return value
    
    async def set(self, key: str, value: Any, ex: int = 86400):
        expires_at = datetime.now() + timedelta(seconds=ex) if ex else None

        self._memory[key] = (value, expires_at)

    async def delete(self, key: str) -> bool:
        return bool(self._memory.pop(key, None))
    
    async def exists(self, key: str) -> bool:
        return bool(self._memory.get(key))
    

class RedisCacheStorage(CacheStorage):

    def __init__(self, redis: Redis):
        super().__init__()
        self._redis = redis

    async def get(self, key: str) -> Optional[Any]:
        try:
            raw = await self._redis.get(key)
            if raw:
                self._memory[key] = raw

                return raw
        except Exception:
            await self._memory.get(key)

    async def set(self, key: str, value: Any):
        self._memory[key] = value
        try:
            await self._redis.set(key, value, ex=86400)
        except Exception:
            pass

    async def delete(self, key: str) -> bool:
        self._memory.pop(key, None)
        try:
            result = await self._redis.delete(key)

            return bool(result)
        except Exception:
            pass

        return True
    
    async def exists(self, key: str) -> bool:
        try:
            return await self._redis.exists(key)
        except Exception:
            return bool(self._memory.get(key, None))