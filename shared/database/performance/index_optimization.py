"""
Database Index Optimization System
Analyzes query patterns and optimizes database indexes for better performance
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import sqlalchemy as sa
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import psycopg2
from psycopg2.extras import RealDictCursor

from shared.utils.logger import get_logger

logger = get_logger("miraikakaku.database.optimization")

@dataclass
class QueryAnalysis:
    """Query analysis result"""
    query_text: str
    execution_count: int
    avg_duration_ms: float
    total_duration_ms: float
    table_scans: int
    index_scans: int
    suggested_indexes: List[str]

@dataclass
class IndexRecommendation:
    """Index recommendation"""
    table: str
    columns: List[str]
    index_type: str  # 'btree', 'hash', 'gin', 'gist'
    estimated_improvement: str
    query_patterns: List[str]
    priority: str  # 'high', 'medium', 'low'

class DatabaseIndexOptimizer:
    """Main database index optimization class"""

    def __init__(self, database_url: str):
        self.engine = create_engine(database_url)
        self.Session = sessionmaker(bind=self.engine)

    def analyze_query_performance(self, hours: int = 24) -> List[QueryAnalysis]:
        """Analyze slow queries and their performance patterns"""
        with self.engine.connect() as conn:
            # Get slow queries from PostgreSQL stats
            slow_queries_sql = """
            SELECT
                query,
                calls,
                mean_exec_time,
                total_exec_time,
                rows,
                100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
            FROM pg_stat_statements
            WHERE mean_exec_time > 100  -- queries slower than 100ms
            ORDER BY total_exec_time DESC
            LIMIT 20;
            """

            try:
                result = conn.execute(text(slow_queries_sql))
                analyses = []

                for row in result:
                    analysis = QueryAnalysis(
                        query_text=row.query,
                        execution_count=row.calls,
                        avg_duration_ms=float(row.mean_exec_time),
                        total_duration_ms=float(row.total_exec_time),
                        table_scans=0,  # Would need to analyze EXPLAIN output
                        index_scans=0,  # Would need to analyze EXPLAIN output
                        suggested_indexes=self.suggest_indexes_for_query(row.query)
                    )
                    analyses.append(analysis)

                return analyses

            except Exception as e:
                logger.error(f"Failed to analyze query performance: {e}")
                return []

    def suggest_indexes_for_query(self, query: str) -> List[str]:
        """Analyze query and suggest appropriate indexes"""
        suggestions = []
        query_lower = query.lower()

        # Analyze WHERE clauses
        if 'where' in query_lower:
            # Extract potential WHERE conditions
            # This is a simplified analysis - in practice, you'd use a SQL parser
            if 'symbol =' in query_lower:
                suggestions.append("CREATE INDEX idx_symbol ON stock_prices(symbol);")

            if 'date >' in query_lower or 'date <' in query_lower:
                suggestions.append("CREATE INDEX idx_date ON stock_prices(date);")

            if 'created_at >' in query_lower:
                suggestions.append("CREATE INDEX idx_created_at ON stock_predictions(created_at);")

        # Analyze ORDER BY clauses
        if 'order by' in query_lower:
            if 'date' in query_lower:
                suggestions.append("CREATE INDEX idx_date_desc ON stock_prices(date DESC);")

        # Analyze JOIN patterns
        if 'join' in query_lower:
            if 'stock_master' in query_lower and 'symbol' in query_lower:
                suggestions.append("CREATE INDEX idx_stock_master_symbol ON stock_master(symbol);")

        return suggestions

    def analyze_existing_indexes(self) -> Dict[str, List[Dict[str, Any]]]:
        """Analyze existing indexes and their usage"""
        with self.engine.connect() as conn:
            # Get index usage statistics
            index_usage_sql = """
            SELECT
                schemaname,
                tablename,
                indexname,
                idx_tup_read,
                idx_tup_fetch,
                idx_scan,
                reltuples as table_rows
            FROM pg_stat_user_indexes
            JOIN pg_class ON pg_class.oid = indexrelid
            ORDER BY idx_scan DESC;
            """

            try:
                result = conn.execute(text(index_usage_sql))
                indexes_by_table = {}

                for row in result:
                    table = row.tablename
                    if table not in indexes_by_table:
                        indexes_by_table[table] = []

                    index_info = {
                        'name': row.indexname,
                        'scans': row.idx_scan or 0,
                        'tuples_read': row.idx_tup_read or 0,
                        'tuples_fetched': row.idx_tup_fetch or 0,
                        'table_rows': row.table_rows or 0,
                        'usage_ratio': (row.idx_scan or 0) / max((row.table_rows or 1), 1)
                    }
                    indexes_by_table[table].append(index_info)

                return indexes_by_table

            except Exception as e:
                logger.error(f"Failed to analyze existing indexes: {e}")
                return {}

    def generate_index_recommendations(self) -> List[IndexRecommendation]:
        """Generate comprehensive index recommendations"""
        recommendations = []

        # Standard recommendations based on common query patterns
        stock_prices_recommendations = [
            IndexRecommendation(
                table="stock_prices",
                columns=["symbol", "date"],
                index_type="btree",
                estimated_improvement="30-50% for time-series queries",
                query_patterns=["SELECT * FROM stock_prices WHERE symbol = ? AND date > ?"],
                priority="high"
            ),
            IndexRecommendation(
                table="stock_prices",
                columns=["date"],
                index_type="btree",
                estimated_improvement="20-40% for date range queries",
                query_patterns=["SELECT * FROM stock_prices WHERE date BETWEEN ? AND ?"],
                priority="medium"
            ),
            IndexRecommendation(
                table="stock_prices",
                columns=["volume"],
                index_type="btree",
                estimated_improvement="15-25% for volume-based queries",
                query_patterns=["SELECT * FROM stock_prices WHERE volume > ?"],
                priority="low"
            )
        ]

        stock_predictions_recommendations = [
            IndexRecommendation(
                table="stock_predictions",
                columns=["symbol", "prediction_date"],
                index_type="btree",
                estimated_improvement="40-60% for prediction queries",
                query_patterns=["SELECT * FROM stock_predictions WHERE symbol = ? AND prediction_date > ?"],
                priority="high"
            ),
            IndexRecommendation(
                table="stock_predictions",
                columns=["model_name"],
                index_type="btree",
                estimated_improvement="25-35% for model-specific queries",
                query_patterns=["SELECT * FROM stock_predictions WHERE model_name = ?"],
                priority="medium"
            ),
            IndexRecommendation(
                table="stock_predictions",
                columns=["confidence_score"],
                index_type="btree",
                estimated_improvement="20-30% for confidence filtering",
                query_patterns=["SELECT * FROM stock_predictions WHERE confidence_score > ?"],
                priority="low"
            )
        ]

        stock_master_recommendations = [
            IndexRecommendation(
                table="stock_master",
                columns=["sector"],
                index_type="btree",
                estimated_improvement="30-45% for sector-based queries",
                query_patterns=["SELECT * FROM stock_master WHERE sector = ?"],
                priority="medium"
            ),
            IndexRecommendation(
                table="stock_master",
                columns=["market_cap"],
                index_type="btree",
                estimated_improvement="25-40% for market cap filtering",
                query_patterns=["SELECT * FROM stock_master WHERE market_cap > ?"],
                priority="low"
            )
        ]

        recommendations.extend(stock_prices_recommendations)
        recommendations.extend(stock_predictions_recommendations)
        recommendations.extend(stock_master_recommendations)

        return recommendations

    def create_optimized_indexes(self, dry_run: bool = True) -> List[str]:
        """Create recommended indexes"""
        recommendations = self.generate_index_recommendations()
        created_indexes = []

        high_priority_recs = [r for r in recommendations if r.priority == "high"]

        for rec in high_priority_recs:
            index_name = f"idx_{rec.table}_{'_'.join(rec.columns).replace(' ', '_')}"
            columns_str = ', '.join(rec.columns)

            create_index_sql = f"""
            CREATE INDEX CONCURRENTLY IF NOT EXISTS {index_name}
            ON {rec.table} USING {rec.index_type} ({columns_str});
            """

            if dry_run:
                logger.info(f"Would create index: {create_index_sql}")
                created_indexes.append(create_index_sql)
            else:
                try:
                    with self.engine.connect() as conn:
                        conn.execute(text(create_index_sql))
                        logger.info(f"Created index: {index_name}")
                        created_indexes.append(index_name)
                except Exception as e:
                    logger.error(f"Failed to create index {index_name}: {e}")

        return created_indexes

    def analyze_table_statistics(self) -> Dict[str, Dict[str, Any]]:
        """Analyze table statistics for optimization insights"""
        with self.engine.connect() as conn:
            table_stats_sql = """
            SELECT
                schemaname,
                tablename,
                n_tup_ins,
                n_tup_upd,
                n_tup_del,
                n_live_tup,
                n_dead_tup,
                last_vacuum,
                last_autovacuum,
                last_analyze,
                last_autoanalyze
            FROM pg_stat_user_tables
            WHERE schemaname = 'public';
            """

            try:
                result = conn.execute(text(table_stats_sql))
                stats = {}

                for row in result:
                    table_name = row.tablename
                    stats[table_name] = {
                        'inserts': row.n_tup_ins or 0,
                        'updates': row.n_tup_upd or 0,
                        'deletes': row.n_tup_del or 0,
                        'live_tuples': row.n_live_tup or 0,
                        'dead_tuples': row.n_dead_tup or 0,
                        'dead_tuple_ratio': (row.n_dead_tup or 0) / max((row.n_live_tup or 1), 1),
                        'last_vacuum': row.last_vacuum,
                        'last_analyze': row.last_analyze,
                        'needs_vacuum': (row.n_dead_tup or 0) > (row.n_live_tup or 0) * 0.1,  # 10% threshold
                    }

                return stats

            except Exception as e:
                logger.error(f"Failed to analyze table statistics: {e}")
                return {}

    def generate_maintenance_recommendations(self) -> List[str]:
        """Generate database maintenance recommendations"""
        recommendations = []
        table_stats = self.analyze_table_statistics()

        for table, stats in table_stats.items():
            # Check if vacuum is needed
            if stats['needs_vacuum']:
                recommendations.append(f"VACUUM ANALYZE {table}; -- Dead tuple ratio: {stats['dead_tuple_ratio']:.2f}")

            # Check if analyze is needed (older than 1 day)
            if stats['last_analyze']:
                days_since_analyze = (datetime.now() - stats['last_analyze']).days
                if days_since_analyze > 1:
                    recommendations.append(f"ANALYZE {table}; -- Last analyzed {days_since_analyze} days ago")

        return recommendations

    def benchmark_query_performance(self, query: str, iterations: int = 5) -> Dict[str, float]:
        """Benchmark query performance before and after optimizations"""
        execution_times = []

        with self.engine.connect() as conn:
            for _ in range(iterations):
                start_time = datetime.now()
                try:
                    conn.execute(text(query))
                    end_time = datetime.now()
                    execution_times.append((end_time - start_time).total_seconds() * 1000)
                except Exception as e:
                    logger.error(f"Query execution failed: {e}")
                    continue

        if execution_times:
            return {
                'min_ms': min(execution_times),
                'max_ms': max(execution_times),
                'avg_ms': sum(execution_times) / len(execution_times),
                'iterations': len(execution_times)
            }
        else:
            return {'error': 'No successful executions'}


class DatabasePerformanceMonitor:
    """Monitor database performance over time"""

    def __init__(self, database_url: str):
        self.optimizer = DatabaseIndexOptimizer(database_url)

    async def continuous_monitoring(self, interval_minutes: int = 60):
        """Continuously monitor database performance"""
        while True:
            try:
                # Analyze current performance
                slow_queries = self.optimizer.analyze_query_performance()
                table_stats = self.optimizer.analyze_table_statistics()
                index_usage = self.optimizer.analyze_existing_indexes()

                # Log findings
                logger.info(f"Found {len(slow_queries)} slow queries")

                for table, stats in table_stats.items():
                    if stats['needs_vacuum']:
                        logger.warning(f"Table {table} needs vacuum (dead ratio: {stats['dead_tuple_ratio']:.2f})")

                # Generate and log maintenance recommendations
                maintenance_recs = self.optimizer.generate_maintenance_recommendations()
                if maintenance_recs:
                    logger.info(f"Generated {len(maintenance_recs)} maintenance recommendations")

                await asyncio.sleep(interval_minutes * 60)

            except Exception as e:
                logger.error(f"Error in database monitoring: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error


# Usage examples
if __name__ == "__main__":
    import asyncio

    async def main():
        database_url = "postgresql://user:pass@localhost/dbname"
        optimizer = DatabaseIndexOptimizer(database_url)

        # Analyze current performance
        print("=== Query Performance Analysis ===")
        slow_queries = optimizer.analyze_query_performance()
        for query in slow_queries[:3]:  # Top 3 slow queries
            print(f"Query: {query.query_text[:100]}...")
            print(f"Avg Duration: {query.avg_duration_ms:.2f}ms")
            print(f"Execution Count: {query.execution_count}")
            print("---")

        # Generate recommendations
        print("\n=== Index Recommendations ===")
        recommendations = optimizer.generate_index_recommendations()
        for rec in recommendations:
            if rec.priority == "high":
                print(f"HIGH PRIORITY: {rec.table}.{', '.join(rec.columns)}")
                print(f"Expected improvement: {rec.estimated_improvement}")
                print("---")

        # Create indexes (dry run)
        print("\n=== Creating Indexes (Dry Run) ===")
        created = optimizer.create_optimized_indexes(dry_run=True)
        for index_sql in created:
            print(index_sql)

        # Maintenance recommendations
        print("\n=== Maintenance Recommendations ===")
        maintenance = optimizer.generate_maintenance_recommendations()
        for rec in maintenance:
            print(rec)

    # Run the example
    # asyncio.run(main())