"""Redis connection manager for caching and ephemeral state."""
import redis.asyncio as aioredis

from backend.app.core.config import settings


class RedisManager:
    def __init__(self):
        self._redis: aioredis.Redis | None = None

    async def connect(self):
        self._redis = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )

    async def disconnect(self):
        if self._redis:
            await self._redis.close()

    @property
    def client(self) -> aioredis.Redis:
        if self._redis is None:
            raise RuntimeError("Redis not connected. Call connect() first.")
        return self._redis

    async def set_cached(self, key: str, value: str, ttl: int = 300):
        await self.client.set(key, value, ex=ttl)

    async def get_cached(self, key: str) -> str | None:
        return await self.client.get(key)

    async def publish(self, channel: str, message: str):
        await self.client.publish(channel, message)

    async def subscribe(self, *channels: str):
        pubsub = self.client.pubsub()
        await pubsub.subscribe(*channels)
        return pubsub


redis_manager = RedisManager()
