#!/usr/bin/env python3
"""
Database Connection Pool Implementation
Provides efficient, thread-safe database connection management
"""
import os
import time
import threading
import psycopg2
from psycopg2 import pool, extras
from contextlib import contextmanager
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class PoolMetrics:
    """Connection pool metrics"""
    total_connections: int = 0
    active_connections: int = 0
    idle_connections: int = 0
    connections_created: int = 0
    connections_closed: int = 0
    pool_hits: int = 0
    pool_misses: int = 0
    connection_errors: int = 0
    average_connection_time: float = 0.0

class DatabaseConnectionPool:
    """Thread-safe database connection pool with comprehensive monitoring"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        """Singleton pattern for connection pool"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, '_initialized'):
            return

        self._initialized = True
        self.pool = None
        self.metrics = PoolMetrics()
        self._connection_times = []
        self._last_health_check = datetime.now()
        self._health_check_interval = timedelta(minutes=5)

        # Configuration from environment
        self.config = self._load_config()
        self._initialize_pool()

    def _load_config(self) -> Dict[str, Any]:
        """Load database configuration from environment"""
        # Load environment variables from .env file if available
        try:
            from dotenv import load_dotenv
            load_dotenv('/mnt/c/Users/yuuku/cursor/miraikakaku/miraikakakuapi/.env')
        except ImportError:
            logger.warning("python-dotenv not available, using system environment variables only")

        # Use Secret Manager for production credentials
        try:
            from config.secrets_manager import secrets_manager
            db_config = secrets_manager.get_database_config()
            config = {
                'host': db_config.get('host', os.getenv('POSTGRES_HOST', 'localhost')),
                'port': int(db_config.get('port', os.getenv('POSTGRES_PORT', 5432))),
                'database': db_config.get('database', os.getenv('POSTGRES_DB', 'miraikakaku')),
                'user': db_config.get('user', os.getenv('POSTGRES_USER', 'postgres')),
                'password': db_config.get('password', os.getenv('POSTGRES_PASSWORD', '')),
            }
        except ImportError:
            logger.warning("Secret manager not available, using environment variables")
            config = {
                'host': os.getenv('POSTGRES_HOST', 'localhost'),
                'port': int(os.getenv('POSTGRES_PORT', 5432)),
                'database': os.getenv('POSTGRES_DB', 'miraikakaku'),
                'user': os.getenv('POSTGRES_USER', 'postgres'),
                'password': os.getenv('POSTGRES_PASSWORD', ''),
            }

        config.update({
            'minconn': int(os.getenv('DB_POOL_MIN_SIZE', 2)),
            'maxconn': int(os.getenv('DB_POOL_SIZE', 20)),
            'maxconnattempts': int(os.getenv('DB_MAX_CONN_ATTEMPTS', 3)),
            'options': {
                'sslmode': os.getenv('DB_SSL_MODE', 'prefer'),
                'connect_timeout': int(os.getenv('DB_POOL_TIMEOUT', 30)),
                'application_name': 'miraikakaku_api'
            }
        })

        return config

    def _initialize_pool(self):
        """Initialize the connection pool"""
        try:
            # Create connection string
            dsn = f"postgresql://{self.config['user']}:{self.config['password']}@{self.config['host']}:{self.config['port']}/{self.config['database']}"

            # Add connection options
            options = []
            for key, value in self.config['options'].items():
                options.append(f"{key}={value}")

            if options:
                dsn += "?" + "&".join(options)

            # Create threaded connection pool
            self.pool = psycopg2.pool.ThreadedConnectionPool(
                minconn=self.config['minconn'],
                maxconn=self.config['maxconn'],
                dsn=dsn,
                cursor_factory=extras.RealDictCursor
            )

            # Update metrics
            self.metrics.total_connections = self.config['maxconn']
            self.metrics.idle_connections = self.config['minconn']

            logger.info(f"Database connection pool initialized: min={self.config['minconn']}, max={self.config['maxconn']}")

            # Perform initial health check
            self._health_check()

        except Exception as e:
            logger.error(f"Failed to initialize database connection pool: {e}")
            raise

    @contextmanager
    def get_connection(self):
        """Context manager for getting database connections"""
        connection = None
        start_time = time.time()

        try:
            # Get connection from pool
            connection = self.pool.getconn()

            if connection is None:
                self.metrics.pool_misses += 1
                self.metrics.connection_errors += 1
                raise Exception("Failed to get connection from pool")

            # Update metrics
            self.metrics.pool_hits += 1
            self.metrics.active_connections += 1

            # Record connection time
            connection_time = time.time() - start_time
            self._connection_times.append(connection_time)

            # Calculate moving average (last 100 connections)
            if len(self._connection_times) > 100:
                self._connection_times = self._connection_times[-100:]

            self.metrics.average_connection_time = sum(self._connection_times) / len(self._connection_times)

            # Test connection
            if connection.closed:
                logger.warning("Got closed connection from pool, creating new one")
                self.pool.putconn(connection, close=True)
                connection = self.pool.getconn()

            yield connection

        except Exception as e:
            logger.error(f"Database connection error: {e}")
            self.metrics.connection_errors += 1

            if connection and not connection.closed:
                # Mark connection as bad
                self.pool.putconn(connection, close=True)
                connection = None

            raise

        finally:
            if connection:
                try:
                    # Return connection to pool
                    self.pool.putconn(connection)
                    self.metrics.active_connections = max(0, self.metrics.active_connections - 1)

                    # Periodic health check
                    if datetime.now() - self._last_health_check > self._health_check_interval:
                        self._health_check()

                except Exception as e:
                    logger.error(f"Error returning connection to pool: {e}")

    def _health_check(self):
        """Perform health check on connection pool"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    cursor.fetchone()

            self._last_health_check = datetime.now()
            logger.debug("Database connection pool health check passed")

        except Exception as e:
            logger.error(f"Database connection pool health check failed: {e}")

    def get_pool_status(self) -> Dict[str, Any]:
        """Get comprehensive pool status"""
        try:
            # Try to get actual pool statistics
            if hasattr(self.pool, '_pool'):
                available_connections = len(self.pool._pool)
                self.metrics.idle_connections = available_connections
        except:
            pass

        return {
            'pool_type': 'ThreadedConnectionPool',
            'min_connections': self.config['minconn'],
            'max_connections': self.config['maxconn'],
            'active_connections': self.metrics.active_connections,
            'idle_connections': self.metrics.idle_connections,
            'total_connections': self.metrics.total_connections,
            'connections_created': self.metrics.connections_created,
            'connections_closed': self.metrics.connections_closed,
            'pool_hits': self.metrics.pool_hits,
            'pool_misses': self.metrics.pool_misses,
            'connection_errors': self.metrics.connection_errors,
            'average_connection_time_ms': round(self.metrics.average_connection_time * 1000, 2),
            'last_health_check': self._last_health_check.isoformat(),
            'pool_efficiency': self._calculate_pool_efficiency(),
            'configuration': self.config
        }

    def _calculate_pool_efficiency(self) -> float:
        """Calculate pool efficiency percentage"""
        total_requests = self.metrics.pool_hits + self.metrics.pool_misses
        if total_requests == 0:
            return 100.0

        return round((self.metrics.pool_hits / total_requests) * 100, 2)

    def close_all_connections(self):
        """Close all connections in the pool"""
        try:
            if self.pool:
                self.pool.closeall()
                logger.info("All database connections closed")
        except Exception as e:
            logger.error(f"Error closing database connections: {e}")

    def reset_metrics(self):
        """Reset connection pool metrics"""
        self.metrics = PoolMetrics()
        self._connection_times = []
        logger.info("Connection pool metrics reset")

# Global connection pool instance
_connection_pool = None

def get_connection_pool() -> DatabaseConnectionPool:
    """Get global connection pool instance"""
    global _connection_pool
    if _connection_pool is None:
        _connection_pool = DatabaseConnectionPool()
    return _connection_pool

@contextmanager
def get_database_connection():
    """Context manager for getting database connections from global pool"""
    pool = get_connection_pool()
    with pool.get_connection() as connection:
        yield connection

def execute_query(query: str, params: tuple = None) -> list:
    """Execute a SELECT query and return results"""
    with get_database_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()

def execute_update(query: str, params: tuple = None) -> int:
    """Execute an INSERT/UPDATE/DELETE query and return affected rows"""
    with get_database_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount

# Health check and monitoring functions
def get_pool_metrics() -> Dict[str, Any]:
    """Get connection pool metrics"""
    pool = get_connection_pool()
    return pool.get_pool_status()

def health_check() -> Dict[str, Any]:
    """Comprehensive database health check"""
    try:
        start_time = time.time()

        # Test basic connectivity
        with get_database_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT version(), current_database(), current_user")
                db_info = cursor.fetchone()

                # Test table access
                cursor.execute("""
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    LIMIT 5
                """)
                tables = cursor.fetchall()

        response_time = time.time() - start_time
        pool_status = get_pool_metrics()

        return {
            'status': 'healthy',
            'response_time_ms': round(response_time * 1000, 2),
            'database_info': {
                'version': db_info['version'],
                'database': db_info['current_database'],
                'user': db_info['current_user']
            },
            'tables_count': len(tables),
            'pool_status': pool_status,
            'timestamp': datetime.now().isoformat()
        }

    except Exception as e:
        return {
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }

if __name__ == "__main__":
    # Test the connection pool
    import time

    print("Testing database connection pool...")

    # Initialize pool
    pool = get_connection_pool()

    # Test multiple connections
    def test_connection(thread_id):
        for i in range(5):
            try:
                with get_database_connection() as conn:
                    with conn.cursor() as cursor:
                        cursor.execute("SELECT %s as thread_id, %s as iteration", (thread_id, i))
                        result = cursor.fetchone()
                        print(f"Thread {thread_id}, Iteration {i}: {result}")
                        time.sleep(0.1)
            except Exception as e:
                print(f"Thread {thread_id}, Iteration {i} failed: {e}")

    # Run concurrent tests
    import threading
    threads = []
    for i in range(3):
        thread = threading.Thread(target=test_connection, args=(i,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    # Print metrics
    metrics = get_pool_metrics()
    print(f"Pool metrics: {metrics}")

    # Health check
    health = health_check()
    print(f"Health check: {health}")