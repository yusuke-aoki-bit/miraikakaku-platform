#!/usr/bin/env python3
"""
GCP Batch Job Monitor for Miraikakaku
Monitor and alert on batch job status
"""

import os
import json
import logging
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import subprocess
import requests
from dataclasses import dataclass

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class BatchJobStatus:
    job_name: str
    status: str
    create_time: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    duration: Optional[str] = None
    exit_code: Optional[int] = None
    error_message: Optional[str] = None

class BatchJobMonitor:
    def __init__(self, project_id: str = "pricewise-huqkr", location: str = "us-central1"):
        self.project_id = project_id
        self.location = location
        self.webhook_url = os.getenv('SLACK_WEBHOOK_URL')  # Optional Slack notifications

    def get_batch_jobs(self, limit: int = 50) -> List[BatchJobStatus]:
        """Get list of batch jobs from GCP"""
        try:
            # Use gcloud CLI to get batch jobs
            cmd = [
                'gcloud', 'batch', 'jobs', 'list',
                '--location', self.location,
                '--limit', str(limit),
                '--format', 'json'
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode != 0:
                logger.error(f"Failed to get batch jobs: {result.stderr}")
                return []

            jobs_data = json.loads(result.stdout) if result.stdout else []
            jobs = []

            for job_data in jobs_data:
                try:
                    job = BatchJobStatus(
                        job_name=job_data.get('name', '').split('/')[-1],
                        status=job_data.get('status', {}).get('state', 'UNKNOWN'),
                        create_time=job_data.get('createTime', ''),
                        start_time=job_data.get('status', {}).get('runDuration', {}).get('startTime'),
                        end_time=job_data.get('status', {}).get('runDuration', {}).get('endTime')
                    )

                    # Calculate duration if available
                    if job.start_time and job.end_time:
                        start = datetime.fromisoformat(job.start_time.replace('Z', '+00:00'))
                        end = datetime.fromisoformat(job.end_time.replace('Z', '+00:00'))
                        duration = end - start
                        job.duration = str(duration)

                    jobs.append(job)

                except Exception as e:
                    logger.warning(f"Error parsing job data: {e}")
                    continue

            return jobs

        except subprocess.TimeoutExpired:
            logger.error("Timeout while getting batch jobs")
            return []
        except Exception as e:
            logger.error(f"Error getting batch jobs: {e}")
            return []

    def get_job_details(self, job_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific job"""
        try:
            cmd = [
                'gcloud', 'batch', 'jobs', 'describe', job_name,
                '--location', self.location,
                '--format', 'json'
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode != 0:
                logger.error(f"Failed to get job details for {job_name}: {result.stderr}")
                return None

            return json.loads(result.stdout) if result.stdout else None

        except Exception as e:
            logger.error(f"Error getting job details for {job_name}: {e}")
            return None

    def get_job_logs(self, job_name: str, lines: int = 100) -> List[str]:
        """Get logs for a specific job"""
        try:
            # Get logs using gcloud logging
            cmd = [
                'gcloud', 'logging', 'read',
                f'resource.type="gce_instance" AND labels."batch.googleapis.com/job_name"="{job_name}"',
                '--limit', str(lines),
                '--format', 'value(textPayload,jsonPayload.message)',
                '--freshness', '7d'
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode != 0:
                logger.warning(f"Failed to get logs for {job_name}: {result.stderr}")
                return []

            logs = result.stdout.strip().split('\n') if result.stdout else []
            return [log for log in logs if log.strip()]

        except Exception as e:
            logger.error(f"Error getting logs for {job_name}: {e}")
            return []

    def check_job_health(self) -> Dict[str, Any]:
        """Check overall health of batch jobs"""
        jobs = self.get_batch_jobs()

        if not jobs:
            return {
                'status': 'unknown',
                'message': 'Could not retrieve job information',
                'jobs_total': 0,
                'jobs_running': 0,
                'jobs_failed': 0,
                'jobs_succeeded': 0
            }

        # Count job statuses
        status_counts = {
            'RUNNING': 0,
            'SUCCEEDED': 0,
            'FAILED': 0,
            'QUEUED': 0,
            'OTHER': 0
        }

        failed_jobs = []
        long_running_jobs = []

        for job in jobs:
            status = job.status.upper()
            if status in status_counts:
                status_counts[status] += 1
            else:
                status_counts['OTHER'] += 1

            # Check for failed jobs
            if status == 'FAILED':
                failed_jobs.append(job.job_name)

            # Check for long-running jobs (> 2 hours)
            if status == 'RUNNING' and job.start_time:
                try:
                    start = datetime.fromisoformat(job.start_time.replace('Z', '+00:00'))
                    duration = datetime.now().replace(tzinfo=start.tzinfo) - start
                    if duration > timedelta(hours=2):
                        long_running_jobs.append({
                            'job_name': job.job_name,
                            'duration': str(duration)
                        })
                except Exception:
                    pass

        # Determine overall health
        health_status = 'healthy'
        issues = []

        if failed_jobs:
            health_status = 'degraded'
            issues.append(f"{len(failed_jobs)} failed job(s)")

        if long_running_jobs:
            if health_status == 'healthy':
                health_status = 'warning'
            issues.append(f"{len(long_running_jobs)} long-running job(s)")

        if status_counts['RUNNING'] == 0 and status_counts['QUEUED'] == 0:
            if health_status == 'healthy':
                health_status = 'warning'
            issues.append("No active jobs")

        return {
            'status': health_status,
            'message': '; '.join(issues) if issues else 'All batch jobs are healthy',
            'jobs_total': len(jobs),
            'jobs_running': status_counts['RUNNING'],
            'jobs_failed': status_counts['FAILED'],
            'jobs_succeeded': status_counts['SUCCEEDED'],
            'jobs_queued': status_counts['QUEUED'],
            'failed_jobs': failed_jobs,
            'long_running_jobs': long_running_jobs,
            'timestamp': datetime.now().isoformat()
        }

    def send_alert(self, alert_data: Dict[str, Any]):
        """Send alert notification"""
        logger.info(f"ALERT: {alert_data}")

        # Send to Slack if webhook URL is configured
        if self.webhook_url:
            try:
                payload = {
                    "text": f"🚨 Batch Job Alert: {alert_data.get('message', 'Unknown issue')}",
                    "attachments": [
                        {
                            "color": "danger" if alert_data.get('status') == 'degraded' else "warning",
                            "fields": [
                                {
                                    "title": "Status",
                                    "value": alert_data.get('status', 'unknown'),
                                    "short": True
                                },
                                {
                                    "title": "Total Jobs",
                                    "value": str(alert_data.get('jobs_total', 0)),
                                    "short": True
                                },
                                {
                                    "title": "Failed Jobs",
                                    "value": str(alert_data.get('jobs_failed', 0)),
                                    "short": True
                                },
                                {
                                    "title": "Running Jobs",
                                    "value": str(alert_data.get('jobs_running', 0)),
                                    "short": True
                                }
                            ]
                        }
                    ]
                }

                response = requests.post(self.webhook_url, json=payload, timeout=10)
                if response.status_code == 200:
                    logger.info("Alert sent to Slack successfully")
                else:
                    logger.error(f"Failed to send alert to Slack: {response.status_code}")

            except Exception as e:
                logger.error(f"Error sending Slack alert: {e}")

    def monitor_continuously(self, check_interval: int = 300, alert_threshold: int = 3):
        """Continuously monitor batch jobs and send alerts"""
        consecutive_issues = 0
        last_alert_time = None

        logger.info(f"Starting continuous batch job monitoring (check every {check_interval}s)")

        while True:
            try:
                health = self.check_job_health()

                logger.info(f"Batch job health check: {health['status']} - {health['message']}")

                # Check if we need to send an alert
                if health['status'] in ['degraded', 'warning']:
                    consecutive_issues += 1

                    # Send alert if we've had issues for multiple consecutive checks
                    # and we haven't sent an alert in the last hour
                    should_alert = (
                        consecutive_issues >= alert_threshold and
                        (last_alert_time is None or
                         datetime.now() - last_alert_time > timedelta(hours=1))
                    )

                    if should_alert:
                        self.send_alert(health)
                        last_alert_time = datetime.now()
                        consecutive_issues = 0  # Reset counter after sending alert

                else:
                    consecutive_issues = 0  # Reset if healthy

                time.sleep(check_interval)

            except KeyboardInterrupt:
                logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(60)  # Wait a minute before retrying

def main():
    """Main function for standalone execution"""
    import argparse

    parser = argparse.ArgumentParser(description='Monitor GCP Batch Jobs')
    parser.add_argument('--project', default='pricewise-huqkr', help='GCP Project ID')
    parser.add_argument('--location', default='us-central1', help='GCP Location')
    parser.add_argument('--continuous', action='store_true', help='Run continuous monitoring')
    parser.add_argument('--interval', type=int, default=300, help='Check interval in seconds')
    parser.add_argument('--job-name', help='Get details for specific job')
    parser.add_argument('--logs', help='Get logs for specific job')

    args = parser.parse_args()

    monitor = BatchJobMonitor(args.project, args.location)

    if args.job_name:
        # Get specific job details
        details = monitor.get_job_details(args.job_name)
        if details:
            print(json.dumps(details, indent=2))
        else:
            print(f"Job {args.job_name} not found")

    elif args.logs:
        # Get logs for specific job
        logs = monitor.get_job_logs(args.logs)
        for log in logs:
            print(log)

    elif args.continuous:
        # Run continuous monitoring
        monitor.monitor_continuously(args.interval)

    else:
        # Single health check
        health = monitor.check_job_health()
        print(json.dumps(health, indent=2))

if __name__ == "__main__":
    main()