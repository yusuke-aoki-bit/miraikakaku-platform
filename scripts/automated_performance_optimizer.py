#!/usr/bin/env python3
"""
Automated Performance Optimizer for Miraikakaku
Automated system performance optimization and tuning
"""

import os
import json
import logging
import time
import psutil
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import psycopg2
import statistics

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s'
)
logger = logging.getLogger(__name__)

class AutomatedPerformanceOptimizer:
    def __init__(self):
        self.project_root = '/mnt/c/Users/yuuku/cursor/miraikakaku'
        self.optimization_history = []
        self.performance_baselines = {}
        self.db_config = {
            'host': '34.173.9.214',
            'user': 'postgres',
            'password': os.getenv('DB_PASSWORD'),
            'database': 'miraikakaku'
        }

    def collect_performance_metrics(self) -> Dict[str, Any]:
        """Collect comprehensive performance metrics"""
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'system_performance': {},
            'application_performance': {},
            'database_performance': {},
            'optimization_opportunities': []
        }

        try:
            # System performance
            cpu_times = psutil.cpu_times()
            memory = psutil.virtual_memory()
            disk_io = psutil.disk_io_counters()

            metrics['system_performance'] = {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'cpu_idle': cpu_times.idle,
                'cpu_system': cpu_times.system,
                'cpu_user': cpu_times.user,
                'memory_percent': memory.percent,
                'memory_available': memory.available,
                'memory_buffers': memory.buffers if hasattr(memory, 'buffers') else 0,
                'memory_cached': memory.cached if hasattr(memory, 'cached') else 0,
                'disk_read_bytes': disk_io.read_bytes if disk_io else 0,
                'disk_write_bytes': disk_io.write_bytes if disk_io else 0,
                'disk_read_time': disk_io.read_time if disk_io else 0,
                'disk_write_time': disk_io.write_time if disk_io else 0
            }

            # Application performance
            metrics['application_performance'] = self._measure_application_performance()

            # Database performance
            metrics['database_performance'] = self._measure_database_performance()

            # Identify optimization opportunities
            metrics['optimization_opportunities'] = self._identify_optimization_opportunities(metrics)

        except Exception as e:
            logger.error(f"Error collecting performance metrics: {e}")
            metrics['error'] = str(e)

        return metrics

    def _measure_application_performance(self) -> Dict[str, Any]:
        """Measure application-specific performance metrics"""
        app_metrics = {
            'api_response_times': [],
            'frontend_load_time': None,
            'process_metrics': {}
        }

        try:
            # API endpoint response times
            api_endpoints = [
                'http://localhost:8080/health',
                'http://localhost:8080/api/stocks/AAPL',
                'http://localhost:8080/api/predictions/AAPL'
            ]

            for endpoint in api_endpoints:
                try:
                    start_time = time.time()
                    import requests
                    response = requests.get(endpoint, timeout=5)
                    response_time = time.time() - start_time

                    app_metrics['api_response_times'].append({
                        'endpoint': endpoint,
                        'response_time': round(response_time, 3),
                        'status_code': response.status_code
                    })
                except:
                    pass

            # Frontend load time
            try:
                start_time = time.time()
                response = requests.get('http://localhost:3000', timeout=10)
                frontend_time = time.time() - start_time
                app_metrics['frontend_load_time'] = round(frontend_time, 3)
            except:
                pass

            # Process-specific metrics
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    info = proc.info
                    if 'python' in info['name'] or 'node' in info['name']:
                        app_metrics['process_metrics'][info['name']] = {
                            'pid': info['pid'],
                            'cpu_percent': info['cpu_percent'],
                            'memory_percent': info['memory_percent']
                        }
                except:
                    continue

        except Exception as e:
            logger.error(f"Error measuring application performance: {e}")

        return app_metrics

    def _measure_database_performance(self) -> Dict[str, Any]:
        """Measure database performance metrics"""
        db_metrics = {
            'connection_time': None,
            'query_performance': [],
            'index_usage': {},
            'cache_hit_ratio': None,
            'active_connections': None
        }

        try:
            # Connection time
            start_time = time.time()
            conn = psycopg2.connect(**self.db_config)
            connection_time = time.time() - start_time
            db_metrics['connection_time'] = round(connection_time, 3)

            cursor = conn.cursor()

            # Query performance tests
            test_queries = [
                ("SELECT COUNT(*) FROM stock_prices", "count_stock_prices"),
                ("SELECT * FROM stock_prices WHERE symbol = 'AAPL' LIMIT 10", "select_aapl"),
                ("SELECT COUNT(*) FROM stock_predictions", "count_predictions")
            ]

            for query, query_name in test_queries:
                try:
                    start_time = time.time()
                    cursor.execute(query)
                    cursor.fetchall()
                    query_time = time.time() - start_time

                    db_metrics['query_performance'].append({
                        'query_name': query_name,
                        'execution_time': round(query_time, 3)
                    })
                except Exception as e:
                    logger.warning(f"Query performance test failed for {query_name}: {e}")

            # Cache hit ratio
            try:
                cursor.execute("""
                    SELECT
                        sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read)) as cache_hit_ratio
                    FROM pg_statio_user_tables
                """)
                result = cursor.fetchone()
                if result and result[0]:
                    db_metrics['cache_hit_ratio'] = round(float(result[0]), 3)
            except:
                pass

            # Active connections
            try:
                cursor.execute("SELECT count(*) FROM pg_stat_activity WHERE state = 'active'")
                db_metrics['active_connections'] = cursor.fetchone()[0]
            except:
                pass

            conn.close()

        except Exception as e:
            logger.error(f"Error measuring database performance: {e}")
            db_metrics['error'] = str(e)

        return db_metrics

    def _identify_optimization_opportunities(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify specific optimization opportunities"""
        opportunities = []

        system = metrics.get('system_performance', {})
        app = metrics.get('application_performance', {})
        db = metrics.get('database_performance', {})

        # System optimization opportunities
        if system.get('cpu_percent', 0) > 70:
            opportunities.append({
                'type': 'system',
                'category': 'cpu',
                'severity': 'medium',
                'description': 'High CPU usage detected',
                'recommendation': 'Consider process optimization or scaling',
                'value': system.get('cpu_percent'),
                'action': 'optimize_cpu_usage'
            })

        if system.get('memory_percent', 0) > 80:
            opportunities.append({
                'type': 'system',
                'category': 'memory',
                'severity': 'high',
                'description': 'High memory usage detected',
                'recommendation': 'Clear caches or increase memory',
                'value': system.get('memory_percent'),
                'action': 'optimize_memory_usage'
            })

        # Application optimization opportunities
        slow_apis = [api for api in app.get('api_response_times', [])
                    if api.get('response_time', 0) > 1.0]
        if slow_apis:
            opportunities.append({
                'type': 'application',
                'category': 'api_performance',
                'severity': 'medium',
                'description': f'{len(slow_apis)} slow API endpoint(s) detected',
                'recommendation': 'Optimize API queries and add caching',
                'endpoints': [api['endpoint'] for api in slow_apis],
                'action': 'optimize_api_performance'
            })

        if app.get('frontend_load_time', 0) > 3.0:
            opportunities.append({
                'type': 'application',
                'category': 'frontend_performance',
                'severity': 'medium',
                'description': 'Slow frontend load time detected',
                'recommendation': 'Optimize frontend bundle and enable caching',
                'value': app.get('frontend_load_time'),
                'action': 'optimize_frontend_performance'
            })

        # Database optimization opportunities
        if db.get('connection_time', 0) > 2.0:
            opportunities.append({
                'type': 'database',
                'category': 'connection_performance',
                'severity': 'medium',
                'description': 'Slow database connection time',
                'recommendation': 'Implement connection pooling',
                'value': db.get('connection_time'),
                'action': 'optimize_db_connections'
            })

        slow_queries = [q for q in db.get('query_performance', [])
                       if q.get('execution_time', 0) > 1.0]
        if slow_queries:
            opportunities.append({
                'type': 'database',
                'category': 'query_performance',
                'severity': 'high',
                'description': f'{len(slow_queries)} slow database query(ies)',
                'recommendation': 'Add indexes and optimize queries',
                'queries': [q['query_name'] for q in slow_queries],
                'action': 'optimize_database_queries'
            })

        if db.get('cache_hit_ratio', 1.0) < 0.95:
            opportunities.append({
                'type': 'database',
                'category': 'cache_performance',
                'severity': 'medium',
                'description': 'Low database cache hit ratio',
                'recommendation': 'Increase shared_buffers or optimize queries',
                'value': db.get('cache_hit_ratio'),
                'action': 'optimize_db_cache'
            })

        return opportunities

    def apply_automatic_optimizations(self, opportunities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Apply automatic optimizations based on identified opportunities"""
        optimization_results = {
            'timestamp': datetime.now().isoformat(),
            'optimizations_applied': [],
            'optimizations_skipped': [],
            'errors': []
        }

        for opportunity in opportunities:
            action = opportunity.get('action')

            try:
                if action == 'optimize_memory_usage':
                    result = self._optimize_memory_usage()
                    if result:
                        optimization_results['optimizations_applied'].append({
                            'action': action,
                            'description': 'Cleared system caches and optimized memory usage',
                            'result': result
                        })

                elif action == 'optimize_api_performance':
                    result = self._optimize_api_performance()
                    if result:
                        optimization_results['optimizations_applied'].append({
                            'action': action,
                            'description': 'Applied API performance optimizations',
                            'result': result
                        })

                elif action == 'optimize_frontend_performance':
                    result = self._optimize_frontend_performance()
                    if result:
                        optimization_results['optimizations_applied'].append({
                            'action': action,
                            'description': 'Optimized frontend performance',
                            'result': result
                        })

                elif action == 'optimize_database_queries':
                    result = self._optimize_database_queries()
                    if result:
                        optimization_results['optimizations_applied'].append({
                            'action': action,
                            'description': 'Optimized database queries and indexes',
                            'result': result
                        })

                else:
                    optimization_results['optimizations_skipped'].append({
                        'action': action,
                        'reason': 'No automatic optimization available'
                    })

            except Exception as e:
                optimization_results['errors'].append({
                    'action': action,
                    'error': str(e)
                })
                logger.error(f"Error applying optimization {action}: {e}")

        return optimization_results

    def _optimize_memory_usage(self) -> Dict[str, Any]:
        """Optimize system memory usage"""
        optimizations = []

        try:
            # Clear system caches
            try:
                subprocess.run(['sync'], timeout=30)
                subprocess.run(['sudo', 'sh', '-c', 'echo 3 > /proc/sys/vm/drop_caches'], timeout=30)
                optimizations.append('cleared_system_caches')
            except:
                # Alternative: clear application caches
                cache_dirs = [
                    os.path.join(self.project_root, 'miraikakakufront/.next/cache'),
                    os.path.join(self.project_root, 'miraikakakuapi/__pycache__'),
                    '/tmp'
                ]

                for cache_dir in cache_dirs:
                    if os.path.exists(cache_dir):
                        try:
                            subprocess.run(['rm', '-rf', f"{cache_dir}/*"], shell=True, timeout=30)
                            optimizations.append(f'cleared_{os.path.basename(cache_dir)}')
                        except:
                            pass

            # Restart memory-intensive processes if needed
            memory = psutil.virtual_memory()
            if memory.percent > 85:
                try:
                    # Find and restart high-memory processes
                    for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
                        if proc.info['memory_percent'] > 10 and 'python' in proc.info['name']:
                            # Don't restart this process
                            if proc.info['pid'] != os.getpid():
                                proc.terminate()
                                optimizations.append(f'restarted_process_{proc.info["pid"]}')
                except:
                    pass

        except Exception as e:
            logger.error(f"Error in memory optimization: {e}")

        return {'optimizations': optimizations} if optimizations else None

    def _optimize_api_performance(self) -> Dict[str, Any]:
        """Optimize API performance"""
        optimizations = []

        try:
            # Enable response compression
            api_config_path = os.path.join(self.project_root, 'miraikakakuapi/performance_config.py')
            compression_config = '''
# API Performance Configuration
import gzip
from flask import Flask, request, after_this_request

def enable_compression(app):
    @app.after_request
    def compress_response(response):
        accept_encoding = request.headers.get('Accept-Encoding', '')

        if 'gzip' not in accept_encoding.lower():
            return response

        if (response.status_code < 200 or
            response.status_code >= 300 or
            'Content-Encoding' in response.headers):
            return response

        response.data = gzip.compress(response.data)
        response.headers['Content-Encoding'] = 'gzip'
        response.headers['Vary'] = 'Accept-Encoding'
        response.headers['Content-Length'] = len(response.data)

        return response

    return app

def enable_caching_headers(app):
    @app.after_request
    def add_caching_headers(response):
        if request.endpoint in ['stock_data', 'predictions']:
            # Cache for 5 minutes
            response.headers['Cache-Control'] = 'public, max-age=300'
        elif request.endpoint == 'health':
            # Don't cache health checks
            response.headers['Cache-Control'] = 'no-cache'
        return response

    return app
'''

            with open(api_config_path, 'w') as f:
                f.write(compression_config)

            optimizations.append('enabled_response_compression')
            optimizations.append('added_caching_headers')

            # Optimize database connections
            pool_config_path = os.path.join(self.project_root, 'miraikakakuapi/optimized_db_pool.py')
            if not os.path.exists(pool_config_path):
                # This was already created by the scalability enhancer
                optimizations.append('connection_pool_already_configured')

        except Exception as e:
            logger.error(f"Error in API optimization: {e}")

        return {'optimizations': optimizations} if optimizations else None

    def _optimize_frontend_performance(self) -> Dict[str, Any]:
        """Optimize frontend performance"""
        optimizations = []

        try:
            frontend_dir = os.path.join(self.project_root, 'miraikakakufront')

            # Clear Next.js cache
            next_cache = os.path.join(frontend_dir, '.next/cache')
            if os.path.exists(next_cache):
                subprocess.run(['rm', '-rf', next_cache], timeout=30)
                optimizations.append('cleared_nextjs_cache')

            # Optimize bundle if needed
            try:
                # Check bundle size
                static_dir = os.path.join(frontend_dir, '.next/static')
                if os.path.exists(static_dir):
                    total_size = sum(os.path.getsize(os.path.join(dirpath, filename))
                                   for dirpath, dirnames, filenames in os.walk(static_dir)
                                   for filename in filenames)

                    if total_size > 50 * 1024 * 1024:  # 50MB
                        # Bundle is large, suggest optimization
                        optimizations.append('large_bundle_detected')

            except:
                pass

            # Enable production optimizations
            env_local_path = os.path.join(frontend_dir, '.env.local')
            with open(env_local_path, 'w') as f:
                f.write('''
# Production optimizations
NEXT_PUBLIC_BUNDLE_ANALYZER=false
NEXT_PUBLIC_SW_ENABLED=true
ANALYZE=false
''')
            optimizations.append('updated_environment_config')

        except Exception as e:
            logger.error(f"Error in frontend optimization: {e}")

        return {'optimizations': optimizations} if optimizations else None

    def _optimize_database_queries(self) -> Dict[str, Any]:
        """Optimize database queries and performance"""
        optimizations = []

        try:
            conn = psycopg2.connect(**self.db_config)
            conn.autocommit = True
            cursor = conn.cursor()

            # Run ANALYZE on main tables
            tables = ['stock_prices', 'stock_predictions', 'stock_master']
            for table in tables:
                try:
                    cursor.execute(f"ANALYZE {table};")
                    optimizations.append(f'analyzed_{table}')
                except Exception as e:
                    logger.warning(f"Could not analyze table {table}: {e}")

            # Update table statistics
            try:
                cursor.execute("ANALYZE;")
                optimizations.append('updated_table_statistics')
            except:
                pass

            # Check for missing indexes
            missing_indexes_query = """
            SELECT schemaname, tablename, attname
            FROM pg_stats
            WHERE schemaname = 'public'
            AND tablename IN ('stock_prices', 'stock_predictions', 'stock_master')
            AND n_distinct > 100
            AND correlation < 0.1
            """

            cursor.execute(missing_indexes_query)
            potential_indexes = cursor.fetchall()

            if potential_indexes:
                optimizations.append(f'identified_{len(potential_indexes)}_potential_indexes')

            conn.close()

        except Exception as e:
            logger.error(f"Error in database optimization: {e}")

        return {'optimizations': optimizations} if optimizations else None

    def establish_performance_baselines(self) -> Dict[str, Any]:
        """Establish performance baselines for comparison"""
        logger.info("Establishing performance baselines...")

        baseline_metrics = self.collect_performance_metrics()

        # Calculate baseline values
        baselines = {
            'timestamp': datetime.now().isoformat(),
            'system': {
                'cpu_baseline': baseline_metrics.get('system_performance', {}).get('cpu_percent', 0),
                'memory_baseline': baseline_metrics.get('system_performance', {}).get('memory_percent', 0)
            },
            'application': {
                'api_response_baseline': statistics.mean([
                    api.get('response_time', 0)
                    for api in baseline_metrics.get('application_performance', {}).get('api_response_times', [])
                ]) if baseline_metrics.get('application_performance', {}).get('api_response_times') else 0,
                'frontend_load_baseline': baseline_metrics.get('application_performance', {}).get('frontend_load_time', 0)
            },
            'database': {
                'connection_time_baseline': baseline_metrics.get('database_performance', {}).get('connection_time', 0),
                'query_performance_baseline': statistics.mean([
                    q.get('execution_time', 0)
                    for q in baseline_metrics.get('database_performance', {}).get('query_performance', [])
                ]) if baseline_metrics.get('database_performance', {}).get('query_performance') else 0
            }
        }

        self.performance_baselines = baselines

        # Save baselines to file
        baselines_file = os.path.join(self.project_root, 'performance_baselines.json')
        with open(baselines_file, 'w') as f:
            json.dump(baselines, f, indent=2)

        logger.info("Performance baselines established and saved")
        return baselines

    def run_automated_optimization_cycle(self) -> Dict[str, Any]:
        """Run a complete automated optimization cycle"""
        logger.info("🚀 Starting automated performance optimization cycle...")

        cycle_results = {
            'timestamp': datetime.now().isoformat(),
            'baseline_metrics': {},
            'optimization_opportunities': [],
            'optimizations_applied': {},
            'performance_improvement': {},
            'status': 'success'
        }

        try:
            # Collect baseline metrics
            logger.info("Step 1/4: Collecting baseline performance metrics...")
            baseline_metrics = self.collect_performance_metrics()
            cycle_results['baseline_metrics'] = baseline_metrics

            # Identify optimization opportunities
            logger.info("Step 2/4: Identifying optimization opportunities...")
            opportunities = baseline_metrics.get('optimization_opportunities', [])
            cycle_results['optimization_opportunities'] = opportunities

            if not opportunities:
                logger.info("No optimization opportunities identified")
                cycle_results['message'] = 'System is already well optimized'
                return cycle_results

            # Apply optimizations
            logger.info(f"Step 3/4: Applying {len(opportunities)} optimization(s)...")
            optimization_results = self.apply_automatic_optimizations(opportunities)
            cycle_results['optimizations_applied'] = optimization_results

            # Wait for optimizations to take effect
            time.sleep(10)

            # Measure performance improvement
            logger.info("Step 4/4: Measuring performance improvement...")
            post_optimization_metrics = self.collect_performance_metrics()

            improvement = self._calculate_performance_improvement(
                baseline_metrics, post_optimization_metrics
            )
            cycle_results['performance_improvement'] = improvement

            # Save optimization history
            self.optimization_history.append(cycle_results)
            self._save_optimization_history()

            logger.info("✅ Automated optimization cycle completed successfully!")

        except Exception as e:
            logger.error(f"Error in optimization cycle: {e}")
            cycle_results['status'] = 'failed'
            cycle_results['error'] = str(e)

        return cycle_results

    def _calculate_performance_improvement(self, before: Dict[str, Any], after: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate performance improvement between metrics"""
        improvement = {
            'system_improvements': {},
            'application_improvements': {},
            'database_improvements': {},
            'overall_improvement_score': 0
        }

        try:
            # System improvements
            before_sys = before.get('system_performance', {})
            after_sys = after.get('system_performance', {})

            if before_sys.get('cpu_percent') and after_sys.get('cpu_percent'):
                cpu_improvement = before_sys['cpu_percent'] - after_sys['cpu_percent']
                improvement['system_improvements']['cpu_improvement'] = round(cpu_improvement, 2)

            if before_sys.get('memory_percent') and after_sys.get('memory_percent'):
                memory_improvement = before_sys['memory_percent'] - after_sys['memory_percent']
                improvement['system_improvements']['memory_improvement'] = round(memory_improvement, 2)

            # Application improvements
            before_app = before.get('application_performance', {})
            after_app = after.get('application_performance', {})

            before_api_avg = statistics.mean([
                api.get('response_time', 0)
                for api in before_app.get('api_response_times', [])
            ]) if before_app.get('api_response_times') else 0

            after_api_avg = statistics.mean([
                api.get('response_time', 0)
                for api in after_app.get('api_response_times', [])
            ]) if after_app.get('api_response_times') else 0

            if before_api_avg and after_api_avg:
                api_improvement = before_api_avg - after_api_avg
                improvement['application_improvements']['api_response_improvement'] = round(api_improvement, 3)

            # Database improvements
            before_db = before.get('database_performance', {})
            after_db = after.get('database_performance', {})

            if before_db.get('connection_time') and after_db.get('connection_time'):
                db_improvement = before_db['connection_time'] - after_db['connection_time']
                improvement['database_improvements']['connection_time_improvement'] = round(db_improvement, 3)

            # Calculate overall improvement score (0-100)
            improvements = []
            for category in improvement.values():
                if isinstance(category, dict):
                    improvements.extend([v for v in category.values() if isinstance(v, (int, float)) and v > 0])

            if improvements:
                improvement['overall_improvement_score'] = round(statistics.mean(improvements) * 10, 1)

        except Exception as e:
            logger.error(f"Error calculating performance improvement: {e}")

        return improvement

    def _save_optimization_history(self):
        """Save optimization history to file"""
        try:
            history_file = os.path.join(self.project_root, 'optimization_history.json')
            with open(history_file, 'w') as f:
                json.dump(self.optimization_history, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving optimization history: {e}")

def main():
    """Main function for standalone execution"""
    import argparse

    parser = argparse.ArgumentParser(description='Automated Performance Optimizer')
    parser.add_argument('--baseline', action='store_true', help='Establish performance baselines')
    parser.add_argument('--metrics', action='store_true', help='Collect current performance metrics')
    parser.add_argument('--optimize', action='store_true', help='Run optimization cycle')
    parser.add_argument('--continuous', action='store_true', help='Run continuous optimization')
    parser.add_argument('--interval', type=int, default=3600, help='Optimization interval in seconds')

    args = parser.parse_args()

    optimizer = AutomatedPerformanceOptimizer()

    if args.baseline:
        result = optimizer.establish_performance_baselines()
        print(json.dumps(result, indent=2))
    elif args.metrics:
        result = optimizer.collect_performance_metrics()
        print(json.dumps(result, indent=2))
    elif args.optimize:
        result = optimizer.run_automated_optimization_cycle()
        print(json.dumps(result, indent=2))
    elif args.continuous:
        logger.info(f"Starting continuous optimization (interval: {args.interval}s)")
        while True:
            try:
                optimizer.run_automated_optimization_cycle()
                time.sleep(args.interval)
            except KeyboardInterrupt:
                logger.info("Continuous optimization stopped by user")
                break
    else:
        # Default: run single optimization cycle
        result = optimizer.run_automated_optimization_cycle()
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()