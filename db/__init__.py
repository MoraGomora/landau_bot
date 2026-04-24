try:
    from redis.asyncio import Redis
except ImportError:
    pass

from structlog.typing import FilteringBoundLogger

from .cache_storage import CacheStorage, RedisCacheStorage
from .memory import SimpleInMemory


async def create_storage(logger: FilteringBoundLogger, redis_url: str | None = None) -> CacheStorage:
    if redis_url:
        await logger.adebug("Redis url is available. Creating Redis object...")

        redis = Redis.from_url(redis_url)
        if redis:
            await logger.adebug("Redis is created. Start pinging...")

        try:
            result = await redis.ping()
            if result:
                await logger.adebug("Redis return \"pong\". Returning the RedisCacheStorage object...")
                return RedisCacheStorage(redis)
            
        except Exception:
            pass
    
    await logger.adebug("Redis url is None. Returning the CacheStorage object...")

    return CacheStorage()


__all__ = [
    "CacheStorage",
    "RedisCacheStorage",
    "SimpleInMemory"
]