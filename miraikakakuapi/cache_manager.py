
import redis
import json
import hashlib
from functools import wraps
from datetime import timedelta

class CacheManager:
    def __init__(self, config_path='/mnt/c/Users/yuuku/cursor/miraikakaku/cache_config.json'):
        with open(config_path, 'r') as f:
            config = json.load(f)
        self.redis_client = redis.Redis(**config)
        self.default_ttl = 3600  # 1 hour

    def cache_key(self, prefix, *args, **kwargs):
        """Generate cache key from arguments"""
        key_data = f"{prefix}:{args}:{sorted(kwargs.items())}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def cache_response(self, ttl=None):
        """Decorator for caching API responses"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                cache_key = self.cache_key(func.__name__, *args, **kwargs)

                # Try to get from cache
                cached = self.redis_client.get(cache_key)
                if cached:
                    return json.loads(cached)

                # Execute function and cache result
                result = func(*args, **kwargs)
                self.redis_client.setex(
                    cache_key,
                    ttl or self.default_ttl,
                    json.dumps(result)
                )
                return result
            return wrapper
        return decorator

    def invalidate_pattern(self, pattern):
        """Invalidate cache entries matching pattern"""
        for key in self.redis_client.scan_iter(match=pattern):
            self.redis_client.delete(key)
