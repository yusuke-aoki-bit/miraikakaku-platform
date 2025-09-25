
from psycopg2 import pool
import logging

class DatabasePool:
    def __init__(self, minconn=2, maxconn=20):
        self.pool = psycopg2.pool.ThreadedConnectionPool(
            minconn,
            maxconn,
            host='34.173.9.214',
            user='postgres',
            password='os.getenv('DB_PASSWORD', '')',
            database='miraikakaku'
        )

    def get_connection(self):
        """Get connection from pool"""
        return self.pool.getconn()

    def return_connection(self, conn):
        """Return connection to pool"""
        self.pool.putconn(conn)

    def close_all(self):
        """Close all connections"""
        self.pool.closeall()

# Global pool instance
db_pool = DatabasePool()
