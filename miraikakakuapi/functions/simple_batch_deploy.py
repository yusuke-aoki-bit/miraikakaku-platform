#!/usr/bin/env python3
"""
シンプルCloud Run バッチデプロイ - 単一サービスでテスト
"""

import subprocess
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def deploy_single_batch():
    """単一バッチサービスをCloud Runにデプロイ"""
    
    logger.info("🚀 シンプルバッチサービスデプロイ開始")
    
    # プロジェクトとリージョン設定
    project_id = 'pricewise-huqkr'
    region = 'us-central1'
    service_name = 'miraikakaku-batch'
    
    try:
        # Cloud Run デプロイコマンド
        cmd = [
            'gcloud', 'run', 'deploy', service_name,
            '--source', '.',
            '--platform', 'managed',
            '--region', region,
            '--project', project_id,
            '--memory', '2Gi',
            '--cpu', '2',
            '--timeout', '3600s',
            '--concurrency', '1',
            '--max-instances', '3',
            '--min-instances', '0',
            '--port', '8080',
            '--allow-unauthenticated',
            '--quiet'
        ]
        
        logger.info("📦 Cloud Run デプロイ実行中...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
        
        if result.returncode == 0:
            logger.info("✅ デプロイ成功!")
            
            # サービスURL取得
            url_cmd = [
                'gcloud', 'run', 'services', 'describe', service_name,
                '--region', region, '--project', project_id,
                '--format', 'value(status.url)'
            ]
            url_result = subprocess.run(url_cmd, capture_output=True, text=True)
            
            if url_result.returncode == 0:
                service_url = url_result.stdout.strip()
                logger.info(f"🌐 サービスURL: {service_url}")
                
                # テストリクエスト
                test_cmd = ['curl', '-X', 'POST', service_url, '-H', 'Content-Type: application/json']
                logger.info("🧪 サービステスト中...")
                
                test_result = subprocess.run(test_cmd, capture_output=True, text=True, timeout=30)
                if test_result.returncode == 0:
                    logger.info("✅ サービス正常動作確認")
                else:
                    logger.warning(f"⚠️  テスト失敗: {test_result.stderr}")
                
                return service_url
            else:
                logger.error("URL取得失敗")
        else:
            logger.error(f"❌ デプロイ失敗:")
            logger.error(f"STDOUT: {result.stdout}")
            logger.error(f"STDERR: {result.stderr}")
            return None
            
    except subprocess.TimeoutExpired:
        logger.error("⏱️  デプロイタイムアウト")
    except Exception as e:
        logger.error(f"💥 デプロイエラー: {e}")
    
    return None

def setup_scheduler(service_url):
    """Cloud Scheduler設定"""
    
    if not service_url:
        logger.error("サービスURLが無いためスケジューラー設定をスキップ")
        return False
    
    logger.info("⏰ Cloud Scheduler設定中...")
    
    try:
        cmd = [
            'gcloud', 'scheduler', 'jobs', 'create', 'http', 'miraikakaku-batch-job',
            '--schedule', '0 */6 * * *',  # 6時間毎
            '--uri', service_url,
            '--http-method', 'POST',
            '--location', 'us-central1',
            '--description', 'Miraikakaku batch data processing'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("✅ スケジューラー設定成功")
            return True
        else:
            logger.error(f"❌ スケジューラー設定失敗: {result.stderr}")
    except Exception as e:
        logger.error(f"💥 スケジューラーエラー: {e}")
    
    return False

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("🚀 Miraikakaku バッチ処理 Cloud Run デプロイ")
    logger.info("=" * 60)
    
    # デプロイ実行
    url = deploy_single_batch()
    
    if url:
        # スケジューラー設定
        scheduled = setup_scheduler(url)
        
        logger.info("=" * 60)
        logger.info("✅ デプロイ完了")
        logger.info(f"🌐 URL: {url}")
        logger.info(f"⏰ スケジューラー: {'設定済み' if scheduled else '設定失敗'}")
        logger.info("=" * 60)
    else:
        logger.error("デプロイ失敗")