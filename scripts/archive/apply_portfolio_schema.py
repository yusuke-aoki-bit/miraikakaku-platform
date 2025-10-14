#!/usr/bin/env python3
"""
Apply Portfolio Management Schema to Database
Phase 5-1: Portfolio Management
"""

import psycopg2
import os

def apply_schema():
    """Apply portfolio management schema to the database"""

    # Database connection parameters
    db_params = {
        'host': os.getenv('POSTGRES_HOST', 'localhost'),
        'port': int(os.getenv('POSTGRES_PORT', '5433')),
        'user': os.getenv('POSTGRES_USER', 'postgres'),
        'password': os.getenv('POSTGRES_PASSWORD', 'Miraikakaku2024!'),
        'database': os.getenv('POSTGRES_DB', 'miraikakaku')
    }

    print(f"Connecting to database: {db_params['host']}:{db_params['port']}/{db_params['database']}")

    try:
        conn = psycopg2.connect(**db_params)
        conn.autocommit = True
        cur = conn.cursor()

        # Read SQL file
        schema_path = os.path.join(os.path.dirname(__file__), 'apply_portfolio_schema.sql')
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()

        print("Applying portfolio schema...")

        # Execute the schema SQL
        cur.execute(schema_sql)

        print("✅ Portfolio schema applied successfully!")

        # Verify the schema
        cur.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name LIKE 'portfolio%'
            ORDER BY table_name
        """)
        tables = cur.fetchall()

        print(f"\n📋 Portfolio tables created: {len(tables)}")
        for table in tables:
            print(f"  - {table[0]}")

        # Check views
        cur.execute("""
            SELECT table_name
            FROM information_schema.views
            WHERE table_schema = 'public'
            AND table_name LIKE '%portfolio%'
            ORDER BY table_name
        """)
        views = cur.fetchall()

        print(f"\n👁️  Portfolio views created: {len(views)}")
        for view in views:
            print(f"  - {view[0]}")

        # Check functions
        cur.execute("""
            SELECT routine_name
            FROM information_schema.routines
            WHERE routine_schema = 'public'
            AND routine_name LIKE '%portfolio%'
            ORDER BY routine_name
        """)
        functions = cur.fetchall()

        print(f"\n⚙️  Portfolio functions created: {len(functions)}")
        for func in functions:
            print(f"  - {func[0]}")

        cur.close()
        conn.close()

        return True

    except Exception as e:
        print(f"❌ Error applying schema: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = apply_schema()
    exit(0 if success else 1)
