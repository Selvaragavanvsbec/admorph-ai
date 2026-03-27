import json

import redis

from backend.config import settings


class CacheService:
    def __init__(self) -> None:
        try:
            self.client = redis.from_url(settings.redis_url, decode_responses=True)
            self.client.ping()
        except Exception:
            self.client = None

    def get(self, key: str):
        if not self.client:
            return None
        value = self.client.get(key)
        return json.loads(value) if value else None

    def set(self, key: str, value, ttl: int = 300) -> None:
        if not self.client:
            return
        self.client.setex(key, ttl, json.dumps(value))


cache_service = CacheService()
