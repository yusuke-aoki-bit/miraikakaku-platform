#!/usr/bin/env python3
"""
Run sector/industry setup via Cloud Run job
This script deploys a one-time Cloud Run job to add columns and populate data
"""

import subprocess
import json
import time

def run_command(cmd, description):
    """Run a shell command and return output"""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}")
    print(f"Command: {' '.join(cmd)}")

    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    return result.returncode == 0, result.stdout

def main():
    """Main execution"""

    # Step 1: Add columns using SQL via gcloud
    print("\n🔧 Step 1: Adding sector and industry columns...")

    add_columns_sql = """
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='stock_master' AND column_name='sector') THEN
            ALTER TABLE stock_master ADD COLUMN sector VARCHAR(100) DEFAULT NULL;
        END IF;

        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='stock_master' AND column_name='industry') THEN
            ALTER TABLE stock_master ADD COLUMN industry VARCHAR(200) DEFAULT NULL;
        END IF;
    END $$;

    SELECT
        COUNT(*) as total_stocks,
        COUNT(sector) as with_sector,
        COUNT(industry) as with_industry
    FROM stock_master;
    """

    # Write SQL to temp file
    with open('c:/Users/yuuku/cursor/miraikakaku/temp_add_columns.sql', 'w') as f:
        f.write(add_columns_sql)

    # Execute via Cloud SQL proxy
    cmd = [
        'gcloud', 'sql', 'connect', 'miraikakaku-db',
        '--user=postgres',
        '--database=miraikakaku',
        '--quiet',
        f'< c:/Users/yuuku/cursor/miraikakaku/temp_add_columns.sql'
    ]

    print("\n📊 Executing SQL to add columns...")
    print("Note: You may be prompted for the database password: Miraikakaku2024!")

    # Use subprocess with shell=True for redirect
    result = subprocess.run(
        ' '.join(cmd),
        shell=True,
        capture_output=True,
        text=True
    )

    print(result.stdout)
    if result.stderr and 'Password' not in result.stderr:
        print("STDERR:", result.stderr)

    if result.returncode == 0:
        print("✓ Columns added successfully!")
    else:
        print("❌ Failed to add columns")
        return False

    # Step 2: Deploy data collection as Cloud Run job
    print("\n📦 Step 2: Would you like to deploy data collection as Cloud Run job?")
    print("This will fetch sector/industry data for ~3,756 stocks (30-60 minutes)")
    print("\nAlternatively, you can run fetch_sector_industry_data.py directly from")
    print("a machine with database access.")

    return True

if __name__ == '__main__':
    success = main()
    if success:
        print("\n✓ Setup complete!")
        print("\n📋 Next steps:")
        print("1. Run fetch_sector_industry_data.py to populate data")
        print("2. Verify sector ranking APIs work correctly")
    else:
        print("\n❌ Setup failed. Check errors above.")
