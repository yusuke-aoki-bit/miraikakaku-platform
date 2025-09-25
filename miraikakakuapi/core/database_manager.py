"""
Permanent Database Manager - 恒久的データベース管理
Production-ready database connection management with Cloud SQL proxy and failover
"""
import asyncio
import logging
import os
import subprocess
import threading
import time
from contextlib import asynccontextmanager
from typing import Optional, Dict, Any, AsyncGenerator
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import ThreadedConnectionPool
import asyncpg
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from alembic import command
from alembic.config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Production-ready database manager with multiple connection methods and failover"""

    def __init__(self):
        self.config = self._load_config()
        self.connection_pool: Optional[ThreadedConnectionPool] = None
        self.asyncpg_pool: Optional[asyncpg.Pool] = None
        self.sqlalchemy_engine = None
        self.sqlalchemy_session = None
        self.cloud_sql_proxy_process: Optional[subprocess.Popen] = None
        self.proxy_running = False
        self.connection_health = {
            'direct': False,
            'proxy': False,
            'last_check': 0
        }

    def _load_config(self) -> Dict[str, Any]:
        """Load database configuration with environment variable support"""
        return {
            'host': os.getenv('DB_HOST', '34.84.191.187'),
            'port': int(os.getenv('DB_PORT', 5432)),
            'database': os.getenv('DB_NAME', 'miraikakaku_db'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'os.getenv('DB_PASSWORD', '')'),
            'proxy_host': '127.0.0.1',
            'proxy_port': 5433,
            'connection_instance': os.getenv('CLOUD_SQL_INSTANCE', 'miraikakaku-440004:asia-northeast1:miraikakaku-postgresql'),
            'max_connections': int(os.getenv('DB_MAX_CONNECTIONS', 20)),
            'connection_timeout': int(os.getenv('DB_TIMEOUT', 30))
        }

    async def start_cloud_sql_proxy(self) -> bool:
        """Start Cloud SQL proxy for secure database connections"""
        if self.proxy_running:
            return True

        try:
            logger.info("🔌 Starting Cloud SQL proxy...")

            # Check if cloud_sql_proxy exists
            proxy_path = './cloud_sql_proxy'
            if not os.path.exists(proxy_path):
                logger.warning("cloud_sql_proxy not found, downloading...")
                await self._download_cloud_sql_proxy()

            # Start proxy
            cmd = [
                proxy_path,
                f"--instances={self.config['connection_instance']}=tcp:{self.config['proxy_port']}",
                "--quiet"
            ]

            self.cloud_sql_proxy_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid if os.name != 'nt' else None
            )

            # Wait for proxy to start
            await asyncio.sleep(5)

            # Test proxy connection
            if await self._test_proxy_connection():
                self.proxy_running = True
                logger.info("✅ Cloud SQL proxy started successfully")
                return True
            else:
                logger.error("❌ Cloud SQL proxy failed to start")
                return False

        except Exception as e:
            logger.error(f"Failed to start Cloud SQL proxy: {e}")
            return False

    async def _download_cloud_sql_proxy(self):
        """Download Cloud SQL proxy if not present"""
        try:
            import urllib.request
            import stat

            logger.info("📥 Downloading Cloud SQL proxy...")
            url = "https://storage.googleapis.com/cloud-sql-connectors/cloud-sql-proxy/v2.12.0/cloud-sql-proxy.linux.amd64"
            urllib.request.urlretrieve(url, './cloud_sql_proxy')

            # Make executable
            os.chmod('./cloud_sql_proxy', stat.S_IRWXU | stat.S_IRGRP | stat.S_IROTH)
            logger.info("✅ Cloud SQL proxy downloaded")

        except Exception as e:
            logger.error(f"Failed to download Cloud SQL proxy: {e}")

    async def _test_proxy_connection(self) -> bool:
        """Test connection through Cloud SQL proxy"""
        try:
            conn = psycopg2.connect(
                host=self.config['proxy_host'],
                port=self.config['proxy_port'],
                database=self.config['database'],
                user=self.config['user'],
                password=self.config['password'],
                connect_timeout=10
            )
            conn.close()
            return True
        except Exception as e:
            logger.warning(f"Proxy connection test failed: {e}")
            return False

    async def _test_direct_connection(self) -> bool:
        """Test direct database connection"""
        try:
            conn = psycopg2.connect(
                host=self.config['host'],
                port=self.config['port'],
                database=self.config['database'],
                user=self.config['user'],
                password=self.config['password'],
                connect_timeout=10
            )
            conn.close()
            return True
        except Exception as e:
            logger.warning(f"Direct connection test failed: {e}")
            return False

    async def initialize(self) -> bool:
        """Initialize database connections with failover strategy"""
        logger.info("🚀 Initializing database manager...")

        # Test connection methods
        direct_ok = await self._test_direct_connection()
        proxy_ok = False

        if not direct_ok:
            proxy_ok = await self.start_cloud_sql_proxy()

        # Update connection health
        self.connection_health.update({
            'direct': direct_ok,
            'proxy': proxy_ok,
            'last_check': time.time()
        })

        if not direct_ok and not proxy_ok:
            logger.error("❌ No database connections available")
            return False

        # Initialize connection pools
        try:
            await self._setup_connection_pools()
            await self._run_migrations()
            logger.info("✅ Database manager initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize database manager: {e}")
            return False

    async def _setup_connection_pools(self):
        """Setup connection pools for both direct and proxy connections"""

        # Choose connection parameters
        if self.connection_health['direct']:
            host, port = self.config['host'], self.config['port']
            logger.info("Using direct database connection")
        else:
            host, port = self.config['proxy_host'], self.config['proxy_port']
            logger.info("Using Cloud SQL proxy connection")

        # PostgreSQL connection pool
        try:
            self.connection_pool = ThreadedConnectionPool(
                minconn=2,
                maxconn=self.config['max_connections'],
                host=host,
                port=port,
                database=self.config['database'],
                user=self.config['user'],
                password=self.config['password'],
                cursor_factory=RealDictCursor
            )
            logger.info("✅ PostgreSQL connection pool created")
        except Exception as e:
            logger.warning(f"Failed to create PostgreSQL pool: {e}")

        # AsyncPG pool
        try:
            dsn = f"postgresql://{self.config['user']}:{self.config['password']}@{host}:{port}/{self.config['database']}"
            self.asyncpg_pool = await asyncpg.create_pool(
                dsn,
                min_size=2,
                max_size=self.config['max_connections'],
                command_timeout=60
            )
            logger.info("✅ AsyncPG connection pool created")
        except Exception as e:
            logger.warning(f"Failed to create AsyncPG pool: {e}")

        # SQLAlchemy engine
        try:
            dsn = f"postgresql://{self.config['user']}:{self.config['password']}@{host}:{port}/{self.config['database']}"
            self.sqlalchemy_engine = create_engine(
                dsn,
                poolclass=QueuePool,
                pool_size=10,
                max_overflow=20,
                echo=False
            )
            self.sqlalchemy_session = sessionmaker(bind=self.sqlalchemy_engine)
            logger.info("✅ SQLAlchemy engine created")
        except Exception as e:
            logger.warning(f"Failed to create SQLAlchemy engine: {e}")

    async def _run_migrations(self):
        """Run Alembic migrations"""
        try:
            logger.info("🔄 Running database migrations...")

            # Configure Alembic
            alembic_cfg = Config()
            alembic_cfg.set_main_option("script_location", "alembic")

            # Use SQLAlchemy engine URL
            if self.sqlalchemy_engine:
                alembic_cfg.set_main_option("sqlalchemy.url", str(self.sqlalchemy_engine.url))
                command.upgrade(alembic_cfg, "head")
                logger.info("✅ Database migrations completed")
            else:
                logger.warning("⚠️ Cannot run migrations - no SQLAlchemy engine")
        except Exception as e:
            logger.error(f"Migration failed: {e}")

    @asynccontextmanager
    async def get_connection(self, connection_type: str = 'psycopg2') -> AsyncGenerator:
        """Get database connection with automatic cleanup"""
        connection = None
        try:
            if connection_type == 'psycopg2' and self.connection_pool:
                connection = self.connection_pool.getconn()
                yield connection

            elif connection_type == 'asyncpg' and self.asyncpg_pool:
                async with self.asyncpg_pool.acquire() as connection:
                    yield connection

            elif connection_type == 'sqlalchemy' and self.sqlalchemy_session:
                session = self.sqlalchemy_session()
                try:
                    yield session
                finally:
                    session.close()
            else:
                raise Exception(f"Connection type {connection_type} not available")

        except Exception as e:
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            if connection_type == 'psycopg2' and connection and self.connection_pool:
                self.connection_pool.putconn(connection)

    async def execute_query(self, query: str, params: tuple = None, fetch: str = 'all'):
        """Execute query with automatic failover"""
        try:
            async with self.get_connection('asyncpg') as conn:
                if fetch == 'all':
                    result = await conn.fetch(query, *(params or ()))
                elif fetch == 'one':
                    result = await conn.fetchrow(query, *(params or ()))
                else:  # execute
                    result = await conn.execute(query, *(params or ()))
                return result
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise

    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check"""
        health = {
            'status': 'healthy',
            'connections': self.connection_health.copy(),
            'pools': {},
            'timestamp': time.time()
        }

        # Check connection pools
        if self.connection_pool:
            try:
                conn = self.connection_pool.getconn()
                cur = conn.cursor()
                cur.execute("SELECT 1")
                cur.close()
                self.connection_pool.putconn(conn)
                health['pools']['psycopg2'] = 'healthy'
            except Exception as e:
                health['pools']['psycopg2'] = f'error: {e}'
                health['status'] = 'degraded'

        if self.asyncpg_pool:
            try:
                async with self.asyncpg_pool.acquire() as conn:
                    await conn.fetchval("SELECT 1")
                health['pools']['asyncpg'] = 'healthy'
            except Exception as e:
                health['pools']['asyncpg'] = f'error: {e}'
                health['status'] = 'degraded'

        return health

    async def close(self):
        """Clean shutdown of all connections"""
        logger.info("🔄 Shutting down database manager...")

        if self.connection_pool:
            self.connection_pool.closeall()

        if self.asyncpg_pool:
            await self.asyncpg_pool.close()

        if self.sqlalchemy_engine:
            self.sqlalchemy_engine.dispose()

        if self.cloud_sql_proxy_process:
            self.cloud_sql_proxy_process.terminate()
            self.cloud_sql_proxy_process.wait()

        logger.info("✅ Database manager shutdown complete")

# Global instance
db_manager = DatabaseManager()

# Convenience functions
async def get_db_connection(connection_type: str = 'psycopg2'):
    """Get database connection"""
    async with db_manager.get_connection(connection_type) as conn:
        yield conn

async def execute_query(query: str, params: tuple = None, fetch: str = 'all'):
    """Execute database query"""
    return await db_manager.execute_query(query, params, fetch)

async def get_db_health():
    """Get database health status"""
    return await db_manager.health_check()