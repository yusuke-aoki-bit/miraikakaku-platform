#!/usr/bin/env python3
"""
Cloud Run バッチサービス比較分析 - batch vs enhanced の違いを詳細調査
"""

import subprocess
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def compare_services():
    """両サービスの詳細比較"""
    
    logger.info("🔍 Cloud Run バッチサービス比較分析")
    logger.info("=" * 80)
    
    services = ['miraikakaku-batch', 'miraikakaku-batch-enhanced']
    comparison = {}
    
    for service in services:
        try:
            # サービス詳細取得
            cmd = ['gcloud', 'run', 'services', 'describe', service, '--region=us-central1', '--format=json']
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                service_data = json.loads(result.stdout)
                
                spec = service_data.get('spec', {}).get('template', {}).get('spec', {})
                metadata = service_data.get('metadata', {})
                status = service_data.get('status', {})
                
                container = spec.get('containers', [{}])[0]
                
                comparison[service] = {
                    'creation_date': metadata.get('creationTimestamp', 'Unknown'),
                    'generation': metadata.get('generation', 0),
                    'image': container.get('image', 'Unknown'),
                    'cpu_limit': container.get('resources', {}).get('limits', {}).get('cpu', 'Unknown'),
                    'memory_limit': container.get('resources', {}).get('limits', {}).get('memory', 'Unknown'),
                    'timeout': spec.get('timeoutSeconds', 'Unknown'),
                    'concurrency': spec.get('containerConcurrency', 'Unknown'),
                    'max_scale': next((ann.get('autoscaling.knative.dev/maxScale', 'Unknown') 
                                     for ann in [spec.get('containers', [{}])[0].get('annotations', {})] if ann), 
                                    'Unknown'),
                    'service_url': status.get('url', 'Unknown'),
                    'revision': status.get('latestReadyRevisionName', 'Unknown')
                }
                
                # 環境変数取得
                env_vars = container.get('env', [])
                comparison[service]['env_vars'] = {env['name']: env.get('value', 'SET') for env in env_vars}
                
            else:
                logger.error(f"❌ {service} 詳細取得失敗: {result.stderr}")
                
        except Exception as e:
            logger.error(f"💥 {service} 分析エラー: {e}")
    
    # 比較結果表示
    logger.info("📊 サービス仕様比較")
    logger.info("-" * 80)
    
    if len(comparison) == 2:
        batch_data = comparison.get('miraikakaku-batch', {})
        enhanced_data = comparison.get('miraikakaku-batch-enhanced', {})
        
        logger.info(f"{'項目':<20} {'batch':<35} {'enhanced':<35}")
        logger.info("-" * 90)
        
        # 基本情報比較
        comparisons = [
            ('作成日', 'creation_date'),
            ('世代', 'generation'),
            ('コンテナイメージ', 'image'),
            ('CPU制限', 'cpu_limit'),
            ('メモリ制限', 'memory_limit'),
            ('タイムアウト', 'timeout'),
            ('同時実行数', 'concurrency'),
            ('最大スケール', 'max_scale'),
            ('リビジョン', 'revision')
        ]
        
        for label, key in comparisons:
            batch_val = str(batch_data.get(key, 'N/A'))
            enhanced_val = str(enhanced_data.get(key, 'N/A'))
            
            # 違いがある場合はマーク
            diff_mark = " ⚠️" if batch_val != enhanced_val else ""
            
            logger.info(f"{label:<20} {batch_val:<35} {enhanced_val:<35}{diff_mark}")
        
        logger.info("")
        logger.info("🌐 URL比較")
        logger.info("-" * 80)
        logger.info(f"batch:    {batch_data.get('service_url', 'N/A')}")
        logger.info(f"enhanced: {enhanced_data.get('service_url', 'N/A')}")
        
        logger.info("")
        logger.info("🔧 環境変数比較")
        logger.info("-" * 80)
        
        # 環境変数の比較
        batch_env = batch_data.get('env_vars', {})
        enhanced_env = enhanced_data.get('env_vars', {})
        
        all_env_keys = set(batch_env.keys()) | set(enhanced_env.keys())
        
        for env_key in sorted(all_env_keys):
            batch_val = batch_env.get(env_key, '未設定')
            enhanced_val = enhanced_env.get(env_key, '未設定')
            
            diff_mark = " ⚠️" if batch_val != enhanced_val else ""
            
            logger.info(f"{env_key:<25} {batch_val:<20} {enhanced_val:<20}{diff_mark}")
    
    return comparison

def test_service_functionality():
    """両サービスの機能テスト"""
    
    logger.info("")
    logger.info("🧪 機能テスト")
    logger.info("-" * 80)
    
    services = [
        ('miraikakaku-batch', 'https://miraikakaku-batch-zbaru5v7za-uc.a.run.app'),
        ('miraikakaku-batch-enhanced', 'https://miraikakaku-batch-enhanced-zbaru5v7za-uc.a.run.app')
    ]
    
    for service_name, url in services:
        try:
            # ヘルスチェック
            health_cmd = ['curl', '-s', url, '-m', '10']
            health_result = subprocess.run(health_cmd, capture_output=True, text=True)
            
            if health_result.returncode == 0:
                try:
                    response_data = json.loads(health_result.stdout)
                    logger.info(f"{service_name}:")
                    logger.info(f"  メッセージ: {response_data.get('message', 'N/A')}")
                    logger.info(f"  バージョン: {response_data.get('version', 'N/A')}")
                    logger.info(f"  状態: {response_data.get('status', 'N/A')}")
                    
                    features = response_data.get('features', {})
                    logger.info(f"  機能:")
                    for feature, enabled in features.items():
                        status = "✅" if enabled else "❌"
                        logger.info(f"    {feature}: {status}")
                        
                except json.JSONDecodeError:
                    logger.warning(f"  ⚠️ {service_name}: JSON解析失敗")
            else:
                logger.error(f"  ❌ {service_name}: アクセス失敗")
                
        except Exception as e:
            logger.error(f"  💥 {service_name}: テストエラー - {e}")

def analyze_deployment_history():
    """デプロイ履歴分析"""
    
    logger.info("")
    logger.info("📅 デプロイ履歴分析")
    logger.info("-" * 80)
    
    try:
        # 最近のビルド取得
        cmd = ['gcloud', 'builds', 'list', '--limit=10', '--format=json']
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            builds = json.loads(result.stdout)
            
            batch_builds = []
            enhanced_builds = []
            
            for build in builds:
                build_id = build.get('id', '')
                create_time = build.get('createTime', '')
                status = build.get('status', 'Unknown')
                
                # ビルド対象を推測（完全ではないが参考情報）
                if 'batch-enhanced' in str(build.get('results', {})):
                    enhanced_builds.append((build_id[:8], create_time, status))
                elif 'batch' in str(build.get('results', {})):
                    batch_builds.append((build_id[:8], create_time, status))
            
            logger.info(f"最近のビルド（推測）:")
            logger.info(f"  batch関連: {len(batch_builds)}個")
            logger.info(f"  enhanced関連: {len(enhanced_builds)}個")
            
        else:
            logger.error(f"ビルド履歴取得失敗: {result.stderr}")
            
    except Exception as e:
        logger.error(f"デプロイ履歴分析エラー: {e}")

if __name__ == "__main__":
    # 詳細比較実行
    comparison_data = compare_services()
    
    # 機能テスト
    test_service_functionality()
    
    # デプロイ履歴
    analyze_deployment_history()
    
    logger.info("")
    logger.info("🎯 結論")
    logger.info("-" * 80)
    logger.info("両サービスの主な違いを特定しました。")
    logger.info("詳細は上記の比較結果をご確認ください。")