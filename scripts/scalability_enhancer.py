#!/usr/bin/env python3
"""
Scalability Enhancer for Miraikakaku
Improve system scalability and performance
"""

import os
import json
import subprocess
import logging
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import psutil
import requests

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s'
)
logger = logging.getLogger(__name__)

class ScalabilityEnhancer:
    def __init__(self):
        self.project_root = '/mnt/c/Users/yuuku/cursor/miraikakaku'
        self.api_dir = os.path.join(self.project_root, 'miraikakakuapi')
        self.frontend_dir = os.path.join(self.project_root, 'miraikakakufront')
        self.batch_dir = os.path.join(self.project_root, 'miraikakakubatch')

    def analyze_current_performance(self) -> Dict[str, Any]:
        """Analyze current system performance metrics"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'system_metrics': {},
            'application_metrics': {},
            'bottlenecks': [],
            'status': 'success'
        }

        try:
            # System resource metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            results['system_metrics'] = {
                'cpu': {
                    'usage_percent': cpu_percent,
                    'cores': psutil.cpu_count(),
                    'load_average': os.getloadavg()
                },
                'memory': {
                    'total_gb': round(memory.total / (1024**3), 2),
                    'used_gb': round(memory.used / (1024**3), 2),
                    'available_gb': round(memory.available / (1024**3), 2),
                    'percent_used': memory.percent
                },
                'disk': {
                    'total_gb': round(disk.total / (1024**3), 2),
                    'used_gb': round(disk.used / (1024**3), 2),
                    'free_gb': round(disk.free / (1024**3), 2),
                    'percent_used': disk.percent
                }
            }

            # Identify bottlenecks
            if cpu_percent > 80:
                results['bottlenecks'].append({
                    'type': 'cpu',
                    'severity': 'high',
                    'message': f'CPU usage is high ({cpu_percent}%)'
                })

            if memory.percent > 85:
                results['bottlenecks'].append({
                    'type': 'memory',
                    'severity': 'high',
                    'message': f'Memory usage is high ({memory.percent}%)'
                })

            if disk.percent > 90:
                results['bottlenecks'].append({
                    'type': 'disk',
                    'severity': 'critical',
                    'message': f'Disk usage is critical ({disk.percent}%)'
                })

            # Test API response time
            try:
                start_time = time.time()
                response = requests.get('http://localhost:8080/health', timeout=5)
                api_response_time = time.time() - start_time

                results['application_metrics']['api_response_time'] = round(api_response_time, 3)

                if api_response_time > 1.0:
                    results['bottlenecks'].append({
                        'type': 'api_performance',
                        'severity': 'medium',
                        'message': f'API response time is slow ({api_response_time:.2f}s)'
                    })
            except:
                results['application_metrics']['api_response_time'] = None

        except Exception as e:
            logger.error(f"Error analyzing performance: {e}")
            results['status'] = 'failed'
            results['error'] = str(e)

        return results

    def implement_caching_strategy(self) -> Dict[str, Any]:
        """Implement caching strategies for better performance"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'caching_implementations': [],
            'optimizations': [],
            'status': 'success'
        }

        try:
            # Create Redis configuration for caching
            redis_config = {
                'host': 'localhost',
                'port': 6379,
                'db': 0,
                'decode_responses': True,
                'max_connections': 50,
                'socket_timeout': 5,
                'socket_connect_timeout': 5,
                'socket_keepalive': True,
                'socket_keepalive_options': {}
            }

            # Create caching configuration file
            cache_config_path = os.path.join(self.project_root, 'cache_config.json')
            with open(cache_config_path, 'w') as f:
                json.dump(redis_config, f, indent=2)

            results['caching_implementations'].append({
                'component': 'redis_config',
                'path': cache_config_path,
                'status': 'created'
            })

            # Create API caching middleware
            api_cache_code = '''
import redis
import json
import hashlib
from functools import wraps
from datetime import timedelta

class CacheManager:
    def __init__(self, config_path='/mnt/c/Users/yuuku/cursor/miraikakaku/cache_config.json'):
        with open(config_path, 'r') as f:
            config = json.load(f)
        self.redis_client = redis.Redis(**config)
        self.default_ttl = 3600  # 1 hour

    def cache_key(self, prefix, *args, **kwargs):
        """Generate cache key from arguments"""
        key_data = f"{prefix}:{args}:{sorted(kwargs.items())}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def cache_response(self, ttl=None):
        """Decorator for caching API responses"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                cache_key = self.cache_key(func.__name__, *args, **kwargs)

                # Try to get from cache
                cached = self.redis_client.get(cache_key)
                if cached:
                    return json.loads(cached)

                # Execute function and cache result
                result = func(*args, **kwargs)
                self.redis_client.setex(
                    cache_key,
                    ttl or self.default_ttl,
                    json.dumps(result)
                )
                return result
            return wrapper
        return decorator

    def invalidate_pattern(self, pattern):
        """Invalidate cache entries matching pattern"""
        for key in self.redis_client.scan_iter(match=pattern):
            self.redis_client.delete(key)
'''

            cache_manager_path = os.path.join(self.api_dir, 'cache_manager.py')
            with open(cache_manager_path, 'w') as f:
                f.write(api_cache_code)

            results['caching_implementations'].append({
                'component': 'cache_manager',
                'path': cache_manager_path,
                'status': 'created'
            })

            # Create database query cache
            db_cache_code = '''
import psycopg2
from psycopg2.extras import RealDictCursor
import json
import hashlib
from datetime import datetime, timedelta

class DatabaseCache:
    def __init__(self, db_config, cache_manager):
        self.db_config = db_config
        self.cache = cache_manager
        self.cache_ttl = {
            'stock_master': 86400,  # 24 hours
            'stock_prices': 300,    # 5 minutes
            'stock_predictions': 3600  # 1 hour
        }

    def cached_query(self, query, params=None, table_hint=None):
        """Execute cached database query"""
        cache_key = self.cache.cache_key(
            'db_query',
            query,
            params
        )

        # Try cache first
        cached = self.cache.redis_client.get(cache_key)
        if cached:
            return json.loads(cached)

        # Execute query
        conn = psycopg2.connect(**self.db_config)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()

        # Cache results
        ttl = self.cache_ttl.get(table_hint, 600)
        self.cache.redis_client.setex(
            cache_key,
            ttl,
            json.dumps(results, default=str)
        )

        return results
'''

            db_cache_path = os.path.join(self.api_dir, 'db_cache.py')
            with open(db_cache_path, 'w') as f:
                f.write(db_cache_code)

            results['caching_implementations'].append({
                'component': 'database_cache',
                'path': db_cache_path,
                'status': 'created'
            })

            results['optimizations'].append('Implemented Redis-based caching for API responses')
            results['optimizations'].append('Created database query caching layer')
            results['optimizations'].append('Set up TTL-based cache invalidation')

        except Exception as e:
            logger.error(f"Error implementing caching: {e}")
            results['status'] = 'failed'
            results['error'] = str(e)

        return results

    def optimize_database_connections(self) -> Dict[str, Any]:
        """Optimize database connection pooling"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'optimizations': [],
            'configurations': [],
            'status': 'success'
        }

        try:
            # Create connection pool configuration
            pool_config = '''
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
'''

            pool_path = os.path.join(self.api_dir, 'db_pool.py')
            with open(pool_path, 'w') as f:
                f.write(pool_config)

            results['configurations'].append({
                'type': 'connection_pool',
                'path': pool_path,
                'min_connections': 2,
                'max_connections': 20
            })

            results['optimizations'].append('Implemented connection pooling with 2-20 connections')
            results['optimizations'].append('Created thread-safe connection pool')

        except Exception as e:
            logger.error(f"Error optimizing database connections: {e}")
            results['status'] = 'failed'
            results['error'] = str(e)

        return results

    def implement_load_balancing(self) -> Dict[str, Any]:
        """Implement load balancing strategies"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'load_balancing_configs': [],
            'recommendations': [],
            'status': 'success'
        }

        try:
            # Create nginx configuration for load balancing
            nginx_config = '''
upstream api_backend {
    least_conn;
    server localhost:8080 weight=1;
    server localhost:8081 weight=1;
    server localhost:8082 weight=1;
    keepalive 32;
}

upstream frontend_backend {
    ip_hash;
    server localhost:3000;
    server localhost:3001;
    keepalive 16;
}

server {
    listen 80;
    server_name miraikakaku.com;

    # API load balancing
    location /api {
        proxy_pass http://api_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Connection pool settings
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;

        # Caching
        proxy_cache_bypass $http_upgrade;
        proxy_cache_valid 200 1m;
        proxy_cache_valid 404 1m;
    }

    # Frontend load balancing
    location / {
        proxy_pass http://frontend_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy";
        add_header Content-Type text/plain;
    }
}
'''

            nginx_path = os.path.join(self.project_root, 'nginx_load_balancer.conf')
            with open(nginx_path, 'w') as f:
                f.write(nginx_config)

            results['load_balancing_configs'].append({
                'type': 'nginx',
                'path': nginx_path,
                'strategy': 'least_conn for API, ip_hash for frontend'
            })

            # Create PM2 ecosystem configuration
            pm2_config = {
                "apps": [
                    {
                        "name": "api-1",
                        "script": "simple_api_server.py",
                        "cwd": self.api_dir,
                        "interpreter": "python3",
                        "env": {
                            "PORT": 8080
                        },
                        "instances": 1,
                        "exec_mode": "fork"
                    },
                    {
                        "name": "api-2",
                        "script": "simple_api_server.py",
                        "cwd": self.api_dir,
                        "interpreter": "python3",
                        "env": {
                            "PORT": 8081
                        },
                        "instances": 1,
                        "exec_mode": "fork"
                    },
                    {
                        "name": "api-3",
                        "script": "simple_api_server.py",
                        "cwd": self.api_dir,
                        "interpreter": "python3",
                        "env": {
                            "PORT": 8082
                        },
                        "instances": 1,
                        "exec_mode": "fork"
                    },
                    {
                        "name": "frontend",
                        "script": "npm",
                        "args": "start",
                        "cwd": self.frontend_dir,
                        "env": {
                            "PORT": 3000
                        },
                        "instances": 2,
                        "exec_mode": "cluster"
                    }
                ]
            }

            pm2_path = os.path.join(self.project_root, 'ecosystem.config.json')
            with open(pm2_path, 'w') as f:
                json.dump(pm2_config, f, indent=2)

            results['load_balancing_configs'].append({
                'type': 'pm2',
                'path': pm2_path,
                'api_instances': 3,
                'frontend_instances': 2
            })

            results['recommendations'].extend([
                'Use PM2 to manage multiple API instances',
                'Configure Nginx as reverse proxy and load balancer',
                'Implement health checks for automatic failover',
                'Consider using Docker Swarm or Kubernetes for container orchestration',
                'Set up auto-scaling based on CPU/memory metrics'
            ])

        except Exception as e:
            logger.error(f"Error implementing load balancing: {e}")
            results['status'] = 'failed'
            results['error'] = str(e)

        return results

    def create_scaling_strategy(self) -> Dict[str, Any]:
        """Create comprehensive scaling strategy"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'horizontal_scaling': {},
            'vertical_scaling': {},
            'auto_scaling': {},
            'implementation_plan': [],
            'status': 'success'
        }

        try:
            # Horizontal scaling strategy
            results['horizontal_scaling'] = {
                'api_servers': {
                    'current': 1,
                    'recommended': 3,
                    'max': 10,
                    'scaling_trigger': 'CPU > 70% or Response Time > 1s'
                },
                'frontend_servers': {
                    'current': 1,
                    'recommended': 2,
                    'max': 5,
                    'scaling_trigger': 'Concurrent Users > 1000'
                },
                'database': {
                    'read_replicas': {
                        'current': 0,
                        'recommended': 2,
                        'max': 5
                    },
                    'sharding_strategy': 'By symbol range (A-F, G-M, N-S, T-Z)'
                },
                'batch_workers': {
                    'current': 1,
                    'recommended': 5,
                    'max': 20,
                    'scaling_trigger': 'Queue depth > 100 or Processing time > 5min'
                }
            }

            # Vertical scaling strategy
            results['vertical_scaling'] = {
                'api_servers': {
                    'current_specs': 'Unknown',
                    'recommended_specs': '4 vCPU, 8GB RAM',
                    'max_specs': '16 vCPU, 32GB RAM'
                },
                'database': {
                    'current_specs': 'Cloud SQL standard',
                    'recommended_specs': '8 vCPU, 32GB RAM, SSD storage',
                    'max_specs': '32 vCPU, 128GB RAM, SSD storage'
                }
            }

            # Auto-scaling configuration
            results['auto_scaling'] = {
                'metrics': [
                    'CPU utilization',
                    'Memory usage',
                    'Request rate',
                    'Response time',
                    'Queue depth'
                ],
                'policies': [
                    {
                        'name': 'scale_up_api',
                        'trigger': 'avg_cpu > 70% for 5 minutes',
                        'action': 'add 1 API instance',
                        'cooldown': '5 minutes'
                    },
                    {
                        'name': 'scale_down_api',
                        'trigger': 'avg_cpu < 30% for 10 minutes',
                        'action': 'remove 1 API instance',
                        'cooldown': '10 minutes',
                        'min_instances': 2
                    },
                    {
                        'name': 'scale_up_batch',
                        'trigger': 'queue_depth > 100',
                        'action': 'add 2 batch workers',
                        'cooldown': '3 minutes'
                    }
                ]
            }

            # Implementation plan
            results['implementation_plan'] = [
                {
                    'phase': 1,
                    'title': 'Basic Load Balancing',
                    'tasks': [
                        'Set up Nginx reverse proxy',
                        'Deploy 3 API instances',
                        'Configure health checks',
                        'Implement connection pooling'
                    ],
                    'duration': '1 week',
                    'complexity': 'Low'
                },
                {
                    'phase': 2,
                    'title': 'Caching Layer',
                    'tasks': [
                        'Deploy Redis cluster',
                        'Implement API response caching',
                        'Add database query caching',
                        'Configure cache invalidation'
                    ],
                    'duration': '1 week',
                    'complexity': 'Medium'
                },
                {
                    'phase': 3,
                    'title': 'Database Scaling',
                    'tasks': [
                        'Set up read replicas',
                        'Implement read/write splitting',
                        'Configure connection pooling',
                        'Optimize queries and indexes'
                    ],
                    'duration': '2 weeks',
                    'complexity': 'High'
                },
                {
                    'phase': 4,
                    'title': 'Auto-scaling',
                    'tasks': [
                        'Configure monitoring metrics',
                        'Set up auto-scaling policies',
                        'Implement graceful shutdown',
                        'Test scaling scenarios'
                    ],
                    'duration': '2 weeks',
                    'complexity': 'High'
                },
                {
                    'phase': 5,
                    'title': 'Container Orchestration',
                    'tasks': [
                        'Containerize all components',
                        'Set up Kubernetes cluster',
                        'Configure service mesh',
                        'Implement rolling updates'
                    ],
                    'duration': '3 weeks',
                    'complexity': 'Very High'
                }
            ]

        except Exception as e:
            logger.error(f"Error creating scaling strategy: {e}")
            results['status'] = 'failed'
            results['error'] = str(e)

        return results

    def run_full_scalability_enhancement(self) -> Dict[str, Any]:
        """Run complete scalability enhancement"""
        logger.info("🚀 Starting scalability enhancement...")

        full_results = {
            'timestamp': datetime.now().isoformat(),
            'analyses': {},
            'implementations': {},
            'strategy': {},
            'overall_status': 'success',
            'summary': {}
        }

        try:
            # Step 1: Analyze current performance
            logger.info("Step 1/5: Analyzing current performance...")
            full_results['analyses']['performance'] = self.analyze_current_performance()

            # Step 2: Implement caching
            logger.info("Step 2/5: Implementing caching strategy...")
            full_results['implementations']['caching'] = self.implement_caching_strategy()

            # Step 3: Optimize database connections
            logger.info("Step 3/5: Optimizing database connections...")
            full_results['implementations']['db_optimization'] = self.optimize_database_connections()

            # Step 4: Configure load balancing
            logger.info("Step 4/5: Configuring load balancing...")
            full_results['implementations']['load_balancing'] = self.implement_load_balancing()

            # Step 5: Create scaling strategy
            logger.info("Step 5/5: Creating scaling strategy...")
            full_results['strategy'] = self.create_scaling_strategy()

            # Generate summary
            total_optimizations = 0
            total_recommendations = 0
            failed_steps = 0

            for category in ['implementations']:
                if category in full_results:
                    for impl_name, impl_result in full_results[category].items():
                        if impl_result.get('status') == 'failed':
                            failed_steps += 1
                            full_results['overall_status'] = 'partial_failure'

                        if 'optimizations' in impl_result:
                            total_optimizations += len(impl_result['optimizations'])

                        if 'recommendations' in impl_result:
                            total_recommendations += len(impl_result['recommendations'])

            full_results['summary'] = {
                'total_optimizations': total_optimizations,
                'total_recommendations': total_recommendations,
                'failed_steps': failed_steps,
                'bottlenecks_found': len(full_results['analyses'].get('performance', {}).get('bottlenecks', [])),
                'scaling_phases': len(full_results['strategy'].get('implementation_plan', []))
            }

            if failed_steps > 0:
                logger.warning(f"⚠️  Scalability enhancement completed with {failed_steps} failed steps")
            else:
                logger.info("✅ Scalability enhancement completed successfully!")

        except Exception as e:
            logger.error(f"Error in scalability enhancement: {e}")
            full_results['overall_status'] = 'failed'
            full_results['error'] = str(e)

        return full_results

def main():
    """Main function for standalone execution"""
    import argparse

    parser = argparse.ArgumentParser(description='Scalability Enhancer')
    parser.add_argument('--analyze', action='store_true', help='Analyze current performance')
    parser.add_argument('--cache', action='store_true', help='Implement caching strategy')
    parser.add_argument('--optimize-db', action='store_true', help='Optimize database connections')
    parser.add_argument('--load-balance', action='store_true', help='Configure load balancing')
    parser.add_argument('--strategy', action='store_true', help='Create scaling strategy')
    parser.add_argument('--full', action='store_true', help='Run full scalability enhancement')

    args = parser.parse_args()

    enhancer = ScalabilityEnhancer()

    if args.analyze:
        result = enhancer.analyze_current_performance()
        print(json.dumps(result, indent=2))
    elif args.cache:
        result = enhancer.implement_caching_strategy()
        print(json.dumps(result, indent=2))
    elif args.optimize_db:
        result = enhancer.optimize_database_connections()
        print(json.dumps(result, indent=2))
    elif args.load_balance:
        result = enhancer.implement_load_balancing()
        print(json.dumps(result, indent=2))
    elif args.strategy:
        result = enhancer.create_scaling_strategy()
        print(json.dumps(result, indent=2))
    elif args.full:
        result = enhancer.run_full_scalability_enhancement()
        print(json.dumps(result, indent=2))
    else:
        # Default: run full enhancement
        result = enhancer.run_full_scalability_enhancement()
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()