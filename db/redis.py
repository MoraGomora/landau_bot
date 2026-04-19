from redis.asyncio import Redis
# from redis.exceptions import ConnectionError

from structlog.typing import FilteringBoundLogger


class RedisClient:

    def __init__(self, url: str, logger: FilteringBoundLogger):
        self.url = url
        self.logger = logger

        if url:
            self.conn = Redis.from_url(url)

    # async def init(self):
    #     try:
    #         if not self.conn:
    #             self.conn = Redis.from_url(self.url)

    #             return self
    #     except ConnectionError as e:
    #         await self.logger.aerror(
    #             "Failed to connect to Redis",
    #             error=str(e)
    #         )
    #         return None
        
    async def write(self, key: str, data: dict):
        if not self.url:
            await self.logger.aerror("Operation Denied. Redis Link is unavailable")
            return
        
        if not self.conn:
            raise RuntimeError("Connection is empty. Please, call 'await init()' function for solve this problem")
        
        return await self.conn.set(key, data)

    async def read(self, key: str):
        if not self.url:
            await self.logger.aerror("Operation Denied. Redis Link is unavailable")
            return
        
        if not self.conn:
            raise RuntimeError("Connection is empty. Please, call 'await init()' function for solve this problem")
        
        return await self.conn.get(key)

    # async def update(self, key: str, update_data: dict):
    #     pass

    async def delete(self, key: str):
        if not self.url:
            await self.logger.aerror("Operation Denied. Redis Link is unavailable")
            return
        
        if not self.conn:
            raise RuntimeError("Connection is empty. Please, call 'await init()' function for solve this problem")
        
        return await self.conn.delete(key)