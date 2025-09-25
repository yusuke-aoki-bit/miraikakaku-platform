#!/usr/bin/env python3
"""
Cloud Scheduler最適化システム
Cloud Scheduler Optimization System

自動スケジューリングとバッチジョブ管理の完全自動化
"""

import json
import logging
from typing import Dict, List, Any
from datetime import datetime, timedelta
import subprocess
import os

logger = logging.getLogger(__name__)

class SchedulerOptimizer:
    """Cloud Scheduler最適化管理システム"""

    def __init__(self):
        self.project_id = "pricewise-huqkr"
        self.region = "us-central1"
        self.time_zone = "Asia/Tokyo"

    def create_scheduler_jobs(self) -> List[Dict[str, Any]]:
        """最適化されたスケジューラージョブを作成"""

        scheduler_configs = [
            {
                'name': 'daily-stock-data-update',
                'description': '毎日の株価データ更新（高優先度）',
                'schedule': '0 9 * * 1-5',  # 平日9:00 JST
                'target_uri': 'https://stock-data-updater-zbaru5v7za-uc.a.run.app/update',
                'http_method': 'POST',
                'timeout': '1800s',  # 30分
                'retry_count': 3,
                'max_backoff': '300s'
            },
            {
                'name': 'hourly-prediction-update',
                'description': '1時間ごとのAI予測更新',
                'schedule': '0 */1 * * *',  # 毎時0分
                'target_uri': 'https://lstm-predictions-v3-zbaru5v7za-uc.a.run.app/predict',
                'http_method': 'POST',
                'timeout': '900s',  # 15分
                'retry_count': 2,
                'max_backoff': '120s'
            },
            {
                'name': 'weekly-system-maintenance',
                'description': '週次システムメンテナンス',
                'schedule': '0 2 * * 0',  # 日曜日2:00 JST
                'target_uri': 'https://miraikakaku-api-zbaru5v7za-uc.a.run.app/maintenance',
                'http_method': 'POST',
                'timeout': '1800s',  # 30分（Cloud Schedulerの最大制限）
                'retry_count': 1,
                'max_backoff': '600s'
            },
            {
                'name': 'health-check-monitor',
                'description': '15分間隔ヘルスチェック',
                'schedule': '*/15 * * * *',  # 15分ごと
                'target_uri': 'https://miraikakaku-api-zbaru5v7za-uc.a.run.app/health',
                'http_method': 'GET',
                'timeout': '60s',
                'retry_count': 2,
                'max_backoff': '30s'
            }
        ]

        results = []
        for config in scheduler_configs:
            try:
                result = self.create_single_scheduler_job(config)
                results.append({
                    'name': config['name'],
                    'status': 'success' if result else 'failed',
                    'config': config
                })
                logger.info(f"Scheduler job created: {config['name']}")
            except Exception as e:
                results.append({
                    'name': config['name'],
                    'status': 'error',
                    'error': str(e),
                    'config': config
                })
                logger.error(f"Failed to create scheduler job {config['name']}: {e}")

        return results

    def create_single_scheduler_job(self, config: Dict[str, Any]) -> bool:
        """単一のスケジューラージョブを作成"""

        # gcloud コマンドを構築
        cmd = [
            'gcloud', 'scheduler', 'jobs', 'create', 'http',
            config['name'],
            f"--location={self.region}",
            f"--schedule={config['schedule']}",
            f"--uri={config['target_uri']}",
            f"--http-method={config['http_method']}",
            f"--time-zone={self.time_zone}",
            f"--attempt-deadline={config['timeout']}",
            f"--max-retry-attempts={config['retry_count']}",
            f"--max-backoff={config['max_backoff']}",
            f"--description={config['description']}",
            '--quiet'
        ]

        # POST リクエストの場合、ヘッダーとボディを追加
        if config['http_method'] == 'POST':
            cmd.extend([
                '--headers=Content-Type=application/json',
                '--message-body={"source":"cloud_scheduler","automated":true}'
            ])

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                logger.info(f"Successfully created scheduler job: {config['name']}")
                return True
            else:
                logger.error(f"gcloud command failed: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            logger.error(f"Timeout creating scheduler job: {config['name']}")
            return False
        except Exception as e:
            logger.error(f"Exception creating scheduler job {config['name']}: {e}")
            return False

    def get_scheduler_status(self) -> Dict[str, Any]:
        """現在のスケジューラー状況を取得"""
        try:
            cmd = [
                'gcloud', 'scheduler', 'jobs', 'list',
                f'--location={self.region}',
                '--format=json'
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                jobs = json.loads(result.stdout) if result.stdout else []
                return {
                    'status': 'success',
                    'total_jobs': len(jobs),
                    'jobs': jobs,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {
                    'status': 'error',
                    'message': result.stderr,
                    'timestamp': datetime.now().isoformat()
                }

        except Exception as e:
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def optimize_existing_jobs(self) -> List[Dict[str, Any]]:
        """既存ジョブの最適化"""
        status = self.get_scheduler_status()

        if status['status'] != 'success':
            return [{'error': 'Failed to fetch existing jobs', 'details': status}]

        optimizations = []

        for job in status.get('jobs', []):
            job_name = job.get('name', '').split('/')[-1]

            # 最適化提案を生成
            suggestions = self.analyze_job_performance(job)
            if suggestions:
                optimizations.append({
                    'job_name': job_name,
                    'current_config': job,
                    'suggestions': suggestions,
                    'priority': self.calculate_optimization_priority(suggestions)
                })

        return sorted(optimizations, key=lambda x: x['priority'], reverse=True)

    def analyze_job_performance(self, job: Dict[str, Any]) -> List[str]:
        """ジョブパフォーマンスを分析"""
        suggestions = []

        # スケジュール頻度のチェック
        schedule = job.get('schedule', '')
        if 'health-check' in job.get('name', '').lower():
            if '*/15' not in schedule:
                suggestions.append('ヘルスチェック間隔を15分に最適化推奨')

        # タイムアウト設定のチェック
        timeout = job.get('attemptDeadline', '')
        if 'prediction' in job.get('name', '').lower():
            if '900s' not in timeout:
                suggestions.append('予測ジョブのタイムアウトを15分に設定推奨')

        # リトライ設定のチェック
        retry_config = job.get('retryConfig', {})
        max_attempts = retry_config.get('maxRetryAttempts', 0)

        if 'update' in job.get('name', '').lower() and max_attempts < 3:
            suggestions.append('データ更新ジョブのリトライ回数を3回に増加推奨')

        return suggestions

    def calculate_optimization_priority(self, suggestions: List[str]) -> int:
        """最適化優先度を計算"""
        priority_keywords = {
            'タイムアウト': 5,
            'リトライ': 4,
            'ヘルスチェック': 3,
            '間隔': 2,
            '設定': 1
        }

        total_priority = 0
        for suggestion in suggestions:
            for keyword, value in priority_keywords.items():
                if keyword in suggestion:
                    total_priority += value

        return total_priority

def setup_production_scheduler():
    """本番環境スケジューラーセットアップ"""
    scheduler = SchedulerOptimizer()

    print("🚀 Starting Cloud Scheduler Optimization Setup")
    print("=" * 50)

    # 1. 現在の状況確認
    print("\n📊 Current Scheduler Status:")
    status = scheduler.get_scheduler_status()
    print(json.dumps(status, indent=2, default=str))

    # 2. 新しいジョブ作成
    print("\n🔧 Creating Optimized Scheduler Jobs:")
    results = scheduler.create_scheduler_jobs()

    for result in results:
        status_icon = "✅" if result['status'] == 'success' else "❌"
        print(f"{status_icon} {result['name']}: {result['status']}")

    # 3. 最適化提案
    print("\n💡 Optimization Suggestions:")
    optimizations = scheduler.optimize_existing_jobs()

    for opt in optimizations[:3]:  # Top 3 suggestions
        print(f"🎯 {opt['job_name']} (Priority: {opt['priority']})")
        for suggestion in opt['suggestions']:
            print(f"   • {suggestion}")

    print("\n✅ Cloud Scheduler Optimization Complete!")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    setup_production_scheduler()