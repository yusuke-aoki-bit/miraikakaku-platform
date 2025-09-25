import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

import asyncpg
from asyncpg import Connection, Pool
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from .config import settings

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Async database manager with connection pooling."""

    def __init__(self):
        self.pool: Optional[Pool] = None
        self.engine = None
        self.SessionLocal = None
        self._setup_sqlalchemy()

    def _setup_sqlalchemy(self):
        """Setup SQLAlchemy async engine and session factory."""
        # Convert psycopg2 URL to asyncpg URL
        async_url = settings.database_url.replace('postgresql://', 'postgresql+asyncpg://')

        self.engine = create_async_engine(
            async_url,
            pool_size=20,
            max_overflow=30,
            pool_pre_ping=True,
            pool_recycle=300,  # Recycle connections every 5 minutes
            echo=settings.debug,
        )

        self.SessionLocal = sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

    async def connect(self):
        """Initialize connection pool."""
        if self.pool is None:
            try:
                self.pool = await asyncpg.create_pool(
                    settings.database_url,
                    min_size=5,
                    max_size=20,
                    command_timeout=60,
                    server_settings={
                        'jit': 'off',  # Disable JIT for better connection performance
                    }
                )
                logger.info("Database connection pool created successfully")
            except Exception as e:
                logger.error(f"Failed to create database pool: {e}")
                raise

    async def disconnect(self):
        """Close connection pool."""
        if self.pool:
            await self.pool.close()
            self.pool = None
            logger.info("Database connection pool closed")

    @asynccontextmanager
    async def get_connection(self) -> AsyncGenerator[Connection, None]:
        """Get a database connection from the pool."""
        if not self.pool:
            await self.connect()

        async with self.pool.acquire() as connection:
            yield connection

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get an async SQLAlchemy session."""
        async with self.SessionLocal() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    async def execute_query(self, query: str, *args, fetch_one: bool = False, fetch_all: bool = True):
        """Execute a raw SQL query."""
        async with self.get_connection() as conn:
            try:
                if fetch_one:
                    return await conn.fetchrow(query, *args)
                elif fetch_all:
                    return await conn.fetch(query, *args)
                else:
                    return await conn.execute(query, *args)
            except Exception as e:
                logger.error(f"Database query error: {e}")
                raise

    async def health_check(self) -> bool:
        """Check database connectivity."""
        try:
            async with self.get_connection() as conn:
                result = await conn.fetchrow("SELECT 1 as healthy")
                return result['healthy'] == 1
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False


# Global database instance
db = DatabaseManager()


# Dependency for FastAPI
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency to get database session."""
    async with db.get_session() as session:
        yield session


async def get_db_connection() -> AsyncGenerator[Connection, None]:
    """FastAPI dependency to get raw database connection."""
    async with db.get_connection() as connection:
        yield connection