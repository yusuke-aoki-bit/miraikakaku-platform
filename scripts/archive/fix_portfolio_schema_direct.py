"""
Direct Database Schema Fix for Portfolio Management
Connects directly to Cloud SQL to investigate and fix schema issues
"""

import psycopg2
from psycopg2 import sql
import os

# Database connection parameters
DB_CONFIG = {
    'host': os.environ.get('POSTGRES_HOST', '34.71.74.137'),
    'port': int(os.environ.get('POSTGRES_PORT', '5432')),
    'dbname': os.environ.get('POSTGRES_DB', 'miraikakaku'),
    'user': os.environ.get('POSTGRES_USER', 'postgres'),
    'password': os.environ.get('POSTGRES_PASSWORD', 'Miraikakaku2024!')
}

def check_table_ownership():
    """Check if portfolio_holdings table exists and who owns it"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    print("=== Checking portfolio_holdings table ownership ===")
    cur.execute("""
        SELECT tablename, tableowner
        FROM pg_tables
        WHERE tablename = 'portfolio_holdings'
    """)
    result = cur.fetchall()

    if result:
        print(f"Table exists! Owner: {result[0][1]}")

        # Check columns
        cur.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'portfolio_holdings'
            ORDER BY ordinal_position
        """)
        columns = cur.fetchall()
        print(f"\nColumns ({len(columns)}):")
        for col in columns:
            print(f"  - {col[0]}: {col[1]}")
    else:
        print("Table does not exist")

    cur.close()
    conn.close()
    return result

def drop_and_recreate():
    """Drop existing portfolio objects and recreate them"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    try:
        print("\n=== Step 1: Dropping existing objects ===")

        # Drop views first (they depend on tables)
        drop_commands = [
            "DROP VIEW IF EXISTS v_portfolio_current_value CASCADE",
            "DROP VIEW IF EXISTS v_portfolio_summary CASCADE",
            "DROP VIEW IF EXISTS v_portfolio_sector_allocation CASCADE",
            "DROP FUNCTION IF EXISTS calculate_portfolio_value(VARCHAR) CASCADE",
            "DROP FUNCTION IF EXISTS update_timestamp() CASCADE",
            "DROP TABLE IF EXISTS portfolio_snapshots CASCADE",
            "DROP TABLE IF EXISTS portfolio_holdings CASCADE"
        ]

        for cmd in drop_commands:
            print(f"  Executing: {cmd}")
            cur.execute(cmd)

        conn.commit()
        print("  ✓ All existing objects dropped")

        print("\n=== Step 2: Reading schema file ===")
        schema_path = os.path.join(os.path.dirname(__file__), 'schema_portfolio.sql')
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()

        print(f"  ✓ Read {len(schema_sql)} characters from schema_portfolio.sql")

        print("\n=== Step 3: Applying complete schema ===")
        cur.execute(schema_sql)
        conn.commit()
        print("  ✓ Schema applied successfully")

        print("\n=== Step 4: Verifying creation ===")

        # Check tables
        cur.execute("""
            SELECT tablename FROM pg_tables
            WHERE tablename LIKE 'portfolio%'
            ORDER BY tablename
        """)
        tables = [row[0] for row in cur.fetchall()]
        print(f"  Tables created: {tables}")

        # Check views
        cur.execute("""
            SELECT table_name FROM information_schema.views
            WHERE table_schema = 'public' AND table_name LIKE '%portfolio%'
            ORDER BY table_name
        """)
        views = [row[0] for row in cur.fetchall()]
        print(f"  Views created: {views}")

        # Check functions
        cur.execute("""
            SELECT routine_name FROM information_schema.routines
            WHERE routine_schema = 'public' AND routine_name LIKE '%portfolio%'
            ORDER BY routine_name
        """)
        functions = [row[0] for row in cur.fetchall()]
        print(f"  Functions created: {functions}")

        print("\n✓ Portfolio schema successfully applied!")

        cur.close()
        conn.close()
        return True

    except Exception as e:
        conn.rollback()
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        cur.close()
        conn.close()
        return False

if __name__ == "__main__":
    print("Portfolio Schema Direct Fix Tool")
    print("=" * 50)

    # First check current state
    check_table_ownership()

    # Ask for confirmation
    print("\n" + "=" * 50)
    response = input("\nDrop and recreate portfolio schema? (yes/no): ")

    if response.lower() == 'yes':
        success = drop_and_recreate()
        if success:
            print("\n" + "=" * 50)
            print("SUCCESS! Portfolio schema is ready to use.")
            print("=" * 50)
    else:
        print("Operation cancelled.")
