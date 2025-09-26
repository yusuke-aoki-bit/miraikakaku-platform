#!/usr/bin/env python3
"""
Database Performance Optimizer for Miraikakaku
Advanced database optimization and performance tuning
"""

import psycopg2
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s'
)
logger = logging.getLogger(__name__)

class DatabasePerformanceOptimizer:
    def __init__(self):
        self.db_config = {
            'host': '34.173.9.214',
            'user': 'postgres',
            'password': 'os.getenv('DB_PASSWORD', '')',
            'database': 'miraikakaku'
        }

    def get_connection(self):
        """Get database connection"""
        try:
            return psycopg2.connect(**self.db_config)
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            return None

    def run_vacuum_analyze(self) -> Dict[str, Any]:
        """Run VACUUM ANALYZE on main tables"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'operations': [],
            'status': 'success'
        }

        conn = self.get_connection()
        if not conn:
            results['status'] = 'failed'
            results['error'] = 'Failed to connect to database'
            return results

        try:
            conn.autocommit = True
            cursor = conn.cursor()

            tables = ['stock_prices', 'stock_predictions', 'stock_master']

            for table in tables:
                try:
                    logger.info(f"Running VACUUM ANALYZE on {table}...")
                    start_time = time.time()

                    cursor.execute(f"VACUUM ANALYZE {table};")

                    duration = time.time() - start_time
                    results['operations'].append({
                        'table': table,
                        'operation': 'VACUUM ANALYZE',
                        'duration_seconds': round(duration, 2),
                        'status': 'completed'
                    })

                    logger.info(f"✅ VACUUM ANALYZE {table} completed in {duration:.2f}s")

                except Exception as e:
                    logger.error(f"Error running VACUUM ANALYZE on {table}: {e}")
                    results['operations'].append({
                        'table': table,
                        'operation': 'VACUUM ANALYZE',
                        'status': 'failed',
                        'error': str(e)
                    })

        except Exception as e:
            logger.error(f"Error in VACUUM ANALYZE operations: {e}")
            results['status'] = 'failed'
            results['error'] = str(e)
        finally:
            if conn:
                conn.close()

        return results

    def analyze_table_statistics(self) -> Dict[str, Any]:
        """Analyze table statistics for optimization"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'table_stats': {},
            'status': 'success'
        }

        conn = self.get_connection()
        if not conn:
            results['status'] = 'failed'
            results['error'] = 'Failed to connect to database'
            return results

        try:
            cursor = conn.cursor()

            # Get table sizes and statistics
            query = """
            SELECT
                schemaname,
                tablename,
                attname,
                n_distinct,
                correlation,
                null_frac,
                avg_width
            FROM pg_stats
            WHERE tablename IN ('stock_prices', 'stock_predictions', 'stock_master')
            AND schemaname = 'public'
            ORDER BY tablename, attname;
            """

            cursor.execute(query)
            stats = cursor.fetchall()

            # Organize stats by table
            for row in stats:
                schema, table, column, n_distinct, correlation, null_frac, avg_width = row

                if table not in results['table_stats']:
                    results['table_stats'][table] = {
                        'columns': {},
                        'recommendations': []
                    }

                results['table_stats'][table]['columns'][column] = {
                    'n_distinct': n_distinct,
                    'correlation': correlation,
                    'null_fraction': null_frac,
                    'avg_width': avg_width
                }

            # Get table sizes
            size_query = """
            SELECT
                tablename,
                pg_size_pretty(pg_total_relation_size(tablename::regclass)) as size,
                pg_total_relation_size(tablename::regclass) as size_bytes
            FROM pg_tables
            WHERE schemaname = 'public'
            AND tablename IN ('stock_prices', 'stock_predictions', 'stock_master');
            """

            cursor.execute(size_query)
            sizes = cursor.fetchall()

            for table, size_pretty, size_bytes in sizes:
                if table in results['table_stats']:
                    results['table_stats'][table]['size'] = size_pretty
                    results['table_stats'][table]['size_bytes'] = size_bytes

        except Exception as e:
            logger.error(f"Error analyzing table statistics: {e}")
            results['status'] = 'failed'
            results['error'] = str(e)
        finally:
            if conn:
                conn.close()

        return results

    def check_index_usage(self) -> Dict[str, Any]:
        """Check index usage and efficiency"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'indexes': {},
            'recommendations': [],
            'status': 'success'
        }

        conn = self.get_connection()
        if not conn:
            results['status'] = 'failed'
            results['error'] = 'Failed to connect to database'
            return results

        try:
            cursor = conn.cursor()

            # Get index usage statistics
            query = """
            SELECT
                schemaname,
                tablename,
                indexname,
                idx_tup_read,
                idx_tup_fetch,
                idx_scan
            FROM pg_stat_user_indexes
            WHERE schemaname = 'public'
            AND tablename IN ('stock_prices', 'stock_predictions', 'stock_master')
            ORDER BY tablename, indexname;
            """

            cursor.execute(query)
            index_stats = cursor.fetchall()

            for schema, table, index, tup_read, tup_fetch, scans in index_stats:
                if table not in results['indexes']:
                    results['indexes'][table] = []

                efficiency = 0
                if tup_read and tup_read > 0:
                    efficiency = (tup_fetch / tup_read) * 100

                index_info = {
                    'index_name': index,
                    'tuples_read': tup_read,
                    'tuples_fetched': tup_fetch,
                    'scans': scans,
                    'efficiency_percent': round(efficiency, 2)
                }

                results['indexes'][table].append(index_info)

                # Add recommendations for unused indexes
                if scans == 0:
                    results['recommendations'].append(
                        f"Index {index} on {table} has never been used - consider dropping"
                    )
                elif efficiency < 50 and tup_read > 1000:
                    results['recommendations'].append(
                        f"Index {index} on {table} has low efficiency ({efficiency:.1f}%) - review usage"
                    )

        except Exception as e:
            logger.error(f"Error checking index usage: {e}")
            results['status'] = 'failed'
            results['error'] = str(e)
        finally:
            if conn:
                conn.close()

        return results

    def analyze_slow_queries(self) -> Dict[str, Any]:
        """Analyze slow queries and performance bottlenecks"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'slow_queries': [],
            'recommendations': [],
            'status': 'success'
        }

        conn = self.get_connection()
        if not conn:
            results['status'] = 'failed'
            results['error'] = 'Failed to connect to database'
            return results

        try:
            cursor = conn.cursor()

            # Test common query patterns and measure performance
            test_queries = [
                {
                    'name': 'Recent stock prices for single symbol',
                    'query': """
                    SELECT date, close_price, volume
                    FROM stock_prices
                    WHERE symbol = 'AAPL'
                    AND date >= CURRENT_DATE - INTERVAL '30 days'
                    ORDER BY date DESC;
                    """,
                    'expected_max_time': 0.5
                },
                {
                    'name': 'Price predictions for symbol',
                    'query': """
                    SELECT prediction_date, predicted_price, model_name
                    FROM stock_predictions
                    WHERE symbol = 'AAPL'
                    AND prediction_date >= CURRENT_DATE
                    ORDER BY prediction_date ASC;
                    """,
                    'expected_max_time': 0.3
                },
                {
                    'name': 'Symbol search by name',
                    'query': """
                    SELECT symbol, company_name, market
                    FROM stock_master
                    WHERE company_name ILIKE '%Apple%'
                    LIMIT 10;
                    """,
                    'expected_max_time': 0.2
                },
                {
                    'name': 'Daily volume analysis',
                    'query': """
                    SELECT symbol, AVG(volume) as avg_volume, COUNT(*) as days
                    FROM stock_prices
                    WHERE date >= CURRENT_DATE - INTERVAL '7 days'
                    GROUP BY symbol
                    ORDER BY avg_volume DESC
                    LIMIT 20;
                    """,
                    'expected_max_time': 2.0
                }
            ]

            for test in test_queries:
                try:
                    start_time = time.time()
                    cursor.execute(f"EXPLAIN ANALYZE {test['query']}")
                    explain_result = cursor.fetchall()
                    execution_time = time.time() - start_time

                    query_result = {
                        'name': test['name'],
                        'execution_time': round(execution_time, 3),
                        'expected_max_time': test['expected_max_time'],
                        'performance': 'good' if execution_time <= test['expected_max_time'] else 'slow',
                        'explain_plan': [str(row[0]) for row in explain_result]
                    }

                    results['slow_queries'].append(query_result)

                    if execution_time > test['expected_max_time']:
                        results['recommendations'].append(
                            f"Query '{test['name']}' is slow ({execution_time:.3f}s > {test['expected_max_time']}s) - review indexes and query plan"
                        )

                    logger.info(f"Query '{test['name']}': {execution_time:.3f}s")

                except Exception as e:
                    logger.error(f"Error testing query '{test['name']}': {e}")
                    results['slow_queries'].append({
                        'name': test['name'],
                        'error': str(e),
                        'performance': 'error'
                    })

        except Exception as e:
            logger.error(f"Error analyzing slow queries: {e}")
            results['status'] = 'failed'
            results['error'] = str(e)
        finally:
            if conn:
                conn.close()

        return results

    def optimize_database_settings(self) -> Dict[str, Any]:
        """Check and recommend database configuration optimizations"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'current_settings': {},
            'recommendations': [],
            'status': 'success'
        }

        conn = self.get_connection()
        if not conn:
            results['status'] = 'failed'
            results['error'] = 'Failed to connect to database'
            return results

        try:
            cursor = conn.cursor()

            # Check important PostgreSQL settings
            important_settings = [
                'shared_buffers',
                'effective_cache_size',
                'work_mem',
                'maintenance_work_mem',
                'random_page_cost',
                'seq_page_cost',
                'max_connections'
            ]

            for setting in important_settings:
                try:
                    cursor.execute(f"SHOW {setting};")
                    value = cursor.fetchone()[0]
                    results['current_settings'][setting] = value
                except Exception as e:
                    logger.warning(f"Could not get setting {setting}: {e}")

            # Add optimization recommendations
            results['recommendations'].extend([
                "Consider setting shared_buffers to 25% of available RAM",
                "Set effective_cache_size to 75% of available RAM",
                "Adjust work_mem based on query complexity and concurrent users",
                "Enable auto_vacuum for automatic maintenance",
                "Consider connection pooling for high-traffic applications"
            ])

        except Exception as e:
            logger.error(f"Error checking database settings: {e}")
            results['status'] = 'failed'
            results['error'] = str(e)
        finally:
            if conn:
                conn.close()

        return results

    def run_full_optimization(self) -> Dict[str, Any]:
        """Run complete database performance optimization"""
        logger.info("🔧 Starting full database performance optimization...")

        full_results = {
            'timestamp': datetime.now().isoformat(),
            'optimizations': {},
            'overall_status': 'success',
            'summary': {}
        }

        # Step 1: VACUUM ANALYZE
        logger.info("Step 1/4: Running VACUUM ANALYZE...")
        vacuum_results = self.run_vacuum_analyze()
        full_results['optimizations']['vacuum_analyze'] = vacuum_results

        # Step 2: Table statistics analysis
        logger.info("Step 2/4: Analyzing table statistics...")
        stats_results = self.analyze_table_statistics()
        full_results['optimizations']['table_statistics'] = stats_results

        # Step 3: Index usage analysis
        logger.info("Step 3/4: Analyzing index usage...")
        index_results = self.check_index_usage()
        full_results['optimizations']['index_analysis'] = index_results

        # Step 4: Query performance analysis
        logger.info("Step 4/4: Analyzing query performance...")
        query_results = self.analyze_slow_queries()
        full_results['optimizations']['query_performance'] = query_results

        # Generate summary
        total_recommendations = 0
        failed_operations = 0

        for category, result in full_results['optimizations'].items():
            if result.get('status') == 'failed':
                failed_operations += 1
                full_results['overall_status'] = 'partial_failure'

            if 'recommendations' in result:
                total_recommendations += len(result['recommendations'])

        full_results['summary'] = {
            'total_recommendations': total_recommendations,
            'failed_operations': failed_operations,
            'categories_analyzed': len(full_results['optimizations'])
        }

        if failed_operations > 0:
            logger.warning(f"⚠️  Optimization completed with {failed_operations} failed operations")
        else:
            logger.info("✅ Database optimization completed successfully!")

        return full_results

def main():
    """Main function for standalone execution"""
    import argparse

    parser = argparse.ArgumentParser(description='Database Performance Optimizer')
    parser.add_argument('--vacuum', action='store_true', help='Run VACUUM ANALYZE only')
    parser.add_argument('--stats', action='store_true', help='Analyze table statistics only')
    parser.add_argument('--indexes', action='store_true', help='Analyze index usage only')
    parser.add_argument('--queries', action='store_true', help='Analyze query performance only')
    parser.add_argument('--full', action='store_true', help='Run full optimization')

    args = parser.parse_args()

    optimizer = DatabasePerformanceOptimizer()

    if args.vacuum:
        result = optimizer.run_vacuum_analyze()
        print(json.dumps(result, indent=2))
    elif args.stats:
        result = optimizer.analyze_table_statistics()
        print(json.dumps(result, indent=2))
    elif args.indexes:
        result = optimizer.check_index_usage()
        print(json.dumps(result, indent=2))
    elif args.queries:
        result = optimizer.analyze_slow_queries()
        print(json.dumps(result, indent=2))
    elif args.full:
        result = optimizer.run_full_optimization()
        print(json.dumps(result, indent=2))
    else:
        # Default: run full optimization
        result = optimizer.run_full_optimization()
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()