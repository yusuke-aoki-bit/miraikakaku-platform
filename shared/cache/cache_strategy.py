"""
Comprehensive Caching Strategy for MiraiKakaku System
Implements multi-layer caching with Redis, in-memory cache, and database caching
"""
import asyncio
import json
import hashlib
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union, Callable
from dataclasses import dataclass, asdict
from functools import wraps
import redis
import redis.asyncio as aioredis
from cachetools import TTLCache, LRUCache
import pickle

from shared.utils.logger import get_logger

logger = get_logger("miraikakaku.cache")

@dataclass
class CacheMetrics:
    """Cache performance metrics"""
    hits: int = 0
    misses: int = 0
    sets: int = 0
    deletes: int = 0
    errors: int = 0

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return (self.hits / total) if total > 0 else 0.0

    @property
    def total_operations(self) -> int:
        return self.hits + self.misses + self.sets + self.deletes

class CacheLayer:
    """Base class for cache layers"""

    def __init__(self, name: str):
        self.name = name
        self.metrics = CacheMetrics()

    async def get(self, key: str) -> Optional[Any]:
        raise NotImplementedError

    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        raise NotImplementedError

    async def delete(self, key: str) -> bool:
        raise NotImplementedError

    async def clear(self) -> bool:
        raise NotImplementedError

class InMemoryCache(CacheLayer):
    """In-memory cache layer using cachetools"""

    def __init__(self, name: str = "memory", maxsize: int = 1000, ttl: int = 3600):
        super().__init__(name)
        self.cache = TTLCache(maxsize=maxsize, ttl=ttl)

    async def get(self, key: str) -> Optional[Any]:
        try:
            value = self.cache.get(key)
            if value is not None:
                self.metrics.hits += 1
                logger.debug(f"Memory cache HIT: {key}")
                return value
            else:
                self.metrics.misses += 1
                logger.debug(f"Memory cache MISS: {key}")
                return None
        except Exception as e:
            self.metrics.errors += 1
            logger.error(f"Memory cache GET error for {key}: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        try:
            self.cache[key] = value
            self.metrics.sets += 1
            logger.debug(f"Memory cache SET: {key}")
            return True
        except Exception as e:
            self.metrics.errors += 1
            logger.error(f"Memory cache SET error for {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        try:
            if key in self.cache:
                del self.cache[key]
                self.metrics.deletes += 1
                return True
            return False
        except Exception as e:
            self.metrics.errors += 1
            logger.error(f"Memory cache DELETE error for {key}: {e}")
            return False

    async def clear(self) -> bool:
        try:
            self.cache.clear()
            return True
        except Exception as e:
            logger.error(f"Memory cache CLEAR error: {e}")
            return False

class RedisCache(CacheLayer):
    """Redis cache layer"""

    def __init__(self, name: str = "redis", redis_url: str = "redis://localhost:6379"):
        super().__init__(name)
        self.redis_url = redis_url
        self.redis_client = None

    async def _get_client(self):
        """Get or create Redis client"""
        if self.redis_client is None:
            self.redis_client = aioredis.from_url(self.redis_url)
        return self.redis_client

    async def get(self, key: str) -> Optional[Any]:
        try:
            client = await self._get_client()
            value = await client.get(key)
            if value is not None:
                self.metrics.hits += 1
                logger.debug(f"Redis cache HIT: {key}")
                return pickle.loads(value)
            else:
                self.metrics.misses += 1
                logger.debug(f"Redis cache MISS: {key}")
                return None
        except Exception as e:
            self.metrics.errors += 1
            logger.error(f"Redis cache GET error for {key}: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        try:
            client = await self._get_client()
            serialized_value = pickle.dumps(value)
            await client.setex(key, ttl, serialized_value)
            self.metrics.sets += 1
            logger.debug(f"Redis cache SET: {key} (TTL: {ttl}s)")
            return True
        except Exception as e:
            self.metrics.errors += 1
            logger.error(f"Redis cache SET error for {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        try:
            client = await self._get_client()
            deleted = await client.delete(key)
            if deleted > 0:
                self.metrics.deletes += 1
                return True
            return False
        except Exception as e:
            self.metrics.errors += 1
            logger.error(f"Redis cache DELETE error for {key}: {e}")
            return False

    async def clear(self) -> bool:
        try:
            client = await self._get_client()
            await client.flushdb()
            return True
        except Exception as e:
            logger.error(f"Redis cache CLEAR error: {e}")
            return False

class MultiLayerCache:
    """Multi-layer cache with fallback strategy"""

    def __init__(self, layers: List[CacheLayer]):
        self.layers = layers
        self.metrics = CacheMetrics()

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache layers (L1 -> L2 -> L3...)"""
        for i, layer in enumerate(self.layers):
            value = await layer.get(key)
            if value is not None:
                # Populate higher-level caches
                for j in range(i):
                    await self.layers[j].set(key, value)

                self.metrics.hits += 1
                return value

        self.metrics.misses += 1
        return None

    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in all cache layers"""
        success = True
        for layer in self.layers:
            layer_success = await layer.set(key, value, ttl)
            success = success and layer_success

        if success:
            self.metrics.sets += 1
        else:
            self.metrics.errors += 1

        return success

    async def delete(self, key: str) -> bool:
        """Delete key from all cache layers"""
        success = True
        for layer in self.layers:
            layer_success = await layer.delete(key)
            success = success and layer_success

        if success:
            self.metrics.deletes += 1
        return success

    async def clear(self) -> bool:
        """Clear all cache layers"""
        success = True
        for layer in self.layers:
            layer_success = await layer.clear()
            success = success and layer_success
        return success

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get comprehensive metrics from all layers"""
        summary = {
            "overall": asdict(self.metrics),
            "layers": {}
        }

        for layer in self.layers:
            summary["layers"][layer.name] = asdict(layer.metrics)

        return summary

class CacheManager:
    """Main cache manager for the MiraiKakaku system"""

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        # Initialize cache layers
        self.memory_cache = InMemoryCache("L1_memory", maxsize=500, ttl=300)  # 5 minutes
        self.redis_cache = RedisCache("L2_redis", redis_url)

        # Multi-layer cache
        self.cache = MultiLayerCache([self.memory_cache, self.redis_cache])

        # Cache strategies by data type
        self.cache_strategies = {
            "stock_prices": {"ttl": 60, "key_prefix": "stock_price:"},      # 1 minute
            "stock_predictions": {"ttl": 300, "key_prefix": "prediction:"}, # 5 minutes
            "stock_master": {"ttl": 3600, "key_prefix": "master:"},        # 1 hour
            "user_sessions": {"ttl": 1800, "key_prefix": "session:"},      # 30 minutes
            "api_responses": {"ttl": 120, "key_prefix": "api:"},           # 2 minutes
        }

    def _generate_key(self, data_type: str, identifier: str, params: Dict[str, Any] = None) -> str:
        """Generate cache key with consistent naming"""
        strategy = self.cache_strategies.get(data_type, {"key_prefix": f"{data_type}:"})
        key = f"{strategy['key_prefix']}{identifier}"

        if params:
            # Create hash of parameters for consistent key generation
            param_str = json.dumps(params, sort_keys=True)
            param_hash = hashlib.md5(param_str.encode()).hexdigest()[:8]
            key = f"{key}:{param_hash}"

        return key

    async def get_stock_price(self, symbol: str, date: str = None) -> Optional[Dict[str, Any]]:
        """Get cached stock price data"""
        params = {"date": date} if date else None
        key = self._generate_key("stock_prices", symbol, params)
        return await self.cache.get(key)

    async def set_stock_price(self, symbol: str, data: Dict[str, Any], date: str = None) -> bool:
        """Cache stock price data"""
        params = {"date": date} if date else None
        key = self._generate_key("stock_prices", symbol, params)
        ttl = self.cache_strategies["stock_prices"]["ttl"]
        return await self.cache.set(key, data, ttl)

    async def get_stock_predictions(self, symbol: str, model: str = None) -> Optional[List[Dict[str, Any]]]:
        """Get cached stock predictions"""
        params = {"model": model} if model else None
        key = self._generate_key("stock_predictions", symbol, params)
        return await self.cache.get(key)

    async def set_stock_predictions(self, symbol: str, predictions: List[Dict[str, Any]], model: str = None) -> bool:
        """Cache stock predictions"""
        params = {"model": model} if model else None
        key = self._generate_key("stock_predictions", symbol, params)
        ttl = self.cache_strategies["stock_predictions"]["ttl"]
        return await self.cache.set(key, predictions, ttl)

    async def get_stock_master(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get cached stock master data"""
        key = self._generate_key("stock_master", symbol)
        return await self.cache.get(key)

    async def set_stock_master(self, symbol: str, data: Dict[str, Any]) -> bool:
        """Cache stock master data"""
        key = self._generate_key("stock_master", symbol)
        ttl = self.cache_strategies["stock_master"]["ttl"]
        return await self.cache.set(key, data, ttl)

    async def invalidate_stock_data(self, symbol: str) -> bool:
        """Invalidate all cached data for a stock symbol"""
        keys_to_delete = [
            self._generate_key("stock_prices", symbol),
            self._generate_key("stock_predictions", symbol),
            self._generate_key("stock_master", symbol)
        ]

        success = True
        for key in keys_to_delete:
            delete_success = await self.cache.delete(key)
            success = success and delete_success

        return success

    async def warm_cache(self, symbols: List[str], data_fetcher: Callable) -> int:
        """Warm cache with frequently accessed data"""
        warmed_count = 0

        for symbol in symbols:
            try:
                # Check if data is already cached
                cached_data = await self.get_stock_price(symbol)
                if cached_data is None:
                    # Fetch and cache data
                    fresh_data = await data_fetcher(symbol)
                    if fresh_data:
                        await self.set_stock_price(symbol, fresh_data)
                        warmed_count += 1
                        logger.debug(f"Warmed cache for {symbol}")

            except Exception as e:
                logger.error(f"Failed to warm cache for {symbol}: {e}")

        logger.info(f"Cache warming completed: {warmed_count}/{len(symbols)} symbols")
        return warmed_count

    async def get_cache_statistics(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        metrics_summary = self.cache.get_metrics_summary()

        # Add system information
        metrics_summary["system"] = {
            "memory_cache_size": len(self.memory_cache.cache),
            "memory_cache_maxsize": self.memory_cache.cache.maxsize,
            "strategies": self.cache_strategies,
            "timestamp": datetime.utcnow().isoformat()
        }

        return metrics_summary

# Decorators for easy caching
def cached_async(cache_manager: CacheManager, data_type: str, ttl: int = None):
    """Decorator for caching async function results"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            key_parts = [func.__name__] + [str(arg) for arg in args]
            if kwargs:
                key_parts.append(str(sorted(kwargs.items())))

            identifier = hashlib.md5(":".join(key_parts).encode()).hexdigest()
            cache_key = cache_manager._generate_key(data_type, identifier)

            # Try to get from cache
            cached_result = await cache_manager.cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache HIT for {func.__name__}")
                return cached_result

            # Execute function and cache result
            result = await func(*args, **kwargs)
            if result is not None:
                cache_ttl = ttl or cache_manager.cache_strategies.get(data_type, {}).get("ttl", 3600)
                await cache_manager.cache.set(cache_key, result, cache_ttl)
                logger.debug(f"Cached result for {func.__name__}")

            return result

        return wrapper
    return decorator

# Usage examples
if __name__ == "__main__":
    async def main():
        # Initialize cache manager
        cache_manager = CacheManager()

        # Example: Cache stock price data
        await cache_manager.set_stock_price("AAPL", {
            "symbol": "AAPL",
            "price": 150.25,
            "timestamp": datetime.utcnow().isoformat()
        })

        # Retrieve cached data
        cached_data = await cache_manager.get_stock_price("AAPL")
        print(f"Cached data: {cached_data}")

        # Cache predictions
        predictions = [
            {"date": "2024-01-01", "predicted_price": 155.0, "confidence": 0.85},
            {"date": "2024-01-02", "predicted_price": 157.0, "confidence": 0.82}
        ]
        await cache_manager.set_stock_predictions("AAPL", predictions, "LSTM_v1")

        # Get cache statistics
        stats = await cache_manager.get_cache_statistics()
        print(f"Cache statistics: {json.dumps(stats, indent=2)}")

        # Clean up
        await cache_manager.cache.clear()

    # asyncio.run(main())