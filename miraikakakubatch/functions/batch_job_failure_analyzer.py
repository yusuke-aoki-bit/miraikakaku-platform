#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import json
import logging
from datetime import datetime, timedelta

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BatchJobFailureAnalyzer:
    def __init__(self):
        pass

    def get_recent_failed_jobs(self):
        """最近の失敗ジョブ取得"""
        try:
            result = subprocess.run([
                'gcloud', 'batch', 'jobs', 'list',
                '--filter=status.state:FAILED',
                '--format=json',
                '--limit=10'
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                jobs = json.loads(result.stdout)
                logger.info(f"📊 最近の失敗ジョブ: {len(jobs)}件")
                return jobs
            else:
                logger.error(f"ジョブ取得失敗: {result.stderr}")
                return []
                
        except Exception as e:
            logger.error(f"失敗ジョブ取得エラー: {e}")
            return []

    def analyze_job_failure(self, job_name):
        """個別ジョブの失敗原因分析"""
        try:
            logger.info(f"🔍 ジョブ分析: {job_name}")
            
            # ジョブ詳細取得
            result = subprocess.run([
                'gcloud', 'batch', 'jobs', 'describe', job_name,
                '--format=json'
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                logger.error(f"ジョブ詳細取得失敗: {result.stderr}")
                return None
            
            job_detail = json.loads(result.stdout)
            
            # 状態とイベント確認
            status = job_detail.get('status', {})
            state = status.get('state', 'UNKNOWN')
            
            logger.info(f"   状態: {state}")
            
            # 失敗イベント確認
            status_events = status.get('statusEvents', [])
            
            failure_reasons = []
            for event in status_events:
                description = event.get('description', '')
                if 'failed' in description.lower() or 'error' in description.lower():
                    failure_reasons.append(description)
                    logger.info(f"   失敗理由: {description}")
            
            # タスク失敗詳細
            task_groups = status.get('taskGroups', {})
            for group_name, group_info in task_groups.items():
                task_count = group_info.get('taskCount', 0)
                failed_count = group_info.get('counts', {}).get('failed', 0)
                
                if failed_count > 0:
                    logger.info(f"   タスクグループ {group_name}: {failed_count}/{task_count} 失敗")
            
            return {
                'job_name': job_name,
                'state': state,
                'failure_reasons': failure_reasons,
                'task_failures': task_groups
            }
            
        except Exception as e:
            logger.error(f"ジョブ分析エラー {job_name}: {e}")
            return None

    def get_job_logs(self, job_name, limit=20):
        """ジョブログの取得"""
        try:
            logger.info(f"📋 ログ取得: {job_name}")
            
            # 直近24時間のログ取得
            since_time = (datetime.now() - timedelta(hours=24)).strftime('%Y-%m-%dT%H:%M:%SZ')
            
            result = subprocess.run([
                'gcloud', 'logging', 'read',
                f'resource.type=batch_task AND labels.job_id="{job_name.split("/")[-1]}"',
                f'--format=value(timestamp,severity,textPayload)',
                f'--limit={limit}',
                f'--freshness=24h'
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0 and result.stdout.strip():
                logs = result.stdout.strip().split('\n')
                logger.info(f"   ログ取得: {len(logs)}行")
                
                # エラーログを重点的に確認
                error_logs = []
                for log in logs:
                    if any(keyword in log.lower() for keyword in ['error', 'failed', 'exception', 'traceback']):
                        error_logs.append(log)
                
                if error_logs:
                    logger.info("   🚨 エラーログ:")
                    for error_log in error_logs[:5]:
                        logger.info(f"      {error_log[:100]}...")
                
                return logs
            else:
                logger.warning(f"   ⚠️ ログ取得失敗: {result.stderr}")
                return []
                
        except Exception as e:
            logger.error(f"ログ取得エラー {job_name}: {e}")
            return []

    def identify_common_failure_patterns(self, failed_jobs):
        """共通失敗パターンの特定"""
        logger.info("🔍 共通失敗パターン分析")
        
        failure_patterns = {}
        
        for job in failed_jobs:
            job_name = job.get('name', '').split('/')[-1]
            
            # ジョブ分析
            analysis = self.analyze_job_failure(job.get('name', ''))
            
            if analysis:
                for reason in analysis['failure_reasons']:
                    # パターンキーワード抽出
                    if 'ModuleNotFoundError' in reason:
                        pattern = 'ModuleNotFoundError'
                    elif 'timeout' in reason.lower():
                        pattern = 'Timeout'
                    elif 'exit code 1' in reason:
                        pattern = 'ExitCode1'
                    elif 'collation' in reason.lower():
                        pattern = 'CollationError'
                    else:
                        pattern = 'OtherError'
                    
                    failure_patterns[pattern] = failure_patterns.get(pattern, 0) + 1
        
        logger.info("📊 失敗パターン統計:")
        for pattern, count in sorted(failure_patterns.items(), key=lambda x: x[1], reverse=True):
            logger.info(f"   {pattern}: {count}件")
        
        return failure_patterns

    def comprehensive_batch_analysis(self):
        """包括的バッチ分析"""
        logger.info("🔍 包括的バッチジョブ失敗分析開始")
        
        # 1. 失敗ジョブ取得
        failed_jobs = self.get_recent_failed_jobs()
        
        if not failed_jobs:
            logger.info("✅ 最近の失敗ジョブなし")
            return
        
        # 2. 共通パターン分析
        patterns = self.identify_common_failure_patterns(failed_jobs)
        
        # 3. 個別詳細分析（最新5件）
        logger.info("=== 個別詳細分析 ===")
        for job in failed_jobs[:5]:
            job_name = job.get('name', '')
            self.analyze_job_failure(job_name)
            self.get_job_logs(job_name, limit=10)
        
        # 4. 推奨修正案
        logger.info("=== 推奨修正案 ===")
        
        if patterns.get('ModuleNotFoundError', 0) > 0:
            logger.info("📦 ModuleNotFoundError対策:")
            logger.info("   - Dockerfileの依存関係確認")
            logger.info("   - requirements.txtの更新")
            logger.info("   - コンテナイメージの再ビルド")
        
        if patterns.get('CollationError', 0) > 0:
            logger.info("🔤 CollationError対策:")
            logger.info("   - ✅ 既に修正済み（今回の修正）")
        
        if patterns.get('Timeout', 0) > 0:
            logger.info("⏰ Timeout対策:")
            logger.info("   - maxRunDurationの延長")
            logger.info("   - 処理バッチサイズの削減")
        
        if patterns.get('ExitCode1', 0) > 0:
            logger.info("💥 ExitCode1対策:")
            logger.info("   - エラーハンドリングの改善")
            logger.info("   - ログレベルの詳細化")

def main():
    analyzer = BatchJobFailureAnalyzer()
    analyzer.comprehensive_batch_analysis()

if __name__ == "__main__":
    main()