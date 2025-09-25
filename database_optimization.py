#!/usr/bin/env python3
"""
Database Optimization Script for Miraikakaku
Create optimized indexes and analyze query performance
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import time

# Database configuration
DB_CONFIG = {
    'host': '34.173.9.214',
    'user': 'postgres',
    'password': 'os.getenv('DB_PASSWORD', '')',
    'database': 'miraikakaku'
}

def get_db_connection():
    """Get database connection"""
    return psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)

def analyze_current_indexes():
    """Analyze current index usage"""
    print("📊 Analyzing Current Indexes...")

    conn = get_db_connection()
    cur = conn.cursor()

    # Get current indexes
    cur.execute("""
        SELECT
            schemaname,
            tablename,
            indexname,
            indexdef
        FROM pg_indexes
        WHERE schemaname = 'public'
        ORDER BY tablename, indexname;
    """)

    indexes = cur.fetchall()
    print(f"🔍 Current Indexes ({len(indexes)} total):")

    current_table = None
    for idx in indexes:
        if idx['tablename'] != current_table:
            current_table = idx['tablename']
            print(f"\n   📋 Table: {current_table}")
        print(f"      • {idx['indexname']}")
    print()

    conn.close()
    return indexes

def analyze_query_performance():
    """Analyze slow queries and performance"""
    print("⚡ Analyzing Query Performance...")

    conn = get_db_connection()
    cur = conn.cursor()

    # Test common query patterns with timing
    test_queries = [
        {
            "name": "Stock price lookup by symbol",
            "query": """
                SELECT date, close_price, volume
                FROM stock_prices
                WHERE symbol = 'AAPL'
                ORDER BY date DESC
                LIMIT 30;
            """
        },
        {
            "name": "Recent predictions for symbol",
            "query": """
                SELECT prediction_date, predicted_price, confidence_score
                FROM stock_predictions
                WHERE symbol = 'AAPL'
                AND prediction_date >= CURRENT_DATE - INTERVAL '30 days'
                ORDER BY prediction_date DESC;
            """
        },
        {
            "name": "Historical predictions with actual prices",
            "query": """
                SELECT sp.prediction_date, sp.predicted_price, sph.close_price as actual_price
                FROM stock_predictions sp
                LEFT JOIN stock_prices sph ON sp.symbol = sph.symbol
                    AND sph.date = (sp.prediction_date + INTERVAL '1 day' * sp.prediction_days)
                WHERE sp.symbol = 'AAPL'
                AND sp.prediction_date >= CURRENT_DATE - INTERVAL '90 days'
                LIMIT 50;
            """
        },
        {
            "name": "Stock ranking by prediction change",
            "query": """
                SELECT sp.symbol, AVG(sp.predicted_price) as avg_predicted_price,
                       COUNT(*) as prediction_count
                FROM stock_predictions sp
                WHERE sp.prediction_date >= CURRENT_DATE - INTERVAL '7 days'
                GROUP BY sp.symbol
                HAVING COUNT(*) >= 1
                ORDER BY avg_predicted_price DESC
                LIMIT 10;
            """
        }
    ]

    for test in test_queries:
        print(f"   🔍 Testing: {test['name']}")

        # Run EXPLAIN ANALYZE
        try:
            start_time = time.time()
            cur.execute(f"EXPLAIN ANALYZE {test['query']}")
            explain_result = cur.fetchall()
            end_time = time.time()

            execution_time = (end_time - start_time) * 1000  # Convert to milliseconds
            print(f"      ⏱️  Execution time: {execution_time:.2f}ms")

            # Extract planning and execution time from EXPLAIN ANALYZE
            for row in explain_result:
                line = row[0]
                if "Planning Time:" in line:
                    planning_time = float(line.split("Planning Time: ")[1].split(" ms")[0])
                    print(f"      📋 Planning time: {planning_time:.2f}ms")
                elif "Execution Time:" in line:
                    exec_time = float(line.split("Execution Time: ")[1].split(" ms")[0])
                    print(f"      ⚡ Query execution: {exec_time:.2f}ms")
            print()

        except Exception as e:
            print(f"      ❌ Error: {e}")
            print()

    conn.close()

def create_optimized_indexes():
    """Create optimized indexes for better performance"""
    print("🚀 Creating Optimized Indexes...")

    conn = get_db_connection()
    cur = conn.cursor()

    # Define optimized indexes
    indexes_to_create = [
        {
            "name": "idx_stock_prices_symbol_date",
            "table": "stock_prices",
            "definition": "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_stock_prices_symbol_date ON stock_prices (symbol, date DESC)",
            "purpose": "Optimize stock price lookups by symbol with date ordering"
        },
        {
            "name": "idx_stock_prices_date_symbol",
            "table": "stock_prices",
            "definition": "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_stock_prices_date_symbol ON stock_prices (date DESC, symbol)",
            "purpose": "Optimize recent data queries across all symbols"
        },
        {
            "name": "idx_stock_predictions_symbol_pred_date",
            "table": "stock_predictions",
            "definition": "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_stock_predictions_symbol_pred_date ON stock_predictions (symbol, prediction_date DESC)",
            "purpose": "Optimize prediction lookups by symbol and date"
        },
        {
            "name": "idx_stock_predictions_pred_date_symbol",
            "table": "stock_predictions",
            "definition": "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_stock_predictions_pred_date_symbol ON stock_predictions (prediction_date DESC, symbol)",
            "purpose": "Optimize recent predictions across all symbols"
        },
        {
            "name": "idx_stock_predictions_target_date",
            "table": "stock_predictions",
            "definition": "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_stock_predictions_target_date ON stock_predictions ((prediction_date + INTERVAL '1 day' * prediction_days))",
            "purpose": "Optimize historical accuracy calculations"
        },
        {
            "name": "idx_stock_predictions_confidence",
            "table": "stock_predictions",
            "definition": "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_stock_predictions_confidence ON stock_predictions (confidence_score DESC) WHERE confidence_score IS NOT NULL",
            "purpose": "Optimize confidence-based rankings"
        },
        {
            "name": "idx_stock_master_symbol",
            "table": "stock_master",
            "definition": "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_stock_master_symbol ON stock_master (symbol) WHERE is_active = true",
            "purpose": "Optimize active symbol lookups"
        }
    ]

    for idx in indexes_to_create:
        print(f"   📝 Creating: {idx['name']}")
        print(f"      Purpose: {idx['purpose']}")

        try:
            start_time = time.time()
            cur.execute(idx['definition'])
            conn.commit()
            end_time = time.time()

            creation_time = end_time - start_time
            print(f"      ✅ Created in {creation_time:.2f}s")

        except Exception as e:
            print(f"      ⚠️  Skipped (already exists or error): {e}")
            conn.rollback()

        print()

    conn.close()

def analyze_table_statistics():
    """Update table statistics for better query planning"""
    print("📈 Updating Table Statistics...")

    conn = get_db_connection()
    cur = conn.cursor()

    tables_to_analyze = ['stock_prices', 'stock_predictions', 'stock_master']

    for table in tables_to_analyze:
        print(f"   📊 Analyzing table: {table}")

        try:
            start_time = time.time()
            cur.execute(f"ANALYZE {table}")
            conn.commit()
            end_time = time.time()

            analyze_time = end_time - start_time
            print(f"      ✅ Analyzed in {analyze_time:.2f}s")

        except Exception as e:
            print(f"      ❌ Error: {e}")
            conn.rollback()

    print()
    conn.close()

def check_index_usage():
    """Check index usage statistics"""
    print("📋 Checking Index Usage Statistics...")

    conn = get_db_connection()
    cur = conn.cursor()

    # Get index usage stats
    cur.execute("""
        SELECT
            schemaname,
            tablename,
            indexname,
            idx_tup_read,
            idx_tup_fetch,
            idx_scan
        FROM pg_stat_user_indexes
        WHERE schemaname = 'public'
        ORDER BY idx_scan DESC, idx_tup_read DESC;
    """)

    index_stats = cur.fetchall()

    print("   🏆 Most Used Indexes:")
    for i, stat in enumerate(index_stats[:10], 1):
        if stat['idx_scan'] > 0:
            print(f"      {i:2d}. {stat['indexname']:30s} - {stat['idx_scan']:,} scans, {stat['idx_tup_read']:,} tuples read")

    print()

    # Check for unused indexes
    unused_indexes = [stat for stat in index_stats if stat['idx_scan'] == 0]
    if unused_indexes:
        print("   ⚠️  Unused Indexes:")
        for stat in unused_indexes:
            print(f"      • {stat['indexname']} on {stat['tablename']}")
        print()

    conn.close()

def optimize_database_settings():
    """Check and suggest database optimization settings"""
    print("⚙️  Database Configuration Analysis...")

    conn = get_db_connection()
    cur = conn.cursor()

    # Get important configuration settings
    settings_to_check = [
        'shared_buffers',
        'effective_cache_size',
        'maintenance_work_mem',
        'checkpoint_completion_target',
        'wal_buffers',
        'default_statistics_target',
        'random_page_cost',
        'effective_io_concurrency'
    ]

    print("   Current PostgreSQL Settings:")
    for setting in settings_to_check:
        try:
            cur.execute(f"SHOW {setting}")
            result = cur.fetchone()
            print(f"      {setting:25s}: {result[0]}")
        except Exception as e:
            print(f"      {setting:25s}: Error - {e}")

    print()

    # Get database size information
    cur.execute("""
        SELECT
            pg_size_pretty(pg_database_size('miraikakaku')) as db_size,
            pg_size_pretty(pg_total_relation_size('stock_prices')) as stock_prices_size,
            pg_size_pretty(pg_total_relation_size('stock_predictions')) as stock_predictions_size
    """)

    size_info = cur.fetchone()
    print("   📏 Database Size Information:")
    print(f"      Total Database Size: {size_info['db_size']}")
    print(f"      Stock Prices Table: {size_info['stock_prices_size']}")
    print(f"      Stock Predictions Table: {size_info['stock_predictions_size']}")
    print()

    conn.close()

def main():
    """Main optimization function"""
    print("🔧 Miraikakaku Database Optimization")
    print("=" * 50)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    try:
        # Step 1: Analyze current state
        analyze_current_indexes()

        # Step 2: Test query performance before optimization
        print("🔍 BEFORE Optimization:")
        analyze_query_performance()

        # Step 3: Create optimized indexes
        create_optimized_indexes()

        # Step 4: Update table statistics
        analyze_table_statistics()

        # Step 5: Test query performance after optimization
        print("🚀 AFTER Optimization:")
        analyze_query_performance()

        # Step 6: Check index usage
        check_index_usage()

        # Step 7: Database configuration analysis
        optimize_database_settings()

        print("✅ Database optimization completed successfully!")
        print("\n💡 Recommendations:")
        print("   1. Monitor index usage over time")
        print("   2. Consider partitioning for very large tables")
        print("   3. Regular VACUUM and ANALYZE operations")
        print("   4. Monitor query performance with pg_stat_statements")
        print("   5. Consider connection pooling for high concurrency")

    except Exception as e:
        print(f"❌ Error during optimization: {e}")

if __name__ == "__main__":
    main()