#!/usr/bin/env python3
"""
Cloud Batch Monitor for LSTM & VertexAI Jobs
Cloud BatchのLSTM & VertexAIジョブ監視システム
"""

import time
import logging
import subprocess
import json
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CloudBatchMonitor:
    """Cloud Batch監視システム"""

    def __init__(self, project_id="pricewise-huqkr", location="us-central1"):
        self.project_id = project_id
        self.location = location

    def get_lstm_jobs_status(self):
        """LSTM関連ジョブのステータス取得"""
        try:
            cmd = [
                "gcloud", "batch", "jobs", "list",
                f"--location={self.location}",
                "--filter=name~stable-lstm-vertexai",
                "--format=json"
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            jobs = json.loads(result.stdout) if result.stdout else []

            return jobs

        except Exception as e:
            logger.error(f"❌ Failed to get job status: {e}")
            return []

    def check_job_logs(self, job_name: str):
        """ジョブのログ確認"""
        try:
            cmd = [
                "gcloud", "logging", "read",
                f"resource.type=batch_task AND resource.labels.job_id={job_name}",
                "--limit=10",
                "--format=value(textPayload)"
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.stdout.strip() if result.stdout else "No logs available"

        except Exception as e:
            logger.error(f"❌ Failed to get logs for {job_name}: {e}")
            return f"Log error: {e}"

    def monitor_jobs(self):
        """継続的ジョブ監視"""
        logger.info("🔍 Cloud Batch LSTM & VertexAI Jobs Monitor Starting")
        logger.info("="*60)

        while True:
            try:
                jobs = self.get_lstm_jobs_status()

                if not jobs:
                    logger.info("⚠️ No LSTM jobs found")
                    time.sleep(60)
                    continue

                logger.info(f"📊 Found {len(jobs)} LSTM jobs")

                running_count = 0
                succeeded_count = 0
                failed_count = 0

                for job in jobs:
                    job_name = job.get('name', 'unknown').split('/')[-1]
                    state = job.get('status', {}).get('state', 'unknown')
                    create_time = job.get('createTime', 'unknown')

                    logger.info(f"  📋 {job_name}: {state} (created: {create_time[:19]})")

                    if state == "RUNNING":
                        running_count += 1
                        # 実行中ジョブのログ確認
                        recent_logs = self.check_job_logs(job_name)
                        if recent_logs and "LSTM" in recent_logs:
                            logger.info(f"    🧠 LSTM activity detected")
                    elif state == "SUCCEEDED":
                        succeeded_count += 1
                    elif state == "FAILED":
                        failed_count += 1
                        # 失敗ジョブの詳細ログ確認
                        error_logs = self.check_job_logs(job_name)
                        if error_logs:
                            logger.warning(f"    ❌ Error: {error_logs[:100]}...")

                # サマリー表示
                logger.info(f"📈 Status Summary: {running_count} running, {succeeded_count} succeeded, {failed_count} failed")

                # 新しいジョブが必要かチェック
                if running_count == 0 and succeeded_count < 3:
                    logger.info("🚀 Need more LSTM jobs, deploying additional batch...")
                    self.deploy_additional_jobs()

                logger.info("="*60)
                time.sleep(120)  # 2分間隔で監視

            except KeyboardInterrupt:
                logger.info("👋 Monitor stopped by user")
                break
            except Exception as e:
                logger.error(f"❌ Monitor error: {e}")
                time.sleep(60)

    def deploy_additional_jobs(self):
        """追加ジョブのデプロイ"""
        try:
            from stable_cloud_batch_lstm import StableCloudBatchLSTM
            system = StableCloudBatchLSTM()
            system.deploy_multiple_stable_jobs(num_jobs=2)
            logger.info("✅ Additional LSTM jobs deployed")
        except Exception as e:
            logger.error(f"❌ Failed to deploy additional jobs: {e}")

def main():
    """メイン実行"""
    monitor = CloudBatchMonitor()
    monitor.monitor_jobs()

if __name__ == "__main__":
    main()