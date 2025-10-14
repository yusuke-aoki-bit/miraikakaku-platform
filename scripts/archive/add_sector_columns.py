#!/usr/bin/env python3
"""
Add sector and industry columns to stock_master table
"""

import psycopg2
import os

def add_columns():
    """Add sector and industry columns to stock_master table"""

    # Database connection
    db_config = {
        'host': os.getenv('POSTGRES_HOST', '34.172.10.4'),
        'port': int(os.getenv('POSTGRES_PORT', '5432')),
        'database': os.getenv('POSTGRES_DB', 'miraikakaku'),
        'user': os.getenv('POSTGRES_USER', 'postgres'),
        'password': os.getenv('POSTGRES_PASSWORD', 'Miraikakaku2024!')
    }

    print(f"Connecting to database at {db_config['host']}:{db_config['port']}...")

    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        # Check if columns already exist
        cursor.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'stock_master'
            AND column_name IN ('sector', 'industry')
        """)
        existing_columns = [row[0] for row in cursor.fetchall()]

        print(f"Existing columns: {existing_columns}")

        # Add sector column if not exists
        if 'sector' not in existing_columns:
            print("Adding 'sector' column...")
            cursor.execute("""
                ALTER TABLE stock_master
                ADD COLUMN sector VARCHAR(100) DEFAULT NULL
            """)
            print("✓ Added 'sector' column")
        else:
            print("✓ 'sector' column already exists")

        # Add industry column if not exists
        if 'industry' not in existing_columns:
            print("Adding 'industry' column...")
            cursor.execute("""
                ALTER TABLE stock_master
                ADD COLUMN industry VARCHAR(200) DEFAULT NULL
            """)
            print("✓ Added 'industry' column")
        else:
            print("✓ 'industry' column already exists")

        # Commit changes
        conn.commit()

        # Verify the columns
        cursor.execute("""
            SELECT column_name, data_type, character_maximum_length
            FROM information_schema.columns
            WHERE table_name = 'stock_master'
            AND column_name IN ('sector', 'industry')
            ORDER BY column_name
        """)

        print("\nColumn verification:")
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]}({row[2]})")

        # Check current NULL count
        cursor.execute("""
            SELECT
                COUNT(*) as total,
                COUNT(sector) as with_sector,
                COUNT(industry) as with_industry
            FROM stock_master
        """)
        stats = cursor.fetchone()
        print(f"\nCurrent data status:")
        print(f"  Total stocks: {stats[0]}")
        print(f"  With sector: {stats[1]} ({stats[1]/stats[0]*100:.1f}%)")
        print(f"  With industry: {stats[2]} ({stats[2]/stats[0]*100:.1f}%)")

        cursor.close()
        conn.close()

        print("\n✓ Schema update complete!")
        return True

    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == '__main__':
    add_columns()
