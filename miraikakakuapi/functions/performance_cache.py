"""
高性能キャッシュシステム
API応答時間を大幅短縮するメモリ＋永続化キャッシュ
"""

import os
import time
import json
import hashlib
import pickle
import logging
from datetime import datetime, timedelta
from typing import Any, Optional, Dict, Union, Callable
from functools import wraps
import threading
from pathlib import Path

logger = logging.getLogger(__name__)

class PerformanceCache:
    """高性能メモリ＋ファイルキャッシュシステム"""

    def __init__(self, max_memory_items: int = 1000, cache_dir: str = "/tmp/miraikakaku_cache"):
        self.memory_cache: Dict[str, Dict] = {}
        self.access_times: Dict[str, float] = {}
        self.max_memory_items = max_memory_items
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.lock = threading.RLock()

        # Cache statistics
        self.stats = {
            'hits': 0,
            'misses': 0,
            'memory_hits': 0,
            'disk_hits': 0,
            'invalidations': 0,
            'size_evictions': 0
        }

        logger.info(f"🚀 PerformanceCache initialized: max_items={max_memory_items}, cache_dir={cache_dir}")

    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """キーを生成（引数からハッシュ化）"""
        key_data = f"{prefix}:{args}:{sorted(kwargs.items())}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def _cleanup_memory_cache(self):
        """メモリキャッシュのサイズ制限実行"""
        if len(self.memory_cache) <= self.max_memory_items:
            return

        # LRU eviction - アクセス時間の古い順に削除
        sorted_keys = sorted(self.access_times.items(), key=lambda x: x[1])
        keys_to_remove = [key for key, _ in sorted_keys[:-self.max_memory_items]]

        for key in keys_to_remove:
            self.memory_cache.pop(key, None)
            self.access_times.pop(key, None)
            self.stats['size_evictions'] += 1

        logger.debug(f"🧹 Evicted {len(keys_to_remove)} items from memory cache")

    def _get_file_path(self, key: str) -> Path:
        """キャッシュファイルパスを生成"""
        return self.cache_dir / f"{key}.cache"

    def _save_to_disk(self, key: str, data: Dict):
        """ディスクにキャッシュ保存"""
        try:
            file_path = self._get_file_path(key)
            with file_path.open('wb') as f:
                pickle.dump(data, f)
            logger.debug(f"💾 Saved {key} to disk cache")
        except Exception as e:
            logger.warning(f"⚠️ Failed to save {key} to disk: {e}")

    def _load_from_disk(self, key: str) -> Optional[Dict]:
        """ディスクからキャッシュ読込"""
        try:
            file_path = self._get_file_path(key)
            if not file_path.exists():
                return None

            with file_path.open('rb') as f:
                data = pickle.load(f)

            # 有効期限チェック
            if data.get('expires_at', 0) < time.time():
                file_path.unlink(missing_ok=True)
                return None

            logger.debug(f"💾 Loaded {key} from disk cache")
            return data

        except Exception as e:
            logger.warning(f"⚠️ Failed to load {key} from disk: {e}")
            return None

    def get(self, key: str) -> Optional[Any]:
        """キャッシュから値を取得"""
        with self.lock:
            current_time = time.time()

            # 1. メモリキャッシュから確認
            if key in self.memory_cache:
                cache_entry = self.memory_cache[key]

                # 有効期限チェック
                if cache_entry.get('expires_at', 0) > current_time:
                    self.access_times[key] = current_time
                    self.stats['hits'] += 1
                    self.stats['memory_hits'] += 1
                    logger.debug(f"⚡ Memory cache HIT: {key}")
                    return cache_entry['data']
                else:
                    # 期限切れのためメモリから削除
                    del self.memory_cache[key]
                    self.access_times.pop(key, None)
                    self.stats['invalidations'] += 1

            # 2. ディスクキャッシュから確認
            disk_data = self._load_from_disk(key)
            if disk_data:
                # メモリキャッシュに復元
                self.memory_cache[key] = disk_data
                self.access_times[key] = current_time
                self._cleanup_memory_cache()

                self.stats['hits'] += 1
                self.stats['disk_hits'] += 1
                logger.debug(f"💾 Disk cache HIT: {key}")
                return disk_data['data']

            # キャッシュミス
            self.stats['misses'] += 1
            logger.debug(f"❌ Cache MISS: {key}")
            return None

    def set(self, key: str, value: Any, ttl_seconds: int = 3600):
        """キャッシュに値を設定"""
        with self.lock:
            current_time = time.time()
            expires_at = current_time + ttl_seconds

            cache_entry = {
                'data': value,
                'created_at': current_time,
                'expires_at': expires_at,
                'ttl': ttl_seconds
            }

            # メモリキャッシュに保存
            self.memory_cache[key] = cache_entry
            self.access_times[key] = current_time

            # サイズ制限実行
            self._cleanup_memory_cache()

            # ディスクにも非同期保存（重要なデータの場合）
            if ttl_seconds > 3600:  # 1時間以上のTTLの場合のみ
                threading.Thread(target=self._save_to_disk, args=(key, cache_entry)).start()

            logger.debug(f"✅ Cached {key} (TTL: {ttl_seconds}s)")

    def delete(self, key: str):
        """キャッシュから削除"""
        with self.lock:
            # メモリから削除
            self.memory_cache.pop(key, None)
            self.access_times.pop(key, None)

            # ディスクから削除
            try:
                self._get_file_path(key).unlink(missing_ok=True)
            except Exception as e:
                logger.warning(f"⚠️ Failed to delete {key} from disk: {e}")

            logger.debug(f"🗑️ Deleted {key} from cache")

    def clear(self):
        """全キャッシュをクリア"""
        with self.lock:
            self.memory_cache.clear()
            self.access_times.clear()

            # ディスクキャッシュもクリア
            try:
                for cache_file in self.cache_dir.glob("*.cache"):
                    cache_file.unlink()
            except Exception as e:
                logger.warning(f"⚠️ Failed to clear disk cache: {e}")

            logger.info("🧹 Cleared all caches")

    def get_stats(self) -> Dict[str, Any]:
        """キャッシュ統計を取得"""
        total_requests = self.stats['hits'] + self.stats['misses']
        hit_rate = (self.stats['hits'] / max(1, total_requests)) * 100

        return {
            **self.stats,
            'hit_rate_percent': round(hit_rate, 2),
            'memory_cache_size': len(self.memory_cache),
            'disk_cache_files': len(list(self.cache_dir.glob("*.cache"))) if self.cache_dir.exists() else 0
        }

# グローバルキャッシュインスタンス
performance_cache = PerformanceCache()

def cached(prefix: str = "", ttl_seconds: int = 3600):
    """デコレーター：関数結果をキャッシュ"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # キャッシュキー生成
            cache_key = performance_cache._generate_key(prefix or func.__name__, *args, **kwargs)

            # キャッシュから確認
            cached_result = performance_cache.get(cache_key)
            if cached_result is not None:
                return cached_result

            # 関数実行
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time

            # 結果をキャッシュに保存（実行時間が長い場合はTTL延長）
            dynamic_ttl = ttl_seconds
            if execution_time > 2.0:  # 2秒以上の処理は長めにキャッシュ
                dynamic_ttl = max(ttl_seconds, int(execution_time * 1800))  # 30分×実行時間

            performance_cache.set(cache_key, result, dynamic_ttl)

            logger.debug(f"⚡ Cached {func.__name__} result (exec: {execution_time:.3f}s, TTL: {dynamic_ttl}s)")
            return result

        return wrapper
    return decorator

# 便利な関数
def cache_stock_data(symbol: str, data: Any, ttl_hours: int = 24):
    """株価データをキャッシュ"""
    key = f"stock_data:{symbol}:{datetime.now().strftime('%Y-%m-%d')}"
    performance_cache.set(key, data, ttl_hours * 3600)

def get_cached_stock_data(symbol: str) -> Optional[Any]:
    """キャッシュされた株価データを取得"""
    key = f"stock_data:{symbol}:{datetime.now().strftime('%Y-%m-%d')}"
    return performance_cache.get(key)

def cache_prediction_data(symbol: str, prediction: Any, ttl_hours: int = 6):
    """予測データをキャッシュ"""
    key = f"prediction:{symbol}:{datetime.now().strftime('%Y-%m-%d-%H')}"
    performance_cache.set(key, prediction, ttl_hours * 3600)

def get_cached_prediction(symbol: str) -> Optional[Any]:
    """キャッシュされた予測データを取得"""
    key = f"prediction:{symbol}:{datetime.now().strftime('%Y-%m-%d-%H')}"
    return performance_cache.get(key)

def warm_up_cache():
    """キャッシュのウォームアップ（アプリケーション起動時に実行）"""
    logger.info("🔥 Starting cache warm-up...")

    # よく使われる銘柄のダミーデータでウォームアップ
    popular_symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA']

    for symbol in popular_symbols:
        # ダミーキー作成（実際のデータ読込時に上書きされる）
        key = f"warmup:{symbol}"
        performance_cache.set(key, {'warmed_up': True}, 60)  # 1分で期限切れ

    logger.info(f"✅ Cache warm-up complete for {len(popular_symbols)} symbols")

# キャッシュ統計をログ出力
def log_cache_stats():
    """キャッシュ統計をログに出力"""
    stats = performance_cache.get_stats()
    logger.info(f"📊 Cache Stats: {stats['hit_rate_percent']:.1f}% hit rate, "
                f"{stats['memory_cache_size']} memory items, "
                f"{stats['disk_cache_files']} disk files")