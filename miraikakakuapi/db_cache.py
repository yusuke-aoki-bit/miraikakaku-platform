
import psycopg2
from psycopg2.extras import RealDictCursor
import json
import hashlib
from datetime import datetime, timedelta

class DatabaseCache:
    def __init__(self, db_config, cache_manager):
        self.db_config = db_config
        self.cache = cache_manager
        self.cache_ttl = {
            'stock_master': 86400,  # 24 hours
            'stock_prices': 300,    # 5 minutes
            'stock_predictions': 3600  # 1 hour
        }

    def cached_query(self, query, params=None, table_hint=None):
        """Execute cached database query"""
        cache_key = self.cache.cache_key(
            'db_query',
            query,
            params
        )

        # Try cache first
        cached = self.cache.redis_client.get(cache_key)
        if cached:
            return json.loads(cached)

        # Execute query
        conn = psycopg2.connect(**self.db_config)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()

        # Cache results
        ttl = self.cache_ttl.get(table_hint, 600)
        self.cache.redis_client.setex(
            cache_key,
            ttl,
            json.dumps(results, default=str)
        )

        return results
