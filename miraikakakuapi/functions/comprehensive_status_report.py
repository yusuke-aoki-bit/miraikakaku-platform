#!/usr/bin/env python3
"""
包括的システム状況レポート - バッチ処理、DB、API全体の詳細状況
"""

import logging
import sys
import os
from datetime import datetime, timedelta
from sqlalchemy import text
import requests
import json
import subprocess

# パスを追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.database import get_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_database_status():
    """データベース状況詳細チェック"""
    logger.info("📊 データベース詳細状況")
    logger.info("="*60)
    
    db = next(get_db())
    try:
        # 基本統計
        result = db.execute(text("""
            SELECT 
                (SELECT COUNT(*) FROM stock_master WHERE is_active = 1) as active_symbols,
                (SELECT COUNT(DISTINCT symbol) FROM stock_prices) as price_symbols,
                (SELECT COUNT(*) FROM stock_prices) as price_records,
                (SELECT COUNT(DISTINCT symbol) FROM stock_predictions) as pred_symbols,
                (SELECT COUNT(*) FROM stock_predictions) as pred_records
        """))
        basic_stats = result.fetchone()
        
        logger.info(f"【基本統計】")
        logger.info(f"  アクティブ銘柄: {basic_stats[0]:,}個")
        logger.info(f"  価格データ銘柄: {basic_stats[1]}個 ({basic_stats[1]/basic_stats[0]*100:.2f}%)")
        logger.info(f"  価格データ件数: {basic_stats[2]:,}件")
        logger.info(f"  予測データ銘柄: {basic_stats[3]}個")
        logger.info(f"  予測データ件数: {basic_stats[4]:,}件")
        
        # 今日のアクティビティ
        result = db.execute(text("""
            SELECT 
                DATE(created_at) as date,
                COUNT(*) as records,
                COUNT(DISTINCT symbol) as symbols
            FROM stock_prices 
            WHERE created_at >= CURDATE() - INTERVAL 3 DAY
            GROUP BY DATE(created_at)
            ORDER BY date DESC
        """))
        daily_activity = result.fetchall()
        
        logger.info(f"\n【過去3日間の価格データ追加】")
        for date, records, symbols in daily_activity:
            logger.info(f"  {date}: {records:,}件 ({symbols}銘柄)")
        
        result = db.execute(text("""
            SELECT 
                DATE(created_at) as date,
                COUNT(*) as records,
                COUNT(DISTINCT symbol) as symbols
            FROM stock_predictions 
            WHERE created_at >= CURDATE() - INTERVAL 3 DAY
            GROUP BY DATE(created_at)
            ORDER BY date DESC
        """))
        daily_pred_activity = result.fetchall()
        
        logger.info(f"\n【過去3日間の予測データ追加】")
        for date, records, symbols in daily_pred_activity:
            logger.info(f"  {date}: {records:,}件 ({symbols}銘柄)")
        
        # 外部キー制約の問題分析
        logger.info(f"\n【外部キー制約分析】")
        
        # 価格データで外部キーが存在しない銘柄
        result = db.execute(text("""
            SELECT DISTINCT sp.symbol 
            FROM stock_prices sp 
            LEFT JOIN stock_master sm ON sp.symbol = sm.symbol 
            WHERE sm.symbol IS NULL
        """))
        orphan_price_symbols = [row[0] for row in result]
        
        # 予測データで外部キーが存在しない銘柄
        result = db.execute(text("""
            SELECT DISTINCT spr.symbol 
            FROM stock_predictions spr 
            LEFT JOIN stock_master sm ON spr.symbol = sm.symbol 
            WHERE sm.symbol IS NULL
        """))
        orphan_pred_symbols = [row[0] for row in result]
        
        logger.info(f"  価格データの孤立銘柄: {len(orphan_price_symbols)}個")
        if orphan_price_symbols:
            logger.info(f"    例: {', '.join(orphan_price_symbols[:5])}")
        
        logger.info(f"  予測データの孤立銘柄: {len(orphan_pred_symbols)}個")
        if orphan_pred_symbols:
            logger.info(f"    例: {', '.join(orphan_pred_symbols[:5])}")
        
        # データ品質チェック
        result = db.execute(text("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN open_price IS NULL THEN 1 ELSE 0 END) as null_open,
                SUM(CASE WHEN high_price IS NULL THEN 1 ELSE 0 END) as null_high,
                SUM(CASE WHEN low_price IS NULL THEN 1 ELSE 0 END) as null_low,
                SUM(CASE WHEN close_price IS NULL THEN 1 ELSE 0 END) as null_close,
                SUM(CASE WHEN volume = 0 THEN 1 ELSE 0 END) as zero_volume
            FROM stock_prices
        """))
        quality_stats = result.fetchone()
        
        logger.info(f"\n【データ品質】")
        logger.info(f"  総レコード: {quality_stats[0]:,}件")
        logger.info(f"  NULL開始価格: {quality_stats[1]}件 ({quality_stats[1]/quality_stats[0]*100:.1f}%)")
        logger.info(f"  NULL高値: {quality_stats[2]}件 ({quality_stats[2]/quality_stats[0]*100:.1f}%)")
        logger.info(f"  NULL安値: {quality_stats[3]}件 ({quality_stats[3]/quality_stats[0]*100:.1f}%)")
        logger.info(f"  NULL終値: {quality_stats[4]}件 ({quality_stats[4]/quality_stats[0]*100:.1f}%)")
        logger.info(f"  ゼロ出来高: {quality_stats[5]}件 ({quality_stats[5]/quality_stats[0]*100:.1f}%)")
        
        return {
            'active_symbols': basic_stats[0],
            'price_symbols': basic_stats[1],
            'price_records': basic_stats[2],
            'pred_symbols': basic_stats[3],
            'pred_records': basic_stats[4],
            'orphan_price_symbols': len(orphan_price_symbols),
            'orphan_pred_symbols': len(orphan_pred_symbols)
        }
        
    finally:
        db.close()

def check_batch_processes():
    """バッチ処理状況チェック"""
    logger.info("\n🔄 バッチ処理状況")
    logger.info("="*60)
    
    # ログファイル一覧
    log_files = [
        'batch_progress.log',
        'massive_expansion.log', 
        'turbo_expansion.log',
        'instant_mega_boost.log',
        'ultimate_system.log',
        'continuous_pipeline.log',
        'synthetic_boost.log',
        'quick_boost.log'
    ]
    
    batch_status = {}
    
    for log_file in log_files:
        if os.path.exists(log_file):
            try:
                # ファイルサイズ
                size = os.path.getsize(log_file)
                
                # 最新の更新時間
                mtime = os.path.getmtime(log_file)
                last_update = datetime.fromtimestamp(mtime)
                
                # 最後の数行を読む
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    last_lines = lines[-5:] if len(lines) >= 5 else lines
                
                # エラー数をカウント
                error_count = sum(1 for line in lines if 'ERROR' in line or 'エラー' in line)
                
                batch_status[log_file] = {
                    'size': size,
                    'last_update': last_update,
                    'total_lines': len(lines),
                    'error_count': error_count,
                    'last_lines': [line.strip() for line in last_lines],
                    'active': (datetime.now() - last_update).seconds < 300  # 5分以内に更新
                }
                
                logger.info(f"📄 {log_file}")
                logger.info(f"  サイズ: {size:,} bytes")
                logger.info(f"  最終更新: {last_update.strftime('%Y-%m-%d %H:%M:%S')}")
                logger.info(f"  総行数: {len(lines):,}")
                logger.info(f"  エラー数: {error_count}")
                logger.info(f"  状態: {'🟢 アクティブ' if batch_status[log_file]['active'] else '🔴 停止中'}")
                
                if last_lines:
                    logger.info(f"  最新ログ:")
                    for line in last_lines[-2:]:  # 最後の2行のみ表示
                        if line.strip():
                            logger.info(f"    {line}")
                
            except Exception as e:
                logger.error(f"  ❌ ログ読み取りエラー: {e}")
                batch_status[log_file] = {'error': str(e)}
        else:
            logger.info(f"📄 {log_file}: ❌ ファイル未存在")
            batch_status[log_file] = {'missing': True}
        
        logger.info("")
    
    return batch_status

def check_api_status():
    """API状況チェック"""
    logger.info("\n🌐 API状況")
    logger.info("="*60)
    
    api_status = {}
    
    # APIが起動しているかチェック
    try:
        response = requests.get('http://localhost:8001/health', timeout=5)
        api_status['health'] = {
            'status_code': response.status_code,
            'response': response.json() if response.status_code == 200 else None,
            'accessible': True
        }
        logger.info("🟢 API サーバー: 稼働中")
        logger.info(f"  ヘルスチェック: {response.status_code}")
        
        if response.status_code == 200:
            logger.info(f"  レスポンス: {response.json()}")
        
    except requests.exceptions.RequestException as e:
        api_status['health'] = {
            'accessible': False,
            'error': str(e)
        }
        logger.info("🔴 API サーバー: 停止中または接続不可")
        logger.info(f"  エラー: {e}")
    
    # 各エンドポイントをテスト
    endpoints = [
        '/api/finance/stock/AAPL/price',
        '/api/finance/stock/AAPL/predictions',
        '/api/finance/stocks/list'
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f'http://localhost:8001{endpoint}', timeout=5)
            api_status[endpoint] = {
                'status_code': response.status_code,
                'accessible': True,
                'response_size': len(response.content) if response.content else 0
            }
            
            logger.info(f"📍 {endpoint}")
            logger.info(f"  ステータス: {response.status_code}")
            logger.info(f"  レスポンスサイズ: {len(response.content)} bytes")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, dict):
                        logger.info(f"  データ件数: {len(data)} keys")
                    elif isinstance(data, list):
                        logger.info(f"  データ件数: {len(data)} items")
                except:
                    logger.info("  レスポンス: JSON以外")
            
        except requests.exceptions.RequestException as e:
            api_status[endpoint] = {
                'accessible': False,
                'error': str(e)
            }
            logger.info(f"📍 {endpoint}: ❌ アクセス不可 - {e}")
    
    return api_status

def check_system_resources():
    """システムリソース状況"""
    logger.info("\n💻 システムリソース")
    logger.info("="*60)
    
    try:
        # プロセス一覧（Python関連）
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        if result.returncode == 0:
            python_processes = [line for line in result.stdout.split('\n') if 'python' in line.lower()]
            logger.info(f"🐍 Python プロセス: {len(python_processes)}個実行中")
            
            # バッチ処理関連のプロセスをカウント
            batch_processes = [p for p in python_processes if any(batch in p for batch in ['batch', 'expansion', 'boost', 'pipeline'])]
            logger.info(f"🔄 バッチ関連プロセス: {len(batch_processes)}個")
            
            if batch_processes:
                logger.info("  実行中のバッチプロセス:")
                for proc in batch_processes[:5]:  # 最初の5個のみ表示
                    logger.info(f"    {proc.split()[-1] if proc.split() else 'Unknown'}")
        
        # ディスク使用量
        result = subprocess.run(['df', '-h', '.'], capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                disk_info = lines[1].split()
                logger.info(f"💾 ディスク使用量: {disk_info[2]}/{disk_info[1]} ({disk_info[4]})")
        
        # メモリ使用量（簡易）
        try:
            with open('/proc/meminfo', 'r') as f:
                meminfo = f.read()
                for line in meminfo.split('\n'):
                    if 'MemTotal:' in line:
                        total_mem = int(line.split()[1]) // 1024
                        logger.info(f"🧠 総メモリ: {total_mem:,} MB")
                        break
        except:
            logger.info("🧠 メモリ情報: 取得不可")
    
    except Exception as e:
        logger.info(f"❌ システム情報取得エラー: {e}")

def generate_comprehensive_status_report():
    """包括的状況レポート生成"""
    logger.info("="*80)
    logger.info("📋 Miraikakaku システム包括的状況レポート")
    logger.info(f"🕐 生成時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("="*80)
    
    # 1. データベース状況
    db_status = check_database_status()
    
    # 2. バッチ処理状況
    batch_status = check_batch_processes()
    
    # 3. API状況
    api_status = check_api_status()
    
    # 4. システムリソース
    check_system_resources()
    
    # 5. 総合評価
    logger.info("\n🎯 総合評価")
    logger.info("="*60)
    
    # データ充実度
    data_completeness = (db_status['price_records'] / 100000) * 100
    symbol_coverage = (db_status['price_symbols'] / db_status['active_symbols']) * 100
    
    logger.info(f"📊 データ充実度:")
    logger.info(f"  価格データ: {data_completeness:.2f}% (目標100,000件に対し{db_status['price_records']:,}件)")
    logger.info(f"  銘柄カバー率: {symbol_coverage:.2f}% ({db_status['price_symbols']}/{db_status['active_symbols']}銘柄)")
    logger.info(f"  予測データ: {db_status['pred_records']:,}件")
    
    # バッチ処理状況
    active_batches = sum(1 for status in batch_status.values() 
                        if isinstance(status, dict) and status.get('active', False))
    total_batches = len([f for f in batch_status.keys() if not batch_status[f].get('missing', False)])
    
    logger.info(f"\n🔄 バッチ処理状況:")
    logger.info(f"  アクティブ: {active_batches}/{total_batches}")
    logger.info(f"  総エラー数: {sum(status.get('error_count', 0) for status in batch_status.values() if isinstance(status, dict))}")
    
    # API状況
    api_accessible = api_status.get('health', {}).get('accessible', False)
    logger.info(f"\n🌐 API状況:")
    logger.info(f"  アクセス可能: {'✅' if api_accessible else '❌'}")
    
    # 問題点と推奨事項
    logger.info(f"\n🚨 検出された問題:")
    issues = []
    
    if db_status['orphan_price_symbols'] > 0:
        issues.append(f"価格データに{db_status['orphan_price_symbols']}個の外部キー制約違反")
    if db_status['orphan_pred_symbols'] > 0:
        issues.append(f"予測データに{db_status['orphan_pred_symbols']}個の外部キー制約違反")
    if not api_accessible:
        issues.append("APIサーバーにアクセスできません")
    if active_batches == 0:
        issues.append("バッチ処理が全て停止中です")
    
    if issues:
        for i, issue in enumerate(issues, 1):
            logger.info(f"  {i}. {issue}")
    else:
        logger.info("  ✅ 重大な問題は検出されませんでした")
    
    logger.info(f"\n💡 推奨事項:")
    recommendations = []
    
    if symbol_coverage < 1:
        recommendations.append("より多くの銘柄でデータ収集を実行")
    if data_completeness < 10:
        recommendations.append("価格データの大幅な増加が必要")
    if db_status['orphan_price_symbols'] > 0 or db_status['orphan_pred_symbols'] > 0:
        recommendations.append("外部キー制約の修正またはstock_masterテーブルの更新")
    if active_batches < 3:
        recommendations.append("停止中のバッチ処理の再起動")
    
    if recommendations:
        for i, rec in enumerate(recommendations, 1):
            logger.info(f"  {i}. {rec}")
    else:
        logger.info("  ✅ 現在の状況は良好です")
    
    logger.info("="*80)
    
    return {
        'database': db_status,
        'batches': batch_status,
        'api': api_status,
        'data_completeness': data_completeness,
        'symbol_coverage': symbol_coverage,
        'active_batches': active_batches,
        'issues': issues,
        'recommendations': recommendations
    }

if __name__ == "__main__":
    report = generate_comprehensive_status_report()
    logger.info("✅ 包括的状況レポート完了")