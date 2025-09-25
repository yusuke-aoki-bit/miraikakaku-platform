#!/usr/bin/env python3
"""
Miraikakaku Batch Job Monitoring & Auto-Recovery System
バッチジョブの監視と自動復旧システム
"""

import os
import sys
import json
import time
import logging
import asyncio
import subprocess
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from enum import Enum
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/batch_monitor.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class JobStatus(Enum):
    QUEUED = "QUEUED"
    SCHEDULED = "SCHEDULED"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    UNKNOWN = "UNKNOWN"

@dataclass
class BatchJob:
    name: str
    status: JobStatus
    create_time: datetime
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    duration: Optional[float]
    failure_reason: Optional[str]
    retry_count: int = 0

@dataclass
class MonitoringConfig:
    project_id: str = "pricewise-huqkr"
    location: str = "us-central1"
    max_retry_count: int = 3
    health_check_interval: int = 300  # 5 minutes
    auto_recovery_enabled: bool = True
    alert_email: Optional[str] = None
    slack_webhook: Optional[str] = None

class BatchJobMonitor:
    """バッチジョブの監視と自動復旧を行うクラス"""

    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.jobs_history: List[BatchJob] = []
        self.last_check_time = datetime.now()
        self.consecutive_failures = 0

    async def get_batch_jobs(self) -> List[BatchJob]:
        """Google Cloud Batchからジョブ一覧を取得"""
        try:
            cmd = [
                "gcloud", "batch", "jobs", "list",
                f"--location={self.config.location}",
                "--format=json",
                "--sort-by=createTime",
                "--limit=50"
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            jobs_data = json.loads(result.stdout) if result.stdout else []

            jobs = []
            for job_data in jobs_data:
                job_name = job_data.get("name", "").split("/")[-1]
                status_str = job_data.get("status", {}).get("state", "UNKNOWN")

                # Parse timestamps
                create_time = self._parse_timestamp(job_data.get("createTime"))
                start_time = self._parse_timestamp(job_data.get("status", {}).get("startTime"))
                end_time = self._parse_timestamp(job_data.get("status", {}).get("endTime"))

                # Calculate duration
                duration = None
                if start_time and end_time:
                    duration = (end_time - start_time).total_seconds()

                # Get failure reason
                failure_reason = None
                if status_str == "FAILED":
                    status_events = job_data.get("status", {}).get("statusEvents", [])
                    for event in status_events:
                        if "FAILED" in event.get("description", ""):
                            failure_reason = event.get("description")
                            break

                job = BatchJob(
                    name=job_name,
                    status=JobStatus(status_str),
                    create_time=create_time,
                    start_time=start_time,
                    end_time=end_time,
                    duration=duration,
                    failure_reason=failure_reason
                )
                jobs.append(job)

            return jobs

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get batch jobs: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error getting batch jobs: {e}")
            return []

    def _parse_timestamp(self, timestamp_str: Optional[str]) -> Optional[datetime]:
        """タイムスタンプ文字列をdatetimeオブジェクトに変換"""
        if not timestamp_str:
            return None
        try:
            # Remove microseconds and timezone info for simple parsing
            clean_ts = timestamp_str.replace('Z', '').split('.')[0]
            return datetime.fromisoformat(clean_ts.replace('T', ' '))
        except:
            return None

    async def analyze_job_health(self, jobs: List[BatchJob]) -> Dict[str, Any]:
        """ジョブの健全性を分析"""
        now = datetime.now()
        recent_jobs = [j for j in jobs if j.create_time and (now - j.create_time).total_seconds() < 86400]  # Last 24 hours

        analysis = {
            "total_jobs": len(jobs),
            "recent_jobs_24h": len(recent_jobs),
            "failed_jobs": len([j for j in recent_jobs if j.status == JobStatus.FAILED]),
            "success_rate": 0,
            "avg_duration": 0,
            "consecutive_failures": self.consecutive_failures,
            "needs_intervention": False,
            "issues": []
        }

        if recent_jobs:
            successful_jobs = [j for j in recent_jobs if j.status == JobStatus.SUCCEEDED]
            analysis["success_rate"] = len(successful_jobs) / len(recent_jobs) * 100

            durations = [j.duration for j in successful_jobs if j.duration]
            if durations:
                analysis["avg_duration"] = sum(durations) / len(durations)

        # Check for issues
        if analysis["success_rate"] < 50:
            analysis["needs_intervention"] = True
            analysis["issues"].append("Low success rate (< 50%)")

        # Check for consecutive failures
        recent_sorted = sorted(recent_jobs, key=lambda x: x.create_time or datetime.min, reverse=True)
        consecutive_failures = 0
        for job in recent_sorted:
            if job.status == JobStatus.FAILED:
                consecutive_failures += 1
            else:
                break

        self.consecutive_failures = consecutive_failures
        if consecutive_failures >= 3:
            analysis["needs_intervention"] = True
            analysis["issues"].append(f"Consecutive failures: {consecutive_failures}")

        # Check for stale data
        latest_success = None
        for job in recent_sorted:
            if job.status == JobStatus.SUCCEEDED:
                latest_success = job.create_time
                break

        if latest_success and (now - latest_success).total_seconds() > 43200:  # 12 hours
            analysis["needs_intervention"] = True
            analysis["issues"].append("No successful jobs in last 12 hours")

        return analysis

    async def attempt_auto_recovery(self) -> bool:
        """自動復旧を試行"""
        if not self.config.auto_recovery_enabled:
            logger.info("Auto-recovery is disabled")
            return False

        logger.info("Attempting auto-recovery...")

        try:
            # Strategy 1: Submit a simple prediction job
            recovery_job_name = f"auto-recovery-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

            cmd = [
                "gcloud", "batch", "jobs", "submit",
                recovery_job_name,
                f"--location={self.config.location}",
                "--config=-"
            ]

            # Simple job configuration
            job_config = {
                "taskGroups": [{
                    "taskSpec": {
                        "runnables": [{
                            "script": {
                                "text": """#!/bin/bash
echo "Starting auto-recovery job..."
echo "Testing database connection..."
python3 -c "
import psycopg2
try:
    conn = psycopg2.connect(
        host='34.173.9.214',
        user='postgres',
        password='os.getenv('DB_PASSWORD', '')',
        database='miraikakaku'
    )
    print('Database connection: OK')
    conn.close()
except Exception as e:
    print(f'Database error: {e}')
    exit(1)
"
echo "Auto-recovery job completed successfully"
"""
                            }
                        }],
                        "computeResource": {
                            "cpuMilli": 1000,
                            "memoryMib": 1024
                        },
                        "maxRetryCount": 1,
                        "maxRunDuration": "600s"
                    },
                    "taskCount": 1,
                    "parallelism": 1
                }],
                "allocationPolicy": {
                    "instances": [{
                        "policy": {
                            "machineType": "e2-micro",
                            "provisioningModel": "STANDARD"
                        }
                    }]
                },
                "logsPolicy": {
                    "destination": "CLOUD_LOGGING"
                }
            }

            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            stdout, stderr = process.communicate(input=json.dumps(job_config))

            if process.returncode == 0:
                logger.info(f"Auto-recovery job submitted: {recovery_job_name}")
                return True
            else:
                logger.error(f"Failed to submit recovery job: {stderr}")
                return False

        except Exception as e:
            logger.error(f"Auto-recovery failed: {e}")
            return False

    async def send_alert(self, analysis: Dict[str, Any], jobs: List[BatchJob]):
        """アラート通知を送信"""
        message = self._format_alert_message(analysis, jobs)
        logger.warning(f"ALERT: {message}")

        # Email notification (if configured)
        if self.config.alert_email:
            await self._send_email_alert(message, analysis)

        # Slack notification (if configured)
        if self.config.slack_webhook:
            await self._send_slack_alert(message, analysis)

    def _format_alert_message(self, analysis: Dict[str, Any], jobs: List[BatchJob]) -> str:
        """アラートメッセージをフォーマット"""
        recent_failed = [j for j in jobs if j.status == JobStatus.FAILED][:5]

        message = f"""
🚨 BATCH JOB MONITORING ALERT 🚨

System Status: {'🔥 CRITICAL' if analysis['needs_intervention'] else '⚠️ WARNING'}
Success Rate: {analysis['success_rate']:.1f}%
Consecutive Failures: {analysis['consecutive_failures']}

Issues Detected:
{chr(10).join('• ' + issue for issue in analysis['issues'])}

Recent Failed Jobs:
{chr(10).join(f'• {job.name}: {job.failure_reason or "Unknown error"}' for job in recent_failed[:3])}

Timestamp: {datetime.now().isoformat()}
Project: {self.config.project_id}
Location: {self.config.location}
"""
        return message.strip()

    async def _send_email_alert(self, message: str, analysis: Dict[str, Any]):
        """メール通知を送信"""
        # Email implementation would go here
        logger.info("Email alert would be sent (not implemented)")

    async def _send_slack_alert(self, message: str, analysis: Dict[str, Any]):
        """Slack通知を送信"""
        # Slack webhook implementation would go here
        logger.info("Slack alert would be sent (not implemented)")

    async def run_monitoring_cycle(self):
        """監視サイクルを実行"""
        logger.info("Starting batch job monitoring cycle...")

        # Get current jobs
        jobs = await self.get_batch_jobs()
        if not jobs:
            logger.warning("No jobs found or failed to retrieve jobs")
            return

        # Analyze health
        analysis = await self.analyze_job_health(jobs)

        logger.info(f"Health Analysis: Success Rate: {analysis['success_rate']:.1f}%, "
                   f"Failed Jobs: {analysis['failed_jobs']}, "
                   f"Consecutive Failures: {analysis['consecutive_failures']}")

        # Check if intervention is needed
        if analysis['needs_intervention']:
            logger.warning("System requires intervention!")
            await self.send_alert(analysis, jobs)

            # Attempt auto-recovery
            if self.consecutive_failures >= 3:
                recovery_success = await self.attempt_auto_recovery()
                if recovery_success:
                    logger.info("Auto-recovery initiated")
                    self.consecutive_failures = 0  # Reset counter on recovery attempt

        self.last_check_time = datetime.now()
        logger.info("Monitoring cycle completed")

class BatchMonitoringService:
    """バッチ監視サービスのメインクラス"""

    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.monitor = BatchJobMonitor(config)
        self.running = False

    async def start(self):
        """監視サービスを開始"""
        self.running = True
        logger.info("Batch monitoring service started")

        while self.running:
            try:
                await self.monitor.run_monitoring_cycle()
                await asyncio.sleep(self.config.health_check_interval)
            except KeyboardInterrupt:
                logger.info("Monitoring service interrupted by user")
                break
            except Exception as e:
                logger.error(f"Error in monitoring cycle: {e}")
                await asyncio.sleep(60)  # Wait before retry

    def stop(self):
        """監視サービスを停止"""
        self.running = False
        logger.info("Batch monitoring service stopped")

async def main():
    """メイン実行関数"""
    config = MonitoringConfig(
        health_check_interval=300,  # 5 minutes
        auto_recovery_enabled=True,
        max_retry_count=3
    )

    service = BatchMonitoringService(config)

    try:
        await service.start()
    except KeyboardInterrupt:
        logger.info("Service interrupted")
    finally:
        service.stop()

if __name__ == "__main__":
    asyncio.run(main())