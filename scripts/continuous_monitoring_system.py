#!/usr/bin/env python3
"""
Continuous Monitoring System for Miraikakaku
Automated monitoring, alerting, and maintenance system
"""

import os
import json
import logging
import time
import psutil
import requests
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import psycopg2
from concurrent.futures import ThreadPoolExecutor
import threading

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s'
)
logger = logging.getLogger(__name__)

class ContinuousMonitoringSystem:
    def __init__(self):
        self.project_root = '/mnt/c/Users/yuuku/cursor/miraikakaku'
        self.monitoring_interval = 300  # 5 minutes
        self.alert_thresholds = {
            'cpu_usage': 80,
            'memory_usage': 85,
            'disk_usage': 90,
            'api_response_time': 2.0,
            'db_connection_time': 5.0,
            'error_rate': 5  # errors per minute
        }
        self.db_config = {
            'host': '34.173.9.214',
            'user': 'postgres',
            'password': 'os.getenv('DB_PASSWORD', '')',
            'database': 'miraikakaku'
        }
        self.metrics_history = []
        self.alerts_sent = {}
        self.running = False

    def collect_system_metrics(self) -> Dict[str, Any]:
        """Collect comprehensive system metrics"""
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'system': {},
            'application': {},
            'database': {},
            'alerts': []
        }

        try:
            # System metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            metrics['system'] = {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available_gb': round(memory.available / (1024**3), 2),
                'disk_percent': disk.percent,
                'disk_free_gb': round(disk.free / (1024**3), 2),
                'load_average': list(os.getloadavg()),
                'processes': len(psutil.pids())
            }

            # Application health checks
            metrics['application'] = self._check_application_health()

            # Database metrics
            metrics['database'] = self._check_database_health()

            # Generate alerts
            metrics['alerts'] = self._generate_alerts(metrics)

        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")
            metrics['error'] = str(e)

        return metrics

    def _check_application_health(self) -> Dict[str, Any]:
        """Check application health status"""
        health_status = {
            'api_server': {'status': 'unknown', 'response_time': None, 'error': None},
            'frontend_server': {'status': 'unknown', 'response_time': None, 'error': None},
            'batch_jobs': {'status': 'unknown', 'active_jobs': 0, 'failed_jobs': 0}
        }

        # Check API server
        try:
            start_time = time.time()
            response = requests.get('http://localhost:8080/health', timeout=10)
            response_time = time.time() - start_time

            health_status['api_server'] = {
                'status': 'healthy' if response.status_code == 200 else 'unhealthy',
                'response_time': round(response_time, 3),
                'status_code': response.status_code
            }
        except Exception as e:
            health_status['api_server'] = {
                'status': 'unhealthy',
                'response_time': None,
                'error': str(e)
            }

        # Check frontend server
        try:
            start_time = time.time()
            response = requests.get('http://localhost:3000', timeout=10)
            response_time = time.time() - start_time

            health_status['frontend_server'] = {
                'status': 'healthy' if response.status_code == 200 else 'unhealthy',
                'response_time': round(response_time, 3),
                'status_code': response.status_code
            }
        except Exception as e:
            health_status['frontend_server'] = {
                'status': 'unhealthy',
                'response_time': None,
                'error': str(e)
            }

        # Check batch jobs
        try:
            result = subprocess.run([
                'gcloud', 'batch', 'jobs', 'list',
                '--location', 'us-central1',
                '--format', 'json'
            ], capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                jobs = json.loads(result.stdout) if result.stdout else []
                active_jobs = sum(1 for job in jobs if job.get('status', {}).get('state') == 'RUNNING')
                failed_jobs = sum(1 for job in jobs if job.get('status', {}).get('state') == 'FAILED')

                health_status['batch_jobs'] = {
                    'status': 'healthy',
                    'active_jobs': active_jobs,
                    'failed_jobs': failed_jobs,
                    'total_jobs': len(jobs)
                }
        except Exception as e:
            health_status['batch_jobs'] = {
                'status': 'unknown',
                'error': str(e)
            }

        return health_status

    def _check_database_health(self) -> Dict[str, Any]:
        """Check database health and performance"""
        db_health = {
            'status': 'unknown',
            'connection_time': None,
            'active_connections': None,
            'table_stats': {},
            'error': None
        }

        try:
            start_time = time.time()
            conn = psycopg2.connect(**self.db_config)
            connection_time = time.time() - start_time

            cursor = conn.cursor()

            # Basic health check
            cursor.execute("SELECT 1")
            cursor.fetchone()

            # Connection stats
            cursor.execute("""
                SELECT count(*) as active_connections
                FROM pg_stat_activity
                WHERE state = 'active'
            """)
            active_connections = cursor.fetchone()[0]

            # Table statistics
            cursor.execute("""
                SELECT
                    schemaname,
                    tablename,
                    n_tup_ins + n_tup_upd + n_tup_del as total_operations,
                    n_tup_ins as inserts,
                    n_tup_upd as updates,
                    n_tup_del as deletes
                FROM pg_stat_user_tables
                WHERE schemaname = 'public'
                ORDER BY total_operations DESC
                LIMIT 10;
            """)

            table_stats = {}
            for row in cursor.fetchall():
                schema, table, total_ops, inserts, updates, deletes = row
                table_stats[table] = {
                    'total_operations': total_ops,
                    'inserts': inserts,
                    'updates': updates,
                    'deletes': deletes
                }

            db_health = {
                'status': 'healthy',
                'connection_time': round(connection_time, 3),
                'active_connections': active_connections,
                'table_stats': table_stats
            }

            conn.close()

        except Exception as e:
            db_health = {
                'status': 'unhealthy',
                'error': str(e)
            }

        return db_health

    def _generate_alerts(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate alerts based on metric thresholds"""
        alerts = []
        now = datetime.now()

        # System alerts
        system = metrics.get('system', {})

        if system.get('cpu_percent', 0) > self.alert_thresholds['cpu_usage']:
            alerts.append({
                'type': 'system',
                'severity': 'warning',
                'message': f"High CPU usage: {system['cpu_percent']:.1f}%",
                'value': system['cpu_percent'],
                'threshold': self.alert_thresholds['cpu_usage']
            })

        if system.get('memory_percent', 0) > self.alert_thresholds['memory_usage']:
            alerts.append({
                'type': 'system',
                'severity': 'warning',
                'message': f"High memory usage: {system['memory_percent']:.1f}%",
                'value': system['memory_percent'],
                'threshold': self.alert_thresholds['memory_usage']
            })

        if system.get('disk_percent', 0) > self.alert_thresholds['disk_usage']:
            alerts.append({
                'type': 'system',
                'severity': 'critical',
                'message': f"High disk usage: {system['disk_percent']:.1f}%",
                'value': system['disk_percent'],
                'threshold': self.alert_thresholds['disk_usage']
            })

        # Application alerts
        application = metrics.get('application', {})

        for service, health in application.items():
            if health.get('status') == 'unhealthy':
                alerts.append({
                    'type': 'application',
                    'severity': 'critical',
                    'message': f"Service {service} is unhealthy",
                    'service': service,
                    'error': health.get('error')
                })

            if health.get('response_time') and health['response_time'] > self.alert_thresholds['api_response_time']:
                alerts.append({
                    'type': 'application',
                    'severity': 'warning',
                    'message': f"Slow response time for {service}: {health['response_time']:.2f}s",
                    'service': service,
                    'value': health['response_time'],
                    'threshold': self.alert_thresholds['api_response_time']
                })

        # Database alerts
        database = metrics.get('database', {})

        if database.get('status') == 'unhealthy':
            alerts.append({
                'type': 'database',
                'severity': 'critical',
                'message': "Database is unhealthy",
                'error': database.get('error')
            })

        if database.get('connection_time') and database['connection_time'] > self.alert_thresholds['db_connection_time']:
            alerts.append({
                'type': 'database',
                'severity': 'warning',
                'message': f"Slow database connection: {database['connection_time']:.2f}s",
                'value': database['connection_time'],
                'threshold': self.alert_thresholds['db_connection_time']
            })

        return alerts

    def send_alert_notification(self, alert: Dict[str, Any]):
        """Send alert notification (log for now, can be extended to email/Slack)"""
        severity_emoji = {
            'info': 'ℹ️',
            'warning': '⚠️',
            'critical': '🚨'
        }

        emoji = severity_emoji.get(alert.get('severity', 'info'), '❓')
        message = f"{emoji} ALERT [{alert.get('severity', 'unknown').upper()}]: {alert.get('message', 'Unknown alert')}"

        # Log the alert
        if alert.get('severity') == 'critical':
            logger.error(message)
        elif alert.get('severity') == 'warning':
            logger.warning(message)
        else:
            logger.info(message)

        # Store alert history
        alert_key = f"{alert.get('type', 'unknown')}_{alert.get('message', '')}"
        self.alerts_sent[alert_key] = datetime.now()

    def perform_automated_maintenance(self, metrics: Dict[str, Any]):
        """Perform automated maintenance tasks"""
        maintenance_actions = []

        try:
            # Clean up old log files
            if self._should_cleanup_logs():
                self._cleanup_old_logs()
                maintenance_actions.append('log_cleanup')

            # Restart unhealthy services
            application = metrics.get('application', {})
            for service, health in application.items():
                if health.get('status') == 'unhealthy' and service in ['api_server', 'frontend_server']:
                    if self._should_restart_service(service):
                        self._restart_service(service)
                        maintenance_actions.append(f'restart_{service}')

            # Database maintenance
            if self._should_run_db_maintenance():
                self._run_database_maintenance()
                maintenance_actions.append('database_maintenance')

            if maintenance_actions:
                logger.info(f"Automated maintenance completed: {', '.join(maintenance_actions)}")

        except Exception as e:
            logger.error(f"Error during automated maintenance: {e}")

    def _should_cleanup_logs(self) -> bool:
        """Check if log cleanup is needed"""
        try:
            # Check if it's been more than 24 hours since last cleanup
            cleanup_marker = os.path.join(self.project_root, '.last_log_cleanup')
            if os.path.exists(cleanup_marker):
                last_cleanup = datetime.fromtimestamp(os.path.getmtime(cleanup_marker))
                return datetime.now() - last_cleanup > timedelta(hours=24)
            return True
        except:
            return True

    def _cleanup_old_logs(self):
        """Clean up old log files"""
        try:
            log_dirs = [
                os.path.join(self.project_root, 'miraikakakuapi'),
                os.path.join(self.project_root, 'miraikakakubatch'),
                '/var/log'
            ]

            for log_dir in log_dirs:
                if os.path.exists(log_dir):
                    # Find and truncate large log files
                    for root, dirs, files in os.walk(log_dir):
                        for file in files:
                            if file.endswith('.log'):
                                log_path = os.path.join(root, file)
                                try:
                                    size = os.path.getsize(log_path)
                                    if size > 100 * 1024 * 1024:  # 100MB
                                        subprocess.run(['tail', '-n', '1000', log_path],
                                                     stdout=open(f"{log_path}.tmp", 'w'))
                                        os.rename(f"{log_path}.tmp", log_path)
                                        logger.info(f"Truncated large log file: {log_path}")
                                except Exception as e:
                                    logger.warning(f"Could not process log file {log_path}: {e}")

            # Create cleanup marker
            cleanup_marker = os.path.join(self.project_root, '.last_log_cleanup')
            with open(cleanup_marker, 'w') as f:
                f.write(str(datetime.now().timestamp()))

        except Exception as e:
            logger.error(f"Error during log cleanup: {e}")

    def _should_restart_service(self, service: str) -> bool:
        """Check if service should be restarted"""
        restart_marker = os.path.join(self.project_root, f'.last_{service}_restart')
        if os.path.exists(restart_marker):
            last_restart = datetime.fromtimestamp(os.path.getmtime(restart_marker))
            return datetime.now() - last_restart > timedelta(minutes=30)
        return True

    def _restart_service(self, service: str):
        """Restart a specific service"""
        try:
            if service == 'api_server':
                # Kill existing API processes
                subprocess.run(['pkill', '-f', 'simple_api_server.py'], timeout=10)
                time.sleep(5)

                # Start new API server
                api_dir = os.path.join(self.project_root, 'miraikakakuapi')
                subprocess.Popen([
                    'python3', 'simple_api_server.py'
                ], cwd=api_dir, env={**os.environ, 'PORT': '8080'})

            elif service == 'frontend_server':
                # Kill existing frontend processes
                subprocess.run(['pkill', '-f', 'npm run dev'], timeout=10)
                time.sleep(5)

                # Start new frontend server
                frontend_dir = os.path.join(self.project_root, 'miraikakakufront')
                subprocess.Popen([
                    'npm', 'run', 'dev'
                ], cwd=frontend_dir, env={**os.environ, 'PORT': '3000'})

            # Create restart marker
            restart_marker = os.path.join(self.project_root, f'.last_{service}_restart')
            with open(restart_marker, 'w') as f:
                f.write(str(datetime.now().timestamp()))

            logger.info(f"Service {service} restarted successfully")

        except Exception as e:
            logger.error(f"Error restarting service {service}: {e}")

    def _should_run_db_maintenance(self) -> bool:
        """Check if database maintenance is needed"""
        maintenance_marker = os.path.join(self.project_root, '.last_db_maintenance')
        if os.path.exists(maintenance_marker):
            last_maintenance = datetime.fromtimestamp(os.path.getmtime(maintenance_marker))
            return datetime.now() - last_maintenance > timedelta(hours=12)
        return True

    def _run_database_maintenance(self):
        """Run database maintenance tasks"""
        try:
            conn = psycopg2.connect(**self.db_config)
            conn.autocommit = True
            cursor = conn.cursor()

            # Run ANALYZE on main tables
            tables = ['stock_prices', 'stock_predictions', 'stock_master']
            for table in tables:
                cursor.execute(f"ANALYZE {table};")
                logger.info(f"ANALYZE completed for table: {table}")

            conn.close()

            # Create maintenance marker
            maintenance_marker = os.path.join(self.project_root, '.last_db_maintenance')
            with open(maintenance_marker, 'w') as f:
                f.write(str(datetime.now().timestamp()))

            logger.info("Database maintenance completed successfully")

        except Exception as e:
            logger.error(f"Error during database maintenance: {e}")

    def save_metrics_history(self, metrics: Dict[str, Any]):
        """Save metrics to history file"""
        try:
            history_file = os.path.join(self.project_root, 'monitoring_history.jsonl')
            with open(history_file, 'a') as f:
                f.write(json.dumps(metrics) + '\n')

            # Keep only last 1000 entries
            if len(self.metrics_history) > 1000:
                self.metrics_history = self.metrics_history[-1000:]

        except Exception as e:
            logger.error(f"Error saving metrics history: {e}")

    def generate_health_report(self) -> Dict[str, Any]:
        """Generate comprehensive health report"""
        if not self.metrics_history:
            return {'error': 'No metrics history available'}

        latest_metrics = self.metrics_history[-1] if self.metrics_history else {}

        # Calculate trends from last 10 measurements
        recent_metrics = self.metrics_history[-10:] if len(self.metrics_history) >= 10 else self.metrics_history

        health_report = {
            'timestamp': datetime.now().isoformat(),
            'current_status': latest_metrics,
            'trends': self._calculate_trends(recent_metrics),
            'alerts_summary': self._get_alerts_summary(),
            'recommendations': self._generate_recommendations(latest_metrics)
        }

        return health_report

    def _calculate_trends(self, metrics_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate performance trends"""
        if len(metrics_list) < 2:
            return {}

        trends = {}

        # CPU trend
        cpu_values = [m.get('system', {}).get('cpu_percent', 0) for m in metrics_list]
        if cpu_values:
            trends['cpu'] = {
                'average': round(sum(cpu_values) / len(cpu_values), 2),
                'trend': 'increasing' if cpu_values[-1] > cpu_values[0] else 'decreasing'
            }

        # Memory trend
        memory_values = [m.get('system', {}).get('memory_percent', 0) for m in metrics_list]
        if memory_values:
            trends['memory'] = {
                'average': round(sum(memory_values) / len(memory_values), 2),
                'trend': 'increasing' if memory_values[-1] > memory_values[0] else 'decreasing'
            }

        return trends

    def _get_alerts_summary(self) -> Dict[str, Any]:
        """Get summary of recent alerts"""
        recent_alerts = []
        cutoff_time = datetime.now() - timedelta(hours=24)

        for alert_key, alert_time in self.alerts_sent.items():
            if alert_time > cutoff_time:
                recent_alerts.append({
                    'alert': alert_key,
                    'time': alert_time.isoformat()
                })

        return {
            'total_alerts_24h': len(recent_alerts),
            'recent_alerts': recent_alerts[-5:]  # Last 5 alerts
        }

    def _generate_recommendations(self, latest_metrics: Dict[str, Any]) -> List[str]:
        """Generate maintenance recommendations"""
        recommendations = []

        system = latest_metrics.get('system', {})
        application = latest_metrics.get('application', {})
        database = latest_metrics.get('database', {})

        if system.get('cpu_percent', 0) > 70:
            recommendations.append("Consider scaling up API instances due to high CPU usage")

        if system.get('memory_percent', 0) > 80:
            recommendations.append("Monitor memory usage - consider optimizing application memory consumption")

        if system.get('disk_percent', 0) > 80:
            recommendations.append("Disk space is running low - clean up old files or expand storage")

        for service, health in application.items():
            if health.get('response_time', 0) > 1.0:
                recommendations.append(f"Optimize {service} performance - response time is slow")

        if database.get('active_connections', 0) > 50:
            recommendations.append("High database connection count - review connection pooling")

        if not recommendations:
            recommendations.append("System is performing well - no immediate actions needed")

        return recommendations

    def run_continuous_monitoring(self):
        """Main continuous monitoring loop"""
        self.running = True
        logger.info(f"🔄 Starting continuous monitoring system (interval: {self.monitoring_interval}s)")

        while self.running:
            try:
                # Collect metrics
                metrics = self.collect_system_metrics()
                self.metrics_history.append(metrics)

                # Save to file
                self.save_metrics_history(metrics)

                # Send alerts
                for alert in metrics.get('alerts', []):
                    self.send_alert_notification(alert)

                # Perform maintenance
                self.perform_automated_maintenance(metrics)

                # Log summary
                system = metrics.get('system', {})
                logger.info(f"✅ Monitoring check: CPU={system.get('cpu_percent', 0):.1f}%, "
                          f"Memory={system.get('memory_percent', 0):.1f}%, "
                          f"Alerts={len(metrics.get('alerts', []))}")

                # Wait for next interval
                time.sleep(self.monitoring_interval)

            except KeyboardInterrupt:
                logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(60)  # Wait 1 minute before retrying

        self.running = False

    def stop_monitoring(self):
        """Stop the monitoring system"""
        self.running = False

def main():
    """Main function for standalone execution"""
    import argparse

    parser = argparse.ArgumentParser(description='Continuous Monitoring System')
    parser.add_argument('--interval', type=int, default=300, help='Monitoring interval in seconds')
    parser.add_argument('--report', action='store_true', help='Generate health report')
    parser.add_argument('--check', action='store_true', help='Run single health check')

    args = parser.parse_args()

    monitor = ContinuousMonitoringSystem()

    if args.report:
        report = monitor.generate_health_report()
        print(json.dumps(report, indent=2))
    elif args.check:
        metrics = monitor.collect_system_metrics()
        print(json.dumps(metrics, indent=2))
    else:
        monitor.monitoring_interval = args.interval
        monitor.run_continuous_monitoring()

if __name__ == "__main__":
    main()