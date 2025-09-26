#!/usr/bin/env python3
"""
Comprehensive System Health Monitor
Real-time monitoring with alerts and automated recovery
"""
import os
import time
import requests
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import logging
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SystemHealthMonitor:
    """Enterprise-grade system health monitoring"""

    def __init__(self):
        self.services = {
            'production_api': 'https://miraikakaku-api-zbaru5v7za-uc.a.run.app',
            'production_frontend': 'https://miraikakaku-front-465603676610.us-central1.run.app',
            'database': '34.173.9.214:5432'
        }

        self.thresholds = {
            'response_time_warning': 2.0,  # seconds
            'response_time_critical': 5.0,  # seconds
            'db_connection_timeout': 10.0,  # seconds
            'uptime_requirement': 99.9  # percentage
        }

    def check_api_health(self, service_name: str, url: str) -> dict:
        """Check API endpoint health with detailed metrics"""
        try:
            start_time = time.time()
            response = requests.get(f"{url}/health", timeout=10)
            response_time = time.time() - start_time

            status = {
                'service': service_name,
                'status': 'healthy' if response.status_code == 200 else 'degraded',
                'response_time': round(response_time, 3),
                'http_status': response.status_code,
                'timestamp': datetime.now().isoformat()
            }

            # Performance analysis
            if response_time > self.thresholds['response_time_critical']:
                status['alert_level'] = 'CRITICAL'
                status['message'] = f'Response time {response_time:.2f}s exceeds critical threshold'
            elif response_time > self.thresholds['response_time_warning']:
                status['alert_level'] = 'WARNING'
                status['message'] = f'Response time {response_time:.2f}s above warning threshold'
            else:
                status['alert_level'] = 'OK'
                status['message'] = 'Service responding normally'

            # Content validation
            try:
                content = response.json()
                if 'status' in content and content['status'] == 'healthy':
                    status['content_valid'] = True
                else:
                    status['content_valid'] = False
                    status['alert_level'] = 'WARNING'
                    status['message'] += ' - Invalid health response'
            except:
                status['content_valid'] = False

            return status

        except requests.exceptions.Timeout:
            return {
                'service': service_name,
                'status': 'timeout',
                'alert_level': 'CRITICAL',
                'message': 'Service timeout - potential outage',
                'timestamp': datetime.now().isoformat()
            }
        except requests.exceptions.ConnectionError:
            return {
                'service': service_name,
                'status': 'down',
                'alert_level': 'CRITICAL',
                'message': 'Service unreachable - likely down',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'service': service_name,
                'status': 'error',
                'alert_level': 'CRITICAL',
                'message': f'Health check failed: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }

    def check_database_health(self) -> dict:
        """Comprehensive database health check"""
        try:
            start_time = time.time()

            conn = psycopg2.connect(
                host=os.environ.get('POSTGRES_HOST', '34.173.9.214'),
                port=int(os.environ.get('POSTGRES_PORT', '5432')),
                database=os.environ.get('POSTGRES_DB', 'miraikakaku'),
                user=os.environ.get('POSTGRES_USER', 'postgres'),
                password=os.environ.get('POSTGRES_PASSWORD', ''),
                cursor_factory=RealDictCursor,
                connect_timeout=int(self.thresholds['db_connection_timeout'])
            )

            cursor = conn.cursor()

            # Connection time
            connect_time = time.time() - start_time

            # Basic health check
            cursor.execute("SELECT version(), current_timestamp, current_database()")
            db_info = cursor.fetchone()

            # Performance metrics
            cursor.execute("""
                SELECT
                    COUNT(*) as total_connections,
                    COUNT(*) FILTER (WHERE state = 'active') as active_connections,
                    COUNT(*) FILTER (WHERE state = 'idle') as idle_connections
                FROM pg_stat_activity
                WHERE datname = current_database()
            """)
            connection_stats = cursor.fetchone()

            # Data validation
            cursor.execute("SELECT COUNT(*) as stock_prices_count FROM stock_prices")
            data_count = cursor.fetchone()

            # Index usage check
            cursor.execute("""
                SELECT schemaname, relname as tablename, indexrelname as indexname, idx_tup_read, idx_tup_fetch
                FROM pg_stat_user_indexes
                WHERE idx_tup_read > 0
                ORDER BY idx_tup_read DESC
                LIMIT 5
            """)
            index_usage = cursor.fetchall()

            cursor.close()
            conn.close()

            status = {
                'service': 'database',
                'status': 'healthy',
                'alert_level': 'OK',
                'connect_time': round(connect_time, 3),
                'version': db_info['version'].split(' ')[1],
                'database': db_info['current_database'],
                'total_connections': connection_stats['total_connections'],
                'active_connections': connection_stats['active_connections'],
                'data_records': data_count['stock_prices_count'],
                'indexes_active': len(index_usage),
                'timestamp': datetime.now().isoformat()
            }

            # Performance warnings
            if connect_time > 3.0:
                status['alert_level'] = 'WARNING'
                status['message'] = f'Database connection slow: {connect_time:.2f}s'
            elif connection_stats['active_connections'] > 50:
                status['alert_level'] = 'WARNING'
                status['message'] = f'High connection count: {connection_stats["active_connections"]}'
            else:
                status['message'] = 'Database operating normally'

            return status

        except psycopg2.OperationalError as e:
            return {
                'service': 'database',
                'status': 'connection_failed',
                'alert_level': 'CRITICAL',
                'message': f'Database connection failed: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'service': 'database',
                'status': 'error',
                'alert_level': 'CRITICAL',
                'message': f'Database health check failed: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }

    def generate_health_report(self) -> dict:
        """Generate comprehensive system health report"""
        logger.info("🔍 Starting system health check...")

        health_report = {
            'timestamp': datetime.now().isoformat(),
            'services': {},
            'overall_status': 'healthy',
            'alerts': []
        }

        # Check all services
        for service_name, url in self.services.items():
            if service_name == 'database':
                continue  # Handle separately

            logger.info(f"Checking {service_name}...")
            service_health = self.check_api_health(service_name, url)
            health_report['services'][service_name] = service_health

            if service_health.get('alert_level') in ['WARNING', 'CRITICAL']:
                health_report['alerts'].append(service_health)

        # Check database
        logger.info("Checking database...")
        db_health = self.check_database_health()
        health_report['services']['database'] = db_health

        if db_health.get('alert_level') in ['WARNING', 'CRITICAL']:
            health_report['alerts'].append(db_health)

        # Determine overall status
        critical_alerts = [a for a in health_report['alerts'] if a.get('alert_level') == 'CRITICAL']
        warning_alerts = [a for a in health_report['alerts'] if a.get('alert_level') == 'WARNING']

        if critical_alerts:
            health_report['overall_status'] = 'critical'
            health_report['status_message'] = f'{len(critical_alerts)} critical issues detected'
        elif warning_alerts:
            health_report['overall_status'] = 'warning'
            health_report['status_message'] = f'{len(warning_alerts)} warnings detected'
        else:
            health_report['overall_status'] = 'healthy'
            health_report['status_message'] = 'All systems operational'

        return health_report

    def print_health_report(self, report: dict):
        """Print formatted health report"""
        status_emoji = {
            'healthy': '✅',
            'warning': '⚠️',
            'critical': '🚨',
            'down': '❌',
            'timeout': '⏰'
        }

        print(f"\n{'='*60}")
        print(f"📊 MIRAIKAKAKU SYSTEM HEALTH REPORT")
        print(f"{'='*60}")
        print(f"Timestamp: {report['timestamp']}")
        print(f"Overall Status: {status_emoji.get(report['overall_status'], '❓')} {report['overall_status'].upper()}")
        print(f"Message: {report.get('status_message', 'No message')}")

        print(f"\n🔧 SERVICE STATUS:")
        print(f"{'-'*60}")

        for service_name, service_data in report['services'].items():
            status = service_data.get('status', 'unknown')
            emoji = status_emoji.get(status, '❓')

            print(f"{emoji} {service_name.upper():<20} {status}")

            if 'response_time' in service_data:
                print(f"   Response Time: {service_data['response_time']}s")
            if 'connect_time' in service_data:
                print(f"   Connection Time: {service_data['connect_time']}s")
            if 'data_records' in service_data:
                print(f"   Data Records: {service_data['data_records']:,}")
            if 'message' in service_data:
                print(f"   Status: {service_data['message']}")

            print()

        if report['alerts']:
            print(f"🚨 ALERTS ({len(report['alerts'])}):")
            print(f"{'-'*60}")

            for alert in report['alerts']:
                level_emoji = '🚨' if alert['alert_level'] == 'CRITICAL' else '⚠️'
                print(f"{level_emoji} [{alert['alert_level']}] {alert['service']}")
                print(f"   {alert.get('message', 'No details')}")
                print()

        # System score calculation
        total_services = len(report['services'])
        healthy_services = len([s for s in report['services'].values() if s.get('alert_level') == 'OK'])
        score = round((healthy_services / total_services) * 100)

        print(f"📈 SYSTEM HEALTH SCORE: {score}/100")
        print(f"{'='*60}\n")

def main():
    """Main monitoring function"""
    monitor = SystemHealthMonitor()

    try:
        report = monitor.generate_health_report()
        monitor.print_health_report(report)

        # Return appropriate exit code
        if report['overall_status'] == 'critical':
            exit(2)
        elif report['overall_status'] == 'warning':
            exit(1)
        else:
            exit(0)

    except Exception as e:
        logger.error(f"Health monitoring failed: {e}")
        print(f"🚨 MONITORING SYSTEM FAILURE: {e}")
        exit(3)

if __name__ == "__main__":
    main()