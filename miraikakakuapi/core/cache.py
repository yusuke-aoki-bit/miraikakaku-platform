import json
import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta

import redis.asyncio as redis
from .config import settings

logger = logging.getLogger(__name__)


class CacheManager:
    """Redis-based caching manager for stock data."""

    def __init__(self):
        self.redis: Optional[redis.Redis] = None

    async def connect(self):
        """Initialize Redis connection."""
        try:
            self.redis = redis.from_url(
                settings.redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
            # Test connection
            await self.redis.ping()
            logger.info("Redis cache connected successfully")
        except Exception as e:
            logger.warning(f"Redis connection failed, using memory cache: {e}")
            self.redis = None

    async def disconnect(self):
        """Close Redis connection."""
        if self.redis:
            await self.redis.close()
            self.redis = None

    def _make_key(self, prefix: str, identifier: str) -> str:
        """Create a cache key with prefix."""
        return f"miraikakaku:{prefix}:{identifier}"

    async def get(self, key: str) -> Optional[Any]:
        """Get cached value."""
        if not self.redis:
            return None

        try:
            cache_key = self._make_key("data", key)
            cached_data = await self.redis.get(cache_key)

            if cached_data:
                return json.loads(cached_data)
            return None

        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set cached value."""
        if not self.redis:
            return False

        try:
            cache_key = self._make_key("data", key)
            serialized_data = json.dumps(value, default=str)

            ttl = ttl or settings.cache_ttl
            await self.redis.setex(cache_key, ttl, serialized_data)
            return True

        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete cached value."""
        if not self.redis:
            return False

        try:
            cache_key = self._make_key("data", key)
            result = await self.redis.delete(cache_key)
            return result > 0

        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False

    async def get_or_set(self, key: str, fetch_function, ttl: int = None) -> Any:
        """Get cached value or set it using fetch function."""
        cached_value = await self.get(key)

        if cached_value is not None:
            return cached_value

        # Fetch fresh data
        try:
            fresh_data = await fetch_function()
            if fresh_data is not None:
                await self.set(key, fresh_data, ttl)
            return fresh_data

        except Exception as e:
            logger.error(f"Fetch function error for key {key}: {e}")
            return None

    # Stock-specific cache methods
    async def get_stock_data(self, symbol: str) -> Optional[Dict]:
        """Get cached stock data."""
        return await self.get(f"stock_data:{symbol}")

    async def set_stock_data(self, symbol: str, data: Dict, ttl: int = 300) -> bool:
        """Cache stock data for 5 minutes by default."""
        return await self.set(f"stock_data:{symbol}", data, ttl)

    async def get_stock_prices(self, symbol: str, days: int) -> Optional[List]:
        """Get cached stock price history."""
        return await self.get(f"stock_prices:{symbol}:{days}")

    async def set_stock_prices(self, symbol: str, days: int, data: List, ttl: int = 600) -> bool:
        """Cache stock prices for 10 minutes by default."""
        return await self.set(f"stock_prices:{symbol}:{days}", data, ttl)

    async def get_predictions(self, symbol: str, days: int) -> Optional[List]:
        """Get cached predictions."""
        return await self.get(f"predictions:{symbol}:{days}")

    async def set_predictions(self, symbol: str, days: int, data: List, ttl: int = 1800) -> bool:
        """Cache predictions for 30 minutes by default."""
        return await self.set(f"predictions:{symbol}:{days}", data, ttl)

    async def get_rankings(self, ranking_type: str) -> Optional[List]:
        """Get cached rankings."""
        return await self.get(f"rankings:{ranking_type}")

    async def set_rankings(self, ranking_type: str, data: List, ttl: int = 300) -> bool:
        """Cache rankings for 5 minutes by default."""
        return await self.set(f"rankings:{ranking_type}", data, ttl)

    async def invalidate_stock_cache(self, symbol: str):
        """Invalidate all cache entries for a specific stock."""
        pattern_keys = [
            f"stock_data:{symbol}",
            f"stock_prices:{symbol}:*",
            f"predictions:{symbol}:*",
            f"ai_factors:{symbol}"
        ]

        for pattern in pattern_keys:
            if "*" in pattern:
                # Handle pattern matching
                cache_key = self._make_key("data", pattern)
                try:
                    keys = await self.redis.keys(cache_key)
                    if keys:
                        await self.redis.delete(*keys)
                except Exception as e:
                    logger.error(f"Cache pattern delete error: {e}")
            else:
                await self.delete(pattern)

    async def health_check(self) -> bool:
        """Check cache connectivity."""
        if not self.redis:
            return False

        try:
            await self.redis.ping()
            return True
        except Exception as e:
            logger.error(f"Cache health check failed: {e}")
            return False


# Global cache instance
cache = CacheManager()