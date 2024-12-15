import redis.asyncio as redis


class RedisUtil:

    def __init__(self, endpoint: str):
        self.client = redis.from_url(url=str(endpoint))

    async def set_cache(self, key: str, value: str, ex: int | None = None, **kwargs):
        await self.client.set(key, value, ex=ex, **kwargs)

    async def get_cache(self, key: str) -> bytes | None:
        return await self.client.get(key)

    async def delete_cache(self, key: str) -> int:
        return await self.client.delete(key)
