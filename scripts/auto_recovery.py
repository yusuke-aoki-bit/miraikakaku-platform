#!/usr/bin/env python3
"""
Auto Recovery System for Miraikakaku
Automated recovery for common system failures
"""

import os
import time
import logging
import subprocess
import psycopg2
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import requests
import json

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s'
)
logger = logging.getLogger(__name__)

class AutoRecoverySystem:
    def __init__(self):
        self.db_config = {
            'host': '34.173.9.214',
            'user': 'postgres',
            'password': os.getenv('DB_PASSWORD'),
            'database': 'miraikakaku'
        }
        self.api_url = 'http://localhost:8080'
        self.frontend_url = 'http://localhost:3000'
        self.recovery_attempts = {}
        self.max_recovery_attempts = 3
        self.recovery_cooldown = 300  # 5 minutes

    def can_attempt_recovery(self, service_name: str) -> bool:
        """Check if recovery can be attempted for a service"""
        now = datetime.now()
        if service_name not in self.recovery_attempts:
            self.recovery_attempts[service_name] = {'count': 0, 'last_attempt': None}

        attempts = self.recovery_attempts[service_name]

        # Reset counter if enough time has passed
        if attempts['last_attempt'] and now - attempts['last_attempt'] > timedelta(seconds=self.recovery_cooldown):
            attempts['count'] = 0

        return attempts['count'] < self.max_recovery_attempts

    def record_recovery_attempt(self, service_name: str):
        """Record a recovery attempt"""
        now = datetime.now()
        if service_name not in self.recovery_attempts:
            self.recovery_attempts[service_name] = {'count': 0, 'last_attempt': None}

        self.recovery_attempts[service_name]['count'] += 1
        self.recovery_attempts[service_name]['last_attempt'] = now

    def test_database_connection(self) -> bool:
        """Test database connectivity"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            conn.close()
            return result is not None
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False

    def test_api_health(self) -> bool:
        """Test API server health"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"API health check failed: {e}")
            return False

    def test_frontend_health(self) -> bool:
        """Test frontend server health"""
        try:
            response = requests.get(self.frontend_url, timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Frontend health check failed: {e}")
            return False

    def restart_api_server(self) -> bool:
        """Restart the API server"""
        try:
            logger.info("Attempting to restart API server...")

            # Kill existing API processes
            try:
                subprocess.run(['pkill', '-f', 'simple_api_server.py'], timeout=10)
                time.sleep(5)
            except subprocess.TimeoutExpired:
                logger.warning("Timeout while killing API processes")

            # Start new API server
            api_dir = '/mnt/c/Users/yuuku/cursor/miraikakaku/miraikakakuapi'
            cmd = ['python3', 'simple_api_server.py']

            subprocess.Popen(
                cmd,
                cwd=api_dir,
                env={**os.environ, 'PORT': '8080'},
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            # Wait and test
            time.sleep(10)
            if self.test_api_health():
                logger.info("✅ API server restarted successfully")
                return True
            else:
                logger.error("❌ API server restart failed - health check failed")
                return False

        except Exception as e:
            logger.error(f"❌ Error restarting API server: {e}")
            return False

    def restart_frontend_server(self) -> bool:
        """Restart the frontend server"""
        try:
            logger.info("Attempting to restart frontend server...")

            # Kill existing frontend processes
            try:
                subprocess.run(['pkill', '-f', 'npm run dev'], timeout=10)
                time.sleep(5)
            except subprocess.TimeoutExpired:
                logger.warning("Timeout while killing frontend processes")

            # Start new frontend server
            frontend_dir = '/mnt/c/Users/yuuku/cursor/miraikakaku/miraikakakufront'
            cmd = ['npm', 'run', 'dev']

            subprocess.Popen(
                cmd,
                cwd=frontend_dir,
                env={**os.environ, 'PORT': '3000'},
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            # Wait and test
            time.sleep(15)
            if self.test_frontend_health():
                logger.info("✅ Frontend server restarted successfully")
                return True
            else:
                logger.error("❌ Frontend server restart failed - health check failed")
                return False

        except Exception as e:
            logger.error(f"❌ Error restarting frontend server: {e}")
            return False

    def restart_failed_batch_jobs(self) -> bool:
        """Restart failed batch jobs"""
        try:
            logger.info("Checking for failed batch jobs...")

            # Get list of failed jobs
            cmd = [
                'gcloud', 'batch', 'jobs', 'list',
                '--location', 'us-central1',
                '--filter', 'status.state=FAILED',
                '--format', 'value(name)',
                '--limit', '10'
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode != 0:
                logger.error(f"Failed to list batch jobs: {result.stderr}")
                return False

            failed_jobs = result.stdout.strip().split('\n') if result.stdout.strip() else []

            if not failed_jobs:
                logger.info("No failed batch jobs found")
                return True

            logger.info(f"Found {len(failed_jobs)} failed batch jobs")

            # Delete failed jobs (they can be recreated by the batch system)
            for job_name in failed_jobs:
                job_name = job_name.split('/')[-1]  # Extract job name from full path
                try:
                    delete_cmd = [
                        'gcloud', 'batch', 'jobs', 'delete', job_name,
                        '--location', 'us-central1',
                        '--quiet'
                    ]

                    subprocess.run(delete_cmd, timeout=30)
                    logger.info(f"Deleted failed job: {job_name}")

                except Exception as e:
                    logger.warning(f"Could not delete failed job {job_name}: {e}")

            return True

        except Exception as e:
            logger.error(f"Error handling failed batch jobs: {e}")
            return False

    def clear_cache_and_temp_files(self) -> bool:
        """Clear temporary files and caches"""
        try:
            logger.info("Clearing cache and temporary files...")

            # Clear Next.js cache
            frontend_dir = '/mnt/c/Users/yuuku/cursor/miraikakaku/miraikakakufront'
            cache_dirs = ['.next/cache', '.next/static', 'node_modules/.cache']

            for cache_dir in cache_dirs:
                cache_path = os.path.join(frontend_dir, cache_dir)
                if os.path.exists(cache_path):
                    try:
                        subprocess.run(['rm', '-rf', cache_path], timeout=30)
                        logger.info(f"Cleared cache: {cache_dir}")
                    except Exception as e:
                        logger.warning(f"Could not clear cache {cache_dir}: {e}")

            # Clear API log files if they're too large (> 100MB)
            log_files = ['miraikakaku_api.log', 'miraikakaku_errors.log']
            api_dir = '/mnt/c/Users/yuuku/cursor/miraikakaku/miraikakakuapi'

            for log_file in log_files:
                log_path = os.path.join(api_dir, log_file)
                if os.path.exists(log_path):
                    try:
                        size = os.path.getsize(log_path)
                        if size > 100 * 1024 * 1024:  # 100MB
                            # Keep last 1000 lines
                            subprocess.run([
                                'tail', '-n', '1000', log_path
                            ], stdout=open(f"{log_path}.tmp", 'w'), timeout=30)
                            os.rename(f"{log_path}.tmp", log_path)
                            logger.info(f"Truncated large log file: {log_file}")
                    except Exception as e:
                        logger.warning(f"Could not process log file {log_file}: {e}")

            return True

        except Exception as e:
            logger.error(f"Error clearing cache and temp files: {e}")
            return False

    def check_and_recover(self) -> Dict[str, Any]:
        """Main recovery function"""
        recovery_report = {
            'timestamp': datetime.now().isoformat(),
            'checks_performed': [],
            'recoveries_attempted': [],
            'successes': [],
            'failures': [],
            'overall_status': 'healthy'
        }

        logger.info("🔧 Starting automated recovery check...")

        # Check database connection
        recovery_report['checks_performed'].append('database_connection')
        if not self.test_database_connection():
            logger.warning("⚠️  Database connection failed")
            recovery_report['overall_status'] = 'degraded'
            recovery_report['failures'].append('database_connection_failed')
        else:
            logger.info("✅ Database connection healthy")

        # Check API server
        recovery_report['checks_performed'].append('api_server')
        if not self.test_api_health():
            logger.warning("⚠️  API server health check failed")

            if self.can_attempt_recovery('api_server'):
                recovery_report['recoveries_attempted'].append('api_server_restart')
                self.record_recovery_attempt('api_server')

                if self.restart_api_server():
                    recovery_report['successes'].append('api_server_restarted')
                    logger.info("✅ API server recovery successful")
                else:
                    recovery_report['failures'].append('api_server_restart_failed')
                    recovery_report['overall_status'] = 'degraded'
            else:
                recovery_report['failures'].append('api_server_recovery_limit_reached')
                recovery_report['overall_status'] = 'degraded'
        else:
            logger.info("✅ API server healthy")

        # Check frontend server
        recovery_report['checks_performed'].append('frontend_server')
        if not self.test_frontend_health():
            logger.warning("⚠️  Frontend server health check failed")

            if self.can_attempt_recovery('frontend_server'):
                recovery_report['recoveries_attempted'].append('frontend_server_restart')
                self.record_recovery_attempt('frontend_server')

                if self.restart_frontend_server():
                    recovery_report['successes'].append('frontend_server_restarted')
                    logger.info("✅ Frontend server recovery successful")
                else:
                    recovery_report['failures'].append('frontend_server_restart_failed')
                    recovery_report['overall_status'] = 'degraded'
            else:
                recovery_report['failures'].append('frontend_server_recovery_limit_reached')
                recovery_report['overall_status'] = 'degraded'
        else:
            logger.info("✅ Frontend server healthy")

        # Check and clean up failed batch jobs
        recovery_report['checks_performed'].append('batch_jobs')
        if self.can_attempt_recovery('batch_jobs'):
            recovery_report['recoveries_attempted'].append('batch_job_cleanup')
            self.record_recovery_attempt('batch_jobs')

            if self.restart_failed_batch_jobs():
                recovery_report['successes'].append('batch_jobs_cleaned')
                logger.info("✅ Batch job cleanup successful")
            else:
                recovery_report['failures'].append('batch_job_cleanup_failed')

        # Clear cache and temp files
        recovery_report['checks_performed'].append('cache_cleanup')
        recovery_report['recoveries_attempted'].append('cache_cleanup')
        if self.clear_cache_and_temp_files():
            recovery_report['successes'].append('cache_cleared')
            logger.info("✅ Cache cleanup successful")
        else:
            recovery_report['failures'].append('cache_cleanup_failed')

        # Summary
        if recovery_report['failures']:
            recovery_report['overall_status'] = 'degraded'
            logger.warning(f"🚨 Recovery completed with issues: {recovery_report['failures']}")
        else:
            logger.info("✅ All recovery checks completed successfully")

        return recovery_report

    def run_continuous_monitoring(self, check_interval: int = 600):
        """Run continuous monitoring with auto-recovery"""
        logger.info(f"🔄 Starting continuous auto-recovery monitoring (check every {check_interval}s)")

        while True:
            try:
                report = self.check_and_recover()

                # Log summary
                logger.info(f"Recovery check complete - Status: {report['overall_status']}")
                if report['successes']:
                    logger.info(f"Recoveries performed: {', '.join(report['successes'])}")

                time.sleep(check_interval)

            except KeyboardInterrupt:
                logger.info("Continuous monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(60)  # Wait 1 minute before retrying

def main():
    """Main function for standalone execution"""
    import argparse

    parser = argparse.ArgumentParser(description='Auto Recovery System for Miraikakaku')
    parser.add_argument('--continuous', action='store_true', help='Run continuous monitoring')
    parser.add_argument('--interval', type=int, default=600, help='Check interval in seconds')
    parser.add_argument('--check-db', action='store_true', help='Test database connection only')
    parser.add_argument('--check-api', action='store_true', help='Test API server only')
    parser.add_argument('--check-frontend', action='store_true', help='Test frontend server only')

    args = parser.parse_args()

    recovery_system = AutoRecoverySystem()

    if args.check_db:
        result = recovery_system.test_database_connection()
        print(f"Database connection: {'✅ OK' if result else '❌ FAILED'}")

    elif args.check_api:
        result = recovery_system.test_api_health()
        print(f"API server: {'✅ OK' if result else '❌ FAILED'}")

    elif args.check_frontend:
        result = recovery_system.test_frontend_health()
        print(f"Frontend server: {'✅ OK' if result else '❌ FAILED'}")

    elif args.continuous:
        recovery_system.run_continuous_monitoring(args.interval)

    else:
        # Single recovery check
        report = recovery_system.check_and_recover()
        print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()