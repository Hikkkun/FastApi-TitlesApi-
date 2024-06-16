from app.core.config import settings
import redis
from typing import Optional

class RedisClient:
    def __init__(self, host: str = settings.REDIS_HOST, port: int = settings.REDIS_PORT, db: int = settings.REDIS_DB):
        self._client = redis.Redis(host=host, port=port, db=db)

    def get_client(self):
        return self._client

    def set(self, key: str, value: str, ex: Optional[int] = None):
        self._client.set(key, value, ex=ex)

    def get(self, key: str) -> Optional[str]:
        value = self._client.get(key)
        return value.decode("utf-8") if value else None

redis_client = RedisClient().get_client()