#!/usr/bin/env python3
"""
Apply watchlist schema to PostgreSQL database
"""

import os
import psycopg2
from psycopg2 import sql

def apply_watchlist_schema():
    """Apply watchlist database schema"""

    # Database connection parameters
    db_params = {
        'host': os.getenv('POSTGRES_HOST', 'localhost'),
        'port': os.getenv('POSTGRES_PORT', '5433'),
        'database': os.getenv('POSTGRES_DB', 'miraikakaku'),
        'user': os.getenv('POSTGRES_USER', 'postgres'),
        'password': os.getenv('POSTGRES_PASSWORD', 'Miraikakaku2024!')
    }

    print("=" * 60)
    print("Watchlist Schema Application")
    print("=" * 60)
    print(f"Database: {db_params['host']}:{db_params['port']}/{db_params['database']}")
    print()

    try:
        # Connect to database
        print("Connecting to database...")
        conn = psycopg2.connect(**db_params)
        conn.autocommit = False
        cursor = conn.cursor()

        # Read SQL schema file
        print("Reading schema file...")
        with open('create_watchlist_schema.sql', 'r', encoding='utf-8') as f:
            schema_sql = f.read()

        # Execute schema
        print("Applying schema...")
        cursor.execute(schema_sql)

        # Commit transaction
        conn.commit()
        print("✅ Schema applied successfully!")
        print()

        # Verify tables
        print("Verifying tables...")
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name = 'watchlist'
        """)

        tables = cursor.fetchall()
        if tables:
            print(f"✅ Found table: {tables[0][0]}")
        else:
            print("⚠️  Warning: watchlist table not found")

        # Verify indexes
        cursor.execute("""
            SELECT indexname
            FROM pg_indexes
            WHERE tablename = 'watchlist'
            ORDER BY indexname
        """)

        indexes = cursor.fetchall()
        print(f"✅ Created {len(indexes)} indexes:")
        for idx in indexes:
            print(f"   - {idx[0]}")

        # Verify views
        cursor.execute("""
            SELECT table_name
            FROM information_schema.views
            WHERE table_schema = 'public'
            AND table_name LIKE 'v_watchlist%'
            ORDER BY table_name
        """)

        views = cursor.fetchall()
        print(f"✅ Created {len(views)} views:")
        for view in views:
            print(f"   - {view[0]}")

        print()
        print("=" * 60)
        print("Watchlist schema application completed!")
        print("=" * 60)

    except psycopg2.Error as e:
        print(f"❌ Database error: {e}")
        if conn:
            conn.rollback()
        raise

    except FileNotFoundError:
        print("❌ Error: create_watchlist_schema.sql not found")
        raise

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        if conn:
            conn.rollback()
        raise

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            print("Database connection closed.")

if __name__ == '__main__':
    apply_watchlist_schema()
