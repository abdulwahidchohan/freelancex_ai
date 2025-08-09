#!/usr/bin/env python3
"""
Simple response cache with Redis (if available) or in-memory fallback.
Keys are short-lived to avoid stale prompts.
"""

import json
import hashlib
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class InMemoryCache:
    def __init__(self):
        self._store: dict[str, tuple[str, int]] = {}

    def get(self, key: str) -> Optional[str]:
        value = self._store.get(key)
        if value is None:
            return None
        return value[0]

    def set(self, key: str, value: str, ttl_seconds: int = 3600):
        self._store[key] = (value, ttl_seconds)


class Cache:
    def __init__(self, redis_url: Optional[str] = None):
        self._memory = InMemoryCache()
        self._redis = None
        if redis_url:
            try:
                import redis
                self._redis = redis.Redis.from_url(redis_url, decode_responses=True)
                self._redis.ping()
                logger.info("Using Redis cache")
            except Exception as e:
                logger.warning(f"Redis unavailable, using in-memory cache: {e}")

    def make_key(self, *parts: str) -> str:
        raw = "::".join(parts)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def get(self, key: str) -> Optional[str]:
        if self._redis is not None:
            try:
                return self._redis.get(key)
            except Exception:
                pass
        return self._memory.get(key)

    def set(self, key: str, value: str, ttl_seconds: int = 3600):
        if self._redis is not None:
            try:
                self._redis.set(key, value, ex=ttl_seconds)
                return
            except Exception:
                pass
        self._memory.set(key, value, ttl_seconds)


